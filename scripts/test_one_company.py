#!/usr/bin/env python3
"""
Test enriched data generation with one company.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.context_orchestrator_agent import ContextOrchestrator
from app.services.product_overview_service import generate_product_overview_service
from app.schemas import ProductOverviewRequest


async def test_company_context():
    """Test company context generation for Intryc."""
    url = "https://intryc.com"
    
    print(f"🏢 Testing company context generation for {url}")
    
    orchestrator = ContextOrchestrator()
    
    request = ProductOverviewRequest(
        website_url=url,
        user_inputted_context=None,
        company_context=None
    )
    
    try:
        result = await generate_product_overview_service(request, orchestrator)
        
        company_context = {
            "company_name": result.company_name,
            "description": result.description,
            "capabilities": result.capabilities[:3] if result.capabilities else [],
            "positioning": result.positioning_insights[:2] if result.positioning_insights else [],
            "objections": result.objections[:2] if result.objections else []
        }
        
        print("✅ Generated company context:")
        print(json.dumps(company_context, indent=2))
        
        # Generate realistic preferences
        preferences = {
            "use_case": "streamline_workflows",
            "emphasis": "pain-point",
            "opening_line": "not-personalized",
            "cta_setting": "meeting",
            "template": "blossomer"
        }
        
        print("\n📋 Generated preferences:")
        print(json.dumps(preferences, indent=2))
        
        return company_context, preferences
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    asyncio.run(test_company_context())