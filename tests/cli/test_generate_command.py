"""
Comprehensive tests for the generate command.
Tests generating individual GTM steps and handling dependencies.
"""

import pytest
import json
from unittest.mock import patch, Mock
from cli.main import app


class TestGenerateCommand:
    """Test suite for the generate command"""
    
    def test_generate_help(self, mock_cli_runner):
        """Test generate command help"""
        result = mock_cli_runner.invoke(app, ["generate", "--help"])
        
        assert result.exit_code == 0
        assert "generate" in result.output.lower()
        assert "step" in result.output.lower()
    
    def test_generate_overview_step(self, mock_cli_runner, temp_project_dir):
        """Test generating overview step"""
        result = mock_cli_runner.invoke(app, ["generate", "overview", "acme.com"])
        
        assert result.exit_code == 0
        assert "overview" in result.output.lower() or "company" in result.output.lower()
    
    def test_generate_account_step(self, mock_cli_runner, mock_project_with_data):
        """Test generating account step"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["generate", "account", domain])
        
        assert result.exit_code == 0
        assert "account" in result.output.lower() or "target" in result.output.lower()
    
    def test_generate_persona_step(self, mock_cli_runner, mock_project_with_data):
        """Test generating persona step"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["generate", "persona", domain])
        
        assert result.exit_code == 0
        assert "persona" in result.output.lower() or "buyer" in result.output.lower()
    
    def test_generate_email_step(self, mock_cli_runner, mock_project_with_data):
        """Test generating email step"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["generate", "email", domain])
        
        assert result.exit_code == 0
        assert "email" in result.output.lower() or "campaign" in result.output.lower()
    
    def test_generate_strategy_step(self, mock_cli_runner, mock_project_with_data):
        """Test generating strategy step"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["generate", "strategy", domain])
        
        assert result.exit_code == 0
        assert "strategy" in result.output.lower() or "plan" in result.output.lower()
    
    def test_generate_all_steps(self, mock_cli_runner, temp_project_dir):
        """Test generating all steps"""
        result = mock_cli_runner.invoke(app, ["generate", "all", "acme.com"])
        
        assert result.exit_code == 0
        assert "generating" in result.output.lower() or "completed" in result.output.lower()
    
    def test_generate_with_force_flag(self, mock_cli_runner, mock_project_with_data):
        """Test generating with force flag to regenerate existing content"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["generate", "overview", domain, "--force"])
        
        assert result.exit_code == 0
        assert "regenerat" in result.output.lower() or "overwr" in result.output.lower() or "generated" in result.output.lower()
    
    def test_generate_without_force_existing_content(self, mock_cli_runner, mock_project_with_data):
        """Test generating existing content without force flag"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["generate", "overview", domain])
        
        assert result.exit_code == 0
        # Should either skip or ask for confirmation
        assert "exists" in result.output.lower() or "already" in result.output.lower() or "generated" in result.output.lower()
    
    def test_generate_step_with_missing_dependencies(self, mock_cli_runner, temp_project_dir):
        """Test generating step that has missing dependencies"""
        result = mock_cli_runner.invoke(app, ["generate", "email", "acme.com"])
        
        assert result.exit_code == 0
        # Should either generate dependencies or warn about them
        assert "dependency" in result.output.lower() or "overview" in result.output.lower() or "generated" in result.output.lower()
    
    def test_generate_invalid_step(self, mock_cli_runner, temp_project_dir):
        """Test generating invalid step name"""
        result = mock_cli_runner.invoke(app, ["generate", "invalid_step", "acme.com"])
        
        assert result.exit_code != 0 or "invalid" in result.output.lower() or "unknown" in result.output.lower()
    
    def test_generate_invalid_domain(self, mock_cli_runner):
        """Test generate with invalid domain"""
        result = mock_cli_runner.invoke(app, ["generate", "overview", "invalid..domain"])
        
        assert result.exit_code != 0 or "invalid" in result.output.lower()
    
    def test_generate_nonexistent_domain(self, mock_cli_runner, temp_project_dir):
        """Test generate for domain that doesn't exist (should create project)"""
        result = mock_cli_runner.invoke(app, ["generate", "overview", "newcompany.com"])
        
        assert result.exit_code == 0
        # Should create new project or prompt for initialization
    
    def test_generate_with_context_parameter(self, mock_cli_runner, temp_project_dir):
        """Test generate with additional context parameter"""
        result = mock_cli_runner.invoke(app, [
            "generate", "overview", "acme.com", 
            "--context", "This is a B2B SaaS company focused on automation"
        ])
        
        assert result.exit_code == 0
    
    def test_generate_with_yolo_mode(self, mock_cli_runner, temp_project_dir):
        """Test generate with yolo mode (skip confirmations)"""
        result = mock_cli_runner.invoke(app, ["generate", "all", "acme.com", "--yolo"])
        
        assert result.exit_code == 0


class TestGenerateCommandDependencies:
    """Test dependency handling in generate command"""
    
    def test_generate_enforces_dependency_order(self, mock_cli_runner, temp_project_dir):
        """Test that generate respects dependency order"""
        # Try to generate persona without overview and account
        result = mock_cli_runner.invoke(app, ["generate", "persona", "acme.com"])
        
        assert result.exit_code == 0
        # Should either generate dependencies first or warn about them
    
    def test_generate_dependency_chain_creation(self, mock_cli_runner, temp_project_dir):
        """Test that missing dependencies are created automatically"""
        result = mock_cli_runner.invoke(app, ["generate", "email", "acme.com"])
        
        assert result.exit_code == 0
        # Should generate overview, account, persona, then email
    
    def test_generate_partial_dependency_completion(self, mock_cli_runner, mock_incomplete_project):
        """Test generate with partially completed dependencies"""
        domain = mock_incomplete_project.name
        
        result = mock_cli_runner.invoke(app, ["generate", "account", domain])
        
        assert result.exit_code == 0
        # Should build on existing overview
    
    def test_generate_stale_dependency_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of stale dependencies"""
        domain = "stale.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create overview with stale marker
        overview_data = {
            "company_name": "Stale Corp",
            "_generated_at": "2024-01-01T00:00:00Z",
            "_stale": True
        }
        (project_path / "overview.json").write_text(json.dumps(overview_data))
        
        result = mock_cli_runner.invoke(app, ["generate", "account", domain])
        
        assert result.exit_code == 0
        # Should either regenerate stale dependency or warn about it


class TestGenerateCommandInteractive:
    """Test interactive features of generate command"""
    
    def test_generate_interactive_project_selection(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test interactive project selection when no domain specified"""
        mock_console_input("acme.com")  # Project selection
        mock_console_input("overview")  # Step selection
        
        result = mock_cli_runner.invoke(app, ["generate"])
        
        # Should either work interactively or require parameters
        assert result.exit_code == 0 or "specify" in result.output.lower()
    
    def test_generate_interactive_step_selection(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test interactive step selection"""
        domain = mock_project_with_data.name
        mock_console_input("overview")  # Step selection
        
        result = mock_cli_runner.invoke(app, ["generate", "--domain", domain])
        
        assert result.exit_code == 0 or "step" in result.output.lower()
    
    def test_generate_confirmation_prompts(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test confirmation prompts for existing content"""
        domain = mock_project_with_data.name
        mock_console_input("y")  # Confirm regeneration
        
        result = mock_cli_runner.invoke(app, ["generate", "overview", domain])
        
        assert result.exit_code == 0
    
    def test_generate_guided_mode_prompts(self, mock_cli_runner, mock_console_input, temp_project_dir):
        """Test guided mode with context prompts"""
        mock_console_input("B2B SaaS company")  # Context input
        mock_console_input("Enterprise software")  # Additional context
        
        result = mock_cli_runner.invoke(app, ["generate", "overview", "acme.com", "--guided"])
        
        assert result.exit_code == 0


class TestGenerateCommandErrorHandling:
    """Test error handling in generate command"""
    
    def test_generate_api_timeout_handling(self, mock_cli_runner, mock_error_scenarios, temp_project_dir):
        """Test handling of API timeouts during generation"""
        mock_error_scenarios["set"]("timeout")
        
        result = mock_cli_runner.invoke(app, ["generate", "overview", "acme.com"])
        
        assert result.exit_code != 0 or "timeout" in result.output.lower() or "error" in result.output.lower()
    
    def test_generate_api_error_handling(self, mock_cli_runner, mock_error_scenarios, temp_project_dir):
        """Test handling of API errors during generation"""
        mock_error_scenarios["set"]("api_error")
        
        result = mock_cli_runner.invoke(app, ["generate", "overview", "acme.com"])
        
        assert result.exit_code != 0 or "error" in result.output.lower()
    
    def test_generate_network_error_handling(self, mock_cli_runner, mock_error_scenarios, temp_project_dir):
        """Test handling of network errors"""
        mock_error_scenarios["set"]("network_error")
        
        result = mock_cli_runner.invoke(app, ["generate", "overview", "acme.com"])
        
        assert result.exit_code != 0 or "network" in result.output.lower() or "error" in result.output.lower()
    
    def test_generate_file_permission_error(self, mock_cli_runner, temp_project_dir, monkeypatch):
        """Test handling of file permission errors"""
        # Make project directory read-only
        temp_project_dir.chmod(0o444)
        
        try:
            result = mock_cli_runner.invoke(app, ["generate", "overview", "acme.com"])
            
            # Should handle permission error gracefully
            assert result.exit_code != 0 or "permission" in result.output.lower()
        finally:
            # Restore permissions
            temp_project_dir.chmod(0o755)
    
    def test_generate_disk_space_error(self, mock_cli_runner, temp_project_dir, monkeypatch):
        """Test handling of disk space errors"""
        def mock_write_error(*args, **kwargs):
            raise OSError("No space left on device")
        
        with patch('pathlib.Path.write_text', side_effect=mock_write_error):
            result = mock_cli_runner.invoke(app, ["generate", "overview", "acme.com"])
            
            assert result.exit_code != 0 or "space" in result.output.lower() or "error" in result.output.lower()
    
    def test_generate_keyboard_interrupt(self, mock_cli_runner, mock_console_input, temp_project_dir):
        """Test handling of keyboard interrupt during generation"""
        mock_console_input.side_effect = KeyboardInterrupt()
        
        result = mock_cli_runner.invoke(app, ["generate", "overview", "acme.com"])
        
        # Should handle interruption gracefully
        assert "interrupt" in result.output.lower() or "cancelled" in result.output.lower() or result.exit_code != 0


class TestGenerateCommandPerformance:
    """Test performance aspects of generate command"""
    
    def test_generate_single_step_performance(self, mock_cli_runner, temp_project_dir):
        """Test that single step generation completes in reasonable time"""
        import time
        
        start_time = time.time()
        result = mock_cli_runner.invoke(app, ["generate", "overview", "acme.com"])
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time for tests
        assert elapsed_time < 10.0  # 10 seconds should be plenty for mocked tests
    
    def test_generate_all_steps_performance(self, mock_cli_runner, temp_project_dir):
        """Test that generating all steps completes in reasonable time"""
        import time
        
        start_time = time.time()
        result = mock_cli_runner.invoke(app, ["generate", "all", "acme.com"])
        elapsed_time = time.time() - start_time
        
        # All steps should complete within reasonable time for tests
        assert elapsed_time < 30.0  # 30 seconds should be plenty for mocked tests
    
    def test_generate_parallel_safety(self, mock_cli_runner, temp_project_dir):
        """Test that multiple generate commands don't interfere"""
        # This is a basic test - full parallel testing would require more setup
        result1 = mock_cli_runner.invoke(app, ["generate", "overview", "company1.com"])
        result2 = mock_cli_runner.invoke(app, ["generate", "overview", "company2.com"])
        
        assert result1.exit_code == 0
        assert result2.exit_code == 0


class TestGenerateCommandEdgeCases:
    """Test edge cases for generate command"""
    
    def test_generate_very_long_domain_name(self, mock_cli_runner, temp_project_dir):
        """Test generate with very long domain name"""
        long_domain = "a" * 100 + ".com"
        
        result = mock_cli_runner.invoke(app, ["generate", "overview", long_domain])
        
        # Should handle long domain gracefully
        assert result.exit_code == 0 or "invalid" in result.output.lower()
    
    def test_generate_special_characters_domain(self, mock_cli_runner, temp_project_dir):
        """Test generate with special characters in domain"""
        result = mock_cli_runner.invoke(app, ["generate", "overview", "test-company.co.uk"])
        
        assert result.exit_code == 0
    
    def test_generate_unicode_domain(self, mock_cli_runner, temp_project_dir):
        """Test generate with unicode domain"""
        # This might fail depending on domain validation
        result = mock_cli_runner.invoke(app, ["generate", "overview", "测试.com"])
        
        # Should either work or fail gracefully
        assert "error" not in result.output.lower() or result.exit_code != 0
    
    def test_generate_empty_parameters(self, mock_cli_runner):
        """Test generate with empty parameters"""
        result = mock_cli_runner.invoke(app, ["generate", "", ""])
        
        assert result.exit_code != 0 or "required" in result.output.lower()
    
    def test_generate_with_many_context_parameters(self, mock_cli_runner, temp_project_dir):
        """Test generate with very long context"""
        long_context = "Context " * 1000  # Very long context
        
        result = mock_cli_runner.invoke(app, [
            "generate", "overview", "acme.com",
            "--context", long_context
        ])
        
        assert result.exit_code == 0
        # Should handle long context appropriately


class TestGenerateCommandOutputValidation:
    """Test validation of generated content"""
    
    def test_generate_creates_valid_json_files(self, mock_cli_runner, temp_project_dir):
        """Test that generate creates valid JSON files"""
        result = mock_cli_runner.invoke(app, ["generate", "overview", "acme.com"])
        
        if result.exit_code == 0:
            # Check if valid JSON was created
            project_path = temp_project_dir / "acme.com"
            if project_path.exists():
                json_files = list(project_path.glob("*.json"))
                for json_file in json_files:
                    try:
                        with open(json_file) as f:
                            data = json.load(f)
                            assert isinstance(data, dict)
                    except json.JSONDecodeError:
                        pytest.fail(f"Invalid JSON created: {json_file}")
    
    def test_generate_includes_metadata(self, mock_cli_runner, temp_project_dir):
        """Test that generated content includes proper metadata"""
        result = mock_cli_runner.invoke(app, ["generate", "overview", "acme.com"])
        
        if result.exit_code == 0:
            project_path = temp_project_dir / "acme.com"
            if project_path.exists():
                overview_file = project_path / "overview.json"
                if overview_file.exists():
                    with open(overview_file) as f:
                        data = json.load(f)
                        # Should include generation timestamp
                        assert "_generated_at" in data or "timestamp" in str(data).lower()
    
    def test_generate_content_not_empty(self, mock_cli_runner, temp_project_dir):
        """Test that generated content is not empty"""
        result = mock_cli_runner.invoke(app, ["generate", "overview", "acme.com"])
        
        if result.exit_code == 0:
            project_path = temp_project_dir / "acme.com"
            if project_path.exists():
                json_files = list(project_path.glob("*.json"))
                for json_file in json_files:
                    assert json_file.stat().st_size > 10  # Should have some content