import logging
from typing import Optional
from app.services.context_orchestrator_agent import ContextOrchestrator
from app.services.context_orchestrator_service import ContextOrchestratorService
from app.services.dynamic_context_orchestrator import DynamicContextOrchestrator
from app.prompts.models import ProductOverviewPromptVars
from app.schemas import ProductOverviewRequest, ProductOverviewResponse

try:
    from fastapi import HTTPException
except ImportError:
    try:
        from starlette.exceptions import HTTPException
    except ImportError:
        # Define a CLI-compatible exception for non-web contexts
        class HTTPException(Exception):
            def __init__(self, status_code: int, detail: str):
                self.status_code = status_code
                self.detail = detail
                super().__init__(detail)

logger = logging.getLogger(__name__)


async def generate_product_overview_service(
    data: ProductOverviewRequest,
    orchestrator: Optional[ContextOrchestrator] = None,
    client_id: str = "default",
    use_dynamic_context: bool = True,
) -> ProductOverviewResponse:
    """
    Orchestrates the generation of a comprehensive product overview.
    Now supports dynamic context with cross-client patterns and performance insights.
    """
    if use_dynamic_context:
        # Use new dynamic context orchestrator
        service = DynamicContextOrchestrator(orchestrator=orchestrator)
        result = await service.analyze(
            request_data=data,
            analysis_type="product_overview",
            prompt_template="product_overview",
            prompt_vars_class=ProductOverviewPromptVars,
            response_model=ProductOverviewResponse,
            client_id=client_id,
        )
    else:
        # Fall back to original static context approach
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
