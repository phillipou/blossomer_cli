from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.schemas import (
    EmailGenerationRequest,
    EmailGenerationResponse,
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
)
from app.services.email_generation_service import (
    generate_email_campaign_service,
)
from app.services.context_orchestrator_agent import ContextOrchestrator
from app.services.database_service import DatabaseService
from sqlalchemy.orm import Session
from app.core.user_rate_limiter import jwt_rate_limit_dependency
from app.core.auth import validate_stack_auth_jwt

from app.api.helpers import run_service


class UniqueSellingPoint(BaseModel):
    theme: str = Field(..., description="USP name or theme")
    description: str = Field(..., description="Brief benefit or outcome")
    evidence: List[str] = Field(..., description="Supporting details or explanations")


class PositioningResponse(BaseModel):
    unique_insight: str = Field(
        ...,
        description=("Core reframe of the problem (unique insight)"),
    )
    unique_selling_points: List[UniqueSellingPoint] = Field(
        ...,
        description=("List of unique selling points (USPs)"),
    )


router = APIRouter()


@router.post(
    "/positioning",
    response_model=PositioningResponse,
    summary="Generate Unique Insight and Unique Selling Points",
    tags=["Campaigns", "Positioning", "AI"],
    response_description=(
        "A unique insight and a list of unique selling points for the given company context."
    ),
)
async def generate_positioning(
    data: dict,  # Should be replaced with a proper request model if available
    user=Depends(validate_stack_auth_jwt),
    db: Session = Depends(get_db),
    _: None = Depends(jwt_rate_limit_dependency("campaign_generate")),
):
    # Placeholder implementation, replace with actual logic as needed
    return PositioningResponse(
        unique_insight=(
            "Most B2B marketing tools focus on automation, but the real bottleneck is "
            "understanding what actually resonates with buyers. Blossomer reframes the "
            "problem: it's not about sending more messages, but about crafting the right "
            "message for the right ICP at the right time."
        ),
        unique_selling_points=[
            UniqueSellingPoint(
                theme="Buyer-Centric Messaging",
                description=(
                    "Delivers messaging tailored to the emotional and practical needs of "
                    "your ICP."
                ),
                evidence=[
                    "Analyzes ICP pain points and language",
                    "Adapts messaging based on real buyer feedback",
                ],
            ),
            UniqueSellingPoint(
                theme="Rapid Time to Value",
                description=("Get actionable campaign assets in minutes, not weeks."),
                evidence=[
                    "Automated campaign generation",
                    "No manual copywriting required",
                ],
            ),
        ],
    )


@router.post(
    "/generate-ai",
    response_model=EmailGenerationResponse,
    summary="AI Generate Email Campaign",
    tags=["Campaigns", "AI"],
    response_description="A complete email campaign with subjects, body segments, and breakdown metadata.",
)
async def generate_email(
    request: EmailGenerationRequest,
    user=Depends(validate_stack_auth_jwt),
    db: Session = Depends(get_db),
    _: None = Depends(jwt_rate_limit_dependency("campaign_generate")),
):
    """
    AI-generate a personalized email campaign based on company context, target account/persona, and user preferences.
    """
    orchestrator = ContextOrchestrator()
    return await run_service(
        generate_email_campaign_service, request, orchestrator=orchestrator
    )


# CRUD Operations for Campaign Management
# ======================================


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    account_id: UUID = Query(..., description="Account ID to create campaign for"),
    persona_id: UUID = Query(..., description="Persona ID to create campaign for"),
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Create a new campaign for an account and persona.

    - **account_id**: Account ID (must be owned by authenticated user via company)
    - **persona_id**: Persona ID (must belong to the account)
    - **name**: Campaign name (required, max 255 chars)
    - **type**: Campaign type (email, linkedin, cold_call, ad)
    - **data**: JSON data with subject_line, content, segments, etc.
    """
    db_service = DatabaseService(db)
    return db_service.create_campaign(
        campaign_data, account_id, persona_id, user["sub"]
    )


@router.get("", response_model=List[CampaignResponse])
async def get_campaigns(
    account_id: UUID = Query(..., description="Account ID to get campaigns for"),
    persona_id: Optional[UUID] = Query(
        None, description="Optional persona ID to filter by"
    ),
    skip: int = Query(0, ge=0, description="Number of campaigns to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of campaigns to return"
    ),
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Get all campaigns for an account.

    - **account_id**: Account ID (must be owned by authenticated user via company)
    - **persona_id**: Optional persona ID to filter campaigns
    - **skip**: Number of campaigns to skip (for pagination)
    - **limit**: Maximum number of campaigns to return (1-1000)
    """
    db_service = DatabaseService(db)
    return db_service.get_campaigns(
        account_id, user["sub"], persona_id=persona_id, skip=skip, limit=limit
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Get a specific campaign by ID.

    Only returns campaigns owned by the authenticated user (via account->company).
    """
    db_service = DatabaseService(db)
    return db_service.get_campaign(campaign_id, user["sub"])


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    campaign_data: CampaignUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Update a campaign.

    Only updates campaigns owned by the authenticated user (via account->company).
    All fields are optional - only provided fields will be updated.
    """
    db_service = DatabaseService(db)
    return db_service.update_campaign(campaign_id, campaign_data, user["sub"])


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Delete a campaign.

    Only deletes campaigns owned by the authenticated user (via account->company).
    """
    db_service = DatabaseService(db)
    db_service.delete_campaign(campaign_id, user["sub"])
    return None
