"""
Demo endpoints for unauthenticated users.

This router provides endpoints for demonstration purposes, with IP-based rate limiting
instead of JWT authentication. These routes mirror the functionality of the core AI
generation endpoints but are intended for trial usage.
"""
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.demo_rate_limiter import demo_ip_rate_limit_dependency
from app.schemas import (
    ProductOverviewRequest,
    ProductOverviewResponse,
    TargetAccountRequest,
    TargetAccountResponse,
    TargetPersonaRequest,
    TargetPersonaResponse,
    EmailGenerationRequest,
    EmailGenerationResponse,
)
from app.services.context_orchestrator_agent import ContextOrchestrator
from app.services.email_generation_service import (
    generate_email_campaign_service,
)
from app.services.product_overview_service import (
    generate_product_overview_service,
)
from app.services.target_account_service import generate_target_account_profile
from app.services.target_persona_service import generate_target_persona_profile

from app.api.helpers import run_service

router = APIRouter()

@router.post(
    "/companies/generate-ai",
    response_model=ProductOverviewResponse,
    summary="[DEMO] AI Generate Company Overview (features, company & persona profiles, pricing)",
    tags=["Demo", "Companies", "AI"],
    response_description="A structured company overview for the given company context.",
)
async def demo_generate_product_overview(
    data: ProductOverviewRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _: None = Depends(demo_ip_rate_limit_dependency("company_generate")),
):
    """
    AI-generate a company overview for demo users, with IP-based rate limiting.
    """
    orchestrator = ContextOrchestrator()
    return await run_service(
        generate_product_overview_service, data, orchestrator=orchestrator
    )

@router.post(
    "/accounts/generate-ai",
    response_model=TargetAccountResponse,
    summary="[DEMO] AI Generate Target Account Profile (discovery call preparation)",
    tags=["Demo", "Accounts", "AI"],
    response_description="A structured discovery call preparation report with company analysis and ICP hypothesis.",
)
async def demo_generate_target_account(
    data: TargetAccountRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    AI-generate a target account profile for demo users, with IP-based rate limiting.
    """
    return await run_service(generate_target_account_profile, data)

@router.post(
    "/personas/generate-ai",
    response_model=TargetPersonaResponse,
    summary="[DEMO] AI Generate Target Persona Profile (attributes, buying signals, rationale)",
    tags=["Demo", "Personas", "AI"],
    response_description="A structured target persona profile for the given company context.",
)
async def demo_generate_target_persona(
    data: TargetPersonaRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    AI-generate a target persona profile for demo users, with IP-based rate limiting.
    """
    return await run_service(generate_target_persona_profile, data)

@router.post(
    "/campaigns/generate-ai",
    response_model=EmailGenerationResponse,
    summary="[DEMO] AI Generate Email Campaign",
    tags=["Demo", "Campaigns", "AI"],
    response_description="A complete email campaign with subjects, body segments, and breakdown metadata.",
)
async def demo_generate_email(
    request: EmailGenerationRequest,
    req: Request,
    res: Response,
    db: Session = Depends(get_db),
    _: None = Depends(demo_ip_rate_limit_dependency("email_generation")),
):
    """
    AI-generate a personalized email campaign for demo users, with IP-based rate limiting.
    """
    orchestrator = ContextOrchestrator()
    return await run_service(
        generate_email_campaign_service, request, orchestrator=orchestrator
    ) 