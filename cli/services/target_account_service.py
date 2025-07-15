"""
CLI-adapted Target Account Service
"""

from typing import Optional, Any
from cli.services.context_orchestrator_service import ContextOrchestratorService
from app.schemas import TargetAccountRequest, TargetAccountResponse
from app.prompts.models import TargetAccountPromptVars


async def generate_target_account_profile(
    request: TargetAccountRequest,
    orchestrator: Optional[Any] = None,
) -> TargetAccountResponse:
    """
    CLI-adapted service for generating target account profile.
    Uses the shared LLM client instance from llm_singleton.
    """
    service = ContextOrchestratorService(orchestrator=orchestrator)
    response: TargetAccountResponse = await service.analyze(
        request_data=request,
        analysis_type="target_account",
        prompt_template="target_account",
        prompt_vars_class=TargetAccountPromptVars,
        response_model=TargetAccountResponse,
    )
    return response