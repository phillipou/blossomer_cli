#!/usr/bin/env python3
"""
LLM Judge implementations using TensorBlock Forge for unified provider access.
"""

import json
import random
import os
from typing import Dict, List, Any, Optional, Tuple

try:
    from openai import OpenAI
except ImportError:
    print("⚠️  openai not installed. Run: pip install openai")
    raise

from judge_prompts import JudgePrompts, PromptValidator


class ForgeJudge:
    """LLM Judge using TensorBlock Forge for unified provider access."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.tensorblock.co/v1"):
        """Initialize Forge judge with API key."""
        
        api_key = api_key or os.getenv("FORGE_API_KEY")
        if not api_key:
            raise ValueError("FORGE_API_KEY environment variable not set")
        
        # Initialize OpenAI client pointed at Forge
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        self.system_prompt = JudgePrompts.get_system_prompt()
        
        self.prompts = JudgePrompts()
        self.validator = PromptValidator()
        
        # Cost tracking (approximate - varies by provider)
        self.cost_estimates = {
            "gemini-1.5-flash": 0.0001,
            "claude-3-5-haiku": 0.001,
            "gpt-4o-mini": 0.0002,
        }
        self.total_calls = 0
    
    def _call_judge(self, prompt: str, expected_check_id: str, model: str = "gemini-1.5-flash", max_retries: int = 2) -> Dict[str, Any]:
        """Make a judge call with error handling and retries."""
        
        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # Low temperature for consistent evaluation
                    max_tokens=1000,
                    response_format={"type": "json_object"}  # Force JSON output
                )
                
                self.total_calls += 1
                
                if not response.choices[0].message.content:
                    raise ValueError("Empty response from model")
                
                response_text = response.choices[0].message.content
                
                # Validate response format
                if not self.validator.validate_response_format(response_text, expected_check_id):
                    if attempt < max_retries:
                        continue  # Retry with same prompt
                    else:
                        raise ValueError("Invalid response format after retries")
                
                result = json.loads(response_text)
                return result
                
            except Exception as e:
                if attempt < max_retries:
                    continue
                
                # Final fallback - return error response
                return {
                    "pass": False,
                    "error": f"Judge evaluation failed after {max_retries + 1} attempts: {str(e)}",
                    "details": [{
                        "check_id": expected_check_id,
                        "reason": f"Technical failure: {str(e)}"
                    }]
                }
        
        return {"pass": False, "error": "Unexpected fallthrough"}
    
    def judge_traceability(self, data: Dict[str, Any], website_content: str, model: str = "gemini-1.5-flash") -> Dict[str, Any]:
        """L-1: Traceability check - verify claims are evidence-based."""
        
        # Sample factual claims from insight fields
        insight_fields = [
            "business_profile_insights",
            "use_case_analysis_insights", 
            "positioning_insights"
        ]
        
        all_claims = []
        for field in insight_fields:
            if field in data and data[field]:
                all_claims.extend([(field, claim) for claim in data[field]])
        
        if len(all_claims) == 0:
            return {
                "pass": False,
                "details": [{
                    "check_id": "L-1",
                    "reason": "No claims found to evaluate"
                }]
            }
        
        # Sample up to 5 claims randomly
        sampled_claims = random.sample(all_claims, min(5, len(all_claims)))
        
        prompt = self.prompts.traceability_prompt(website_content, sampled_claims)
        return self._call_judge(prompt, "L-1", model)
    
    def judge_actionability(self, data: Dict[str, Any], model: str = "gemini-1.5-flash") -> Dict[str, Any]:
        """L-2: Actionability check - evaluate specificity and discovery value."""
        
        prompt = self.prompts.actionability_prompt(data)
        return self._call_judge(prompt, "L-2", model)
    
    def judge_redundancy(self, data: Dict[str, Any], model: str = "gemini-1.5-flash") -> Dict[str, Any]:
        """L-3: Content redundancy check - ensure sections don't duplicate content."""
        
        description = data.get("description", "")
        insights = data.get("business_profile_insights", [])
        
        if not description or not insights:
            return {
                "pass": True,  # Auto-pass if insufficient data
                "details": [{
                    "check_id": "L-3",
                    "reason": "Insufficient data for redundancy check - auto-pass"
                }]
            }
        
        prompt = self.prompts.redundancy_prompt(description, insights)
        return self._call_judge(prompt, "L-3", model)
    
    def judge_context_steering(self, data: Dict[str, Any], user_context: str, context_type: str, model: str = "gemini-1.5-flash") -> Dict[str, Any]:
        """L-4: Context steering check - validate appropriate context usage."""
        
        if context_type == "none":
            # Auto-pass for no context
            return {
                "pass": True,
                "details": [{
                    "check_id": "L-4",
                    "context_type": "none",
                    "reason": "No context provided - auto-pass"
                }]
            }
        
        prompt = self.prompts.context_steering_prompt(data, user_context, context_type)
        return self._call_judge(prompt, "L-4", model)
    
    def run_all_judges(self, data: Dict[str, Any], website_content: str, 
                       user_context: str = "", context_type: str = "none", 
                       model: str = "gemini-1.5-flash") -> Dict[str, Any]:
        """Run all LLM judges and aggregate results."""
        
        results = {
            "overall_pass": False,
            "judges": {},
            "total_cost_estimate": 0.0,
            "judge_calls_made": 0,
            "model_used": model
        }
        
        # Track initial call count
        initial_calls = self.total_calls
        
        # Run each judge with specified model
        judges = [
            ("L-1_traceability", lambda: self.judge_traceability(data, website_content, model)),
            ("L-2_actionability", lambda: self.judge_actionability(data, model)),
            ("L-3_redundancy", lambda: self.judge_redundancy(data, model)),
            ("L-4_context_steering", lambda: self.judge_context_steering(data, user_context, context_type, model))
        ]
        
        all_passed = True
        for judge_name, judge_func in judges:
            result = judge_func()
            results["judges"][judge_name] = result
            
            if not result.get("pass", False):
                all_passed = False
        
        # Calculate actual cost based on calls made and model used
        calls_made = self.total_calls - initial_calls
        cost_per_call = self.cost_estimates.get(model, 0.001)
        results["judge_calls_made"] = calls_made
        results["total_cost_estimate"] = calls_made * cost_per_call
        results["overall_pass"] = all_passed
        
        return results
    
    def get_total_cost(self) -> float:
        """Get total cost for all judge calls made."""
        return self.total_calls * self.cost_per_call


# Main entry point for Promptfoo integration
def evaluate_with_llm_judges(output: str, input_vars: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for Promptfoo integration."""
    
    try:
        data = json.loads(output)
    except json.JSONDecodeError as e:
        return {"pass": False, "error": f"Invalid JSON output: {e}"}
    
    try:
        # Allow model specification via input vars or default to Gemini
        model = input_vars.get("eval_model", "gemini-1.5-flash")
        judge = ForgeJudge()
        
        return judge.run_all_judges(
            data=data,
            website_content=input_vars.get("website_content", ""),
            user_context=input_vars.get("user_inputted_context", ""),
            context_type=input_vars.get("context_type", "none"),
            model=model
        )
        
    except Exception as e:
        return {"pass": False, "error": f"Judge setup failed: {e}"}


if __name__ == "__main__":
    # Test with sample data
    sample_output = '''
    {
        "company_name": "Test Company",
        "company_url": "https://test.com",
        "description": "A test company that provides automated testing solutions for software development teams.",
        "business_profile_insights": [
            "Category: Software Testing Platform",
            "Business Model: SaaS subscription with tiered pricing",
            "Existing Customers: Mid-market software companies and enterprise development teams"
        ],
        "capabilities": [
            "Automated Testing: Runs comprehensive test suites automatically",
            "Performance Monitoring: Tracks application performance metrics",
            "Bug Tracking: Identifies and categorizes software defects"
        ],
        "use_case_analysis_insights": [
            "Process Impact: Streamlines software quality assurance workflows",
            "Problems Addressed: Reduces manual testing overhead and human error",
            "Current State: Teams rely on time-consuming manual testing processes"
        ],
        "positioning_insights": [
            "Key Market Belief: Manual testing is inefficient and error-prone for modern development",
            "Unique Approach: AI-powered automated testing with predictive analytics",
            "Language Used: Emphasizes speed, reliability, and developer productivity"
        ],
        "objections": [
            "Cost Concerns: Higher upfront investment compared to manual testing",
            "Integration Complexity: Requires changes to existing development workflows",
            "Trust Issues: Teams may not initially trust automated test results"
        ],
        "target_customer_insights": [
            "Target Accounts: Mid-market to enterprise software companies with active development",
            "Key Personas: QA managers, development team leads, and DevOps engineers"
        ],
        "metadata": {
            "sources_used": ["website"],
            "context_quality": "medium",
            "assessment_summary": "Based on comprehensive website analysis"
        }
    }
    '''
    
    sample_website_content = "Test Company provides automated testing solutions for software teams. Our platform helps developers ship faster with confidence through AI-powered testing automation."
    
    input_vars = {
        "website_content": sample_website_content,
        "user_inputted_context": "They focus on enterprise clients",
        "context_type": "valid"
    }
    
    print("🧪 Testing Forge Judge Implementation...")
    
    # Test individual functions first
    try:
        from judge_prompts import JudgePrompts
        prompts = JudgePrompts()
        
        sample_claims = [("business_profile_insights", "Category: Software Testing Platform")]
        prompt = prompts.traceability_prompt(sample_website_content, sample_claims)
        
        print("✅ Prompt generation successful")
        print(f"📝 Sample prompt length: {len(prompt)} characters")
        
    except Exception as e:
        print(f"❌ Prompt generation failed: {e}")
    
    # Test full evaluation (requires API key)
    if os.getenv("FORGE_API_KEY"):
        try:
            # Test with different models
            models_to_test = ["gemini-1.5-flash", "claude-3-5-haiku", "gpt-4o-mini"]
            
            for model in models_to_test:
                print(f"\n🔬 Testing with {model}...")
                
                # Add model to input vars for this test
                test_input_vars = {**input_vars, "eval_model": model}
                
                results = evaluate_with_llm_judges(sample_output, test_input_vars)
                
                print(f"📊 Results for {model}:")
                print(f"  Overall Pass: {results.get('overall_pass', 'Unknown')}")
                print(f"  Cost: ${results.get('total_cost_estimate', 0):.4f}")
                print(f"  Judge Calls: {results.get('judge_calls_made', 0)}")
                print(f"  Model Used: {results.get('model_used', 'Unknown')}")
                
                for judge_name, judge_result in results.get("judges", {}).items():
                    status = "✅ PASS" if judge_result.get("pass", False) else "❌ FAIL"
                    print(f"  {judge_name}: {status}")
                    
                    if "error" in judge_result:
                        print(f"    Error: {judge_result['error']}")
                        
        except Exception as e:
            print(f"❌ Full evaluation failed: {e}")
    else:
        print("\n⚠️  Set FORGE_API_KEY environment variable to test actual evaluation")
        print("💡 Forge provides unified access to multiple providers (Gemini, Claude, OpenAI, etc.)")
        print("💡 Models are specified per API call, not via environment variables")