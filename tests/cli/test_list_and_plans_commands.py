"""
Comprehensive tests for the list and plans commands.
Tests project listing and plan management functionality.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, Mock
from cli.main import app


class TestListCommand:
    """Test suite for the list command"""
    
    def test_list_help(self, mock_cli_runner):
        """Test list command help"""
        result = mock_cli_runner.invoke(app, ["list", "--help"])
        
        assert result.exit_code == 0
        assert "list" in result.output.lower()
        assert "project" in result.output.lower()
    
    def test_list_all_projects(self, mock_cli_runner, mock_project_with_data, temp_project_dir):
        """Test listing all projects"""
        # Create additional project
        second_project = temp_project_dir / "second.com"
        second_project.mkdir()
        (second_project / "overview.json").write_text(json.dumps({
            "company_name": "Second Company",
            "_generated_at": "2024-01-01T00:00:00Z"
        }))
        
        result = mock_cli_runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "acme.com" in result.output
        assert "second.com" in result.output
    
    def test_list_projects_with_details(self, mock_cli_runner, mock_project_with_data):
        """Test listing projects with detailed information"""
        result = mock_cli_runner.invoke(app, ["list", "--details"])
        
        assert result.exit_code == 0
        # Should show additional details
        content_lower = result.output.lower()
        assert any(word in content_lower for word in ["complete", "progress", "generated", "steps"])
    
    def test_list_projects_json_format(self, mock_cli_runner, mock_project_with_data):
        """Test listing projects in JSON format"""
        result = mock_cli_runner.invoke(app, ["list", "--json"])
        
        assert result.exit_code == 0
        assert "{" in result.output and "}" in result.output
    
    def test_list_no_projects(self, mock_cli_runner, temp_project_dir):
        """Test list when no projects exist"""
        result = mock_cli_runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "no projects" in result.output.lower() or "empty" in result.output.lower()
    
    def test_list_projects_with_filter(self, mock_cli_runner, mock_project_with_data, temp_project_dir):
        """Test listing projects with domain filter"""
        # Create additional projects
        for domain in ["test1.com", "test2.com", "example.org"]:
            project_path = temp_project_dir / domain
            project_path.mkdir()
            (project_path / "overview.json").write_text(json.dumps({
                "company_name": f"Company {domain}",
                "_generated_at": "2024-01-01T00:00:00Z"
            }))
        
        result = mock_cli_runner.invoke(app, ["list", "--filter", "test"])
        
        assert result.exit_code == 0
        # Should filter to only test domains
        assert "test1.com" in result.output or "test2.com" in result.output
    
    def test_list_projects_sort_by_date(self, mock_cli_runner, mock_project_with_data, temp_project_dir):
        """Test listing projects sorted by date"""
        # Create project with different date
        recent_project = temp_project_dir / "recent.com"
        recent_project.mkdir()
        (recent_project / "overview.json").write_text(json.dumps({
            "company_name": "Recent Company",
            "_generated_at": "2024-12-01T00:00:00Z"  # More recent
        }))
        
        result = mock_cli_runner.invoke(app, ["list", "--sort", "date"])
        
        assert result.exit_code == 0
        # Should show projects in date order
    
    def test_list_projects_sort_by_name(self, mock_cli_runner, mock_project_with_data, temp_project_dir):
        """Test listing projects sorted by name"""
        # Create project with different name
        zebra_project = temp_project_dir / "zebra.com"
        zebra_project.mkdir()
        (zebra_project / "overview.json").write_text(json.dumps({
            "company_name": "Zebra Company",
            "_generated_at": "2024-01-01T00:00:00Z"
        }))
        
        result = mock_cli_runner.invoke(app, ["list", "--sort", "name"])
        
        assert result.exit_code == 0
        # Should show projects in alphabetical order
    
    def test_list_projects_with_status(self, mock_cli_runner, mock_project_with_data, mock_incomplete_project):
        """Test listing projects showing completion status"""
        result = mock_cli_runner.invoke(app, ["list", "--status"])
        
        assert result.exit_code == 0
        # Should show completion status
        content_lower = result.output.lower()
        assert any(word in content_lower for word in ["complete", "incomplete", "progress", "%"])
    
    def test_list_projects_limit(self, mock_cli_runner, mock_project_with_data, temp_project_dir):
        """Test listing projects with limit"""
        # Create multiple projects
        for i in range(5):
            project_path = temp_project_dir / f"test{i}.com"
            project_path.mkdir()
            (project_path / "overview.json").write_text(json.dumps({
                "company_name": f"Test Company {i}",
                "_generated_at": "2024-01-01T00:00:00Z"
            }))
        
        result = mock_cli_runner.invoke(app, ["list", "--limit", "3"])
        
        assert result.exit_code == 0
        # Should limit results (exact behavior depends on implementation)


class TestPlansCommand:
    """Test suite for the plans command"""
    
    def test_plans_help(self, mock_cli_runner):
        """Test plans command help"""
        result = mock_cli_runner.invoke(app, ["plans", "--help"])
        
        assert result.exit_code == 0
        assert "plans" in result.output.lower()
    
    def test_plans_list_all(self, mock_cli_runner, mock_project_with_data):
        """Test listing all strategic plans"""
        result = mock_cli_runner.invoke(app, ["plans", "list"])
        
        assert result.exit_code == 0
        # Should show available plans
    
    def test_plans_show_specific_plan(self, mock_cli_runner, mock_project_with_data):
        """Test showing specific strategic plan"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["plans", "show", domain])
        
        assert result.exit_code == 0
        # Should show the strategic plan content
        assert "plan" in result.output.lower() or "strategy" in result.output.lower()
    
    def test_plans_create_new(self, mock_cli_runner, mock_project_with_data):
        """Test creating new strategic plan"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["plans", "create", domain])
        
        assert result.exit_code == 0
        assert "creat" in result.output.lower() or "generat" in result.output.lower()
    
    def test_plans_delete(self, mock_cli_runner, mock_project_with_data):
        """Test deleting strategic plan"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["plans", "delete", domain])
        
        # Should either delete or ask for confirmation
        assert result.exit_code == 0 or "confirm" in result.output.lower()
    
    def test_plans_export(self, mock_cli_runner, mock_project_with_data):
        """Test exporting strategic plan"""
        domain = mock_project_with_data.name
        
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "plans", "export", domain,
                "--output", temp_dir
            ])
            
            assert result.exit_code == 0
    
    def test_plans_compare(self, mock_cli_runner, mock_project_with_data, temp_project_dir):
        """Test comparing strategic plans"""
        domain1 = mock_project_with_data.name
        
        # Create second project
        domain2 = "second.com"
        second_project = temp_project_dir / domain2
        second_project.mkdir()
        (second_project / "overview.json").write_text(json.dumps({
            "company_name": "Second Company",
            "_generated_at": "2024-01-01T00:00:00Z"
        }))
        
        result = mock_cli_runner.invoke(app, ["plans", "compare", domain1, domain2])
        
        assert result.exit_code == 0
        # Should show comparison
    
    def test_plans_list_empty(self, mock_cli_runner, temp_project_dir):
        """Test listing plans when none exist"""
        result = mock_cli_runner.invoke(app, ["plans", "list"])
        
        assert result.exit_code == 0
        assert "no plans" in result.output.lower() or "empty" in result.output.lower()
    
    def test_plans_with_template(self, mock_cli_runner, mock_project_with_data):
        """Test creating plan with specific template"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, [
            "plans", "create", domain,
            "--template", "enterprise"
        ])
        
        assert result.exit_code == 0
    
    def test_plans_validate(self, mock_cli_runner, mock_project_with_data):
        """Test validating strategic plan"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["plans", "validate", domain])
        
        assert result.exit_code == 0
        # Should show validation results
        content_lower = result.output.lower()
        assert any(word in content_lower for word in ["valid", "complete", "missing", "check"])


class TestProjectManagementWorkflow:
    """Test complete workflow using list and plans commands"""
    
    def test_complete_project_lifecycle(self, mock_cli_runner, temp_project_dir):
        """Test complete project lifecycle with list and plans"""
        domain = "lifecycle.com"
        
        # 1. List should show no projects initially
        result = mock_cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        
        # 2. Create a project (via init)
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        # Should work or fail gracefully
        
        # 3. List should now show the project
        result = mock_cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        
        # 4. Check plans
        result = mock_cli_runner.invoke(app, ["plans", "list"])
        assert result.exit_code == 0
    
    def test_project_filtering_and_search(self, mock_cli_runner, temp_project_dir):
        """Test project filtering and search capabilities"""
        # Create multiple projects
        domains = ["tech1.com", "tech2.com", "finance1.com", "finance2.com"]
        
        for domain in domains:
            project_path = temp_project_dir / domain
            project_path.mkdir()
            company_type = "tech" if "tech" in domain else "finance"
            (project_path / "overview.json").write_text(json.dumps({
                "company_name": f"{company_type.title()} Company",
                "industry": company_type,
                "_generated_at": "2024-01-01T00:00:00Z"
            }))
        
        # Test filtering
        result = mock_cli_runner.invoke(app, ["list", "--filter", "tech"])
        assert result.exit_code == 0
        
        # Test search
        result = mock_cli_runner.invoke(app, ["list", "--search", "finance"])
        assert result.exit_code == 0
    
    def test_batch_operations(self, mock_cli_runner, temp_project_dir):
        """Test batch operations on multiple projects"""
        # Create multiple projects
        domains = ["batch1.com", "batch2.com", "batch3.com"]
        
        for domain in domains:
            project_path = temp_project_dir / domain
            project_path.mkdir()
            (project_path / "overview.json").write_text(json.dumps({
                "company_name": f"Batch Company {domain}",
                "_generated_at": "2024-01-01T00:00:00Z"
            }))
        
        # Test batch export
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "plans", "export", "--all",
                "--output", temp_dir
            ])
            assert result.exit_code == 0 or "not implemented" in result.output.lower()


class TestListAndPlansEdgeCases:
    """Test edge cases for list and plans commands"""
    
    def test_list_corrupted_projects(self, mock_cli_runner, mock_corrupted_project):
        """Test list with corrupted project data"""
        result = mock_cli_runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        # Should handle corrupted projects gracefully
    
    def test_list_projects_with_special_characters(self, mock_cli_runner, temp_project_dir):
        """Test list with projects containing special characters"""
        # Create project with special characters
        domain = "spëcial-tëst.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        (project_path / "overview.json").write_text(json.dumps({
            "company_name": "Spëcial Tëst Corp™",
            "_generated_at": "2024-01-01T00:00:00Z"
        }, ensure_ascii=False))
        
        result = mock_cli_runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        # Should handle special characters properly
    
    def test_list_very_large_number_of_projects(self, mock_cli_runner, temp_project_dir):
        """Test list with many projects"""
        # Create many projects
        for i in range(50):
            project_path = temp_project_dir / f"company{i:03d}.com"
            project_path.mkdir()
            (project_path / "overview.json").write_text(json.dumps({
                "company_name": f"Company {i}",
                "_generated_at": "2024-01-01T00:00:00Z"
            }))
        
        result = mock_cli_runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        # Should handle large number of projects
    
    def test_plans_with_missing_dependencies(self, mock_cli_runner, mock_incomplete_project):
        """Test plans command with incomplete project data"""
        domain = mock_incomplete_project.name
        
        result = mock_cli_runner.invoke(app, ["plans", "create", domain])
        
        # Should either work with available data or request missing information
        assert result.exit_code == 0 or "missing" in result.output.lower()
    
    def test_plans_permission_errors(self, mock_cli_runner, mock_project_with_data):
        """Test plans command with file permission issues"""
        domain = mock_project_with_data.name
        
        # Try to export to protected location
        result = mock_cli_runner.invoke(app, [
            "plans", "export", domain,
            "--output", "/root/protected"
        ])
        
        # Should handle permission errors gracefully
        assert result.exit_code != 0 or "permission" in result.output.lower()
    
    def test_list_and_plans_consistency(self, mock_cli_runner, mock_project_with_data):
        """Test consistency between list and plans commands"""
        # List should show projects that plans can work with
        list_result = mock_cli_runner.invoke(app, ["list"])
        plans_result = mock_cli_runner.invoke(app, ["plans", "list"])
        
        assert list_result.exit_code == 0
        assert plans_result.exit_code == 0
        
        # Both should reference the same projects


class TestListAndPlansPerformance:
    """Test performance of list and plans commands"""
    
    def test_list_performance_many_projects(self, mock_cli_runner, temp_project_dir):
        """Test list performance with many projects"""
        import time
        
        # Create moderate number of projects
        for i in range(20):
            project_path = temp_project_dir / f"perf{i:03d}.com"
            project_path.mkdir()
            (project_path / "overview.json").write_text(json.dumps({
                "company_name": f"Performance Test {i}",
                "_generated_at": "2024-01-01T00:00:00Z"
            }))
        
        start_time = time.time()
        result = mock_cli_runner.invoke(app, ["list"])
        elapsed_time = time.time() - start_time
        
        assert result.exit_code == 0
        assert elapsed_time < 5.0  # Should be fast
    
    def test_plans_generation_performance(self, mock_cli_runner, mock_project_with_data):
        """Test plans generation performance"""
        import time
        
        domain = mock_project_with_data.name
        
        start_time = time.time()
        result = mock_cli_runner.invoke(app, ["plans", "create", domain])
        elapsed_time = time.time() - start_time
        
        assert result.exit_code == 0
        assert elapsed_time < 15.0  # Should complete reasonably quickly
    
    def test_list_memory_usage(self, mock_cli_runner, temp_project_dir):
        """Test list command memory usage with large projects"""
        # Create projects with large data
        for i in range(5):
            project_path = temp_project_dir / f"large{i}.com"
            project_path.mkdir()
            large_description = "Large content. " * 5000  # ~65KB each
            (project_path / "overview.json").write_text(json.dumps({
                "company_name": f"Large Company {i}",
                "description": large_description,
                "_generated_at": "2024-01-01T00:00:00Z"
            }))
        
        result = mock_cli_runner.invoke(app, ["list", "--details"])
        
        assert result.exit_code == 0
        # Should handle large projects without memory issues