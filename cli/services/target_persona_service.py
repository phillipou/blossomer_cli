"""
CLI-adapted Target Persona Service
"""

from typing import Optional, Any
from cli.services.context_orchestrator_service import ContextOrchestratorService
from app.schemas import TargetPersonaRequest, TargetPersonaResponse
from app.prompts.models import TargetPersonaPromptVars


async def generate_target_persona_profile(
    request: TargetPersonaRequest,
    orchestrator: Optional[Any] = None,
) -> TargetPersonaResponse:
    """
    CLI-adapted service for generating target persona profile.
    Uses the shared LLM client instance from llm_singleton.
    """
    service = ContextOrchestratorService(orchestrator=orchestrator)
    response: TargetPersonaResponse = await service.analyze(
        request_data=request,
        analysis_type="target_persona",
        prompt_template="target_persona",
        prompt_vars_class=TargetPersonaPromptVars,
        response_model=TargetPersonaResponse,
    )
    return response