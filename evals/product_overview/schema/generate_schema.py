#!/usr/bin/env python3
"""
Generate JSON Schema from Pydantic models for evaluation purposes.
This ensures our evaluation schemas stay in sync with the actual models.
"""

import json
import sys
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "app"))

from schemas import ProductOverviewResponse


def generate_json_schema():
    """Generate JSON Schema from ProductOverviewResponse Pydantic model."""
    
    # Generate schema from Pydantic model
    schema = ProductOverviewResponse.model_json_schema()
    
    # Add evaluation-specific constraints
    schema["title"] = "Product Overview Evaluation Schema"
    schema["description"] = "Schema for validating product_overview.jinja2 template output"
    
    # Add custom validation rules for evaluation
    properties = schema.get("properties", {})
    
    # Ensure Key: Value format validation for insight fields
    insight_fields = [
        "business_profile_insights",
        "capabilities", 
        "use_case_analysis_insights",
        "positioning_insights",
        "objections",
        "target_customer_insights"
    ]
    
    for field in insight_fields:
        if field in properties:
            # Handle both direct arrays and optional arrays (anyOf with null)
            if "items" in properties[field]:
                # Direct array
                properties[field]["items"]["pattern"] = "^[^:]+:.+"
                properties[field]["items"]["description"] = "Must follow 'Key: Value' format"
            elif "anyOf" in properties[field]:
                # Optional array (anyOf with null)
                for any_of_item in properties[field]["anyOf"]:
                    if any_of_item.get("type") == "array" and "items" in any_of_item:
                        any_of_item["items"]["pattern"] = "^[^:]+:.+"
                        any_of_item["items"]["description"] = "Must follow 'Key: Value' format"
    
    # Add URL validation for company_url
    if "company_url" in properties:
        properties["company_url"]["format"] = "uri"
        properties["company_url"]["description"] = "Must match input_website_url exactly"
    
    # Ensure metadata structure
    if "metadata" in properties:
        metadata_props = properties["metadata"].get("properties", {})
        if "context_quality" in metadata_props:
            metadata_props["context_quality"]["enum"] = ["high", "medium", "low"]
    
    return schema


def save_schema(schema: dict, output_path: str):
    """Save generated schema to file."""
    with open(output_path, 'w') as f:
        json.dump(schema, f, indent=2)
    print(f"✅ Generated schema saved to {output_path}")


if __name__ == "__main__":
    # Generate schema
    schema = generate_json_schema()
    
    # Save to file
    output_path = Path(__file__).parent / "product_overview_schema.json"
    save_schema(schema, str(output_path))
    
    # Print summary
    print(f"\n📋 Schema Summary:")
    print(f"Required fields: {len(schema.get('required', []))}")
    print(f"Total properties: {len(schema.get('properties', {}))}")
    print(f"Based on: ProductOverviewResponse Pydantic model")