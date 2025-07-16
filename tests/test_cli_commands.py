#!/usr/bin/env python3
"""
CLI command tests using Typer's testing framework.
Tests all major commands: init, show, export, generate, edit, list
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pytest
from typer.testing import CliRunner

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.main import app
from cli.services.project_storage import project_storage


class TestCLICommands:
    """Test suite for all CLI commands"""
    
    @pytest.fixture
    def runner(self):
        """Provide a CLI test runner"""
        return CliRunner()
    
    @pytest.fixture
    def test_domain(self):
        """Provide a test domain and clean up after tests"""
        domain = "cli-test.com"
        yield domain
        # Cleanup
        if project_storage.project_exists(domain):
            project_storage.delete_project(domain)
    
    @pytest.fixture
    def sample_project_data(self):
        """Sample data for testing"""
        return {
            "overview": {
                "company_name": "CLI Test Corp",
                "description": "Test company for CLI testing",
                "cli_summary": {
                    "title": "CLI Test Corp",
                    "key_points": ["B2B SaaS", "Testing platform", "Automation focus"],
                    "metrics": {"category": "B2B SaaS"}
                }
            },
            "account": {
                "target_name": "Test Target Market",
                "cli_summary": {
                    "title": "Test Target Market",
                    "key_points": ["Mid-market", "Tech companies", "North America"],
                    "metrics": {"size": "100-500"}
                }
            },
            "persona": {
                "title": "Test Persona",
                "cli_summary": {
                    "title": "Test Persona",
                    "key_points": ["Decision maker", "Technical background"],
                    "metrics": {"team_size": "10-20"}
                }
            },
            "email": {
                "subject": "test email subject",
                "body": "Test email body",
                "cli_summary": {
                    "title": "Test Email Campaign",
                    "key_points": ["Pain point focus", "Meeting CTA"],
                    "metrics": {"emphasis": "pain_point"}
                }
            },
            "plan": {
                "execution_plan": {"week_1": ["Test task 1", "Test task 2"]},
                "cli_summary": {
                    "title": "Test GTM Plan",
                    "key_points": ["4-week timeline", "Lead generation focus"],
                    "metrics": {"timeline": "30 days"}
                }
            }
        }

    def test_init_command_yolo_mode(self, runner, test_domain):
        """Test init command in YOLO mode (non-interactive)"""
        print(f"🚀 Testing init command YOLO mode for {test_domain}")
        
        with patch('cli.commands.init_sync.run_init_flow') as mock_init:
            mock_init.return_value = True
            
            result = runner.invoke(app, ["init", test_domain, "--yolo"])
            
            assert result.exit_code == 0, f"Command failed: {result.output}"
            mock_init.assert_called_once()
            print("  ✓ YOLO mode init completed successfully")

    def test_init_command_with_context(self, runner, test_domain):
        """Test init command with additional context"""
        print(f"📝 Testing init command with context for {test_domain}")
        
        with patch('cli.commands.init_sync.run_init_flow') as mock_init:
            mock_init.return_value = True
            
            context = "Series A startup building AI tools"
            result = runner.invoke(app, ["init", test_domain, "--context", context])
            
            assert result.exit_code == 0, f"Command failed: {result.output}"
            # Verify context was passed
            call_args = mock_init.call_args
            assert context in str(call_args), "Context should be passed to init flow"
            print("  ✓ Context parameter handled correctly")

    def test_init_existing_project(self, runner, test_domain, sample_project_data):
        """Test init command on existing project"""
        print(f"♻️ Testing init on existing project {test_domain}")
        
        # Create existing project
        project_storage.create_project(test_domain)
        project_storage.save_step_data(test_domain, "overview", sample_project_data["overview"])
        
        with patch('questionary.select') as mock_select:
            mock_select.return_value.ask.return_value = "View existing analysis"
            
            result = runner.invoke(app, ["init", test_domain])
            
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "already exists" in result.output.lower(), "Should detect existing project"
            print("  ✓ Existing project detection working")

    def test_show_command_all(self, runner, test_domain, sample_project_data):
        """Test show command for all assets"""
        print(f"👀 Testing show all command for {test_domain}")
        
        # Create project with data
        project_storage.create_project(test_domain)
        for step, data in sample_project_data.items():
            project_storage.save_step_data(test_domain, step, data)
        
        with patch('cli.commands.show.get_current_project_domain') as mock_domain:
            mock_domain.return_value = test_domain
            
            result = runner.invoke(app, ["show", "all"])
            
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "CLI Test Corp" in result.output, "Should show company name"
            assert "Test Target Market" in result.output, "Should show target market"
            print("  ✓ Show all assets working correctly")

    def test_show_command_specific_asset(self, runner, test_domain, sample_project_data):
        """Test show command for specific asset"""
        print(f"🎯 Testing show specific asset for {test_domain}")
        
        # Create project with data
        project_storage.create_project(test_domain)
        project_storage.save_step_data(test_domain, "overview", sample_project_data["overview"])
        
        with patch('cli.commands.show.get_current_project_domain') as mock_domain:
            mock_domain.return_value = test_domain
            
            result = runner.invoke(app, ["show", "overview"])
            
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "CLI Test Corp" in result.output, "Should show company overview"
            print("  ✓ Show specific asset working correctly")

    def test_show_command_json_output(self, runner, test_domain, sample_project_data):
        """Test show command with JSON output"""
        print(f"📊 Testing show JSON output for {test_domain}")
        
        # Create project with data
        project_storage.create_project(test_domain)
        project_storage.save_step_data(test_domain, "overview", sample_project_data["overview"])
        
        with patch('cli.commands.show.get_current_project_domain') as mock_domain:
            mock_domain.return_value = test_domain
            
            result = runner.invoke(app, ["show", "overview", "--json"])
            
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert '"company_name"' in result.output, "Should output raw JSON"
            print("  ✓ JSON output working correctly")

    def test_generate_command(self, runner, test_domain):
        """Test generate command for specific step"""
        print(f"⚡ Testing generate command for {test_domain}")
        
        with patch('cli.services.gtm_generation_service.gtm_service.generate_step') as mock_generate:
            mock_generate.return_value = {
                "success": True,
                "data": {"test": "generated data"},
                "file_path": Path(f"gtm_projects/{test_domain}/email.json")
            }
            
            result = runner.invoke(app, ["generate", "email", test_domain])
            
            assert result.exit_code == 0, f"Command failed: {result.output}"
            mock_generate.assert_called_once_with(test_domain, "email", guided_mode=False)
            print("  ✓ Generate command working correctly")

    def test_list_command_empty(self, runner):
        """Test list command with no projects"""
        print("📋 Testing list command with no projects")
        
        with patch('cli.services.project_storage.project_storage.list_projects') as mock_list:
            mock_list.return_value = []
            
            result = runner.invoke(app, ["list"])
            
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "no projects" in result.output.lower() or "0" in result.output, "Should indicate no projects"
            print("  ✓ Empty list handled correctly")

    def test_list_command_with_projects(self, runner, sample_project_data):
        """Test list command with existing projects"""
        print("📁 Testing list command with projects")
        
        mock_projects = [
            {
                "domain": "test1.com",
                "created": "2024-01-01T10:00:00",
                "modified": "2024-01-01T10:30:00",
                "available_steps": ["overview", "account"],
                "step_count": 2,
                "total_steps": 5
            },
            {
                "domain": "test2.com",
                "created": "2024-01-02T10:00:00",
                "modified": "2024-01-02T11:00:00",
                "available_steps": ["overview", "account", "persona", "email", "plan"],
                "step_count": 5,
                "total_steps": 5
            }
        ]
        
        with patch('cli.services.project_storage.project_storage.list_projects') as mock_list:
            mock_list.return_value = mock_projects
            
            result = runner.invoke(app, ["list"])
            
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "test1.com" in result.output, "Should show first project"
            assert "test2.com" in result.output, "Should show second project"
            assert "2/5" in result.output or "partial" in result.output.lower(), "Should show partial status"
            assert "5/5" in result.output or "complete" in result.output.lower(), "Should show complete status"
            print("  ✓ Project listing working correctly")

    def test_export_command(self, runner, test_domain, sample_project_data):
        """Test export command"""
        print(f"📄 Testing export command for {test_domain}")
        
        # Create project with data
        project_storage.create_project(test_domain)
        for step, data in sample_project_data.items():
            project_storage.save_step_data(test_domain, step, data)
        
        with patch('cli.commands.export.get_current_project_domain') as mock_domain, \
             patch('builtins.open', mock_open()) as mock_file:
            mock_domain.return_value = test_domain
            
            result = runner.invoke(app, ["export"])
            
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "exported" in result.output.lower() or "saved" in result.output.lower(), "Should indicate export success"
            mock_file.assert_called_once()  # Verify file was opened for writing
            print("  ✓ Export command working correctly")

    def test_command_error_handling(self, runner):
        """Test error handling for various command scenarios"""
        print("❌ Testing command error handling")
        
        # Test show command without project
        result = runner.invoke(app, ["show", "overview"])
        assert result.exit_code != 0 or "no project" in result.output.lower(), "Should handle missing project"
        
        # Test generate with invalid step
        result = runner.invoke(app, ["generate", "invalid_step", "test.com"])
        assert result.exit_code != 0 or "invalid" in result.output.lower(), "Should handle invalid step"
        
        # Test show with invalid asset
        with patch('cli.commands.show.get_current_project_domain') as mock_domain:
            mock_domain.return_value = "test.com"
            result = runner.invoke(app, ["show", "invalid_asset"])
            assert result.exit_code != 0 or "invalid" in result.output.lower(), "Should handle invalid asset"
        
        print("  ✓ Error handling working correctly")


if __name__ == "__main__":
    # Run with pytest for proper fixture handling
    pytest.main([__file__, "-v"])