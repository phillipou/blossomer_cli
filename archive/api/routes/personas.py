from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query, HTTPException
from app.schemas import (
    TargetPersonaRequest,
    TargetPersonaResponse,
    PersonaCreate,
    PersonaUpdate,
    PersonaResponse,
    PersonaWithRelations,
)
from app.services.target_persona_service import generate_target_persona_profile
from app.services.database_service import DatabaseService
from app.core.database import get_db
from app.core.auth import validate_stack_auth_jwt
from app.core.user_rate_limiter import jwt_rate_limit_dependency
from sqlalchemy.orm import Session

from app.api.helpers import run_service


router = APIRouter()


@router.post(
    "/personas/generate-ai",
    response_model=TargetPersonaResponse,
    summary="AI Generate Target Persona Profile (attributes, buying signals, rationale)",
    tags=["Personas", "AI"],
    response_description="A structured target persona profile for the given company context.",
)
async def prod_generate_target_persona(
    data: TargetPersonaRequest,
    user=Depends(validate_stack_auth_jwt),
    db: Session = Depends(get_db),
    _: None = Depends(jwt_rate_limit_dependency("persona_generate")),
):
    """
    AI-generate a target persona profile for authenticated users (Stack Auth JWT required).
    """
    return await run_service(generate_target_persona_profile, data)


# CRUD Operations for Persona Management
# =====================================


@router.post(
    "/personas", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED
)
async def create_persona(
    persona_data: PersonaCreate,
    account_id: UUID = Query(..., description="Account ID to create persona for"),
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Create a new persona for an account.
    """
    db_service = DatabaseService(db)
    return db_service.create_persona(persona_data, account_id, user["sub"])


# ---
# GET /personas endpoint supports flexible filtering:
# - Both company_id and account_id: personas for account if it belongs to company (404 otherwise)
# - Only company_id: all personas for all accounts in company
# - Only account_id: all personas for that account
# - Neither: all personas for all user accounts (403 if user has no accounts)
# ---


@router.get("/personas", response_model=List[PersonaResponse])
async def get_personas(
    account_id: UUID = Query(None, description="Account ID to get personas for"),
    company_id: UUID = Query(
        None, description="Company ID to get personas for all accounts in company"
    ),
    skip: int = Query(0, ge=0, description="Number of personas to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of personas to return"
    ),
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Get personas with flexible filtering:
    - If both company_id and account_id are provided, return personas for the account only if it
      belongs to the company (404 otherwise). (Efficient: early return)
    - If only company_id is provided, return all personas for all accounts in the company.
    - If only account_id is provided, return all personas for that account.
    - If neither is provided, return all personas for all accounts the user has access to (403 if user
      has no accounts).
    """
    db_service = DatabaseService(db)

    # Efficient: Early return if both company_id and account_id are provided
    if company_id and account_id:
        account = db_service.get_account(account_id, user["sub"])
        if not account or str(account.company_id) != str(company_id):
            raise HTTPException(
                status_code=404, detail="Account does not belong to company"
            )
        return db_service.get_personas(account_id, user["sub"], skip=skip, limit=limit)

    # Only company_id provided: all personas for all accounts in company
    elif company_id:
        accounts = db_service.get_accounts(company_id, user["sub"], skip=0, limit=limit)
        personas = []
        for acc in accounts:
            personas.extend(
                db_service.get_personas(acc.id, user["sub"], skip=0, limit=limit)
            )
        return personas

    # Only account_id provided: all personas for that account
    elif account_id:
        return db_service.get_personas(account_id, user["sub"], skip=skip, limit=limit)

    # Neither provided: all personas for all user accounts
    else:
        companies = db_service.get_companies(user["sub"], skip=0, limit=100)
        if not companies:
            raise HTTPException(
                status_code=403, detail="User has no companies/accounts"
            )
        personas = []
        for company in companies:
            accounts = db_service.get_accounts(
                company.id, user["sub"], skip=0, limit=100
            )
            for acc in accounts:
                personas.extend(
                    db_service.get_personas(acc.id, user["sub"], skip=0, limit=limit)
                )
        return personas


@router.get("/personas/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Get a specific persona by ID.
    """
    db_service = DatabaseService(db)
    return db_service.get_persona(persona_id, user["sub"])


@router.get("/personas/{persona_id}/relations", response_model=PersonaWithRelations)
async def get_persona_with_relations(
    persona_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Get a persona with all related campaigns.
    """
    db_service = DatabaseService(db)
    return db_service.get_persona_with_relations(persona_id, user["sub"])


@router.put("/personas/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: UUID,
    persona_data: PersonaUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Update a persona.
    """
    db_service = DatabaseService(db)
    return db_service.update_persona(persona_id, persona_data, user["sub"])


@router.delete("/personas/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_persona(
    persona_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Delete a persona and all related campaigns.
    """
    db_service = DatabaseService(db)
    db_service.delete_persona(persona_id, user["sub"])
    return None
