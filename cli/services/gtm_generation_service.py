"""
GTM Generation Service - Orchestrates the complete 5-step GTM generation flow
"""

import logging
from typing import Any, Dict, Optional
from cli.services.project_storage import project_storage
from cli.services.product_overview_service import generate_product_overview_service
from cli.services.target_account_service import generate_target_account_profile
from cli.services.target_persona_service import generate_target_persona_profile
from cli.services.email_generation_service import generate_email_campaign_service
from cli.utils.domain import normalize_domain
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

logger = logging.getLogger(__name__)


class GTMGenerationService:
    """Orchestrates the complete GTM generation pipeline with file storage"""
    
    def __init__(self):
        self.storage = project_storage
    
    async def generate_company_overview(
        self, 
        domain: str, 
        user_context: Optional[str] = None,
        force_regenerate: bool = False
    ) -> ProductOverviewResponse:
        """Generate or load company overview (Step 1)"""
        normalized_domain = normalize_domain(domain)
        
        # Check if already exists and not forcing regeneration
        if not force_regenerate:
            existing_data = self.storage.load_step_data(normalized_domain, "overview")
            if existing_data:
                logger.info(f"Loading existing company overview for {normalized_domain}")
                return ProductOverviewResponse.model_validate(existing_data)
        
        # Generate new overview
        logger.info(f"Generating company overview for {normalized_domain}")
        request = ProductOverviewRequest(
            website_url=normalized_domain,
            user_inputted_context=user_context
        )
        
        result = await generate_product_overview_service(request)
        
        # Save to storage
        self.storage.save_step_data(normalized_domain, "overview", result)
        
        # Mark dependent steps as stale if regenerating
        if force_regenerate:
            stale_steps = self.storage.mark_steps_stale(normalized_domain, "overview")
            if stale_steps:
                logger.info(f"Marked dependent steps as stale: {stale_steps}")
        
        return result
    
    async def generate_target_account(
        self,
        domain: str,
        account_profile_name: Optional[str] = None,
        hypothesis: Optional[str] = None,
        additional_context: Optional[str] = None,
        force_regenerate: bool = False
    ) -> TargetAccountResponse:
        """Generate or load target account profile (Step 2)"""
        normalized_domain = normalize_domain(domain)
        
        # Check if already exists and not forcing regeneration
        if not force_regenerate:
            existing_data = self.storage.load_step_data(normalized_domain, "account")
            if existing_data:
                logger.info(f"Loading existing target account for {normalized_domain}")
                return TargetAccountResponse.model_validate(existing_data)
        
        # Load company context from step 1
        company_data = self.storage.load_step_data(normalized_domain, "overview")
        if not company_data:
            raise ValueError("Company overview must be generated first (Step 1)")
        
        # Generate new account profile
        logger.info(f"Generating target account for {normalized_domain}")
        request = TargetAccountRequest(
            website_url=normalized_domain,
            account_profile_name=account_profile_name,
            hypothesis=hypothesis,
            additional_context=additional_context,
            company_context=company_data
        )
        
        result = await generate_target_account_profile(request)
        
        # Save to storage
        self.storage.save_step_data(normalized_domain, "account", result)
        
        # Mark dependent steps as stale if regenerating
        if force_regenerate:
            stale_steps = self.storage.mark_steps_stale(normalized_domain, "account")
            if stale_steps:
                logger.info(f"Marked dependent steps as stale: {stale_steps}")
        
        return result
    
    async def generate_target_persona(
        self,
        domain: str,
        persona_profile_name: Optional[str] = None,
        hypothesis: Optional[str] = None,
        additional_context: Optional[str] = None,
        force_regenerate: bool = False
    ) -> TargetPersonaResponse:
        """Generate or load target persona profile (Step 3)"""
        normalized_domain = normalize_domain(domain)
        
        # Check if already exists and not forcing regeneration
        if not force_regenerate:
            existing_data = self.storage.load_step_data(normalized_domain, "persona")
            if existing_data:
                logger.info(f"Loading existing target persona for {normalized_domain}")
                return TargetPersonaResponse.model_validate(existing_data)
        
        # Load dependencies from previous steps
        company_data = self.storage.load_step_data(normalized_domain, "overview")
        account_data = self.storage.load_step_data(normalized_domain, "account")
        
        if not company_data:
            raise ValueError("Company overview must be generated first (Step 1)")
        if not account_data:
            raise ValueError("Target account must be generated first (Step 2)")
        
        # Generate new persona profile
        logger.info(f"Generating target persona for {normalized_domain}")
        request = TargetPersonaRequest(
            website_url=normalized_domain,
            persona_profile_name=persona_profile_name,
            hypothesis=hypothesis,
            additional_context=additional_context,
            company_context=company_data,
            target_account_context=account_data
        )
        
        result = await generate_target_persona_profile(request)
        
        # Save to storage
        self.storage.save_step_data(normalized_domain, "persona", result)
        
        # Mark dependent steps as stale if regenerating
        if force_regenerate:
            stale_steps = self.storage.mark_steps_stale(normalized_domain, "persona")
            if stale_steps:
                logger.info(f"Marked dependent steps as stale: {stale_steps}")
        
        return result
    
    async def generate_email_campaign(
        self,
        domain: str,
        preferences: Optional[Dict[str, Any]] = None,
        force_regenerate: bool = False
    ) -> EmailGenerationResponse:
        """Generate or load email campaign (Step 4)"""
        normalized_domain = normalize_domain(domain)
        
        # Check if already exists and not forcing regeneration
        if not force_regenerate:
            existing_data = self.storage.load_step_data(normalized_domain, "email")
            if existing_data:
                logger.info(f"Loading existing email campaign for {normalized_domain}")
                return EmailGenerationResponse.model_validate(existing_data)
        
        # Load dependencies from previous steps
        company_data = self.storage.load_step_data(normalized_domain, "overview")
        account_data = self.storage.load_step_data(normalized_domain, "account")
        persona_data = self.storage.load_step_data(normalized_domain, "persona")
        
        if not company_data:
            raise ValueError("Company overview must be generated first (Step 1)")
        if not account_data:
            raise ValueError("Target account must be generated first (Step 2)")
        if not persona_data:
            raise ValueError("Target persona must be generated first (Step 3)")
        
        # Generate new email campaign
        logger.info(f"Generating email campaign for {normalized_domain}")
        request = EmailGenerationRequest(
            company_context=company_data,
            target_account=account_data,
            target_persona=persona_data,
            preferences=preferences or {}
        )
        
        result = await generate_email_campaign_service(request)
        
        # Save to storage
        self.storage.save_step_data(normalized_domain, "email", result)
        
        return result
    
    async def run_complete_flow(
        self,
        domain: str,
        user_context: Optional[str] = None,
        account_profile_name: Optional[str] = None,
        account_hypothesis: Optional[str] = None,
        persona_profile_name: Optional[str] = None,
        persona_hypothesis: Optional[str] = None,
        email_preferences: Optional[Dict[str, Any]] = None,
        force_regenerate_all: bool = False
    ) -> Dict[str, Any]:
        """Run the complete 5-step GTM generation flow"""
        normalized_domain = normalize_domain(domain)
        results = {}
        
        # Step 1: Company Overview
        logger.info(f"Starting complete GTM flow for {normalized_domain}")
        results["overview"] = await self.generate_company_overview(
            domain, user_context, force_regenerate_all
        )
        
        # Step 2: Target Account
        results["account"] = await self.generate_target_account(
            domain, account_profile_name, account_hypothesis, force_regenerate=force_regenerate_all
        )
        
        # Step 3: Target Persona
        results["persona"] = await self.generate_target_persona(
            domain, persona_profile_name, persona_hypothesis, force_regenerate=force_regenerate_all
        )
        
        # Step 4: Email Campaign
        results["email"] = await self.generate_email_campaign(
            domain, email_preferences, force_regenerate=force_regenerate_all
        )
        
        # Step 5: GTM Plan (placeholder for now)
        # results["plan"] = await self.generate_gtm_plan(domain, force_regenerate=force_regenerate_all)
        
        logger.info(f"Completed GTM flow for {normalized_domain}")
        return results
    
    def get_project_status(self, domain: str) -> Dict[str, Any]:
        """Get current status of a GTM project"""
        normalized_domain = normalize_domain(domain)
        
        if not self.storage.project_exists(normalized_domain):
            return {"exists": False}
        
        available_steps = self.storage.get_available_steps(normalized_domain)
        metadata = self.storage.load_metadata(normalized_domain)
        
        status = {
            "exists": True,
            "domain": normalized_domain,
            "available_steps": available_steps,
            "completed_count": len(available_steps),
            "total_steps": 5,  # Will be 5 when GTM plan is added
            "progress_percentage": (len(available_steps) / 4) * 100,  # Current: 4 steps
        }
        
        if metadata:
            status.update({
                "created_at": metadata.created_at,
                "updated_at": metadata.updated_at,
                "last_step": metadata.last_step
            })
        
        # Check for stale data
        stale_steps = []
        for step in available_steps:
            step_data = self.storage.load_step_data(normalized_domain, step)
            if step_data and step_data.get("_stale"):
                stale_steps.append(step)
        
        if stale_steps:
            status["stale_steps"] = stale_steps
            status["has_stale_data"] = True
        else:
            status["has_stale_data"] = False
        
        return status


# Global instance
gtm_service = GTMGenerationService()