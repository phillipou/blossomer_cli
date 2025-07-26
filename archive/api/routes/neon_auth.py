import os
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Annotated
from datetime import datetime
from jose import jwt, JWTError
import requests
import uuid
from functools import lru_cache

from app.core.database import get_db
from app.models import User

router = APIRouter()


# Request/Response Models for Neon Auth Integration
class NeonAuthUserRequest(BaseModel):
    neon_auth_user_id: str


class UserProfileResponse(BaseModel):
    user_id: str
    neon_auth_user_id: str
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None


# --- Stack Auth JWT Validation ---
# Reads project ID from environment. Ensure you set STACK_PROJECT_ID in your .env file.
# For production, use the production project ID. For dev, use the dev project ID.
STACK_PROJECT_ID = os.environ.get("STACK_PROJECT_ID")
if not STACK_PROJECT_ID:
    raise RuntimeError(
        "STACK_PROJECT_ID not set in environment. Set this in your .env file."
    )
JWKS_URL = f"https://api.stack-auth.com/api/v1/projects/{STACK_PROJECT_ID}/.well-known/jwks.json"


@lru_cache(maxsize=1)
def get_jwks():
    resp = requests.get(JWKS_URL)
    resp.raise_for_status()
    return resp.json()


def get_public_key(token):
    jwks = get_jwks()
    unverified_header = jwt.get_unverified_header(token)
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            return key
    raise HTTPException(status_code=401, detail="Public key not found for token.")


async def validate_stack_auth_token(
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    """
    Validate Stack Auth JWT token and return user info from claims.
    - Verifies JWT signature using Stack Auth public keys (JWKS)
    - Checks token expiration
    - Extracts user information from verified token
    - Returns user data (user_id, email, name, etc.)
    """
    print("validate_stack_auth_token: Received request for token validation.")
    if not authorization or not authorization.startswith("Bearer "):
        print("validate_stack_auth_token: Missing or invalid authorization header.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    token = authorization.split(" ", 1)[1]
    print(f"validate_stack_auth_token: Attempting to validate token: {token[:30]}...")
    try:
        public_key = get_public_key(token)
        # Support both ES256 and RS256 algorithms, with ES256 being the primary
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["ES256", "RS256"],
            audience=STACK_PROJECT_ID,  # Enable audience validation
        )
        print(
            f"validate_stack_auth_token: Token is valid. Payload sub: {payload.get('sub')}"
        )

        # Extract user info from payload
        return {
            "user_id": payload.get("sub"),
        }
    except JWTError as e:
        print(f"validate_stack_auth_token: Invalid Stack Auth token. Error: {e}")
        raise HTTPException(
            status_code=401, detail=f"Invalid Stack Auth token: {str(e)}"
        )


# Routes


@router.post("/sync-user")
async def sync_neon_auth_user(
    request: NeonAuthUserRequest,
    neon_auth_user: dict = Depends(validate_stack_auth_token),
    db: Session = Depends(get_db),
):
    """
    Sync a Neon Auth user to our local user table.
    Called when a Neon Auth user first accesses the API.
    """
    # Verify the request matches the authenticated user
    if request.neon_auth_user_id != neon_auth_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User ID mismatch"
        )

    user = User(
        neon_auth_user_id=request.neon_auth_user_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User synced successfully",
        "user_id": str(user.id),
        "neon_auth_user_id": user.neon_auth_user_id,
    }


# TODO: Reimplement any needed endpoints using Stack Auth JWTs only


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    neon_auth_user: dict = Depends(validate_stack_auth_token),
    db: Session = Depends(get_db),
):
    """
    Get user profile information and API keys for authenticated Neon Auth user.
    """
    user_id = neon_auth_user.get("user_id")
    print(f"Attempting to get or create profile for user_id: {user_id}")

    # Convert string user_id to UUID for database operations
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError as e:
        print(f"Invalid UUID format for user_id: {user_id}. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )

    user = db.query(User).filter(User.id == user_uuid).first()

    if not user:
        print(f"User not found for user_id: {user_id}. Creating new user.")
        # Create user if they don't exist
        user = User(
            id=user_uuid,
            role="user",  # Explicitly set the default role
        )
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Successfully created and committed new user with ID: {user.id}")
        except Exception as e:
            print(f"Failed to commit new user for user_id: {user_id}. Error: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user profile in the database.",
            )
    else:
        print(f"User found in database with ID: {user.id}")

    return UserProfileResponse(
        user_id=str(user.id),
        neon_auth_user_id=str(
            user.id
        ),  # Use the same ID since it's the Stack Auth user ID
        role=user.role,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.delete("/user")
async def delete_user(
    neon_auth_user: dict = Depends(validate_stack_auth_token),
    db: Session = Depends(get_db),
):
    """
    Delete user from Neon database.
    This should be called when a user is deleted from Stack Auth.
    All related data (companies, accounts, personas, campaigns) will be cascade deleted.
    """
    user_id = neon_auth_user.get("user_id")
    print(f"Attempting to delete user with ID: {user_id}")

    # Convert string user_id to UUID for database operations
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError as e:
        print(f"Invalid UUID format for user_id: {user_id}. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )

    user = db.query(User).filter(User.id == user_uuid).first()

    if not user:
        print(f"User not found for user_id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found in database"
        )

    try:
        # Delete user - cascade will handle related data
        db.delete(user)
        db.commit()
        print(f"Successfully deleted user with ID: {user_id}")

        # Clear the JWKS cache to prevent any cached authentication issues
        get_jwks.cache_clear()
        print("JWKS cache cleared")

        return {
            "message": "User successfully deleted from database",
            "user_id": user_id,
        }
    except Exception as e:
        print(f"Failed to delete user for user_id: {user_id}. Error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user from database",
        )


@router.post("/logout")
async def logout(
    neon_auth_user: dict = Depends(validate_stack_auth_token),
):
    """
    Handle user logout by clearing server-side caches.
    The actual JWT invalidation should be handled by Stack Auth on the client side.
    """
    user_id = neon_auth_user.get("user_id")
    print(f"User {user_id} logging out, clearing caches")

    # Clear the JWKS cache to ensure fresh key validation
    get_jwks.cache_clear()
    print("JWKS cache cleared for logout")

    return {"message": "Logout successful, caches cleared", "user_id": user_id}


# API key management is no longer supported - authentication is now handled via Stack Auth JWT tokens
