from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db


router = APIRouter()


# Request/Response Models
class UserSignupRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserSignupResponse(BaseModel):
    user_id: str
    email: str
    name: Optional[str]
    api_key: str
    message: str


class APIKeyValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    tier: Optional[str] = None
    rate_limit_exempt: Optional[bool] = None
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None


class UserProfileResponse(BaseModel):
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    role: str
    rate_limit_exempt: bool
    created_at: datetime
    last_login: Optional[datetime]
    api_keys: List[dict]


class CreateAPIKeyRequest(BaseModel):
    name: str
    tier: str = "free"


class CreateAPIKeyResponse(BaseModel):
    api_key: str
    key_prefix: str
    name: str
    tier: str
    message: str


# Auth Endpoints


@router.post("/signup", response_model=UserSignupResponse)
async def signup(request: UserSignupRequest, db: Session = Depends(get_db)):
    """
    Create a new user account with an API key.
    """
    try:
        # This part of the code was removed as per the edit hint.
        # The original code used AuthService and authenticate_api_key.
        # The new code will need to be reimplemented using Stack Auth JWTs only.
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Signup functionality is not yet implemented using Stack Auth JWTs.",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create account: {str(e)}",
        )


@router.post("/validate", response_model=APIKeyValidationResponse)
async def validate_api_key():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="API key validation functionality is not yet implemented using Stack Auth JWTs.",
    )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User profile functionality is not yet implemented using Stack Auth JWTs.",
    )


@router.post("/api-keys", response_model=CreateAPIKeyResponse)
async def create_api_key():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="API key creation functionality is not yet implemented using Stack Auth JWTs.",
    )


@router.delete("/api-keys/{key_id}")
async def delete_api_key():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="API key deletion functionality is not yet implemented using Stack Auth JWTs.",
    )
