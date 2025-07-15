"""
CLI-adapted Product Overview Service
"""

import logging
from typing import Optional, Any
from cli.services.context_orchestrator_service import ContextOrchestratorService
from cli.services.llm_service import CLIException
from app.prompts.models import ProductOverviewPromptVars
from app.schemas import ProductOverviewRequest, ProductOverviewResponse

logger = logging.getLogger(__name__)


async def generate_product_overview_service(
    data: ProductOverviewRequest,
    orchestrator: Optional[Any] = None,
) -> ProductOverviewResponse:
    """
    CLI-adapted service for generating comprehensive product overview.
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
        raise CLIException(
            "Insufficient website content for valid output. "
            "Please provide a richer website or more context.",
            details={
                "analysis_type": "product_overview",
                "error_type": "insufficient_content"
            }
        )
    return result