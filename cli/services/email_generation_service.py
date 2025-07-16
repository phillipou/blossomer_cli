"""
CLI-adapted Email Generation Service
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional
from cli.services.context_orchestrator_service import ContextOrchestratorService
from cli.utils.debug import debug_print
from app.prompts.models import EmailGenerationPromptVars
from app.schemas import (
    EmailGenerationRequest,
    EmailGenerationResponse,
    get_default_email_breakdown,
    EmailBreakdown,
)

logger = logging.getLogger(__name__)


async def generate_email_campaign_service(
    data: EmailGenerationRequest,
    orchestrator: Optional[Any] = None,
) -> EmailGenerationResponse:
    """
    CLI-adapted service for generating personalized email campaigns.
    Synthesizes company context, target account/persona data, and user preferences.
    """
    start_time = time.time()
    generation_id = str(uuid.uuid4())

    try:
        logger.info(f"Starting email generation {generation_id}")

        # Use the context orchestrator service for LLM generation
        service = ContextOrchestratorService(orchestrator=orchestrator)

        # Handle guided mode preferences or default template
        guided_mode = False
        prompt_template = "email_generation_blossomer"  # Default template
        
        if data.preferences and isinstance(data.preferences, dict):
            # Check if this is guided mode
            if data.preferences.get("guided_mode"):
                guided_mode = True
                # For now, use the main template but with guided preferences
                prompt_template = "email_generation_blossomer"
                logger.info(f"Using guided mode with preferences: {data.preferences}")
            else:
                # Legacy template preference handling
                template_type = data.preferences.get("template", "blossomer")
                if template_type == "custom":
                    prompt_template = "email_generation_custom"
                else:
                    prompt_template = "email_generation_blossomer"
        elif hasattr(data.preferences, "template"):
            template_type = data.preferences.template
            if template_type == "custom":
                prompt_template = "email_generation_custom"
            else:
                prompt_template = "email_generation_blossomer"

        logger.info(f"Using template: {prompt_template} for generation {generation_id}")

        # Generate the email using the LLM
        result = await service.analyze(
            request_data=data,
            analysis_type="email_generation",
            prompt_template=prompt_template,
            prompt_vars_class=EmailGenerationPromptVars,
            response_model=EmailGenerationResponse,
        )

        # Ensure we have the right type
        if not isinstance(result, EmailGenerationResponse):
            result = EmailGenerationResponse.model_validate(result)

        # Assign colors to breakdown entries
        result.breakdown = assign_breakdown_colors(result.breakdown)

        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)

        # Update metadata with actual processing time and generation ID
        if hasattr(result, "metadata"):
            result.metadata.processing_time_ms = processing_time
            result.metadata.generation_id = generation_id

        logger.info(
            f"Email generation {generation_id} completed in {processing_time}ms"
        )
        debug_print(
            f"[EmailGenerationService] Email generation {generation_id} response: {result}"
        )
        return result

    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        logger.error(
            f"Email generation {generation_id} failed after {processing_time}ms: {str(e)}"
        )
        raise e


def determine_personalization_level(
    opening_line_strategy: str,
    account_data: Dict[str, Any],
    persona_data: Dict[str, Any],
) -> str:
    """
    Determine the personalization level based on available data and strategy.
    """
    if opening_line_strategy == "not-personalized":
        return "low"

    # Check for high-quality personalization data
    has_buying_signals = bool(account_data.get("buying_signals"))
    has_specific_company_info = bool(account_data.get("target_account_description"))
    has_persona_use_cases = bool(persona_data.get("use_cases"))

    if opening_line_strategy == "buying-signal" and has_buying_signals:
        return "high"
    elif opening_line_strategy == "company-research" and has_specific_company_info:
        return "high"
    elif has_persona_use_cases and has_specific_company_info:
        return "medium"
    else:
        return "low"


def validate_email_generation_context(data: EmailGenerationRequest) -> Dict[str, str]:
    """Validate that required context is available for email generation."""
    warnings = {}

    # Check company context completeness
    if not data.company_context.company_name:
        warnings["company_name"] = "Missing company name"

    if not data.company_context.capabilities:
        warnings["capabilities"] = "No capabilities listed"

    # Check target account context
    if not data.target_account.target_account_description:
        warnings["account_description"] = "Missing account description"

    # Check target persona context
    if not data.target_persona.use_cases:
        warnings["use_cases"] = "No use cases available for persona"

    if not data.target_persona.demographics.job_titles:
        warnings["job_titles"] = "No job titles specified for persona"

    return warnings


def assign_breakdown_colors(breakdown: Dict[str, Any]) -> Dict[str, Any]:
    """Assign consistent colors to breakdown entries based on segment types."""
    # Default color mapping for common segment types
    COLOR_MAPPING = {
        "subject": "bg-purple-50 border-purple-200",
        "greeting": "bg-purple-50 border-purple-200",
        "intro": "bg-blue-50 border-blue-200",
        "opening": "bg-blue-50 border-blue-200",
        "context": "bg-teal-50 border-teal-200",
        "pain-point": "bg-red-50 border-red-200",
        "problem": "bg-red-50 border-red-200",
        "solution": "bg-green-50 border-green-200",
        "company-intro": "bg-green-50 border-green-200",
        "emphasis": "bg-indigo-50 border-indigo-200",
        "value": "bg-indigo-50 border-indigo-200",
        "evidence": "bg-indigo-50 border-indigo-200",
        "social-proof": "bg-pink-50 border-pink-200",
        "testimonial": "bg-pink-50 border-pink-200",
        "urgency": "bg-orange-50 border-orange-200",
        "cta": "bg-yellow-50 border-yellow-200",
        "call-to-action": "bg-yellow-50 border-yellow-200",
        "next-steps": "bg-yellow-50 border-yellow-200",
        "signature": "bg-gray-50 border-gray-200",
        "closing": "bg-gray-50 border-gray-200",
        "ps": "bg-gray-50 border-gray-200",
    }

    # Default color for unknown segment types
    DEFAULT_COLOR = "bg-blue-50 border-blue-200"

    # Assign colors to each breakdown entry
    for segment_type, entry in breakdown.items():
        if isinstance(entry, dict):
            # Use mapped color or default
            entry["color"] = COLOR_MAPPING.get(segment_type, DEFAULT_COLOR)

    return breakdown