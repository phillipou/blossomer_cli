"""
Context Store - PostgreSQL-based dynamic context management
Replaces static JSON handoffs with enriched, multi-source context
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

try:
    import asyncpg
except ImportError:
    asyncpg = None

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

logger = logging.getLogger(__name__)


class ContextUpdateSource(Enum):
    """Sources that can update context"""
    ANALYSIS_AGENT = "analysis_agent"
    HUMAN_UPLOAD = "human_upload" 
    AGENT_SUGGESTION = "agent_suggestion"
    CROSS_CLIENT_PATTERN = "cross_client_pattern"
    BEST_PRACTICE_UPDATE = "best_practice_update"


@dataclass
class ContextUpdate:
    """Represents a context update with metadata"""
    client_id: str
    source: ContextUpdateSource
    agent_type: Optional[str]
    update_data: Dict[str, Any]
    confidence: float
    requires_approval: bool
    created_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class ContextStore:
    """
    PostgreSQL-based context storage with Redis caching
    Handles dynamic, multi-source context updates
    """
    
    def __init__(self, db_url: str = None, redis_url: str = None):
        self.db_url = db_url or "postgresql://localhost/blossomer_context"
        self.redis_url = redis_url or "redis://localhost:6379"
        self.db_pool = None
        self.redis_client = None
        
    async def initialize(self):
        """Initialize database connections and create schema"""
        if asyncpg is None:
            raise ImportError("asyncpg is required for ContextStore. Install with: pip install asyncpg")
            
        self.db_pool = await asyncpg.create_pool(self.db_url)
        
        if redis is not None:
            try:
                self.redis_client = redis.from_url(self.redis_url)
                await self.redis_client.ping()
                logger.info("Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis unavailable, running without cache: {e}")
                self.redis_client = None
        
        await self._create_schema()
        logger.info("ContextStore initialized")
    
    async def _create_schema(self):
        """Create PostgreSQL schema for context storage"""
        schema_sql = """
        -- Client contexts with JSONB for flexibility
        CREATE TABLE IF NOT EXISTS client_contexts (
            id SERIAL PRIMARY KEY,
            client_id VARCHAR(255) NOT NULL,
            agent_type VARCHAR(100) NOT NULL,
            context_data JSONB NOT NULL,
            context_version INTEGER DEFAULT 1,
            performance_metrics JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(client_id, agent_type)
        );
        
        -- Context updates and approval workflow
        CREATE TABLE IF NOT EXISTS context_updates (
            id SERIAL PRIMARY KEY,
            client_id VARCHAR(255) NOT NULL,
            source VARCHAR(50) NOT NULL,
            agent_type VARCHAR(100),
            update_data JSONB NOT NULL,
            confidence REAL NOT NULL,
            requires_approval BOOLEAN DEFAULT FALSE,
            approved BOOLEAN DEFAULT FALSE,
            approved_by VARCHAR(255),
            approved_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Performance tracking for context effectiveness
        CREATE TABLE IF NOT EXISTS context_performance (
            id SERIAL PRIMARY KEY,
            client_id VARCHAR(255) NOT NULL,
            agent_type VARCHAR(100) NOT NULL,
            context_version INTEGER NOT NULL,
            metric_name VARCHAR(100) NOT NULL,
            metric_value REAL NOT NULL,
            recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Cross-client patterns (anonymized)
        CREATE TABLE IF NOT EXISTS cross_client_patterns (
            id SERIAL PRIMARY KEY,
            pattern_type VARCHAR(100) NOT NULL,
            industry VARCHAR(100),
            company_size_bucket VARCHAR(50),
            pattern_data JSONB NOT NULL,
            success_rate REAL NOT NULL,
            sample_size INTEGER NOT NULL,
            confidence_score REAL NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_client_contexts_lookup 
            ON client_contexts(client_id, agent_type);
        CREATE INDEX IF NOT EXISTS idx_context_updates_approval 
            ON context_updates(requires_approval, approved) WHERE requires_approval = true;
        CREATE INDEX IF NOT EXISTS idx_context_performance_lookup 
            ON context_performance(client_id, agent_type, recorded_at);
        CREATE INDEX IF NOT EXISTS idx_cross_client_patterns_lookup 
            ON cross_client_patterns(industry, company_size_bucket, success_rate);
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(schema_sql)
    
    async def get_context_for_agent(self, client_id: str, agent_type: str) -> Dict[str, Any]:
        """
        Get enriched context for a specific agent
        Combines client-specific context with relevant cross-client patterns
        """
        cache_key = f"context:{client_id}:{agent_type}"
        
        # Try Redis cache first
        if self.redis_client:
            try:
                cached = await self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Redis cache read failed: {e}")
        
        async with self.db_pool.acquire() as conn:
            # Get base context
            base_context = await conn.fetchrow("""
                SELECT context_data, performance_metrics, context_version
                FROM client_contexts 
                WHERE client_id = $1 AND agent_type = $2
            """, client_id, agent_type)
            
            if not base_context:
                # Return empty context for new clients
                context = {"client_id": client_id, "agent_type": agent_type}
            else:
                context = dict(base_context['context_data'])
                context['_performance_metrics'] = base_context['performance_metrics']
                context['_context_version'] = base_context['context_version']
            
            # Get client profile for pattern matching
            client_profile = await self._get_client_profile(conn, client_id)
            
            # Enrich with relevant cross-client patterns
            if client_profile:
                patterns = await conn.fetch("""
                    SELECT pattern_type, pattern_data, success_rate, confidence_score
                    FROM cross_client_patterns
                    WHERE industry = $1 AND company_size_bucket = $2
                    AND success_rate >= 0.7 AND confidence_score >= 0.8
                    ORDER BY success_rate DESC, confidence_score DESC
                    LIMIT 10
                """, client_profile.get('industry'), client_profile.get('company_size_bucket'))
                
                if patterns:
                    context['_cross_client_patterns'] = [
                        {
                            'type': p['pattern_type'],
                            'data': p['pattern_data'],
                            'success_rate': p['success_rate'],
                            'confidence': p['confidence_score']
                        }
                        for p in patterns
                    ]
        
        # Cache result
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    cache_key, 300, json.dumps(context, default=str)  # 5 min cache
                )
            except Exception as e:
                logger.warning(f"Redis cache write failed: {e}")
        
        return context
    
    async def update_context(self, update: ContextUpdate) -> bool:
        """
        Submit a context update for processing
        Returns True if update was applied immediately, False if pending approval
        """
        async with self.db_pool.acquire() as conn:
            # Store the update
            await conn.execute("""
                INSERT INTO context_updates 
                (client_id, source, agent_type, update_data, confidence, requires_approval)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, 
                update.client_id,
                update.source.value,
                update.agent_type,
                json.dumps(update.update_data),
                update.confidence,
                update.requires_approval
            )
            
            # If no approval required, apply immediately
            if not update.requires_approval:
                await self._apply_context_update(conn, update)
                await self._invalidate_cache(update.client_id, update.agent_type)
                return True
            
        return False
    
    async def _apply_context_update(self, conn, update: ContextUpdate):
        """Apply an approved context update"""
        # Upsert context data
        await conn.execute("""
            INSERT INTO client_contexts (client_id, agent_type, context_data, updated_at)
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT (client_id, agent_type) 
            DO UPDATE SET 
                context_data = client_contexts.context_data || $3,
                context_version = client_contexts.context_version + 1,
                updated_at = NOW()
        """, 
            update.client_id,
            update.agent_type or 'general',
            json.dumps(update.update_data)
        )
    
    async def _get_client_profile(self, conn, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client profile for pattern matching"""
        # This would typically come from a client profiles table
        # For now, return a simple profile
        return {
            'industry': 'technology',  # Would be from client data
            'company_size_bucket': 'small'  # Would be calculated
        }
    
    async def _invalidate_cache(self, client_id: str, agent_type: str = None):
        """Invalidate Redis cache for client context"""
        if not self.redis_client:
            return
            
        try:
            if agent_type:
                await self.redis_client.delete(f"context:{client_id}:{agent_type}")
            else:
                # Invalidate all agent contexts for client
                pattern = f"context:{client_id}:*"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
        except Exception as e:
            logger.warning(f"Cache invalidation failed: {e}")
    
    async def get_pending_approvals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get context updates pending human approval"""
        async with self.db_pool.acquire() as conn:
            updates = await conn.fetch("""
                SELECT id, client_id, source, agent_type, update_data, 
                       confidence, created_at
                FROM context_updates 
                WHERE requires_approval = true AND approved = false
                ORDER BY confidence DESC, created_at ASC
                LIMIT $1
            """, limit)
            
            return [dict(update) for update in updates]
    
    async def approve_update(self, update_id: int, approved_by: str) -> bool:
        """Approve a pending context update"""
        async with self.db_pool.acquire() as conn:
            # Get the update
            update_row = await conn.fetchrow("""
                SELECT client_id, source, agent_type, update_data, confidence
                FROM context_updates 
                WHERE id = $1 AND requires_approval = true AND approved = false
            """, update_id)
            
            if not update_row:
                return False
            
            # Mark as approved
            await conn.execute("""
                UPDATE context_updates 
                SET approved = true, approved_by = $1, approved_at = NOW()
                WHERE id = $2
            """, approved_by, update_id)
            
            # Apply the update
            update = ContextUpdate(
                client_id=update_row['client_id'],
                source=ContextUpdateSource(update_row['source']),
                agent_type=update_row['agent_type'],
                update_data=json.loads(update_row['update_data']),
                confidence=update_row['confidence'],
                requires_approval=False,
                created_at=datetime.now(),
                approved_by=approved_by,
                approved_at=datetime.now()
            )
            
            await self._apply_context_update(conn, update)
            await self._invalidate_cache(update.client_id, update.agent_type)
            
            return True
    
    async def track_performance(self, client_id: str, agent_type: str, 
                              metric_name: str, metric_value: float):
        """Track context performance metrics"""
        async with self.db_pool.acquire() as conn:
            # Get current context version
            version_row = await conn.fetchrow("""
                SELECT context_version FROM client_contexts
                WHERE client_id = $1 AND agent_type = $2
            """, client_id, agent_type)
            
            version = version_row['context_version'] if version_row else 1
            
            # Record performance
            await conn.execute("""
                INSERT INTO context_performance 
                (client_id, agent_type, context_version, metric_name, metric_value)
                VALUES ($1, $2, $3, $4, $5)
            """, client_id, agent_type, version, metric_name, metric_value)
    
    async def close(self):
        """Clean up connections"""
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_client:
            await self.redis_client.close()


# Global instance (will be initialized in main app)
context_store: Optional[ContextStore] = None


async def get_context_store() -> ContextStore:
    """Get the global context store instance"""
    global context_store
    if context_store is None:
        context_store = ContextStore()
        await context_store.initialize()
    return context_store