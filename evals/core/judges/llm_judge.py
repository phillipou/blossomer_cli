"""
Base LLM judge framework using Jinja2 templates.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import random

from jinja2 import Environment, FileSystemLoader, Template
from rich.console import Console

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.core.forge_llm_service import get_forge_llm_service, LLMRequest
from evals.core.config import EvalConfig


class LLMJudge:
    """LLM Judge using TensorBlock Forge with Jinja2 templates."""
    
    def __init__(self, config: EvalConfig, console: Console = None):
        self.config = config
        self.console = console or Console()
        self.forge_service = get_forge_llm_service(use_evals_key=True)
        
        # Initialize Jinja2 environments for system and user templates
        template_base_dir = Path(__file__).parent / "templates"
        self.system_jinja_env = Environment(
            loader=FileSystemLoader(str(template_base_dir / "system")),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.user_jinja_env = Environment(
            loader=FileSystemLoader(str(template_base_dir / "user")),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Call tracking
        self.total_calls = 0
        
    async def evaluate_all(self, output: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run all enabled LLM judges."""
        
        results = {
            "overall_pass": False,
            "judges": {},
            "total_calls": 0
        }
        
        # Parse output for judge evaluation
        try:
            parsed_output = json.loads(output)
            # Only show debug info in verbose mode
            # if self.console:
            #     self.console.print(f"🔍 LLM Judge - Parsed output keys: {list(parsed_output.keys())}")
        except json.JSONDecodeError as e:
            # Only show debug info in verbose mode  
            # if self.console:
            #     self.console.print(f"❌ LLM Judge - JSON decode error: {e}")
            #     self.console.print(f"🔍 Output sample: {output[:200]}...")
            return {
                "overall_pass": False,
                "error": f"Cannot parse output as JSON for LLM evaluation: {e}",
                "judges": {},
                "total_calls": 0
            }
        
        # Define available judges
        judge_functions = {
            "content_integrity": self._judge_content_integrity,
            "business_insight": self._judge_business_insight,
            "account_targeting_quality": self._judge_account_targeting_quality
        }
        
        # Get enabled judges from config
        enabled_judges = self.config.llm_judges or list(judge_functions.keys())
        
        # Validate that all requested judges exist
        invalid_judges = [judge for judge in enabled_judges if judge not in judge_functions]
        if invalid_judges:
            available_judges = list(judge_functions.keys())
            raise ValueError(
                f"Invalid LLM judge(s) in config: {invalid_judges}. "
                f"Available judges are: {available_judges}. "
                f"Please update your config.yaml to use the correct judge names."
            )
        
        all_passed = True
        
        for judge_name in enabled_judges:
            if judge_name in judge_functions:
                try:
                    judge_result = await judge_functions[judge_name](parsed_output, test_case)
                    
                    # Track calls
                    results["total_calls"] += 1
                    
                    # Handle new format where each judge returns multiple individual checks
                    if isinstance(judge_result, dict) and any(key in judge_result for key in ["evidence_support", "context_handling", "content_distinctness", "industry_sophistication", "strategic_depth", "authentic_voice_capture", "actionable_specificity", "proxy_strength", "detection_feasibility", "profile_crispness"]):
                        # New format: multiple individual checks
                        for check_name, check_result in judge_result.items():
                            # Validate that each check_result is a dict
                            if not isinstance(check_result, dict):
                                raise ValueError(
                                    f"Judge {judge_name} returned invalid format for check '{check_name}'. "
                                    f"Expected dict, got {type(check_result).__name__}: {check_result}"
                                )
                            results["judges"][check_name] = check_result
                            if not check_result.get("pass", False):
                                all_passed = False
                    else:
                        # Legacy format or unexpected format
                        if not isinstance(judge_result, dict):
                            raise ValueError(
                                f"Judge {judge_name} returned invalid format. "
                                f"Expected dict, got {type(judge_result).__name__}: {judge_result}"
                            )
                        results["judges"][judge_name] = judge_result
                        if not judge_result.get("pass", False):
                            all_passed = False
                        
                except Exception as e:
                    # Only show debug info in verbose mode
                    # if self.console:
                    #     self.console.print(f"❌ LLM Judge {judge_name} failed: {e}", style="red")
                    results["judges"][judge_name] = {
                        "check_name": judge_name,
                        "description": f"Judge category {judge_name} evaluation",
                        "inputs_evaluated": [{"field": "error", "value": str(e)}],
                        "pass": False,
                        "rationale": f"Judge evaluation failed: {str(e)}"
                    }
                    all_passed = False
        
        results["overall_pass"] = all_passed
        return results
    
    async def _call_judge(
        self, 
        template_name: str, 
        context: Dict[str, Any], 
        expected_format: str = "json",
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Make a standardized judge call using Jinja2 template."""
        
        try:
            # Only show debug info in verbose mode
            # if self.console:
            #     self.console.print(f"🔍 Judge - Loading template: {template_name}.j2")
            
            # Load system prompt template
            system_template = self.system_jinja_env.get_template(f"{template_name}.j2")
            system_prompt = system_template.render()
            
            # Load and render user prompt template
            user_template = self.user_jinja_env.get_template(f"{template_name}.j2")
            user_prompt = user_template.render(**context)
            
            # Only show debug info in verbose mode
            # if self.console:
            #     self.console.print(f"🔍 Judge - Rendered prompt length: {len(user_prompt)}")
            
            # Create LLM request
            request = LLMRequest(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=self.config.default_model,
                parameters={
                    "temperature": 0.1,
                    "max_tokens": max_tokens,
                    "response_format": {"type": "json_object"} if expected_format == "json" else None
                }
            )
            
            # Only show debug info in verbose mode
            # if self.console:
            #     self.console.print(f"🔍 Judge - Making request to model: {self.config.default_model}")
            
            # Make request to Forge
            response = await self.forge_service.generate(request)
            self.total_calls += 1
            
            # Only show debug info in verbose mode
            # if self.console:
            #     self.console.print(f"🔍 Judge - Got response: {response.text[:100]}...")
            
            # Parse response
            if expected_format == "json":
                result = json.loads(response.text)
                # For new multi-check format, just return as-is
                # The templates should return properly formatted individual checks
            else:
                result = {"response": response.text}
            
            return result
            
        except Exception as e:
            import traceback
            error_details = f"Judge call failed: {str(e)}\n{traceback.format_exc()}"
            if hasattr(self, 'console') and self.console:
                self.console.print(f"❌ LLM Judge Error: {error_details}", style="red")
            return {
                "check_name": template_name,
                "description": f"LLM evaluation using {template_name} template",
                "inputs_evaluated": [{"field": "error", "value": str(e)}],
                "pass": False,
                "rationale": f"This check failed due to an error: {str(e)}"
            }
    
    
    async def _judge_business_insight(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """L-2: Business insight check - evaluate sophisticated understanding that would impress founders."""
        
        context = {
            "analysis": data
        }
        
        return await self._call_judge("business_insight", context)
    
    async def _judge_content_integrity(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """L-1: Content integrity check - evaluate evidence support, context handling, and content distinctness."""
        
        context = {
            "analysis": data,
            "context_type": test_case.get("context_type", "none"),
            "user_context": test_case.get("user_inputted_context", ""),
            "website_content": test_case.get("website_content", "")
        }
        
        return await self._call_judge("content_integrity", context)
    
    async def _judge_account_targeting_quality(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """L-3: Account targeting quality check - evaluate profile crispness, detection feasibility, and business logic depth."""
        
        # Extract company context if available
        company_context = None
        if test_case.get("input_website_url"):
            company_context = {
                "company_url": test_case.get("input_website_url"),
                "description": f"Company analysis based on {test_case.get('input_website_url')}"
            }
        
        context = {
            "analysis": data,
            "company_context": company_context
        }
        
        return await self._call_judge("account_targeting_quality", context)


# For standalone testing
if __name__ == "__main__":
    import asyncio
    
    async def test_llm_judge():
        from evals.core.config import EvalConfig
        
        config = EvalConfig(
            name="Test Config",
            prompt_name="test",
            service_module="test",
            service_function="test",
            llm_judges=["actionability"],
            default_model="OpenAI/gpt-4.1-nano"
        )
        
        console = Console()
        judge = LLMJudge(config, console=console)
        
        sample_data = {
            "description": "A company that provides AI-powered testing automation",
            "business_profile_insights": [
                "Category: Software Testing Tools",
                "Business Model: SaaS subscription with enterprise features",
                "Target Market: Mid-market software companies with CI/CD pipelines"
            ],
            "positioning_insights": [
                "Key Differentiator: AI-powered test case generation",
                "Market Position: Premium automation tool for quality-focused teams",
                "Competitive Advantage: Reduces testing time by 80%"
            ],
            "target_customer_insights": [
                "Primary Buyers: QA Directors and Engineering Managers",
                "Decision Criteria: ROI on testing efficiency and integration capabilities"
            ]
        }
        
        test_case = {
            "input_website_url": "https://test.com",
            "context_type": "none",
            "website_content": "Test website content about AI testing automation..."
        }
        
        print("🧪 Testing LLM Judge...")
        results = await judge.evaluate_all(json.dumps(sample_data), test_case)
        
        print(f"Overall Pass: {results['overall_pass']}")
        print(f"Total Calls: {results['total_calls']}")
        
        for judge_name, judge_result in results["judges"].items():
            status = "✅ PASS" if judge_result.get("pass", False) else "❌ FAIL"
            print(f"{judge_name}: {status}")
            if "error" in judge_result:
                print(f"  Error: {judge_result['error']}")
    
    # Only run test if templates exist
    template_dir = Path(__file__).parent / "templates" / "system"
    if template_dir.exists():
        asyncio.run(test_llm_judge())
    else:
        print("⚠️  Templates not found - skipping test")