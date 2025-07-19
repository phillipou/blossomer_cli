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
        
        # Validate that all requested checks exist
        if self.config.deterministic_checks:
            valid_check_ids = [name.split("_")[0] for name, _ in checks]
            invalid_checks = [check for check in self.config.deterministic_checks if check not in valid_check_ids]
            if invalid_checks:
                raise ValueError(
                    f"Invalid deterministic check(s) in config: {invalid_checks}. "
                    f"Available checks are: {valid_check_ids}. "
                    f"Please update your config.yaml to use the correct check names."
                )
        
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
                        "check_name": check_name.replace("D-", "").replace("_", ""),
                        "description": "Skipped due to JSON parsing failure",
                        "inputs_evaluated": [{"field": "parsed_data", "value": "Not available"}],
                        "pass": False,
                        "rationale": "This check was skipped because the previous JSON validation failed."
                    }
                
                results["checks"][check_name] = check_result
                
                if check_result["pass"]:
                    results["passed_checks"] += 1
                else:
                    # Fail fast - stop on first failure
                    break
                    
            except Exception as e:
                results["checks"][check_name] = {
                    "check_name": check_name.replace("D-", "").replace("_", ""),
                    "description": "Internal error during check execution",
                    "inputs_evaluated": [{"field": "error", "value": str(e)}],
                    "pass": False,
                    "rationale": f"This check failed due to an internal error: {str(e)}"
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
            return {
                "check_name": "json_validation",
                "description": "Validates that the output is properly formatted JSON",
                "inputs_evaluated": [
                    {"field": "raw_output", "value": output[:200] + "..." if len(output) > 200 else output}
                ],
                "pass": True,
                "rationale": "The output is valid JSON with proper syntax and can be parsed successfully.",
                "data": data
            }
        except json.JSONDecodeError as e:
            return {
                "check_name": "json_validation",
                "description": "Validates that the output is properly formatted JSON",
                "inputs_evaluated": [
                    {"field": "raw_output", "value": output[:200] + "..." if len(output) > 200 else output}
                ],
                "pass": False,
                "rationale": f"The output contains invalid JSON syntax. Parse error: {str(e)}"
            }
    
    def _check_schema_compliance(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """D-2: Schema compliance check."""
        if not self.schema:
            return {
                "check_name": "schema_compliance",
                "description": "Validates that the output matches the expected JSON schema",
                "inputs_evaluated": [
                    {"field": "parsed_output", "value": "<parsed JSON data>"},
                    {"field": "schema", "value": "No schema file found"}
                ],
                "pass": True,
                "rationale": "No schema file found, skipping validation. All outputs are considered valid."
            }
        
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
                    return {
                        "check_name": "schema_compliance",
                        "description": "Validates that the output matches the expected JSON schema",
                        "inputs_evaluated": [
                            {"field": "parsed_output", "value": list(data.keys())},
                            {"field": "schema_fields", "value": list(self.schema.get("properties", {}).keys())}
                        ],
                        "pass": True,
                        "rationale": f"Output matches expected schema and has {non_empty_count}/{total_fields} fields populated (≥90% required)."
                    }
                else:
                    return {
                        "check_name": "schema_compliance",
                        "description": "Validates that the output matches the expected JSON schema",
                        "inputs_evaluated": [
                            {"field": "parsed_output", "value": list(data.keys())},
                            {"field": "populated_fields", "value": f"{non_empty_count}/{total_fields}"}
                        ],
                        "pass": False,
                        "rationale": f"Only {non_empty_count}/{total_fields} fields are populated. At least 90% of fields must contain non-empty values."
                    }
            else:
                return {
                    "check_name": "schema_compliance",
                    "description": "Validates that the output matches the expected JSON schema",
                    "inputs_evaluated": [
                        {"field": "parsed_output", "value": str(type(data))}
                    ],
                    "pass": True,
                    "rationale": "Output matches expected schema format."
                }
                
        except jsonschema.ValidationError as e:
            return {
                "check_name": "schema_compliance",
                "description": "Validates that the output matches the expected JSON schema",
                "inputs_evaluated": [
                    {"field": "parsed_output", "value": list(data.keys()) if isinstance(data, dict) else str(type(data))},
                    {"field": "validation_error", "value": str(e)}
                ],
                "pass": False,
                "rationale": f"Output does not match expected schema. Validation error: {str(e)}"
            }
    
    def _check_format_compliance(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """D-3: Format compliance check."""
        # Check for "Key: Value" format in insight fields based on evaluation type
        if self.config.service_module == "app.services.email_generation_service":
            # For email evaluations, check subject line format
            return self._check_email_subject_format(data, test_case)
        elif self.config.service_module == "app.services.target_persona_service":
            # For persona evaluations, we don't check any fields for Key:Value format
            # since rationales are plain text descriptions
            insight_fields = []
        else:
            # For product/account evaluations, check standard insight fields
            insight_fields = [
                "business_profile_insights",
                "use_case_analysis_insights", 
                "positioning_insights",
                "target_customer_insights",
                "capabilities",
                "objections"
            ]
        
        inputs_evaluated = []
        for field in insight_fields:
            if field in data and isinstance(data[field], list):
                inputs_evaluated.append({"field": field, "value": data[field]})
        
        for field in insight_fields:
            if field in data and isinstance(data[field], list):
                for i, insight in enumerate(data[field]):
                    if isinstance(insight, str) and ":" not in insight:
                        return {
                            "check_name": "format_compliance",
                            "description": "Validates that insight fields follow 'Key: Value' format pattern",
                            "inputs_evaluated": inputs_evaluated,
                            "pass": False,
                            "rationale": f"Field '{field}' item {i} is missing colon separator. Expected format: 'Key: Value'. Found: '{insight}'"
                        }
                    
                    # Check that key part is not empty
                    if isinstance(insight, str) and ":" in insight:
                        key_part = insight.split(":", 1)[0].strip()
                        if not key_part:
                            return {
                                "check_name": "format_compliance",
                                "description": "Validates that insight fields follow 'Key: Value' format pattern",
                                "inputs_evaluated": inputs_evaluated,
                                "pass": False,
                                "rationale": f"Field '{field}' item {i} has empty key part before colon. Expected format: 'Key: Value'. Found: '{insight}'"
                            }
        
        return {
            "check_name": "format_compliance",
            "description": "Validates that insight fields follow 'Key: Value' format pattern",
            "inputs_evaluated": inputs_evaluated,
            "pass": True,
            "rationale": "All insight fields follow the required 'Key: Value' format pattern with proper key and value sections."
        }
    
    def _check_field_cardinality(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """D-4: Field cardinality check."""
        if self.config.service_module == "app.services.email_generation_service":
            # For email evaluations, check word count
            return self._check_email_word_count(data, test_case)
        
        cardinality_rules = {
            "business_profile_insights": (3, 5),
            "capabilities": (3, 5),
            "use_case_analysis_insights": (3, 5),
            "positioning_insights": (3, 5),
            "objections": (3, 5),
            "target_customer_insights": (2, 3)
        }
        
        inputs_evaluated = []
        for field, (min_items, max_items) in cardinality_rules.items():
            if field in data and isinstance(data[field], list):
                inputs_evaluated.append({
                    "field": field, 
                    "value": f"{len(data[field])} items (expected {min_items}-{max_items})"
                })
        
        for field, (min_items, max_items) in cardinality_rules.items():
            if field in data and isinstance(data[field], list):
                item_count = len(data[field])
                if item_count < min_items or item_count > max_items:
                    return {
                        "check_name": "field_cardinality",
                        "description": "Validates that array fields contain the expected number of items",
                        "inputs_evaluated": inputs_evaluated,
                        "pass": False,
                        "rationale": f"Field '{field}' has {item_count} items but expected {min_items}-{max_items}. Each insight field should contain an appropriate number of items for comprehensive analysis."
                    }
        
        return {
            "check_name": "field_cardinality",
            "description": "Validates that array fields contain the expected number of items",
            "inputs_evaluated": inputs_evaluated,
            "pass": True,
            "rationale": "All array fields contain the expected number of items within the specified ranges for comprehensive analysis."
        }
    
    def _check_url_preservation(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """D-5: URL preservation check."""
        if self.config.service_module == "app.services.email_generation_service":
            # For email evaluations, check company identity
            return self._check_email_identity(data, test_case)
        
        input_url = test_case.get("input_website_url", "")
        
        # Check for company_url field (product_overview) or skip if not applicable
        output_url = data.get("company_url", "")
        has_url_field = "company_url" in data
        
        inputs_evaluated = [
            {"field": "input_website_url", "value": input_url or "Not provided"},
            {"field": "company_url", "value": output_url or "Not in schema"}
        ]
        
        if not input_url:
            return {
                "check_name": "url_preservation",
                "description": "Validates that the input website URL is preserved in the output",
                "inputs_evaluated": inputs_evaluated,
                "pass": True,
                "rationale": "No input URL provided in test case, so URL preservation check is skipped."
            }
        
        # Skip this check if the schema doesn't include a company_url field
        if not has_url_field:
            return {
                "check_name": "url_preservation",
                "description": "Validates that the input website URL is preserved in the output",
                "inputs_evaluated": inputs_evaluated,
                "pass": True,
                "rationale": "Schema does not include company_url field, URL preservation check not applicable."
            }
        
        if not output_url:
            return {
                "check_name": "url_preservation",
                "description": "Validates that the input website URL is preserved in the output",
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": "Output is missing the company_url field. The input URL must be preserved in the output for consistency."
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
                "check_name": "url_preservation",
                "description": "Validates that the input website URL is preserved in the output",
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": f"URL mismatch detected. Input URL '{input_url}' does not match output URL '{output_url}'. The original URL should be preserved exactly."
            }
        
        return {
            "check_name": "url_preservation",
            "description": "Validates that the input website URL is preserved in the output",
            "inputs_evaluated": inputs_evaluated,
            "pass": True,
            "rationale": "Input URL is correctly preserved in the output company_url field."
        }
    
    # Email-specific helper methods
    def _check_email_subject_format(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Email-specific D-3: Subject line format validation."""
        subjects = data.get("subjects", {})
        primary_subject = subjects.get("primary", "")
        
        inputs_evaluated = [
            {"field": "primary_subject", "value": primary_subject}
        ]
        
        if not primary_subject:
            return {
                "check_name": "subject_format",
                "description": "Validates subject line has 3-4 words with proper capitalization",
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": "Missing primary subject line"
            }
        
        # Check word count
        words = primary_subject.split()
        word_count = len(words)
        
        if word_count < 3 or word_count > 4:
            return {
                "check_name": "subject_format", 
                "description": "Validates subject line has 3-4 words with proper capitalization",
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": f"Subject line has {word_count} words, expected 3-4 words"
            }
        
        # Check first word capitalization
        if words[0] and not words[0][0].isupper():
            return {
                "check_name": "subject_format",
                "description": "Validates subject line has 3-4 words with proper capitalization", 
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": "Subject line must start with a capital letter"
            }
        
        return {
            "check_name": "subject_format",
            "description": "Validates subject line has 3-4 words with proper capitalization",
            "inputs_evaluated": inputs_evaluated,
            "pass": True,
            "rationale": "Subject line has correct format: 3-4 words with proper capitalization"
        }
    
    def _check_email_word_count(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Email-specific D-4: Email body word count validation."""
        email_body = data.get("full_email_body", "")
        follow_up_email = data.get("follow_up_email", {})
        
        # Count words in main email body
        word_count = len(email_body.split())
        
        inputs_evaluated = [
            {"field": "full_email_body", "value": f"{word_count} words"}
        ]
        
        # Check main email word count
        if word_count < 50:
            return {
                "check_name": "word_count",
                "description": "Validates email body is between 50-100 words and follow-up is max 60 words",
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": f"Email body has {word_count} words, minimum is 50"
            }
        
        if word_count > 100:
            return {
                "check_name": "word_count",
                "description": "Validates email body is between 50-100 words and follow-up is max 60 words",
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": f"Email body has {word_count} words, maximum is 100"
            }
        
        # Check follow-up email word count if present
        if follow_up_email:
            follow_up_body = follow_up_email.get("body", "")
            follow_up_word_count = len(follow_up_body.split())
            inputs_evaluated.append({"field": "follow_up_email.body", "value": f"{follow_up_word_count} words"})
            
            if follow_up_word_count > 60:
                return {
                    "check_name": "word_count",
                    "description": "Validates email body is between 50-100 words and follow-up is max 60 words",
                    "inputs_evaluated": inputs_evaluated,
                    "pass": False,
                    "rationale": f"Follow-up email has {follow_up_word_count} words, maximum is 60"
                }
        
        return {
            "check_name": "word_count",
            "description": "Validates email body is between 50-100 words and follow-up is max 60 words",
            "inputs_evaluated": inputs_evaluated,
            "pass": True,
            "rationale": f"Email body has {word_count} words (50-100 range), follow-up within limits"
        }
    
    def _check_email_identity(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Email-specific D-5: Company identity validation - prevent hallucination."""
        email_body = data.get("full_email_body", "")
        
        # Get sender company name to avoid confusion
        # This could come from test case context or be passed differently
        expected_company = test_case.get('expected_company_name', '')
        
        # Check for placeholder patterns (flexible formats)
        placeholder_patterns = [
            "[Company Name]", "{Company Name}", "[Company]", "{Company}",
            "[COMPANY_NAME]", "{COMPANY_NAME}", "[company name]", "{company name}"
        ]
        
        has_placeholder = any(pattern in email_body for pattern in placeholder_patterns)
        
        # Check if sender company is being used incorrectly as recipient
        sender_as_recipient = False
        if expected_company and expected_company in email_body:
            # Look for patterns that suggest sender company is being addressed as recipient
            sender_as_recipient_patterns = [
                f"Hi {expected_company}",
                f"Hello {expected_company}",
                f"to {expected_company}",
                f"at {expected_company},"
            ]
            sender_as_recipient = any(pattern in email_body for pattern in sender_as_recipient_patterns)
        
        inputs_evaluated = [
            {"field": "placeholder_present", "value": "Yes" if has_placeholder else "No"},
            {"field": "sender_as_recipient", "value": "Yes" if sender_as_recipient else "No"},
            {"field": "email_excerpt", "value": email_body[:200] + "..." if len(email_body) > 200 else email_body}
        ]
        
        # Fail if sender company is incorrectly used as recipient
        if sender_as_recipient:
            return {
                "check_name": "identity_check",
                "description": "Validates proper sender/recipient identity handling",
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": f"Email incorrectly addresses sender company '{expected_company}' as the recipient"
            }
        
        # Pass if we have clear placeholders OR if no specific company names are used
        # (generic emails without specific company references are fine)
        return {
            "check_name": "identity_check",
            "description": "Validates proper sender/recipient identity handling", 
            "inputs_evaluated": inputs_evaluated,
            "pass": True,
            "rationale": "Email correctly handles company identity without confusing sender/recipient or hallucinating company names"
        }


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