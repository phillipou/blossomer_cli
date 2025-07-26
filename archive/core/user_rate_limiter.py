import os
import time
import asyncio
import logging
from typing import Optional, Dict, Tuple, Any, Callable
from fastapi import Request, Response, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.auth import validate_stack_auth_jwt
from app.core.database import get_db
from app.models import User, UserRole

try:
    import redis.asyncio as aioredis  # noqa: E402
except ImportError:
    aioredis = None  # type: ignore

logger = logging.getLogger(__name__)


class UserRateLimiter:
    """
    JWT-based user rate limiter for authenticated endpoints. Supports Redis (preferred) and in-memory fallback.
    Implements tiered rate limiting based on user subscription/role with admin bypass.
    """

    # Rate limit tiers based on design document
    RATE_LIMIT_TIERS = {
        "free": {
            "company_generate": {"limit": 10, "window": 3600},       # 10/hour
            "account_generate": {"limit": 20, "window": 3600},       # 20/hour
            "persona_generate": {"limit": 20, "window": 3600},       # 20/hour
            "campaign_generate": {"limit": 5, "window": 3600},       # 5/hour
            "daily_total": {"limit": 100, "window": 86400},          # 100/day
            "monthly_total": {"limit": 1000, "window": 2592000},     # 1000/month
        },
        "pro": {
            "company_generate": {"limit": 100, "window": 3600},
            "account_generate": {"limit": 200, "window": 3600},
            "persona_generate": {"limit": 200, "window": 3600},
            "campaign_generate": {"limit": 50, "window": 3600},
            "daily_total": {"limit": 1000, "window": 86400},
            "monthly_total": {"limit": 10000, "window": 2592000},
        },
        "enterprise": {
            "company_generate": {"limit": 1000, "window": 3600},
            "account_generate": {"limit": 2000, "window": 3600},
            "persona_generate": {"limit": 2000, "window": 3600},
            "campaign_generate": {"limit": 500, "window": 3600},
            "daily_total": {"limit": 10000, "window": 86400},
            "monthly_total": {"limit": 100000, "window": 2592000},
        },
    }

    # Development environment has relaxed limits
    DEV_RATE_LIMITS = {
        "free": {
            "company_generate": {"limit": 1000, "window": 3600},
            "account_generate": {"limit": 1000, "window": 3600},
            "persona_generate": {"limit": 1000, "window": 3600},
            "campaign_generate": {"limit": 1000, "window": 3600},
            "daily_total": {"limit": 10000, "window": 86400},
            "monthly_total": {"limit": 100000, "window": 2592000},
        }
    }

    def __init__(self, redis_url: Optional[str] = None) -> None:
        self.redis_url = redis_url
        self.redis: Optional[Any] = None
        self.in_memory: Dict[str, Dict[str, Any]] = {}
        self.lock = asyncio.Lock()
        self.is_dev = os.getenv("ENVIRONMENT", "development").lower() == "development"
        
        if redis_url and aioredis:
            self.redis = aioredis.from_url(
                redis_url, encoding="utf-8", decode_responses=True
            )
        else:
            logger.warning(
                "UserRateLimiter: Using in-memory fallback (not suitable for production)"
            )

    def _get_rate_limits(self) -> Dict[str, Dict[str, Dict[str, int]]]:
        """Get rate limits based on environment"""
        if self.is_dev:
            return self.DEV_RATE_LIMITS
        return self.RATE_LIMIT_TIERS

    async def is_admin(self, user_id: str, db: Session) -> bool:
        """Check if user has admin role for rate limit bypass"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            return user.role in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]
        except Exception as e:
            logger.error(f"Error checking admin status for user {user_id}: {e}")
            return False

    async def get_user_tier(self, user_id: str, db: Session) -> str:
        """Get user subscription tier. Currently defaults to 'free', can be extended."""
        try:
            # Try Redis cache first
            if self.redis:
                cached_tier = await self.redis.get(f"user_tier:{user_id}")
                if cached_tier:
                    return cached_tier

            # For now, all users are on free tier
            # This can be extended to check subscription status from database
            tier = "free"
            
            # Cache in Redis for 1 hour
            if self.redis:
                await self.redis.setex(f"user_tier:{user_id}", 3600, tier)
                
            return tier
        except Exception as e:
            logger.error(f"Error getting user tier for {user_id}: {e}")
            return "free"

    async def check_user_limit(
        self, user_id: str, endpoint: str, tier: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if the user is within rate limits for the endpoint.
        Returns (is_allowed, rate_info_dict)
        """
        limits = self._get_rate_limits()
        tier_limits = limits.get(tier, limits["free"])
        now = int(time.time())
        
        # Check endpoint-specific limit
        endpoint_key = f"user_rate_limit:{endpoint}:{user_id}"
        endpoint_conf = tier_limits.get(endpoint, {"limit": 10, "window": 3600})
        
        # Check daily total limit
        today = time.strftime("%Y-%m-%d", time.gmtime(now))
        daily_key = f"user_rate_limit:daily:{user_id}:{today}"
        daily_conf = tier_limits.get("daily_total", {"limit": 100, "window": 86400})
        
        # Check monthly total limit
        year_month = time.strftime("%Y-%m", time.gmtime(now))
        monthly_key = f"user_rate_limit:monthly:{user_id}:{year_month}"
        monthly_conf = tier_limits.get("monthly_total", {"limit": 1000, "window": 2592000})
        
        results: Dict[str, Dict[str, Any]] = {}
        allowed = True
        
        # Check all limits
        for key, conf in [
            (endpoint_key, endpoint_conf),
            (daily_key, daily_conf),
            (monthly_key, monthly_conf),
        ]:
            if self.redis:
                allowed_key, info = await self._check_redis(key, conf, now)
            else:
                allowed_key, info = await self._check_memory(key, conf, now)
            results[key] = info
            if not allowed_key:
                allowed = False
        
        # Compose rate info for response headers
        info = self._compose_rate_info(results, endpoint_conf, tier, now)
        return allowed, info

    async def _check_redis(
        self, key: str, conf: Dict[str, int], now: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit using Redis backend"""
        assert self.redis is not None
        window = conf["window"]
        limit = conf["limit"]
        
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.ttl(key)
        res = await pipe.execute()
        count, ttl = res[0], res[1]
        
        if ttl == -1:
            await self.redis.expire(key, window)
            ttl = window
            
        allowed = count <= limit
        reset = now + (ttl if ttl > 0 else window)
        
        info = {
            "limit": limit,
            "remaining": max(0, limit - count),
            "reset": reset,
            "count": count,
        }
        return allowed, info

    async def _check_memory(
        self, key: str, conf: Dict[str, int], now: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit using in-memory fallback"""
        async with self.lock:
            window = conf["window"]
            limit = conf["limit"]
            entry = self.in_memory.get(key)
            
            if not entry or entry["reset"] <= now:
                entry = {"count": 1, "reset": now + window}
            else:
                entry["count"] += 1
                
            self.in_memory[key] = entry
            self._cleanup_memory(now)
            
            allowed = entry["count"] <= limit
            info = {
                "limit": limit,
                "remaining": max(0, limit - entry["count"]),
                "reset": entry["reset"],
                "count": entry["count"],
            }
            return allowed, info

    def _cleanup_memory(self, now: int) -> None:
        """Clean up expired entries from in-memory storage"""
        expired = [k for k, v in self.in_memory.items() if v["reset"] <= now]
        for k in expired:
            del self.in_memory[k]

    def _compose_rate_info(
        self,
        results: Dict[str, Dict[str, Any]],
        endpoint_conf: Dict[str, int],
        tier: str,
        now: int,
    ) -> Dict[str, Any]:
        """Compose rate limit info for response headers"""
        infos = list(results.values())
        if not infos:
            return {
                "limit": endpoint_conf["limit"],
                "remaining": endpoint_conf["limit"],
                "reset": now + endpoint_conf["window"],
                "tier": tier,
            }
            
        # Use the most restrictive limit for headers
        min_remaining = min(i["remaining"] for i in infos)
        min_reset = min(i["reset"] for i in infos)
        
        return {
            "limit": endpoint_conf["limit"],
            "remaining": min_remaining,
            "reset": min_reset,
            "tier": tier,
        }


# Global instance
_user_rate_limiter: Optional[UserRateLimiter] = None


def get_user_rate_limiter() -> UserRateLimiter:
    """Get global UserRateLimiter instance"""
    global _user_rate_limiter
    if _user_rate_limiter is None:
        redis_url = os.getenv("REDIS_URL")
        _user_rate_limiter = UserRateLimiter(redis_url)
    return _user_rate_limiter


def jwt_rate_limit_dependency(endpoint: str) -> Callable:
    """
    FastAPI dependency for JWT-based user rate limiting.
    Usage: Depends(jwt_rate_limit_dependency("company_generate"))
    """
    
    async def dependency(
        request: Request,
        response: Response,
        user=Depends(validate_stack_auth_jwt),
        db: Session = Depends(get_db)
    ):
        user_id = user["sub"]
        limiter = get_user_rate_limiter()
        
        # Check if user is admin - bypass rate limiting
        if await limiter.is_admin(user_id, db):
            response.headers["X-RateLimit-Bypass"] = "admin"
            return
        
        # Regular rate limiting for non-admin users
        tier = await limiter.get_user_tier(user_id, db)
        
        try:
            allowed, info = await limiter.check_user_limit(user_id, endpoint, tier)
        except Exception as e:
            logger.error(f"Rate limiting error for user {user_id}: {e}")
            # Allow request but log error for monitoring
            allowed, info = True, {
                "limit": 100,
                "remaining": 100,
                "reset": int(time.time()) + 3600,
                "tier": tier,
            }
        
        # Set rate limit headers
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
        response.headers["X-RateLimit-Tier"] = info.get("tier", tier)
        response.headers["X-RateLimit-Scope"] = "endpoint"
        
        if not allowed:
            retry_after = max(1, info["reset"] - int(time.time()))
            response.headers["Retry-After"] = str(retry_after)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Rate limit exceeded for {tier} tier. "
                    "Upgrade your plan for higher limits."
                ),
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": str(info["remaining"]),
                    "X-RateLimit-Reset": str(info["reset"]),
                    "X-RateLimit-Tier": info.get("tier", tier),
                },
            )
    
    return dependency