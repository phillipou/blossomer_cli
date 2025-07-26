#!/usr/bin/env python3
"""
Generate enriched dataset for email evaluation by calling actual services.
Creates realistic company context, target accounts, and personas.
"""

import asyncio
import csv
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.context_orchestrator_agent import ContextOrchestrator
from app.services.product_overview_service import generate_product_overview_service
from app.services.target_account_service import generate_target_account_profile  
from app.services.target_persona_service import generate_target_persona_profile
from app.schemas import ProductOverviewRequest, TargetAccountRequest, TargetPersonaRequest


async def generate_company_context(url: str, orchestrator: ContextOrchestrator):
    """Generate realistic company context using product_overview_service."""
    print(f"🏢 Generating company context for {url}")
    
    request = ProductOverviewRequest(
        website_url=url,
        user_inputted_context=None,
        company_context=None
    )
    
    try:
        result = await generate_product_overview_service(request, orchestrator)
        return {
            "company_name": result.company_name,
            "description": result.description,
            "capabilities": result.capabilities[:3],  # Top 3 capabilities
            "positioning": result.positioning_insights[:2] if result.positioning_insights else [],
            "objections": result.objections[:2] if result.objections else []
        }
    except Exception as e:
        print(f"❌ Error generating company context for {url}: {e}")
        return None


async def generate_target_account_context(url: str, account_name: str, hypothesis: str):
    """Generate realistic target account context."""
    print(f"🎯 Generating target account context for {account_name}")
    
    request = TargetAccountRequest(
        website_url=url,
        account_profile_name=account_name,
        hypothesis=hypothesis,
        additional_context=None
    )
    
    try:
        result = await generate_target_account_profile(request)
        return {
            "account_profile_name": result.target_account_name,
            "firmographics": result.firmographics.dict() if result.firmographics else {},
            "buying_signals": [signal.dict() for signal in result.buying_signals[:2]] if result.buying_signals else [],
            "use_cases": result.primary_use_cases[:2] if result.primary_use_cases else []
        }
    except Exception as e:
        print(f"❌ Error generating target account for {account_name}: {e}")
        return None


async def generate_target_persona_context(url: str, persona_name: str, hypothesis: str):
    """Generate realistic target persona context."""
    print(f"👤 Generating target persona context for {persona_name}")
    
    request = TargetPersonaRequest(
        website_url=url,
        persona_profile_name=persona_name,
        hypothesis=hypothesis,
        additional_context=None
    )
    
    try:
        result = await generate_target_persona_profile(request)
        return {
            "target_persona_name": result.target_persona_name,
            "responsibilities": result.responsibilities[:3] if result.responsibilities else [],
            "pain_points": result.pain_points[:3] if result.pain_points else [],
            "goals": result.goals[:2] if result.goals else [],
            "persona_signals": [signal.dict() for signal in result.persona_signals[:2]] if result.persona_signals else []
        }
    except Exception as e:
        print(f"❌ Error generating target persona for {persona_name}: {e}")
        return None


def generate_realistic_preferences(account_context: dict, persona_context: dict) -> dict:
    """Generate realistic email preferences based on account/persona context."""
    
    # Determine use case based on persona pain points
    use_cases = [
        "streamline_workflows", "reduce_manual_work", "improve_efficiency", 
        "scale_operations", "enhance_security", "reduce_costs"
    ]
    
    pain_points = persona_context.get("pain_points", []) if persona_context else []
    if pain_points and any("workflow" in str(pain).lower() for pain in pain_points):
        use_case = "streamline_workflows"
    elif pain_points and any("manual" in str(pain).lower() for pain in pain_points):
        use_case = "reduce_manual_work"
    elif pain_points and any("scale" in str(pain).lower() for pain in pain_points):
        use_case = "scale_operations"
    else:
        use_case = "improve_efficiency"
    
    # Vary other preferences for diversity
    emphases = ["pain-point", "desired-outcome"]
    opening_lines = ["not-personalized", "buying-signal", "company-research"]
    cta_settings = ["meeting", "demo", "resource"]
    
    return {
        "use_case": use_case,
        "emphasis": "pain-point",  # Most common for founder emails
        "opening_line": "not-personalized",  # Safe default for evaluation
        "cta_setting": "meeting",  # Most common CTA
        "template": "blossomer"
    }


async def main():
    print("🚀 Generating enriched email evaluation dataset...")
    
    # Load existing dataset
    input_file = Path("evals/datasets/eval_test_inputs.csv")
    output_file = Path("evals/datasets/email_eval_enriched.csv")
    
    orchestrator = ContextOrchestrator()
    enriched_rows = []
    
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        existing_rows = list(reader)
    
    # Filter to only "valid" context type rows for enrichment
    valid_rows = [row for row in existing_rows if row['context_type'] == 'valid']
    
    print(f"📊 Processing {len(valid_rows)} companies with valid context...")
    
    for row in valid_rows:
        url = row['input_website_url']
        company_name = row['expected_company_name']
        account_name = row['account_profile_name']
        persona_name = row['persona_profile_name']
        account_hypothesis = row['account_hypothesis']
        persona_hypothesis = row['persona_hypothesis']
        
        print(f"\n🔄 Processing {company_name} ({url})")
        
        # Generate enriched contexts
        company_context = await generate_company_context(url, orchestrator)
        account_context = await generate_target_account_context(url, account_name, account_hypothesis)
        persona_context = await generate_target_persona_context(url, persona_name, persona_hypothesis)
        
        if company_context and account_context and persona_context:
            preferences = generate_realistic_preferences(account_context, persona_context)
            
            enriched_row = {
                "input_website_url": url,
                "context_type": "valid",
                "expected_company_name": company_name,
                "company_context": json.dumps(company_context),
                "target_account_context": json.dumps(account_context),
                "target_persona_context": json.dumps(persona_context),
                "preferences": json.dumps(preferences),
                # Keep original fields for backward compatibility
                "account_profile_name": account_name,
                "persona_profile_name": persona_name,
                "account_hypothesis": account_hypothesis,
                "persona_hypothesis": persona_hypothesis
            }
            
            enriched_rows.append(enriched_row)
            print(f"✅ Successfully enriched {company_name}")
        else:
            print(f"❌ Failed to enrich {company_name} - skipping")
    
    # Write enriched dataset
    if enriched_rows:
        fieldnames = [
            "input_website_url", "context_type", "expected_company_name",
            "company_context", "target_account_context", "target_persona_context", 
            "preferences", "account_profile_name", "persona_profile_name",
            "account_hypothesis", "persona_hypothesis"
        ]
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched_rows)
        
        print(f"\n🎉 Generated enriched dataset: {output_file}")
        print(f"📝 Created {len(enriched_rows)} enriched rows")
        
        # Show preview
        print(f"\n📋 Preview of first row:")
        first_row = enriched_rows[0]
        for key, value in first_row.items():
            if key in ["company_context", "target_account_context", "target_persona_context", "preferences"]:
                # Pretty print JSON
                parsed = json.loads(value)
                print(f"  {key}: {json.dumps(parsed, indent=2)[:200]}...")
            else:
                print(f"  {key}: {value}")
    else:
        print("❌ No enriched rows generated - check for errors above")


if __name__ == "__main__":
    asyncio.run(main())