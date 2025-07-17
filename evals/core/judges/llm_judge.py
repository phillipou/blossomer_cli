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
        
        # Initialize Jinja2 environment
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
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
            "traceability": self._judge_traceability,
            "actionability": self._judge_actionability,
            "redundancy": self._judge_redundancy,
            "context_steering": self._judge_context_steering
        }
        
        # Get enabled judges from config
        enabled_judges = self.config.llm_judges or list(judge_functions.keys())
        
        all_passed = True
        
        for judge_name in enabled_judges:
            if judge_name in judge_functions:
                try:
                    judge_result = await judge_functions[judge_name](parsed_output, test_case)
                    results["judges"][judge_name] = judge_result
                    
                    # Track calls
                    results["total_calls"] += 1
                    
                    if not judge_result.get("pass", False):
                        all_passed = False
                        
                except Exception as e:
                    # Only show debug info in verbose mode
                    # if self.console:
                    #     self.console.print(f"❌ LLM Judge {judge_name} failed: {e}", style="red")
                    results["judges"][judge_name] = {
                        "pass": False,
                        "error": f"Judge evaluation failed: {str(e)}"
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
            
            # Load and render template
            template = self.jinja_env.get_template(f"{template_name}.j2")
            prompt = template.render(**context)
            
            # Only show debug info in verbose mode
            # if self.console:
            #     self.console.print(f"🔍 Judge - Rendered prompt length: {len(prompt)}")
            
            # Create LLM request
            request = LLMRequest(
                system_prompt="You are an expert evaluator. Respond only with valid JSON.",
                user_prompt=prompt,
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
                # Ensure the result has the required standardized structure
                if "check_name" not in result:
                    result["check_name"] = template_name
                if "description" not in result:
                    result["description"] = f"LLM evaluation using {template_name} template"
                if "inputs_evaluated" not in result:
                    result["inputs_evaluated"] = [{"field": "context", "value": "Template context"}]
                if "rationale" not in result:
                    result["rationale"] = "LLM evaluation result"
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
    
    
    async def _judge_traceability(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """L-1: Traceability check - verify claims are evidence-based."""
        
        # Sample factual claims from insight fields
        insight_fields = [
            "business_profile_insights",
            "use_case_analysis_insights",
            "positioning_insights"
        ]
        
        all_claims = []
        for field in insight_fields:
            if field in data and isinstance(data[field], list):
                all_claims.extend([(field, claim) for claim in data[field]])
                # Only show debug info in verbose mode
                # if self.console:
                #     self.console.print(f"🔍 Traceability - Found {len(data[field])} claims in {field}")
        
        # Only show debug info in verbose mode
        # if self.console:
        #     self.console.print(f"🔍 Traceability - Total claims found: {len(all_claims)}")
        
        if not all_claims:
            return {
                "pass": False,
                "error": "No claims found to evaluate"
            }
        
        # Sample up to 5 claims
        sampled_claims = random.sample(all_claims, min(5, len(all_claims)))
        
        context = {
            "website_content": test_case.get("website_content", ""),
            "claims": [
                {
                    "field": field,
                    "claim": claim,
                    "number": i + 1
                }
                for i, (field, claim) in enumerate(sampled_claims)
            ]
        }
        
        # Only show debug info in verbose mode
        # if self.console:
        #     self.console.print(f"🔍 Traceability - Calling judge with {len(context['claims'])} claims")
        
        return await self._call_judge("traceability", context)
    
    async def _judge_actionability(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """L-2: Actionability check - evaluate specificity and discovery value."""
        
        context = {
            "analysis": {
                "description": data.get("description", ""),
                "business_profile_insights": data.get("business_profile_insights", []),
                "positioning_insights": data.get("positioning_insights", []),
                "target_customer_insights": data.get("target_customer_insights", [])
            }
        }
        
        return await self._call_judge("actionability", context)
    
    async def _judge_redundancy(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """L-3: Content redundancy check - ensure sections don't duplicate content."""
        
        context = {
            "description": data.get("description", ""),
            "business_insights": data.get("business_profile_insights", [])
        }
        
        return await self._call_judge("redundancy", context)
    
    async def _judge_context_steering(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """L-4: Context steering check - validate appropriate context usage."""
        
        context_type = test_case.get("context_type", "none")
        
        if context_type == "none":
            return {
                "pass": True,
                "reason": "No context provided - auto-pass"
            }
        
        context = {
            "user_context": test_case.get("user_inputted_context", ""),
            "context_type": context_type,
            "analysis": data
        }
        
        return await self._call_judge("context_steering", context)


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
    template_dir = Path(__file__).parent / "templates"
    if template_dir.exists():
        asyncio.run(test_llm_judge())
    else:
        print("⚠️  Templates not found - skipping test")