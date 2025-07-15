from app.schemas import TargetPersonaRequest, TargetPersonaResponse
from app.prompts.models import TargetPersonaPromptVars
from app.services.context_orchestrator_service import ContextOrchestratorService


async def generate_target_persona_profile(
    request: TargetPersonaRequest,
) -> TargetPersonaResponse:
    """
    Generate a target persona profile using the shared analysis service.
    Uses the shared LLM client instance from llm_singleton.

    Args:
        request (TargetPersonaRequest): The validated request object.

    Returns:
        TargetPersonaResponse: The structured response model.
    """
    service = ContextOrchestratorService(
        orchestrator=None,  # Not used anymore
    )
    response = await service.analyze(
        request_data=request,
        analysis_type="target_persona",
        prompt_template="target_persona",
        prompt_vars_class=TargetPersonaPromptVars,
        response_model=TargetPersonaResponse,
    )
    # Set target_persona_name from persona_profile_name if present
    if request.persona_profile_name:
        response.target_persona_name = request.persona_profile_name
    return response
