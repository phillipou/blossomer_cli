#!/usr/bin/env python3
"""
Tests for project storage system and file management.
"""

import sys
from pathlib import Path

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.services.project_storage import project_storage
from cli.utils.domain import normalize_domain


def test_project_storage_initialization():
    """Test project storage system initialization"""
    print("📁 Testing project storage initialization...")
    
    # Test base directory creation
    assert project_storage.base_dir.exists(), "Base directory should exist"
    print(f"  ✓ Base directory exists: {project_storage.base_dir}")
    
    # Test state file path
    state_file = project_storage.base_dir / ".gtm-cli-state.json"
    print(f"  ✓ State file path correct: {state_file}")
    
    print("  ✅ Project storage initialized correctly\n")


def test_project_creation_and_deletion():
    """Test project creation and deletion"""
    print("🏗️  Testing project creation and deletion...")
    
    test_domain = "test-domain.com"
    
    # Test creation
    project_dir = project_storage.create_project(test_domain)
    assert project_dir.exists(), "Project directory should exist after creation"
    print(f"  ✓ Created project directory: {project_dir}")
    
    # Test export directory
    export_dir = project_dir / "export"
    assert export_dir.exists(), "Export directory should exist"
    print(f"  ✓ Export directory created: {export_dir}")
    
    # Test metadata file
    metadata_file = project_dir / ".metadata.json"
    assert metadata_file.exists(), "Metadata file should exist"
    print(f"  ✓ Metadata file created: {metadata_file}")
    
    # Test existence check
    assert project_storage.project_exists(test_domain), "Project should exist"
    print(f"  ✓ Project existence check working")
    
    # Test deletion
    success = project_storage.delete_project(test_domain)
    assert success, "Project deletion should succeed"
    assert not project_storage.project_exists(test_domain), "Project should not exist after deletion"
    print(f"  ✓ Project deleted successfully")
    
    print("  ✅ Project creation and deletion working correctly\n")


def test_step_data_storage():
    """Test step data storage and retrieval"""
    print("💾 Testing step data storage...")
    
    test_domain = "storage-test.com"
    test_data = {
        "company_name": "Test Company",
        "description": "A test company for storage testing"
    }
    
    # Save data
    file_path = project_storage.save_step_data(test_domain, "overview", test_data)
    assert file_path.exists(), "Step file should exist after saving"
    print(f"  ✓ Saved overview data to: {file_path}")
    
    # Load data
    loaded_data = project_storage.load_step_data(test_domain, "overview")
    assert loaded_data is not None, "Should be able to load saved data"
    assert loaded_data["company_name"] == "Test Company", "Loaded data should match saved data"
    print(f"  ✓ Loaded data correctly: {loaded_data['company_name']}")
    
    # Check available steps
    available_steps = project_storage.get_available_steps(test_domain)
    assert "overview" in available_steps, "Overview should be in available steps"
    print(f"  ✓ Available steps: {available_steps}")
    
    # Cleanup
    project_storage.delete_project(test_domain)
    
    print("  ✅ Step data storage working correctly\n")


def test_project_listing():
    """Test project listing functionality"""
    print("📋 Testing project listing...")
    
    # Create multiple test projects
    test_domains = ["list-test-1.com", "list-test-2.com"]
    normalized_domains = [normalize_domain(d).domain for d in test_domains]
    
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


if __name__ == "__main__":
    test_project_storage_initialization()
    test_project_creation_and_deletion()
    test_step_data_storage()
    test_project_listing()
    print("🎉 All project storage tests passed!")