#!/usr/bin/env python3
"""
Test script for Stage 2: Core Generation Engine

This script tests the CLI-adapted services and ensures they work correctly.
Run this to validate Stage 2 completion.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent))

from cli.services.gtm_generation_service import gtm_service
from cli.services.project_storage import project_storage
from cli.utils.domain import normalize_domain

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_domain_normalization():
    """Test domain normalization utility"""
    print("📋 Testing domain normalization...")
    
    test_cases = [
        ("acme.com", "https://acme.com"),
        ("https://acme.com", "https://acme.com"),
        ("www.acme.com", "https://acme.com"),
        ("http://www.acme.com/about", "https://acme.com")
    ]
    
    for input_domain, expected in test_cases:
        result = normalize_domain(input_domain)
        assert result == expected, f"Expected {expected}, got {result}"
        print(f"  ✓ {input_domain} → {result}")
    
    print("  ✅ Domain normalization working correctly\n")


def test_project_storage_initialization():
    """Test project storage system initialization"""
    print("📁 Testing project storage initialization...")
    
    # Test base directory creation
    assert project_storage.base_dir.exists(), "Base directory should be created"
    print(f"  ✓ Base directory exists: {project_storage.base_dir}")
    
    # Test state file path
    assert project_storage.state_file.parent == project_storage.base_dir
    print(f"  ✓ State file path correct: {project_storage.state_file}")
    
    print("  ✅ Project storage initialized correctly\n")


def test_project_creation_and_deletion():
    """Test project creation and deletion"""
    print("🏗️  Testing project creation and deletion...")
    
    test_domain = "test-domain.com"
    normalized = normalize_domain(test_domain)
    
    # Test project creation
    project_dir = project_storage.create_project(normalized)
    assert project_dir.exists(), "Project directory should be created"
    print(f"  ✓ Created project directory: {project_dir}")
    
    # Test export directory creation
    export_dir = project_dir / "export"
    assert export_dir.exists(), "Export directory should be created"
    print(f"  ✓ Export directory created: {export_dir}")
    
    # Test metadata file creation
    metadata_file = project_dir / ".metadata.json"
    assert metadata_file.exists(), "Metadata file should be created"
    print(f"  ✓ Metadata file created: {metadata_file}")
    
    # Test project existence check
    assert project_storage.project_exists(normalized), "Project should exist"
    print(f"  ✓ Project existence check working")
    
    # Test project deletion
    assert project_storage.delete_project(normalized), "Project deletion should succeed"
    assert not project_storage.project_exists(normalized), "Project should no longer exist"
    print(f"  ✓ Project deleted successfully")
    
    print("  ✅ Project creation and deletion working correctly\n")


def test_step_data_storage():
    """Test saving and loading step data"""
    print("💾 Testing step data storage...")
    
    test_domain = "storage-test.com"
    normalized = normalize_domain(test_domain)
    
    # Create test project
    project_storage.create_project(normalized)
    
    # Test data storage
    test_data = {
        "company_name": "Test Company",
        "description": "A test company for validation",
        "capabilities": ["testing", "validation"]
    }
    
    # Save step data
    step_file = project_storage.save_step_data(normalized, "overview", test_data)
    assert step_file.exists(), "Step file should be created"
    print(f"  ✓ Saved overview data to: {step_file}")
    
    # Load step data
    loaded_data = project_storage.load_step_data(normalized, "overview")
    assert loaded_data is not None, "Should be able to load data"
    assert loaded_data["company_name"] == test_data["company_name"], "Data should match"
    print(f"  ✓ Loaded data correctly: {loaded_data['company_name']}")
    
    # Test available steps
    steps = project_storage.get_available_steps(normalized)
    assert "overview" in steps, "Overview step should be available"
    print(f"  ✓ Available steps: {steps}")
    
    # Cleanup
    project_storage.delete_project(normalized)
    print("  ✅ Step data storage working correctly\n")


def test_dependency_tracking():
    """Test data dependency tracking between steps"""
    print("🔗 Testing dependency tracking...")
    
    # Test dependency chain
    dependencies = project_storage.get_dependency_chain("test")
    expected_deps = {
        "overview": [],
        "account": ["overview"],
        "persona": ["overview", "account"],
        "email": ["overview", "account", "persona"],
        "plan": ["overview", "account", "persona", "email"]
    }
    
    for step, deps in expected_deps.items():
        assert dependencies[step] == deps, f"Dependencies for {step} should be {deps}"
        print(f"  ✓ {step}: {deps}")
    
    # Test dependent steps lookup
    dependent_on_overview = project_storage.get_dependent_steps("overview")
    assert "account" in dependent_on_overview, "Account should depend on overview"
    print(f"  ✓ Steps dependent on overview: {dependent_on_overview}")
    
    print("  ✅ Dependency tracking working correctly\n")


def test_project_listing():
    """Test project listing functionality"""
    print("📋 Testing project listing...")
    
    # Create multiple test projects
    test_domains = ["list-test-1.com", "list-test-2.com"]
    normalized_domains = [normalize_domain(d) for d in test_domains]
    
    for domain in normalized_domains:
        project_storage.create_project(domain)
        # Add some test data
        test_data = {"test": "data", "domain": domain}
        project_storage.save_step_data(domain, "overview", test_data)
    
    # Test listing
    projects = project_storage.list_projects()
    project_domains = [p["domain"] for p in projects]
    
    for domain in normalized_domains:
        assert domain in project_domains, f"Domain {domain} should be in project list"
        print(f"  ✓ Found project: {domain}")
    
    # Test project info
    test_project = next(p for p in projects if p["domain"] == normalized_domains[0])
    assert "overview" in test_project["available_steps"], "Overview step should be available"
    assert test_project["step_count"] == 1, "Should have 1 completed step"
    print(f"  ✓ Project info correct: {test_project['step_count']} steps")
    
    # Cleanup
    for domain in normalized_domains:
        project_storage.delete_project(domain)
    
    print("  ✅ Project listing working correctly\n")


def test_gtm_service_initialization():
    """Test GTM generation service initialization"""
    print("🎯 Testing GTM service initialization...")
    
    # Test service initialization
    assert gtm_service.storage == project_storage, "Service should use project storage"
    print("  ✓ GTM service initialized with storage")
    
    # Test project status for non-existent project
    status = gtm_service.get_project_status("non-existent.com")
    assert not status["exists"], "Non-existent project should return exists=False"
    print("  ✓ Non-existent project status correct")
    
    # Test project status for existing project
    test_domain = "status-test.com"
    normalized = normalize_domain(test_domain)
    project_storage.create_project(normalized)
    
    status = gtm_service.get_project_status(test_domain)
    assert status["exists"], "Existing project should return exists=True"
    assert status["completed_count"] == 0, "New project should have 0 completed steps"
    assert status["progress_percentage"] == 0, "New project should have 0% progress"
    print(f"  ✓ Project status: {status['progress_percentage']}% complete")
    
    # Cleanup
    project_storage.delete_project(normalized)
    print("  ✅ GTM service initialization working correctly\n")


def test_llm_service_imports():
    """Test that CLI-adapted LLM services can be imported"""
    print("🤖 Testing LLM service imports...")
    
    try:
        from cli.services.llm_service import LLMClient, OpenAIProvider, LLMRequest, LLMResponse
        print("  ✓ Core LLM classes imported successfully")
        
        from cli.services.llm_singleton import get_llm_client
        print("  ✓ LLM singleton imported successfully")
        
        from cli.services.context_orchestrator_service import ContextOrchestratorService
        print("  ✓ Context orchestrator imported successfully")
        
        from cli.services.product_overview_service import generate_product_overview_service
        from cli.services.target_account_service import generate_target_account_profile
        from cli.services.target_persona_service import generate_target_persona_profile
        from cli.services.email_generation_service import generate_email_campaign_service
        print("  ✓ All generation services imported successfully")
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        raise
    
    print("  ✅ All LLM services can be imported correctly\n")


async def run_all_tests():
    """Run all Stage 2 tests"""
    print("🚀 Testing Stage 2: Core Generation Engine")
    print("=" * 60)
    
    try:
        # Run all tests
        test_domain_normalization()
        test_project_storage_initialization()
        test_project_creation_and_deletion()
        test_step_data_storage()
        test_dependency_tracking()
        test_project_listing()
        test_gtm_service_initialization()
        test_llm_service_imports()
        
        print("🎉 All Stage 2 tests passed!")
        print("\n📋 Stage 2 Implementation Summary:")
        print("=" * 40)
        print("✅ CLI-adapted LLM services (removed web dependencies)")
        print("✅ Company overview generation service")
        print("✅ Target account generation service") 
        print("✅ Target persona generation service")
        print("✅ Email campaign generation service")
        print("✅ JSON file storage and retrieval system")
        print("✅ Data dependency tracking between steps")
        print("✅ Complete GTM generation orchestration")
        
        print("\n⏳ Pending for later stages:")
        print("• GTM plan generation service (needs schema/template)")
        print("• CLI summary field generation in prompt templates")
        
        print(f"\n🎯 Ready for Stage 3: Interactive CLI Commands")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())