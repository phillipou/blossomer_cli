#!/usr/bin/env python3
"""
Tests for dependency tracking and stale data detection.
"""

import sys
from pathlib import Path

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.services.project_storage import project_storage
from cli.services.gtm_generation_service import gtm_service


def test_dependency_tracking():
    """Test dependency tracking between steps"""
    print("🔗 Testing dependency tracking...")
    
    # Create a test project to get dependency chain
    test_domain = "dependency-test.com"
    project_storage.create_project(test_domain)
    
    # Test dependency chain
    dependency_chain = project_storage.get_dependency_chain(test_domain)
    
    # Expected dependencies
    expected_dependencies = {
        "overview": [],
        "account": ["overview"],
        "persona": ["overview", "account"],
        "email": ["overview", "account", "persona"],
        "plan": ["overview", "account", "persona", "email"]
    }
    
    for step, expected_deps in expected_dependencies.items():
        actual_deps = dependency_chain.get(step, [])
        assert actual_deps == expected_deps, f"Step {step} should depend on {expected_deps}, got {actual_deps}"
        print(f"  ✓ {step}: {actual_deps}")
    
    # Test dependent steps
    dependent_steps = project_storage.get_dependent_steps("overview")
    expected_dependent = ["account", "persona", "email", "plan"]
    assert dependent_steps == expected_dependent, f"Overview dependents should be {expected_dependent}"
    print(f"  ✓ Steps dependent on overview: {dependent_steps}")
    
    # Cleanup
    project_storage.delete_project(test_domain)
    
    print("  ✅ Dependency tracking working correctly\n")


def test_stale_data_detection():
    """Test stale data detection and marking"""
    print("🚨 Testing stale data detection...")
    
    test_domain = "stale-test.com"
    
    # Create project with full pipeline
    project_storage.create_project(test_domain)
    
    # Add mock data for all steps
    steps_data = {
        "overview": {"company_name": "Test Corp", "version": 1},
        "account": {"target_name": "Enterprise", "version": 1},
        "persona": {"persona_name": "Decision Maker", "version": 1},
        "email": {"subject": "Test Email", "version": 1}
    }
    
    for step, data in steps_data.items():
        project_storage.save_step_data(test_domain, step, data)
    
    print("  ✓ Created project with complete pipeline")
    
    # Force regeneration of overview (simulates user edit)
    new_overview = {"company_name": "Test Corp", "version": 2}
    stale_steps = project_storage.mark_steps_stale(test_domain, "overview")
    project_storage.save_step_data(test_domain, "overview", new_overview)
    
    expected_stale = ["account", "persona", "email"]
    assert stale_steps == expected_stale, f"Expected stale steps {expected_stale}, got {stale_steps}"
    print(f"  ✓ Steps marked as stale: {stale_steps}")
    
    # Check stale detection by loading step data
    for step in expected_stale:
        step_data = project_storage.load_step_data(test_domain, step)
        assert step_data.get("_stale", False), f"Step {step} should be marked as stale"
        print(f"  ✓ {step} is correctly marked as stale")
    
    # Cleanup
    project_storage.delete_project(test_domain)
    
    print("  ✅ Stale data detection working correctly\n")


if __name__ == "__main__":
    test_dependency_tracking()
    test_stale_data_detection()
    print("🎉 All dependency tracking tests passed!")