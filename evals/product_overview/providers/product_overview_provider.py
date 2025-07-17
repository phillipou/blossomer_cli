#!/usr/bin/env python3
"""
Custom Promptfoo provider for product overview template evaluation.
Integrates with our existing TensorForge infrastructure and cached website content.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List

# Setup environment using shared utility
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.env_setup import full_setup, get_project_root
full_setup()

# Add project root to path for imports
sys.path.insert(0, str(get_project_root()))

def call_api(prompt: str, options: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simplified Promptfoo provider using existing CLI infrastructure.
    This function is called by Promptfoo for each test case.
    """
    
    # Check for required environment variables
    if not os.getenv("FORGE_API_KEY"):
        return {
            "error": "FORGE_API_KEY environment variable is not set. Please add it to your .env file or environment.",
            "output": None
        }
    
    try:
        # Import existing CLI service
        from cli.services.product_overview_service import generate_product_overview_service
        from app.schemas import ProductOverviewRequest
        
        # Extract variables from context (comes from CSV)
        test_vars = context.get("vars", {})
        if not test_vars:
            test_vars = context
        
        input_website_url = test_vars.get("input_website_url", "")
        user_inputted_context = test_vars.get("user_inputted_context", "")
        
        if not input_website_url:
            return {
                "error": "input_website_url not provided in test variables",
                "output": None
            }
        
        # Create request object
        request_data = ProductOverviewRequest(
            website_url=input_website_url,
            user_inputted_context=user_inputted_context
        )
        
        # Use async wrapper for the analysis call
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Call the CLI service directly
            result = loop.run_until_complete(
                generate_product_overview_service(request_data)
            )
            
            # Convert result to JSON string
            if hasattr(result, 'model_dump'):
                response_json = result.model_dump()
            elif hasattr(result, 'dict'):
                response_json = result.dict()
            else:
                response_json = result
            
            response_text = json.dumps(response_json, indent=2)
            
            return {
                "output": response_text,
                "tokenUsage": {
                    "total": 0,  # Not tracked in CLI
                    "prompt": 0,
                    "completion": 0
                },
                "cost": 0.0  # Not tracked in CLI
            }
            
        finally:
            loop.close()
            
    except ImportError as e:
        return {
            "error": f"Failed to import CLI service: {e}. Make sure CLI is properly set up.",
            "output": None
        }
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "output": None
        }

if __name__ == "__main__":
    # Test the provider directly
    test_context = {
        "vars": {
            "input_website_url": "https://mandrel.tech",
            "context_type": "none",
            "user_inputted_context": ""
        }
    }
    
    result = call_api("", {}, test_context)
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ Provider test successful!")
        print(f"📊 Output length: {len(result.get('output', ''))}")
        print(f"💰 Cost: ${result.get('cost', 0):.6f}")
        
        # Try to parse as JSON to validate format
        try:
            json.loads(result.get('output', ''))
            print("✅ Output is valid JSON")
        except json.JSONDecodeError as e:
            print(f"❌ Output is not valid JSON: {e}")