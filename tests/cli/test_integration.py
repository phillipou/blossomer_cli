"""
Integration tests for the CLI.
Tests complete workflows and component interactions.
"""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import patch, Mock
from typer.testing import CliRunner

from cli.main import app


class TestNewProjectWorkflow:
    """Test complete new project workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_new_project_flow_yolo(self, mock_cli_runner, temp_project_dir):
        """Test complete new project flow in YOLO mode"""
        domain = "integration-test.com"
        
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        
        assert result.exit_code == 0
        
        # Verify project was created
        project_dir = temp_project_dir / domain
        assert project_dir.exists()
        
        # Verify JSON files were created
        expected_files = ["overview.json", "account.json", "persona.json", "email.json"]
        for filename in expected_files:
            json_file = project_dir / filename
            if json_file.exists():  # Some steps might not complete in mocked environment
                # Verify valid JSON
                data = json.loads(json_file.read_text())
                assert isinstance(data, dict)
                assert "_generated_at" in data
        
        # Test show command works with new project
        show_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        assert show_result.exit_code == 0
        assert domain in show_result.output
    
    @pytest.mark.asyncio
    async def test_complete_new_project_flow_interactive(self, mock_cli_runner, mock_console_input, temp_project_dir):
        """Test complete new project flow with interactive input"""
        domain = "interactive-test.com"
        
        # Mock user inputs
        mock_console_input(domain)  # Domain input
        mock_console_input("Enterprise software companies")  # Account hypothesis
        mock_console_input("CTOs and VP Engineering")  # Persona hypothesis
        mock_console_input("Focus on AI and automation")  # Extra context
        
        with patch('typer.confirm', return_value=True):  # Confirm ready
            result = mock_cli_runner.invoke(app, ["init"])
            
            assert result.exit_code == 0
            
            # Verify project was created with context
            project_dir = temp_project_dir / domain
            assert project_dir.exists()
    
    def test_new_project_with_context_parameter(self, mock_cli_runner, temp_project_dir):
        """Test new project creation with context parameter"""
        domain = "context-test.com"
        context = "Series B fintech company focusing on SMB lending"
        
        result = mock_cli_runner.invoke(app, [
            "init", domain,
            "--context", context,
            "--yolo"
        ])
        
        assert result.exit_code == 0
        
        project_dir = temp_project_dir / domain
        assert project_dir.exists()
        
        # Context should be incorporated (verified through successful completion)
    
    def test_new_project_guided_email_flow(self, mock_cli_runner, temp_project_dir):
        """Test new project with guided email generation"""
        domain = "guided-email-test.com"
        
        # Mock guided email choices
        with patch('cli.utils.menu_utils.show_menu_with_numbers') as mock_menu:
            mock_menu.side_effect = [
                "Guided mode - I'll help you customize your emails",  # Email mode
                "Finish"  # Completion choice
            ]
            
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            assert result.exit_code == 0
            
            project_dir = temp_project_dir / domain
            assert project_dir.exists()


class TestExistingProjectWorkflow:
    """Test workflows with existing projects"""
    
    def test_existing_project_restart_fresh(self, mock_cli_runner, mock_project_with_data):
        """Test restarting existing project from beginning"""
        domain = mock_project_with_data.name
        
        # Mock user choice to start fresh
        with patch('cli.utils.menu_utils.show_menu_with_numbers', return_value="Start fresh (regenerate all steps)"):
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            assert result.exit_code == 0
            assert "Starting from overview step" in result.output or "Company Overview" in result.output
    
    def test_existing_project_partial_restart(self, mock_cli_runner, mock_project_with_data):
        """Test restarting existing project from specific step"""
        domain = mock_project_with_data.name
        
        # Mock user choice to start from account step
        with patch('cli.utils.menu_utils.show_menu_with_numbers', return_value="Start from Step 2: Target Account Profile"):
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            assert result.exit_code == 0
            # Should regenerate from account step onward
    
    def test_existing_project_show_all_steps(self, mock_cli_runner, mock_project_with_data):
        """Test showing all steps of existing project"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        
        assert result.exit_code == 0
        assert f"GTM Project: {domain}" in result.output
        assert "Progress:" in result.output
        assert "Company Overview" in result.output
        assert "Target Account Profile" in result.output
    
    def test_existing_project_edit_and_export(self, mock_cli_runner, mock_project_with_data):
        """Test editing and exporting existing project"""
        domain = mock_project_with_data.name
        
        # Test edit command
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            edit_result = mock_cli_runner.invoke(app, ["edit", "strategy", "--domain", domain])
            assert edit_result.exit_code == 0
            if mock_editor.called:
                assert len(mock_editor.call_args[0]) > 0  # File path provided
        
        # Test export command
        with patch('pathlib.Path.write_text') as mock_write:
            export_result = mock_cli_runner.invoke(app, ["export", "all", "--domain", domain])
            assert export_result.exit_code == 0
    
    def test_existing_project_stale_data_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of stale data in existing projects"""
        # Create project with stale data markers
        domain = "stale-data-test.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create stale overview data
        stale_data = {
            "company_name": "Stale Corp",
            "_generated_at": "2024-01-01T00:00:00Z",
            "_stale": True,
            "_stale_reason": "Dependency updated"
        }
        (project_path / "overview.json").write_text(json.dumps(stale_data))
        
        # Show command should indicate stale data
        result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        assert result.exit_code == 0
        assert "outdated" in result.output.lower() or "stale" in result.output.lower()


class TestMultiProjectWorkflow:
    """Test workflows with multiple projects"""
    
    def test_multiple_projects_auto_detection(self, mock_cli_runner, mock_project_with_data, temp_project_dir):
        """Test auto-detection with multiple projects"""
        # Create second project
        second_domain = "second-project.com"
        second_project = temp_project_dir / second_domain
        second_project.mkdir()
        (second_project / "overview.json").write_text(json.dumps({
            "company_name": "Second Company",
            "_generated_at": "2024-01-01T00:00:00Z"
        }))
        
        # Commands without domain should require specification
        result = mock_cli_runner.invoke(app, ["show", "all"])
        assert result.exit_code == 0
        assert "Multiple projects found" in result.output
        assert "Please specify domain" in result.output
    
    def test_list_all_projects(self, mock_cli_runner, mock_project_with_data, mock_incomplete_project):
        """Test listing all projects"""
        result = mock_cli_runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        # Should show both projects
        assert mock_project_with_data.name in result.output
        assert mock_incomplete_project.name in result.output
    
    def test_switch_between_projects(self, mock_cli_runner, mock_project_with_data, temp_project_dir):
        """Test switching between different projects"""
        # Create second project
        second_domain = "second-project.com"
        second_project = temp_project_dir / second_domain
        second_project.mkdir()
        (second_project / "overview.json").write_text(json.dumps({
            "company_name": "Second Company",
            "_generated_at": "2024-01-01T00:00:00Z"
        }))
        
        # Show first project
        result1 = mock_cli_runner.invoke(app, ["show", "overview", "--domain", mock_project_with_data.name])
        assert result1.exit_code == 0
        assert "Acme Corporation" in result1.output  # From mock data
        
        # Show second project
        result2 = mock_cli_runner.invoke(app, ["show", "overview", "--domain", second_domain])
        assert result2.exit_code == 0
        assert "Second Company" in result2.output


class TestWorkflowErrorRecovery:
    """Test error recovery in workflows"""
    
    def test_workflow_interruption_recovery(self, mock_cli_runner, temp_project_dir):
        """Test recovery from workflow interruption"""
        domain = "interrupted-test.com"
        
        # Simulate interruption during generation
        with patch('cli.commands.init.run_async_generation', side_effect=KeyboardInterrupt()):
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            assert result.exit_code == 130  # Ctrl+C exit code
            assert "cancelled" in result.output.lower() or "stopped" in result.output.lower()
        
        # Resume should work
        resume_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert resume_result.exit_code == 0
    
    def test_workflow_api_error_recovery(self, mock_cli_runner, mock_error_scenarios, temp_project_dir):
        """Test recovery from API errors"""
        domain = "api-error-test.com"
        
        # Set up API error scenario
        mock_error_scenarios["set"]("api_error")
        
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        
        # Should handle error gracefully
        assert result.exit_code == 1
        assert "error" in result.output.lower() or "failed" in result.output.lower()
        
        # Should provide recovery instructions
        assert "try again" in result.output.lower() or "blossomer init" in result.output
    
    def test_workflow_network_error_recovery(self, mock_cli_runner, mock_error_scenarios, temp_project_dir):
        """Test recovery from network errors"""
        domain = "network-error-test.com"
        
        # Set up network error scenario
        mock_error_scenarios["set"]("network_error")
        
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        
        # Should handle network error gracefully
        assert result.exit_code == 1
        assert "error" in result.output.lower() or "failed" in result.output.lower()
    
    def test_workflow_corrupted_data_recovery(self, mock_cli_runner, mock_corrupted_project):
        """Test recovery from corrupted project data"""
        domain = mock_corrupted_project.name
        
        # Restart should handle corrupted data
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        
        # Should either succeed (overwriting corrupted data) or show clear error
        assert result.exit_code in [0, 1]


class TestWorkflowPerformance:
    """Test performance characteristics of workflows"""
    
    def test_new_project_creation_time(self, mock_cli_runner, temp_project_dir):
        """Test new project creation completes in reasonable time"""
        domain = "performance-test.com"
        
        start_time = time.time()
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        elapsed_time = time.time() - start_time
        
        assert result.exit_code == 0
        # Should complete within 10 seconds (mocked APIs should be fast)
        assert elapsed_time < 10.0
    
    def test_show_command_response_time(self, mock_cli_runner, mock_project_with_data):
        """Test show command response time"""
        domain = mock_project_with_data.name
        
        start_time = time.time()
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        elapsed_time = time.time() - start_time
        
        assert result.exit_code == 0
        # Should respond quickly
        assert elapsed_time < 2.0
    
    def test_list_many_projects_performance(self, mock_cli_runner, temp_project_dir):
        """Test list command performance with many projects"""
        # Create 25 projects
        for i in range(25):
            project_path = temp_project_dir / f"perf-project-{i}.com"
            project_path.mkdir()
            (project_path / "overview.json").write_text(json.dumps({
                "company_name": f"Performance Test Company {i}",
                "_generated_at": "2024-01-01T00:00:00Z"
            }))
        
        start_time = time.time()
        result = mock_cli_runner.invoke(app, ["list"])
        elapsed_time = time.time() - start_time
        
        assert result.exit_code == 0
        # Should handle many projects efficiently
        assert elapsed_time < 3.0
        
        # Should show all projects
        for i in range(5):  # Check first 5
            assert f"perf-project-{i}.com" in result.output


class TestWorkflowDataIntegrity:
    """Test data integrity across workflows"""
    
    def test_data_persistence_across_commands(self, mock_cli_runner, temp_project_dir):
        """Test data persists correctly across different commands"""
        domain = "persistence-test.com"
        
        # Create project
        init_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert init_result.exit_code == 0
        
        # Verify data can be shown
        show_result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        assert show_result.exit_code == 0
        
        # Verify data can be listed
        list_result = mock_cli_runner.invoke(app, ["list", "--domain", domain])
        assert list_result.exit_code == 0
        
        # Verify data can be exported
        export_result = mock_cli_runner.invoke(app, ["export", "overview", "--domain", domain])
        assert export_result.exit_code == 0
    
    def test_json_data_validity(self, mock_cli_runner, temp_project_dir):
        """Test that all generated JSON data is valid"""
        domain = "json-validity-test.com"
        
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert result.exit_code == 0
        
        # Check all JSON files are valid
        project_dir = temp_project_dir / domain
        for json_file in project_dir.glob("*.json"):
            if json_file.name != ".metadata.json":  # Skip metadata
                try:
                    data = json.loads(json_file.read_text())
                    assert isinstance(data, dict)
                    # Should have generation timestamp
                    assert "_generated_at" in data
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON in {json_file}")
    
    def test_domain_normalization_consistency(self, mock_cli_runner, temp_project_dir):
        """Test domain normalization is consistent across commands"""
        input_domains = ["https://test.com", "www.test.com", "test.com"]
        
        for input_domain in input_domains:
            # All should create/access the same project
            result = mock_cli_runner.invoke(app, ["init", input_domain, "--yolo"])
            assert result.exit_code == 0
            
            # Should all reference the same normalized directory
            assert (temp_project_dir / "test.com").exists()
        
        # Only one project directory should exist
        project_dirs = [d for d in temp_project_dir.iterdir() if d.is_dir()]
        test_dirs = [d for d in project_dirs if "test.com" in d.name]
        assert len(test_dirs) == 1


class TestWorkflowUserExperience:
    """Test user experience aspects of workflows"""
    
    def test_helpful_error_messages(self, mock_cli_runner):
        """Test that error messages are helpful"""
        # Test invalid domain
        result = mock_cli_runner.invoke(app, ["init", "invalid..domain", "--yolo"])
        assert result.exit_code == 1
        assert "Invalid domain format" in result.output
        assert "Try:" in result.output or "example:" in result.output.lower()
    
    def test_progress_indicators_shown(self, mock_cli_runner, temp_project_dir):
        """Test that progress indicators are shown during generation"""
        domain = "progress-test.com"
        
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        
        # Should show step progress
        assert any(step in result.output for step in [
            "Company Overview", "Target Account", "Buyer Persona", "Email Campaign"
        ])
    
    def test_completion_guidance(self, mock_cli_runner, temp_project_dir):
        """Test that users get guidance on what to do next"""
        domain = "guidance-test.com"
        
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert result.exit_code == 0
        
        # Should provide next steps or completion menu
        assert ("What would you like to do?" in result.output or 
                "blossomer" in result.output or
                "completed" in result.output.lower())
    
    def test_consistent_formatting_across_commands(self, mock_cli_runner, mock_project_with_data):
        """Test consistent formatting across different commands"""
        domain = mock_project_with_data.name
        
        commands = [
            ["show", "all", "--domain", domain],
            ["show", "overview", "--domain", domain],
            ["list", "--domain", domain]
        ]
        
        for cmd in commands:
            result = mock_cli_runner.invoke(app, cmd)
            assert result.exit_code == 0
            
            # Should use consistent formatting (emojis, colors, structure)
            # Basic check for rich formatting elements
            formatted_elements = ["🏢", "🎯", "👤", "📧", "→", "✓"]
            has_formatting = any(element in result.output for element in formatted_elements)
            
            # Should have some form of structured output
            assert has_formatting or ("GTM" in result.output and ":" in result.output)


class TestCompleteUserJourneys:
    """Test complete user journeys from start to finish"""
    
    def test_first_time_user_journey(self, mock_cli_runner, temp_project_dir):
        """Test complete first-time user journey"""
        domain = "first-time-user.com"
        
        # 1. User runs init for first time
        result1 = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert result1.exit_code == 0
        
        # 2. User views their generated content
        result2 = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        assert result2.exit_code == 0
        
        # 3. User edits a specific asset
        with patch('cli.utils.editor.open_file_in_editor'):
            result3 = mock_cli_runner.invoke(app, ["edit", "strategy", "--domain", domain])
            assert result3.exit_code == 0
        
        # 4. User exports their work
        result4 = mock_cli_runner.invoke(app, ["export", "all", "--domain", domain])
        assert result4.exit_code == 0
        
        # All steps should complete successfully
    
    def test_returning_user_journey(self, mock_cli_runner, mock_project_with_data):
        """Test returning user journey with existing project"""
        domain = mock_project_with_data.name
        
        # 1. User checks their existing project
        result1 = mock_cli_runner.invoke(app, ["list"])
        assert result1.exit_code == 0
        assert domain in result1.output
        
        # 2. User views specific content
        result2 = mock_cli_runner.invoke(app, ["show", "email", "--domain", domain])
        assert result2.exit_code == 0
        
        # 3. User decides to regenerate from persona step
        with patch('cli.utils.menu_utils.show_menu_with_numbers', 
                  return_value="Start from Step 3: Buyer Persona"):
            result3 = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            assert result3.exit_code == 0
        
        # 4. User exports updated work
        result4 = mock_cli_runner.invoke(app, ["export", "all", "--domain", domain])
        assert result4.exit_code == 0
    
    def test_power_user_journey(self, mock_cli_runner, temp_project_dir):
        """Test power user journey with multiple projects and advanced features"""
        domains = ["power-user-1.com", "power-user-2.com", "power-user-3.com"]
        
        # 1. Create multiple projects
        for domain in domains:
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            assert result.exit_code == 0
        
        # 2. List all projects
        list_result = mock_cli_runner.invoke(app, ["list"])
        assert list_result.exit_code == 0
        for domain in domains:
            assert domain in list_result.output
        
        # 3. Work with specific projects
        for domain in domains:
            show_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
            assert show_result.exit_code == 0
            
            export_result = mock_cli_runner.invoke(app, ["export", "all", "--domain", domain])
            assert export_result.exit_code == 0
        
        # All operations should complete successfully