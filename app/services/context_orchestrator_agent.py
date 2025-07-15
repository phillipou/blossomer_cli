"""
This module defines the ContextOrchestrator agent, which is responsible for
assessing context quality for campaign generation endpoints.
"""

from typing import Dict, Any, Optional
import json

from app.prompts.models import (
    ContextAssessmentResult,
    ContextAssessmentVars,
    ContextQuality,
    CompanyOverviewResult,
)
from app.prompts.registry import render_prompt
from app.core.llm_singleton import get_llm_client
from app.services.web_content_service import WebContentService


def ensure_dict(context: Any) -> Dict[str, Any]:
    if isinstance(context, dict):
        return context
    if isinstance(context, str):
        try:
            return json.loads(context)
        except Exception:
            return {}
    return {}


def is_company_context_sufficient(context: Any) -> bool:
    ctx = ensure_dict(context)
    print(f"[Sufficiency] Checking company context: {ctx}")
    name = ctx.get("company_name", "") or ctx.get("target_company_name", "")
    overview = ctx.get("company_overview", "")
    use_cases = ctx.get("use_cases", [])
    capabilities = ctx.get("capabilities", [])
    result = (
        bool(name.strip())
        and bool(overview.strip())
        and (bool(use_cases) or bool(capabilities))
    )
    if not result:
        print(
            f"[Sufficiency] Company context insufficient: name='{name}', "
            f"overview='{overview}', use_cases={use_cases}, capabilities={capabilities}"
        )
    else:
        print("[Sufficiency] Company context is sufficient.")
    return result


def is_target_account_context_sufficient(context: Any) -> bool:
    ctx = ensure_dict(context) if not isinstance(context, list) else context
    print(f"[Sufficiency] Checking target account context: {ctx}")
    # If context is a list (firmographics array), scan for relevant variables
    if isinstance(ctx, list):
        industry = employees = revenue = None
        for item in ctx:
            if not isinstance(item, dict):
                continue
            # Industry: accept non-empty list or string
            if industry is None and item.get("industry"):
                val = item["industry"]
                if isinstance(val, list):
                    if val:
                        industry = ", ".join(val)
                elif isinstance(val, str) and val.strip():
                    industry = val
            # Employees: check top-level, then company_size
            if employees is None:
                if item.get("employees"):
                    employees = item["employees"]
                elif item.get("company_size") and isinstance(
                    item["company_size"], dict
                ):
                    employees = item["company_size"].get("employees")
            # Revenue: check top-level, then company_size
            if revenue is None:
                if item.get("revenue"):
                    revenue = item["revenue"]
                elif item.get("company_size") and isinstance(
                    item["company_size"], dict
                ):
                    revenue = item["company_size"].get("revenue")
        size_ok = any(
            [
                industry not in (None, "", []),
                employees not in (None, "", []),
                revenue not in (None, "", []),
            ]
        )
        result = size_ok
        if not result:
            print(
                f"[Sufficiency] Target account context insufficient (array): "
                f"industry='{industry}', employees='{employees}', "
                f"revenue='{revenue}', size_ok={size_ok}"
            )
        else:
            print("[Sufficiency] Target account context is sufficient (array).")
        return result
    # If context is a dict, use improved logic
    industry = ctx.get("industry", "")
    if isinstance(industry, list):
        industry = ", ".join(industry) if industry else None
    elif isinstance(industry, str) and not industry.strip():
        industry = None
    employees = ctx.get("employees", None)
    revenue = ctx.get("revenue", None)
    # Check company_size nested dict if not found at top level
    company_size = ctx.get("company_size", {})
    if isinstance(company_size, dict):
        if employees in (None, "", []):
            employees = company_size.get("employees")
        if revenue in (None, "", []):
            revenue = company_size.get("revenue")
    size_ok = any(
        [
            industry not in (None, "", []),
            employees not in (None, "", []),
            revenue not in (None, "", []),
        ]
    )
    result = size_ok
    if not result:
        print(
            f"[Sufficiency] Target account context insufficient: "
            f"industry='{industry}', employees='{employees}', "
            f"revenue='{revenue}', size_ok={size_ok}"
        )
    else:
        print("[Sufficiency] Target account context is sufficient.")
    return result


def is_target_persona_context_sufficient(context: dict) -> bool:
    """
    Checks if context has sufficient information for target persona (requires company and target account context).
    """
    return is_company_context_sufficient(
        context
    ) and is_target_account_context_sufficient(context)


async def resolve_context_for_endpoint(
    request, endpoint_name: str, orchestrator
) -> Dict[str, Any]:
    """
    Resolve the best context for a given endpoint, preferring LLM-inferred, then website scraping.
    For target_account, only check company context sufficiency on company_context.
    user_inputted_context is used as a steer, not for sufficiency.
    Returns a dict with keys: 'source', 'context', 'is_ready'.
    """
    user_ctx = ensure_dict(getattr(request, "user_inputted_context", None))
    company_ctx = ensure_dict(getattr(request, "company_context", None))
    website_url = getattr(request, "website_url", None)

    if endpoint_name == "target_account":
        # Only check company context sufficiency on company_context
        if company_ctx:
            print(
                "[ContextOrchestrator] Checking company context for company sufficiency..."
            )
            sufficient = is_company_context_sufficient(company_ctx)
            print(
                f"[ContextOrchestrator] Company context company sufficiency: {sufficient}"
            )
            if sufficient:
                print("[ContextOrchestrator] Using company context for generation.")
                return {
                    "source": "company_context",
                    "context": company_ctx,
                    "is_ready": True,
                }
        if website_url:
            print("[ContextOrchestrator] Resorting to website scraping for context.")
            content_result = WebContentService().get_content_for_llm(website_url)
            content = content_result["processed_content"]
            cache_status = content_result["cache_status"]
            return {
                "source": "website",
                "context": content,
                "content": content,
                "processed_content": content,
                "is_ready": True,
                "from_cache": cache_status != "fresh_scrape",
            }
        print(
            "[ContextOrchestrator] No sufficient context found and no website_url provided."
        )
        return {"source": None, "context": None, "is_ready": False}

    if endpoint_name == "target_persona":
        # Target persona requires sufficient company and target account context
        for ctx, label in [
            (user_ctx, "user-provided"),
            (company_ctx, "company_context"),
        ]:
            if ctx:
                print(
                    f"[ContextOrchestrator] Checking {label} context for persona sufficiency..."
                )
                sufficient = is_target_persona_context_sufficient(ctx)
                print(
                    f"[ContextOrchestrator] {label} context persona sufficiency: {sufficient}"
                )
                if sufficient:
                    print(
                        f"[ContextOrchestrator] Using {label} context for generation."
                    )
                    return {"source": label, "context": ctx, "is_ready": True}
        if website_url:
            print("[ContextOrchestrator] Resorting to website scraping for context.")
            content_result = WebContentService().get_content_for_llm(website_url)
            content = content_result["processed_content"]
            cache_status = content_result["cache_status"]
            return {
                "source": "website",
                "context": content,
                "content": content,
                "processed_content": content,
                "is_ready": True,
                "from_cache": cache_status != "fresh_scrape",
            }
        print(
            "[ContextOrchestrator] No sufficient context found and no website_url provided."
        )
        return {"source": None, "context": None, "is_ready": False}

    # For other endpoints, try user-provided context first
    if user_ctx:
        print("[ContextOrchestrator] Using user-provided context.")
        return {"source": "user-provided", "context": user_ctx, "is_ready": True}

    # Then try website scraping
    if website_url:
        print("[ContextOrchestrator] Resorting to website scraping for context.")
        content_result = WebContentService().get_content_for_llm(website_url)
        content = content_result["processed_content"]
        cache_status = content_result["cache_status"]
        return {
            "source": "website",
            "context": content,
            "content": content,
            "processed_content": content,
            "is_ready": True,
            "from_cache": cache_status != "fresh_scrape",
        }

    print("[ContextOrchestrator] No context found and no website_url provided.")
    return {"source": None, "context": None, "is_ready": False}


class ContextOrchestrator:
    """
    Orchestrates context assessment and enrichment for campaign generation endpoints.
    """

    def __init__(self, llm_client=None) -> None:  # Kept for backward compatibility
        """Initialize the orchestrator."""
        pass

    async def assess_context(
        self,
        website_content: str,
        target_endpoint: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> CompanyOverviewResult:
        """
        Assess the quality of website content for a target endpoint.
        Uses the shared LLM client instance from llm_singleton.
        """
        prompt_vars = ContextAssessmentVars(
            website_content=website_content,
            user_inputted_context=user_context,
            target_endpoint=target_endpoint,
        )
        prompt = render_prompt("context_assessment", prompt_vars)
        result = await get_llm_client().generate_structured_output(
            prompt=prompt, response_model=CompanyOverviewResult
        )
        return result

    async def assess_url_context(
        self,
        url: str,
        target_endpoint: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
        crawl: bool = False,
    ) -> ContextAssessmentResult:
        """
        Assess the quality of a website URL's content for a target endpoint.
        Uses the shared LLM client instance from llm_singleton.
        """
        content_result = WebContentService().get_content_for_llm(url)
        content = content_result["processed_content"]
        cache_status = content_result["cache_status"]

        if not content:
            return ContextAssessmentResult(
                quality=ContextQuality.INSUFFICIENT,
                reason="No content extracted from website.",
                source="website",
                from_cache=cache_status != "fresh_scrape",
            )

        assessment = await self.assess_context(
            website_content=content,
            target_endpoint=target_endpoint,
            user_context=user_context,
        )

        return ContextAssessmentResult(
            overall_quality=assessment.metadata.get(
                "context_quality", ContextQuality.INSUFFICIENT
            ),
            overall_confidence=assessment.metadata.get("overall_confidence", 0.0),
            content_sections=[],  # Placeholder, as CompanyOverviewResult doesn't directly provide this
            company_clarity={},  # Placeholder
            endpoint_readiness=[],  # Placeholder
            data_quality_metrics={},  # Placeholder
            recommendations={},  # Placeholder
            summary=assessment.company_overview,  # Using company_overview as summary for now
            source="website",
            from_cache=cache_status != "fresh_scrape",
        )

    def check_endpoint_readiness(
        self,
        assessment: Any,  # Changed to Any for flexibility
        endpoint: str,
    ) -> Dict[str, Any]:
        """
        Check if an endpoint is ready for generation based on context assessment.
        """
        quality_value = "INSUFFICIENT"
        if hasattr(assessment, "overall_quality"):
            quality_value = assessment.overall_quality
        elif (
            hasattr(assessment, "metadata") and "context_quality" in assessment.metadata
        ):
            quality_value = assessment.metadata["context_quality"]

        is_ready = False
        missing_requirements = []

        if endpoint == "target_account":
            is_ready = quality_value in ("GOOD", "EXCELLENT")
            if not is_ready:
                missing_requirements.append("company_context")
        elif endpoint == "target_persona":
            company_ready = quality_value in ("GOOD", "EXCELLENT")
            target_account_ready = False
            if hasattr(assessment, "target_account_quality"):
                target_account_ready = assessment.target_account_quality in (
                    "GOOD",
                    "EXCELLENT",
                )

            is_ready = company_ready and target_account_ready
            if not company_ready:
                missing_requirements.append("company_context")
            if not target_account_ready:
                missing_requirements.append("target_account_context")
        else:
            # Default case for other endpoints
            is_ready = quality_value in ("GOOD", "EXCELLENT")
            # No specific missing requirements for default case, but can be extended

        return {
            "is_ready": is_ready,
            "confidence": (
                assessment.overall_confidence
                if hasattr(assessment, "overall_confidence")
                else (
                    assessment.metadata.get("overall_confidence")
                    if hasattr(assessment, "metadata")
                    else 0.0
                )
            ),  # Add confidence
            "missing_requirements": missing_requirements,
            "recommendations": (
                assessment.recommendations
                if hasattr(assessment, "recommendations")
                else (
                    assessment.metadata.get("recommended_improvements")
                    if hasattr(assessment, "metadata")
                    else []
                )
            ),  # Add recommendations
            "assessment_summary": (
                assessment.summary
                if hasattr(assessment, "summary")
                else (
                    assessment.metadata.get("assessment_summary")
                    if hasattr(assessment, "metadata")
                    else ""
                )
            ),  # Add summary
            "missing": missing_requirements,  # Ensure 'missing' key is always present
        }

    async def orchestrate_context(
        self,
        website_url: str,
        target_endpoint: str,
        user_context: Optional[Dict[str, Any]] = None,
        auto_enrich: bool = True,
        max_steps: int = 3,
    ) -> Dict[str, Any]:
        """
        Orchestrate context assessment and enrichment for a target endpoint.
        Uses the shared LLM client instance from llm_singleton.
        """
        # Initial assessment
        assessment = await self.assess_url_context(
            url=website_url,
            target_endpoint=target_endpoint,
            user_context=user_context,
        )

        # Check if we have sufficient context
        readiness = self.check_endpoint_readiness(assessment, target_endpoint)
        if readiness["is_ready"]:
            return {
                "is_ready": True,
                "assessment": assessment,
                "enrichment_steps": [],
            }

        # If auto-enrichment is disabled, return current state
        if not auto_enrich:
            return {
                "is_ready": False,
                "assessment": assessment,
                "enrichment_steps": [],
                "missing": readiness["missing"],
            }

        # Plan and execute enrichment
        enrichment_plan = self._create_enrichment_plan(assessment, target_endpoint)
        enrichment_result = self._execute_enrichment(enrichment_plan, website_url)

        return {
            "is_ready": enrichment_result["is_ready"],
            "assessment": assessment,
            "enrichment_steps": enrichment_result["steps"],
            "missing": readiness["missing"],
        }

    def _create_enrichment_plan(
        self, assessment: CompanyOverviewResult, target_endpoint: str
    ) -> Dict[str, Any]:
        """Create a plan for enriching insufficient context."""
        # TODO: Implement enrichment planning
        return {"steps": []}

    def _execute_enrichment(
        self, enrichment_plan: Dict[str, Any], website_url: str
    ) -> Dict[str, Any]:
        """Execute an enrichment plan."""
        # TODO: Implement enrichment execution
        return {"is_ready": False, "steps": []}
