from app.schemas import TargetAccountRequest, TargetAccountResponse
from app.prompts.models import TargetAccountPromptVars
from app.services.context_orchestrator_service import ContextOrchestratorService


async def generate_target_account_profile(
    request: TargetAccountRequest,
) -> TargetAccountResponse:
    """
    Generate a target account profile using the shared analysis service.
    Uses the shared LLM client instance from llm_singleton.
    """
    service = ContextOrchestratorService(
        orchestrator=None,  # Not used anymore
    )
    response: TargetAccountResponse = await service.analyze(
        request_data=request,
        analysis_type="target_account",
        prompt_template="target_account",
        prompt_vars_class=TargetAccountPromptVars,
        response_model=TargetAccountResponse,
    )
    return response
