"""
Company CRUD endpoints with Row-Level Security.

This module provides CRUD operations for companies, with proper user scoping
and authentication through Stack Auth JWT tokens.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query, HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import validate_stack_auth_jwt
from app.services.database_service import DatabaseService
from app.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyWithRelations,
)
from app.schemas import ProductOverviewRequest, ProductOverviewResponse
from app.services.product_overview_service import (
    generate_product_overview_service,
)
from app.services.context_orchestrator_agent import ContextOrchestrator
from app.api.helpers import run_service
from pydantic import ValidationError
import uuid

# OpenAPI Examples
company_create_example = {
    "name": "TechFlow Solutions",
    "url": "https://techflowsolutions.com",
    "data": {
        "description": "AI-powered workflow automation platform for software teams",
        "business_profile": {
            "category": "B2B SaaS workflow automation",
            "business_model": "Monthly/annual subscriptions with tiered pricing",
            "existing_customers": "50+ software companies using the platform",
        },
        "capabilities": [
            "Automated code review workflows",
            "CI/CD pipeline optimization",
            "Team collaboration tools",
            "Performance analytics dashboard",
        ],
        "positioning": {
            "key_market_belief": "Manual dev processes are the biggest bottleneck in software delivery",
            "unique_approach": "AI-driven automation that learns from team patterns",
        },
    },
}

company_update_example = {
    "name": "TechFlow Solutions (Updated)",
    "data": {
        "description": "Updated: AI-powered workflow automation platform for software teams",
        "last_updated": "2024-Q4",
    },
}

router = APIRouter(tags=["companies"])


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new company from AI-generated overview",
    description="Create a new company record for the authenticated user using a "
    "pre-generated ProductOverviewResponse. This endpoint is used by the "
    "frontend's auto-save mechanism after AI generation.",
    responses={
        201: {"description": "Company created successfully"},
        400: {"description": "Invalid data provided"},
        401: {"description": "Not authenticated"},
        422: {"description": "Validation error"},
    },
)
async def create_company(
    company_overview: ProductOverviewResponse,
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Create a new company for the authenticated user from a ProductOverviewResponse.
    """
    try:
        print(f"[DEBUG] Received company_overview data: {company_overview.model_dump()}")
        print(f"[DEBUG] Required fields check:")
        print(f"  - company_name: {company_overview.company_name}")
        print(f"  - company_url: {company_overview.company_url}")
        print(f"  - description: {company_overview.description}")
        print(f"  - capabilities: {company_overview.capabilities}")
        print(f"  - objections: {company_overview.objections}")
        print(f"  - metadata: {company_overview.metadata}")
        
        user_id_str = user.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=401, detail="User ID not found in token"
            )

        # Convert string user_id to UUID for database operations
        try:
            user_uuid = uuid.UUID(user_id_str)
        except ValueError as e:
            print(f"Invalid UUID format for user_id: {user_id_str}. Error: {e}")
            raise HTTPException(
                status_code=400, detail="Invalid user ID format"
            )

        # Ensure user exists in database (auto-create if needed)
        from app.models import User
        existing_user = db.query(User).filter(User.id == user_uuid).first()
        if not existing_user:
            print(f"User not found for user_id: {user_id_str}. Creating new user.")
            new_user = User(
                id=user_uuid,
                role="user",  # Explicitly set the default role
            )
            try:
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                print(f"Successfully created new user with ID: {new_user.id}")
            except Exception as e:
                print(f"Failed to create user for user_id: {user_id_str}. Error: {e}")
                db.rollback()
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create user profile in database."
                )

        # Transform the ProductOverviewResponse to the database format
        company_data = CompanyCreate(
            name=company_overview.company_name,
            url=company_overview.company_url,
            data=company_overview.model_dump(),  # Store the entire response as JSONB
        )

        db_service = DatabaseService(db)
        result = db_service.create_company(company_data, str(user_uuid))
        return result
    except ValidationError as e:
        print(f"[DEBUG] Validation error details: {e}")
        print(f"[DEBUG] Validation error JSON: {e.json()}")
        raise HTTPException(
            status_code=422,
            detail=f"Validation failed: {str(e)}"
        )
    except Exception as e:
        print(f"[DEBUG] Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("", response_model=List[CompanyResponse])
async def get_companies(
    skip: int = Query(0, ge=0, description="Number of companies to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of companies to return"
    ),
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Get all companies for the authenticated user.

    - **skip**: Number of companies to skip (for pagination)
    - **limit**: Maximum number of companies to return (1-1000)
    """
    user_id = user.get("sub")
    print(
        f"📋 [GET-COMPANIES] Fetching companies for user {user_id} (skip={skip}, limit={limit})"
    )

    db_service = DatabaseService(db)
    result = db_service.get_companies(user_id, skip=skip, limit=limit)

    print(f"✅ [GET-COMPANIES] Found {len(result)} companies for user {user_id}")
    if result:
        print(f"📊 [GET-COMPANIES] Company names: {[c.name for c in result]}")

    return result


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Get a specific company by ID.

    Only returns companies owned by the authenticated user.
    """
    user_id = user.get("sub")
    print(f"📋 [GET-COMPANY] Fetching company {company_id} for user {user_id}")

    db_service = DatabaseService(db)
    result = db_service.get_company(company_id, user_id)

    print(
        f"✅ [GET-COMPANY] Company fetched successfully: name='{result.name}', url='{result.url}'"
    )
    print(
        f"📊 [GET-COMPANY] Company data keys: {list(result.data.keys()) if result.data else 'No data'}"
    )

    return result


@router.get("/{company_id}/relations", response_model=CompanyWithRelations)
async def get_company_with_relations(
    company_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Get a company with all related accounts.

    Only returns companies owned by the authenticated user.
    Includes nested account data.
    """
    db_service = DatabaseService(db)
    return db_service.get_company_with_relations(company_id, user["sub"])


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: UUID,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Update a company.

    Only updates companies owned by the authenticated user.
    All fields are optional - only provided fields will be updated.
    """
    user_id = user.get("sub")
    print(f"✏️ [UPDATE-COMPANY] Incoming PUT /companies/{company_id} for user {user_id}")
    raw_payload = company_data.model_dump(exclude_unset=False)
    print(f"📝 [UPDATE-COMPANY] Raw payload: {raw_payload}")
    print(
        f"📝 [UPDATE-COMPANY] Update data: name='{company_data.name}', "
        f"has_data={bool(company_data.data)}"
    )
    if company_data.data:
        print(f"📊 [UPDATE-COMPANY] Data keys: {list(company_data.data.keys())}")
        data_preview = str(company_data.data)
        print(f"📄 [UPDATE-COMPANY] Data preview: {data_preview[:200]}")
    db_service = DatabaseService(db)
    result = db_service.update_company(company_id, company_data, user_id)
    print(
        f"✅ [UPDATE-COMPANY] Company updated successfully: name='{result.name}', "
        f"id={result.id}"
    )
    updated_keys = list(result.data.keys()) if result.data else "No data"
    print(f"📊 [UPDATE-COMPANY] Updated data keys: {updated_keys}")
    return result


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(validate_stack_auth_jwt),
):
    """
    Delete a company and all related data.

    Only deletes companies owned by the authenticated user.
    This will cascade delete all accounts, personas, and campaigns.
    """
    db_service = DatabaseService(db)
    db_service.delete_company(company_id, user["sub"])
    return None


@router.post(
    "/generate-ai",
    response_model=ProductOverviewResponse,
    summary="AI Generate Company Overview",
    tags=["Companies", "AI"],
    response_description="A structured company overview for the given company context.",
)
async def prod_generate_product_overview(
    data: ProductOverviewRequest,
    user: dict = Depends(validate_stack_auth_jwt),
    db: Session = Depends(get_db),
):
    """
    AI-generate a company overview for authenticated users (Stack Auth JWT required).
    """
    print(f"🤖 [AI-GEN] Generating company overview for user {user.get('sub')}")
    print(f"🌐 [AI-GEN] Website URL: {data.website_url}")
    print(
        f"💡 [AI-GEN] User context: {data.user_inputted_context[:100] if data.user_inputted_context else 'None'}..."
    )

    orchestrator = ContextOrchestrator()
    result = await run_service(
        generate_product_overview_service, data, orchestrator=orchestrator
    )

    print(f"✅ [AI-GEN] Company overview generated successfully")
    print(
        f"📊 [AI-GEN] Generated company name: {getattr(result, 'company_name', 'Unknown')}"
    )
    return result
