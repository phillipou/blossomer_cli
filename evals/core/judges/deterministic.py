"""
Base deterministic checks for evaluation.
These checks run fast and have zero LLM cost.
"""

import json
import jsonschema
from typing import Dict, List, Any, Optional
from pathlib import Path

from evals.core.config import EvalConfig


class DeterministicJudge:
    """Handles fast, zero-cost deterministic validation checks."""
    
    def __init__(self, config: EvalConfig):
        self.config = config
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """Load JSON schema for validation."""
        try:
            schema_path = Path(f"evals/prompts/{self.config.prompt_name}/schema.json")
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def evaluate_all(self, output: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all deterministic checks in sequence.
        Aborts on first failure for efficiency.
        """
        results = {
            "overall_pass": False,
            "checks": {},
            "summary": "Deterministic validation results",
            "passed_checks": 0,
            "total_checks": 0
        }
        
        # Define checks to run based on config
        checks = [
            ("D-1_valid_json", self._check_valid_json),
            ("D-2_schema_compliance", self._check_schema_compliance),
            ("D-3_format_compliance", self._check_format_compliance),
            ("D-4_field_cardinality", self._check_field_cardinality),
            ("D-5_url_preservation", self._check_url_preservation),
        ]
        
        # Filter checks based on config
        enabled_checks = [
            (name, func) for name, func in checks 
            if self._is_check_enabled(name)
        ]
        
        results["total_checks"] = len(enabled_checks)
        
        # Parse JSON once if possible
        parsed_data = None
        
        for check_name, check_func in enabled_checks:
            try:
                if check_name == "D-1_valid_json":
                    check_result = check_func(output)
                    if check_result["pass"]:
                        parsed_data = check_result.get("data")
                elif parsed_data is not None:
                    check_result = check_func(parsed_data, test_case)
                else:
                    # Skip remaining checks if JSON parsing failed
                    check_result = {
                        "pass": False,
                        "error": "Skipped due to JSON parsing failure"
                    }
                
                results["checks"][check_name] = check_result
                
                if check_result["pass"]:
                    results["passed_checks"] += 1
                else:
                    # Fail fast - stop on first failure
                    break
                    
            except Exception as e:
                results["checks"][check_name] = {
                    "pass": False,
                    "error": f"Check failed with exception: {str(e)}"
                }
                break
        
        # Overall pass requires all checks to pass
        results["overall_pass"] = results["passed_checks"] == results["total_checks"]
        
        return results
    
    def _is_check_enabled(self, check_name: str) -> bool:
        """Check if a deterministic check is enabled in config."""
        if not self.config.deterministic_checks:
            return True  # Default to all enabled
        
        check_id = check_name.split("_")[0]  # Extract D-1, D-2, etc.
        return check_id in self.config.deterministic_checks
    
    def _check_valid_json(self, output: str) -> Dict[str, Any]:
        """D-1: Valid JSON check."""
        try:
            data = json.loads(output)
            return {"pass": True, "data": data}
        except json.JSONDecodeError as e:
            return {"pass": False, "error": f"Invalid JSON: {str(e)}"}
    
    def _check_schema_compliance(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """D-2: Schema compliance check."""
        if not self.schema:
            return {"pass": True, "warning": "No schema file found, skipping validation"}
        
        try:
            jsonschema.validate(data, self.schema)
            
            # Check that ≥90% of top-level fields are non-empty
            if isinstance(data, dict):
                total_fields = len(data)
                non_empty_count = sum(
                    1 for v in data.values() 
                    if v is not None and v != "" and v != []
                )
                
                if non_empty_count / total_fields >= 0.9:
                    return {"pass": True}
                else:
                    return {
                        "pass": False,
                        "error": f"Only {non_empty_count}/{total_fields} fields populated (need ≥90%)"
                    }
            else:
                return {"pass": True}
                
        except jsonschema.ValidationError as e:
            return {"pass": False, "error": f"Schema validation failed: {str(e)}"}
    
    def _check_format_compliance(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """D-3: Format compliance check."""
        # Check for "Key: Value" format in insight fields
        insight_fields = [
            "business_profile_insights",
            "use_case_analysis_insights", 
            "positioning_insights",
            "target_customer_insights",
            "capabilities",
            "objections"
        ]
        
        for field in insight_fields:
            if field in data and isinstance(data[field], list):
                for i, insight in enumerate(data[field]):
                    if isinstance(insight, str) and ":" not in insight:
                        return {
                            "pass": False,
                            "error": f"Field '{field}' item {i} missing colon separator: '{insight}'"
                        }
                    
                    # Check that key part is not empty
                    if isinstance(insight, str) and ":" in insight:
                        key_part = insight.split(":", 1)[0].strip()
                        if not key_part:
                            return {
                                "pass": False,
                                "error": f"Field '{field}' item {i} has empty key part: '{insight}'"
                            }
        
        return {"pass": True}
    
    def _check_field_cardinality(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """D-4: Field cardinality check."""
        cardinality_rules = {
            "business_profile_insights": (3, 5),
            "capabilities": (3, 5),
            "use_case_analysis_insights": (3, 5),
            "positioning_insights": (3, 5),
            "objections": (3, 5),
            "target_customer_insights": (2, 3)
        }
        
        for field, (min_items, max_items) in cardinality_rules.items():
            if field in data and isinstance(data[field], list):
                item_count = len(data[field])
                if item_count < min_items or item_count > max_items:
                    return {
                        "pass": False,
                        "error": f"Field '{field}' has {item_count} items, expected {min_items}-{max_items}"
                    }
        
        return {"pass": True}
    
    def _check_url_preservation(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """D-5: URL preservation check."""
        input_url = test_case.get("input_website_url", "")
        output_url = data.get("company_url", "")
        
        if not input_url:
            return {"pass": True, "warning": "No input URL to check"}
        
        if not output_url:
            return {
                "pass": False,
                "error": "Output missing company_url field"
            }
        
        # Normalize URLs for comparison
        input_normalized = input_url.lower().rstrip('/')
        output_normalized = output_url.lower().rstrip('/')
        
        # Remove protocol for comparison
        for protocol in ['https://', 'http://']:
            input_normalized = input_normalized.replace(protocol, '')
            output_normalized = output_normalized.replace(protocol, '')
        
        if input_normalized != output_normalized:
            return {
                "pass": False,
                "error": f"URL mismatch: input '{input_url}' vs output '{output_url}'"
            }
        
        return {"pass": True}


# For standalone testing
if __name__ == "__main__":
    # Test with sample data
    from evals.core.config import EvalConfig
    
    config = EvalConfig(
        name="Test Config",
        prompt_name="test",
        service_module="test",
        service_function="test",
        deterministic_checks=["D-1", "D-2", "D-3", "D-4"]
    )
    
    judge = DeterministicJudge(config)
    
    sample_output = """
    {
        "company_name": "Test Company",
        "company_url": "https://test.com",
        "description": "A test company that does testing things.",
        "business_profile_insights": [
            "Category: Testing Software",
            "Business Model: SaaS subscription model",
            "Existing Customers: Fortune 500 companies"
        ],
        "capabilities": [
            "Automated Testing: Runs tests automatically",
            "Performance Monitoring: Tracks application performance", 
            "Bug Tracking: Identifies and tracks bugs"
        ],
        "use_case_analysis_insights": [
            "Process Impact: Streamlines software testing workflows",
            "Problems Addressed: Reduces manual testing overhead",
            "Current State: Teams rely on manual testing processes"
        ],
        "positioning_insights": [
            "Key Market Belief: Manual testing is inefficient and error-prone",
            "Unique Approach: AI-powered automated testing platform",
            "Language Used: Emphasizes speed and reliability"
        ],
        "objections": [
            "Cost Concerns: Higher upfront investment than manual testing",
            "Integration Complexity: Requires changes to existing workflows",
            "Trust Issues: Teams may not trust automated results initially"
        ],
        "target_customer_insights": [
            "Target Accounts: Mid-market to enterprise software companies",
            "Key Personas: QA managers and development team leads"
        ]
    }
    """
    
    test_case = {"input_website_url": "https://test.com"}
    
    results = judge.evaluate_all(sample_output, test_case)
    
    print("🧪 Deterministic Judge Test Results:")
    print(f"Overall Pass: {results['overall_pass']}")
    print(f"Passed Checks: {results['passed_checks']}/{results['total_checks']}")
    
    for check_name, check_result in results["checks"].items():
        status = "✅ PASS" if check_result["pass"] else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not check_result["pass"]:
            print(f"  Error: {check_result.get('error', 'Unknown error')}")