import logging
import json
from typing import Any, Type, Optional, Dict

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
from app.core.llm_singleton import get_llm_client
from app.prompts.registry import render_prompt
from app.services.web_content_service import WebContentService

# Import debug utility for conditional debug printing
try:
    from cli.utils.debug import debug_print
except ImportError:
    # Fallback if running outside CLI context
    debug_print = print

try:
    from pydantic import BaseModel, ValidationError
except ImportError:
    from pydantic.v1 import BaseModel, ValidationError
import time
import os

logger = logging.getLogger(__name__)


def flatten_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten one level of nested dicts into the top-level dict."""
    out = dict(d)
    for k, v in d.items():
        if isinstance(v, dict):
            for subk, subv in v.items():
                if subk not in out:
                    out[subk] = subv
    return out


def is_target_account_context_sufficient(context: Any) -> bool:
    """Check if the target account context has sufficient information."""
    ctx = context
    if not isinstance(ctx, (dict, list)):
        try:
            ctx = json.loads(ctx)
        except Exception:
            ctx = {}
    debug_print(f"[Sufficiency] Checking target account context: {ctx}")
    required_fields = [
        "company_size",
        "target_account_name",
        "target_account_description",
    ]

    def is_present(val):
        if isinstance(val, dict):
            return bool(val)
        if isinstance(val, str):
            return bool(val.strip())
        return val is not None

    if isinstance(ctx, list):
        merged = {}
        for item in ctx:
            if not isinstance(item, dict):
                continue
            merged.update(item)
        ctx = merged
    missing = [f for f in required_fields if not is_present(ctx.get(f))]
    result = not missing
    if not result:
        debug_print(
            f"[Sufficiency] Target account context insufficient: missing fields: {missing}"
        )
    else:
        debug_print(
            "[Sufficiency] Target account context is sufficient (all required fields present)."
        )
    return result


class ContextOrchestratorService:
    """
    Main service for orchestrating context analysis for all endpoints.
    Handles context resolution, preprocessing, caching, prompt rendering, and LLM calls.
    """

    def __init__(
        self,
        orchestrator: Optional[Any] = None,
    ):
        self.orchestrator = orchestrator

    async def analyze(
        self,
        *,
        request_data: Any,
        analysis_type: str,
        prompt_template: str,
        prompt_vars_class: Type[Any],
        response_model: Type[BaseModel],
    ) -> BaseModel:
        """
        Run the analysis pipeline with a two-level caching system.
        """
        try:
            total_start = time.monotonic()
            website_url = getattr(request_data, "website_url", None)

            # --- Prompt Construction and LLM Call ---
            t4 = time.monotonic()
            prompt_vars_kwargs = self._build_prompt_vars(
                analysis_type, request_data, website_url
            )
            prompt_vars = prompt_vars_class(**prompt_vars_kwargs)

            # --- TRACE LOG: Verify content before rendering ---
            if hasattr(prompt_vars, "website_content"):
                content_to_render = getattr(prompt_vars, "website_content", None)
                if content_to_render:
                    logger.info(
                        f"[PROMPT_TRACE] Rendering prompt with {len(content_to_render)} chars of website_content."
                    )
                    logger.info(
                        f"[PROMPT_TRACE] First 100 chars: {content_to_render[:100]}"
                    )
                else:
                    logger.warning(
                        "[PROMPT_TRACE] website_content is None or empty before rendering."
                    )
            # --- END TRACE LOG ---

            prompt = render_prompt(prompt_template, prompt_vars)
            t5 = time.monotonic()
            debug_print(f"[{analysis_type}] Prompt construction took {t5 - t4:.2f}s")

            t6 = time.monotonic()
            system_prompt, user_prompt = prompt
            response = await get_llm_client().generate_structured_output(
                prompt=user_prompt,
                system_prompt=system_prompt,
                response_model=response_model,
            )
            t7 = time.monotonic()
            debug_print(f"[{analysis_type}] LLM call took {t7 - t6:.2f}s")

            total_end = time.monotonic()
            debug_print(f"[{analysis_type}] Total time: {total_end - total_start:.2f}s")
            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Analysis failed | analysis_type: {analysis_type} | error: {e}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed for {analysis_type}: {e}",
            )

    def _build_prompt_vars(
        self, analysis_type: str, request_data: Any, website_url: Optional[str]
    ) -> Dict[str, Any]:
        """Helper to construct prompt variables based on analysis type."""
        prompt_vars_kwargs = {"input_website_url": website_url}

        website_content = None
        if website_url:
            try:
                content_result = WebContentService().get_content_for_llm(website_url)
                website_content = content_result["processed_content"]

                # Log cache performance
                cache_status = content_result["cache_status"]
                content_length = content_result["processed_content_length"]
                debug_print(
                    f"[WEB_CONTENT] Cache status: {cache_status}, Content length: {content_length} chars"
                )
                debug_print(
                    f"[WEB_CONTENT] Passing {content_length} chars of website content to prompt."
                )

            except Exception as e:
                logger.warning(
                    f"Failed to fetch website content for {website_url}: {e}"
                )
                website_content = None

        if analysis_type == "product_overview":
            prompt_vars_kwargs.update(
                {
                    "user_inputted_context": getattr(
                        request_data, "user_inputted_context", None
                    ),
                    "website_content": website_content,
                }
            )
        elif analysis_type == "target_account":
            prompt_vars_kwargs.update(
                {
                    "company_context": getattr(request_data, "company_context", None),
                    "account_profile_name": getattr(
                        request_data, "account_profile_name", None
                    ),
                    "hypothesis": getattr(request_data, "hypothesis", None),
                    "additional_context": getattr(
                        request_data, "additional_context", None
                    ),
                }
            )
        elif analysis_type == "target_persona":
            prompt_vars_kwargs.update(
                {
                    "company_context": getattr(request_data, "company_context", None),
                    "target_account_context": getattr(
                        request_data, "target_account_context", None
                    ),
                    "persona_profile_name": getattr(
                        request_data, "persona_profile_name", None
                    ),
                    "hypothesis": getattr(request_data, "hypothesis", None),
                    "additional_context": getattr(
                        request_data, "additional_context", None
                    ),
                }
            )
        elif analysis_type == "email_generation":
            prompt_vars_kwargs.update(
                {
                    "company_context": getattr(request_data, "company_context", None),
                    "target_account": getattr(request_data, "target_account", None),
                    "target_persona": getattr(request_data, "target_persona", None),
                    "preferences": getattr(request_data, "preferences", None),
                }
            )

        return prompt_vars_kwargs

    async def _resolve_context(self, request_data: Any, analysis_type: str) -> dict:
        raise NotImplementedError(
            "_resolve_context is deprecated. Orchestration is handled in the analyze method."
        )
