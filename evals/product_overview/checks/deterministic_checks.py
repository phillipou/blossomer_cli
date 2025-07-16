#!/usr/bin/env python3
"""
Deterministic checks for product_overview template evaluation.
These checks run fast and have zero LLM cost.
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, List, Any, Union


def load_schema() -> Dict[str, Any]:
    """Load the JSON schema for validation."""
    schema_path = Path(__file__).parent.parent / "schema" / "product_overview_schema.json"
    with open(schema_path, 'r') as f:
        return json.load(f)


def validate_json(output: str) -> Dict[str, Any]:
    """
    D-1: Valid JSON check
    Ensures the output can be parsed as valid JSON.
    """
    try:
        data = json.loads(output)
        return {"pass": True, "data": data}
    except json.JSONDecodeError as e:
        return {"pass": False, "error": f"Invalid JSON: {str(e)}"}


def validate_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    D-2: Schema compliance check
    Validates against JSON schema and ensures 90% of fields are non-empty.
    """
    schema = load_schema()
    
    try:
        jsonschema.validate(data, schema)
        
        # Check that ≥90% of top-level fields are non-empty
        total_fields = len(data)
        non_empty_count = sum(1 for v in data.values() if v is not None and v != "" and v != [])
        
        if non_empty_count / total_fields >= 0.9:
            return {"pass": True}
        else:
            return {
                "pass": False, 
                "error": f"Only {non_empty_count}/{total_fields} fields populated (need ≥90%)"
            }
            
    except jsonschema.ValidationError as e:
        return {"pass": False, "error": f"Schema validation failed: {str(e)}"}


def validate_format_compliance(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    D-3: Format compliance check
    Ensures all *_insights fields follow "Key: Value" format.
    """
    insight_fields = [
        "business_profile_insights", 
        "use_case_analysis_insights",
        "positioning_insights",
        "target_customer_insights",
        "capabilities",
        "objections"
    ]
    
    for field in insight_fields:
        if field in data and data[field] is not None:
            for i, insight in enumerate(data[field]):
                if ":" not in insight:
                    return {
                        "pass": False, 
                        "error": f"Field '{field}' item {i} missing colon separator: '{insight}'"
                    }
                
                # Check that key part is not empty
                key_part = insight.split(":", 1)[0].strip()
                if not key_part:
                    return {
                        "pass": False,
                        "error": f"Field '{field}' item {i} has empty key part: '{insight}'"
                    }
    
    return {"pass": True}


def validate_field_cardinality(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    D-4: Field cardinality check
    Ensures arrays have appropriate number of items (3-5 for most fields).
    """
    cardinality_rules = {
        "business_profile_insights": (3, 5),
        "capabilities": (3, 5),
        "use_case_analysis_insights": (3, 5),
        "positioning_insights": (3, 5),
        "objections": (3, 5),
        "target_customer_insights": (2, 3)  # Different rule for this field
    }
    
    for field, (min_items, max_items) in cardinality_rules.items():
        if field in data and data[field] is not None:
            item_count = len(data[field])
            if item_count < min_items or item_count > max_items:
                return {
                    "pass": False,
                    "error": f"Field '{field}' has {item_count} items, expected {min_items}-{max_items}"
                }
    
    return {"pass": True}


def validate_url_preservation(data: Dict[str, Any], input_url: str) -> Dict[str, Any]:
    """
    D-5: URL preservation check
    Ensures company_url matches input_website_url exactly.
    """
    if "company_url" not in data:
        return {"pass": False, "error": "company_url field missing"}
    
    if data["company_url"] != input_url:
        return {
            "pass": False,
            "error": f"company_url '{data['company_url']}' does not match input '{input_url}'"
        }
    
    return {"pass": True}


def run_all_checks(output: str, input_vars: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run all deterministic checks in sequence.
    Aborts on first failure for efficiency.
    """
    results = {
        "overall_pass": False,
        "checks": {}
    }
    
    # D-1: Valid JSON
    json_result = validate_json(output)
    results["checks"]["D-1_valid_json"] = json_result
    
    if not json_result["pass"]:
        return results
    
    data = json_result["data"]
    
    # D-2: Schema compliance
    schema_result = validate_schema(data)
    results["checks"]["D-2_schema_compliance"] = schema_result
    
    if not schema_result["pass"]:
        return results
    
    # D-3: Format compliance
    format_result = validate_format_compliance(data)
    results["checks"]["D-3_format_compliance"] = format_result
    
    if not format_result["pass"]:
        return results
    
    # D-4: Field cardinality
    cardinality_result = validate_field_cardinality(data)
    results["checks"]["D-4_field_cardinality"] = cardinality_result
    
    if not cardinality_result["pass"]:
        return results
    
    # D-5: URL preservation
    input_url = input_vars.get("input_website_url", "")
    url_result = validate_url_preservation(data, input_url)
    results["checks"]["D-5_url_preservation"] = url_result
    
    if not url_result["pass"]:
        return results
    
    # All checks passed
    results["overall_pass"] = True
    return results


if __name__ == "__main__":
    # Test with sample data
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
        ],
        "metadata": {
            "sources_used": ["website"],
            "context_quality": "medium",
            "assessment_summary": "Based on website analysis"
        }
    }
    """
    
    input_vars = {"input_website_url": "https://test.com"}
    
    results = run_all_checks(sample_output, input_vars)
    
    print("🧪 Test Results:")
    print(f"Overall Pass: {results['overall_pass']}")
    
    for check_name, check_result in results["checks"].items():
        status = "✅ PASS" if check_result["pass"] else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not check_result["pass"]:
            print(f"  Error: {check_result['error']}")