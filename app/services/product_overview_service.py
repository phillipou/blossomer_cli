import logging
from app.services.context_orchestrator_agent import ContextOrchestrator
from app.services.context_orchestrator_service import ContextOrchestratorService
from app.prompts.models import ProductOverviewPromptVars
from app.schemas import ProductOverviewRequest, ProductOverviewResponse

try:
    from fastapi import HTTPException
except ImportError:
    from starlette.exceptions import HTTPException

logger = logging.getLogger(__name__)


async def generate_product_overview_service(
    data: ProductOverviewRequest,
    orchestrator: ContextOrchestrator,
) -> ProductOverviewResponse:
    """
    Orchestrates the generation of a comprehensive product overview.
    """
    service = ContextOrchestratorService(orchestrator=orchestrator)
    result = await service.analyze(
        request_data=data,
        analysis_type="product_overview",
        prompt_template="product_overview",
        prompt_vars_class=ProductOverviewPromptVars,
        response_model=ProductOverviewResponse,
    )
    # Check for insufficient content
    if (
        hasattr(result, "metadata")
        and result.metadata.get("context_quality") == "insufficient"
    ):
        raise HTTPException(
            status_code=422,
            detail={
                "error": (
                    "Insufficient website content for valid output. "
                    "Please provide a richer website or more context."
                ),
                "analysis_type": "product_overview",
            },
        )
    return result
