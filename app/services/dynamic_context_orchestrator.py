"""
Dynamic Context Orchestrator
Replaces static JSON handoffs with enriched, multi-source context
"""

import logging
import json
from typing import Any, Type, Optional, Dict
from datetime import datetime

try:
    from fastapi import HTTPException
except ImportError:
    try:
        from starlette.exceptions import HTTPException
    except ImportError:
        class HTTPException(Exception):
            def __init__(self, status_code: int, detail: str):
                self.status_code = status_code
                self.detail = detail
                super().__init__(detail)

from app.core.llm_singleton import get_llm_client
from app.prompts.registry import render_prompt
from app.services.web_content_service import WebContentService
from app.services.context_store import get_context_store, ContextUpdate, ContextUpdateSource
from app.services.context_event_bus import event_bus, ContextEvent

try:
    from cli.utils.debug import debug_print
except ImportError:
    debug_print = print

try:
    from pydantic import BaseModel, ValidationError
except ImportError:
    from pydantic.v1 import BaseModel, ValidationError

import time
import os

logger = logging.getLogger(__name__)


class DynamicContextOrchestrator:
    """
    Enhanced orchestrator that uses dynamic context instead of static JSON
    Integrates with ContextStore for enriched, multi-source context
    """

    def __init__(self, orchestrator: Optional[Any] = None):
        self.orchestrator = orchestrator

    async def analyze(
        self,
        *,
        request_data: Any,
        analysis_type: str,
        prompt_template: str,
        prompt_vars_class: Type[Any],
        response_model: Type[BaseModel],
        client_id: str = "default",  # New: client identification
    ) -> BaseModel:
        """
        Enhanced analysis pipeline with dynamic context
        """
        try:
            total_start = time.monotonic()
            website_url = getattr(request_data, "website_url", None)
            
            # Get context store
            context_store = await get_context_store()
            
            # Get enriched context for this agent type
            t_context_start = time.monotonic()
            agent_context = await context_store.get_context_for_agent(
                client_id=client_id, 
                agent_type=analysis_type
            )
            t_context_end = time.monotonic()
            debug_print(f"[{analysis_type}] Context retrieval took {t_context_end - t_context_start:.2f}s")
            
            # Build prompt variables with enriched context
            t4 = time.monotonic()
            prompt_vars_kwargs = self._build_enhanced_prompt_vars(
                analysis_type, request_data, website_url, agent_context
            )
            prompt_vars = prompt_vars_class(**prompt_vars_kwargs)

            # Render prompt with enhanced context
            prompt = render_prompt(prompt_template, prompt_vars)
            t5 = time.monotonic()
            debug_print(f"[{analysis_type}] Enhanced prompt construction took {t5 - t4:.2f}s")

            # Call LLM
            t6 = time.monotonic()
            system_prompt, user_prompt = prompt
            response = await get_llm_client().generate_structured_output(
                prompt=user_prompt,
                system_prompt=system_prompt,
                response_model=response_model,
            )
            t7 = time.monotonic()
            debug_print(f"[{analysis_type}] LLM call took {t7 - t6:.2f}s")

            # Post-process: extract insights and update context
            await self._post_process_response(
                client_id, analysis_type, request_data, response, agent_context
            )

            total_end = time.monotonic()
            debug_print(f"[{analysis_type}] Total enhanced time: {total_end - total_start:.2f}s")
            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Enhanced analysis failed | analysis_type: {analysis_type} | error: {e}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail=f"Enhanced analysis failed for {analysis_type}: {e}",
            )

    def _build_enhanced_prompt_vars(
        self, 
        analysis_type: str, 
        request_data: Any, 
        website_url: Optional[str],
        agent_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build prompt variables enhanced with dynamic context"""
        
        # Start with base variables
        prompt_vars_kwargs = {"input_website_url": website_url}
        
        # Add website content
        website_content = None
        if website_url:
            try:
                content_result = WebContentService().get_content_for_llm(website_url)
                website_content = content_result["processed_content"]
                
                cache_status = content_result["cache_status"]
                content_length = content_result["processed_content_length"]
                debug_print(
                    f"[WEB_CONTENT] Cache status: {cache_status}, Content length: {content_length} chars"
                )
            except Exception as e:
                logger.warning(f"Failed to fetch website content for {website_url}: {e}")
                website_content = None

        # Add cross-client patterns to context
        cross_client_insights = ""
        if agent_context.get('_cross_client_patterns'):
            patterns = agent_context['_cross_client_patterns']
            insights = []
            for pattern in patterns[:3]:  # Top 3 patterns
                insights.append(
                    f"- {pattern['type']}: {pattern['data'].get('description', 'Pattern')} "
                    f"(Success rate: {pattern['success_rate']:.1%})"
                )
            if insights:
                cross_client_insights = f"\n\nCross-client insights:\n" + "\n".join(insights)

        # Add performance context
        performance_context = ""
        if agent_context.get('_performance_metrics'):
            metrics = agent_context['_performance_metrics']
            if metrics:
                performance_context = f"\n\nPrevious performance metrics: {metrics}"

        # Build analysis-specific variables with enhanced context
        if analysis_type == "product_overview":
            base_context = getattr(request_data, "user_inputted_context", "") or ""
            enhanced_context = base_context + cross_client_insights + performance_context
            
            prompt_vars_kwargs.update({
                "user_inputted_context": enhanced_context,
                "website_content": website_content,
            })
            
        elif analysis_type == "target_account":
            # Enhance company context with patterns
            company_context = getattr(request_data, "company_context", None)
            if isinstance(company_context, dict):
                # Add cross-client patterns to company context
                enhanced_company = dict(company_context)
                if cross_client_insights:
                    enhanced_company['_cross_client_insights'] = cross_client_insights
                company_context = enhanced_company
            
            prompt_vars_kwargs.update({
                "company_context": company_context,
                "account_profile_name": getattr(request_data, "account_profile_name", None),
                "hypothesis": getattr(request_data, "hypothesis", None),
                "additional_context": getattr(request_data, "additional_context", None),
            })
            
        elif analysis_type == "target_persona":
            # Enhance both company and account context
            company_context = getattr(request_data, "company_context", None)
            account_context = getattr(request_data, "target_account_context", None)
            
            # Add insights to both contexts
            if isinstance(company_context, dict) and cross_client_insights:
                enhanced_company = dict(company_context)
                enhanced_company['_cross_client_insights'] = cross_client_insights
                company_context = enhanced_company
            
            prompt_vars_kwargs.update({
                "company_context": company_context,
                "target_account_context": account_context,
                "persona_profile_name": getattr(request_data, "persona_profile_name", None),
                "hypothesis": getattr(request_data, "hypothesis", None),
                "additional_context": getattr(request_data, "additional_context", None),
            })
            
        elif analysis_type == "email_generation":
            prompt_vars_kwargs.update({
                "company_context": getattr(request_data, "company_context", None),
                "target_account": getattr(request_data, "target_account", None),
                "target_persona": getattr(request_data, "target_persona", None),
                "preferences": getattr(request_data, "preferences", None),
            })

        return prompt_vars_kwargs

    async def _post_process_response(
        self,
        client_id: str,
        analysis_type: str,
        request_data: Any,
        response: BaseModel,
        agent_context: Dict[str, Any]
    ):
        """Post-process response to extract insights and update context"""
        
        try:
            context_store = await get_context_store()
            
            # Extract insights from response for context updates
            insights = self._extract_insights_from_response(analysis_type, response)
            
            if insights:
                # Create context update
                update = ContextUpdate(
                    client_id=client_id,
                    source=ContextUpdateSource.ANALYSIS_AGENT,
                    agent_type=analysis_type,
                    update_data=insights,
                    confidence=0.8,  # High confidence for agent insights
                    requires_approval=False,  # Auto-approve agent insights
                    created_at=datetime.now()
                )
                
                # Apply context update
                await context_store.update_context(update)
                
                # Publish event for other modules
                await event_bus.publish(ContextEvent(
                    event_type="context_updated",
                    client_id=client_id,
                    agent_type=analysis_type,
                    data={"insights": insights, "source": "analysis_agent"}
                ))
                
                debug_print(f"[{analysis_type}] Updated context with {len(insights)} insights")
        
        except Exception as e:
            logger.warning(f"Context update failed for {analysis_type}: {e}")

    def _extract_insights_from_response(self, analysis_type: str, response: BaseModel) -> Dict[str, Any]:
        """Extract actionable insights from agent responses"""
        
        insights = {}
        
        try:
            if analysis_type == "product_overview" and hasattr(response, 'company_description'):
                insights.update({
                    'company_industry': getattr(response, 'industry', None),
                    'product_category': getattr(response, 'product_category', None),
                    'key_value_props': getattr(response, 'value_propositions', [])[:3]  # Top 3
                })
                
            elif analysis_type == "target_account" and hasattr(response, 'target_account_description'):
                insights.update({
                    'account_size_preference': getattr(response, 'company_size', None),
                    'target_industries': getattr(response, 'target_industries', [])[:3],
                    'account_criteria': getattr(response, 'ideal_customer_profile', {})
                })
                
            elif analysis_type == "target_persona" and hasattr(response, 'persona_description'):
                insights.update({
                    'target_titles': getattr(response, 'job_titles', [])[:3],
                    'persona_pain_points': getattr(response, 'pain_points', [])[:3],
                    'communication_style': getattr(response, 'communication_preferences', {})
                })
                
            elif analysis_type == "email_generation" and hasattr(response, 'emails'):
                emails = getattr(response, 'emails', [])
                if emails:
                    insights.update({
                        'effective_subject_patterns': [email.get('subject', '') for email in emails[:2]],
                        'message_themes': [email.get('theme', '') for email in emails[:2]],
                        'call_to_action_types': [email.get('cta_type', '') for email in emails[:2]]
                    })
        
        except Exception as e:
            logger.warning(f"Insight extraction failed for {analysis_type}: {e}")
        
        return insights