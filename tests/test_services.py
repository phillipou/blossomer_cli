#!/usr/bin/env python3
"""
Tests for core generation services and LLM integration.
"""

import sys
from pathlib import Path

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.services.gtm_generation_service import gtm_service


def test_gtm_service_initialization():
    """Test GTM service initialization"""
    print("🎯 Testing GTM service initialization...")
    
    # Test service initialization
    assert gtm_service is not None, "GTM service should be initialized"
    assert gtm_service.storage is not None, "GTM service should have storage"
    print("  ✓ GTM service initialized with storage")
    
    # Test non-existent project status
    status = gtm_service.get_project_status("non-existent-domain.com")
    assert not status["exists"], "Non-existent project should not exist"
    print("  ✓ Non-existent project status correct")
    
    # Test new project status
    test_domain = "gtm-test.com"
    gtm_service.storage.create_project(test_domain)
    status = gtm_service.get_project_status(test_domain)
    assert status["exists"], "Created project should exist"
    assert status["progress_percentage"] == 0.0, "New project should have 0% progress"
    print(f"  ✓ Project status: {status['progress_percentage']}% complete")
    
    # Cleanup
    gtm_service.storage.delete_project(test_domain)
    
    print("  ✅ GTM service initialization working correctly\n")


def test_llm_service_imports():
    """Test that all LLM services can be imported"""
    print("🤖 Testing LLM service imports...")
    
    try:
        # Test core LLM classes
        from cli.services.llm_service import LLMClient, OpenAIProvider, LLMRequest, LLMResponse
        print("  ✓ Core LLM classes imported successfully")
        
        # Test LLM singleton
        from cli.services.llm_singleton import get_llm_client
        print("  ✓ LLM singleton imported successfully")
        
        # Test context orchestrator
        from cli.services.context_orchestrator_service import ContextOrchestratorService
        print("  ✓ Context orchestrator imported successfully")
        
        # Test generation services
        from cli.services.product_overview_service import generate_product_overview_service
        from cli.services.target_account_service import generate_target_account_profile
        from cli.services.target_persona_service import generate_target_persona_profile
        from cli.services.email_generation_service import generate_email_campaign_service
        print("  ✓ All generation services imported successfully")
        
    except ImportError as e:
        raise AssertionError(f"Failed to import LLM services: {e}")
    
    print("  ✅ All LLM services can be imported correctly\n")


if __name__ == "__main__":
    test_gtm_service_initialization()
    test_llm_service_imports()
    print("🎉 All service tests passed!")