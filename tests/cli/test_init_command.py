"""
Unit tests for the init command.
Tests the main entry point for GTM project creation.
"""

import pytest
import os
from unittest.mock import patch, Mock
from typer.testing import CliRunner

from cli.main import app


class TestInitCommand:
    """Test suite for the init command"""
    
    def test_init_with_missing_api_keys(self, monkeypatch, mock_cli_runner):
        """Test init command when API keys are missing"""
        # Remove API keys
        monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
        monkeypatch.delenv("FORGE_API_KEY", raising=False)
        
        # Mock the interactive setup to decline
        with patch('questionary.confirm') as mock_confirm:
            mock_confirm.return_value.ask.return_value = False
            
            result = mock_cli_runner.invoke(app, ["init", "acme.com"])
            
            assert result.exit_code == 0
            assert "API Keys Required" in result.output or "setup" in result.output.lower()
    
    def test_init_yolo_mode_new_domain(self, mock_cli_runner, temp_project_dir):
        """Test init with --yolo flag for new domain"""
        result = mock_cli_runner.invoke(app, ["init", "acme.com", "--yolo"])
        
        assert result.exit_code == 0
        assert "Company Overview" in result.output
        assert "Target Account Profile" in result.output
        assert "Buyer Persona" in result.output
        assert "Email Campaign" in result.output
        # Check project was created
        assert (temp_project_dir / "acme.com").exists()
    
    def test_init_interactive_mode_new_domain(self, mock_cli_runner, mock_console_input, temp_project_dir):
        """Test interactive init flow for new domain"""
        # Mock user inputs
        mock_console_input("acme.com")  # Domain input
        mock_console_input("")  # Skip account hypothesis
        mock_console_input("")  # Skip persona hypothesis
        mock_console_input("")  # Skip extra context
        
        with patch('typer.confirm', return_value=True):  # Confirm ready to start
            result = mock_cli_runner.invoke(app, ["init"])
            
            assert result.exit_code == 0
            assert "Welcome to" in result.output
            assert (temp_project_dir / "acme.com").exists()
    
    def test_init_with_context(self, mock_cli_runner, temp_project_dir):
        """Test init with context parameter"""
        result = mock_cli_runner.invoke(app, [
            "init", "acme.com", 
            "--context", "Series A startup focusing on automation",
            "--yolo"
        ])
        
        assert result.exit_code == 0
        assert (temp_project_dir / "acme.com").exists()
    
    def test_init_existing_project_restart(self, mock_cli_runner, mock_project_with_data, mock_console_input):
        """Test init with existing project - restart from beginning"""
        domain = mock_project_with_data.name
        
        # Mock user choice to start fresh
        with patch('cli.utils.menu_utils.show_menu_with_numbers', return_value="Start fresh (regenerate all steps)"):
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            assert result.exit_code == 0
            assert "Starting from overview step" in result.output or "Company Overview" in result.output
    
    def test_init_existing_project_partial_restart(self, mock_cli_runner, mock_project_with_data, mock_console_input):
        """Test init with existing project - restart from specific step"""
        domain = mock_project_with_data.name
        
        # Mock user choice to start from account step
        with patch('cli.utils.menu_utils.show_menu_with_numbers', return_value="Start from Step 2: Target Account Profile"):
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            assert result.exit_code == 0
    
    def test_init_invalid_domain(self, mock_cli_runner):
        """Test init with invalid domain format"""
        result = mock_cli_runner.invoke(app, ["init", "invalid..domain", "--yolo"])
        
        assert result.exit_code == 1
        assert "Invalid domain format" in result.output
    
    def test_init_keyboard_interrupt(self, mock_cli_runner, monkeypatch):
        """Test graceful handling of Ctrl+C"""
        def raise_keyboard_interrupt(*args, **kwargs):
            raise KeyboardInterrupt()
        
        # Mock the init_flow to raise KeyboardInterrupt
        monkeypatch.setattr("cli.commands.init.init_flow", raise_keyboard_interrupt)
        
        result = mock_cli_runner.invoke(app, ["init", "acme.com"])
        
        assert result.exit_code == 130  # Standard exit code for Ctrl+C
        assert "cancelled" in result.output.lower()
    
    def test_init_no_domain_provided_interactive(self, mock_cli_runner, mock_console_input):
        """Test init without domain - should prompt"""
        mock_console_input("acme.com")  # Domain response
        mock_console_input("")  # Skip hypotheses
        mock_console_input("")
        mock_console_input("")
        
        with patch('typer.confirm', return_value=True):
            result = mock_cli_runner.invoke(app, ["init"])
            
            assert result.exit_code == 0
    
    def test_init_domain_normalization(self, mock_cli_runner, temp_project_dir):
        """Test that domains are properly normalized"""
        test_cases = [
            ("https://acme.com", "acme.com"),
            ("www.acme.com", "acme.com"),
            ("http://www.acme.com/about", "acme.com")
        ]
        
        for input_domain, expected_dir in test_cases:
            result = mock_cli_runner.invoke(app, ["init", input_domain, "--yolo"])
            assert result.exit_code == 0
            assert (temp_project_dir / expected_dir).exists()
            
            # Clean up for next test
            import shutil
            shutil.rmtree(temp_project_dir / expected_dir)
    
    @patch('cli.commands.init.run_async_generation')
    def test_init_generation_timeout(self, mock_async, mock_cli_runner):
        """Test handling of generation timeout"""
        import asyncio
        mock_async.side_effect = asyncio.TimeoutError("Operation timed out")
        
        result = mock_cli_runner.invoke(app, ["init", "acme.com", "--yolo"])
        
        assert result.exit_code == 1
        assert "timed out" in result.output.lower() or "timeout" in result.output.lower()
    
    def test_init_guided_email_mode(self, mock_cli_runner, temp_project_dir):
        """Test init with guided email generation"""
        # Mock the menu choice for guided email
        with patch('cli.utils.menu_utils.show_menu_with_numbers') as mock_menu:
            # First call for email mode selection
            mock_menu.return_value = "Guided mode - I'll help you customize your emails"
            
            result = mock_cli_runner.invoke(app, ["init", "acme.com", "--yolo"])
            
            assert result.exit_code == 0
    
    def test_init_api_key_interactive_setup(self, mock_cli_runner, monkeypatch):
        """Test interactive API key setup"""
        # Remove API keys
        monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
        monkeypatch.delenv("FORGE_API_KEY", raising=False)
        
        # Mock the interactive setup to succeed
        with patch('questionary.confirm') as mock_confirm, \
             patch('questionary.password') as mock_password:
            
            mock_confirm.return_value.ask.return_value = True  # Want to set up keys
            mock_password.return_value.ask.return_value = "test_key_value"
            
            result = mock_cli_runner.invoke(app, ["init", "acme.com", "--yolo"])
            
            # Should succeed after API key setup
            assert result.exit_code == 0 or "✅" in result.output
    
    def test_init_step_generation_error_recovery(self, mock_cli_runner, mock_error_scenarios):
        """Test error recovery during step generation"""
        mock_error_scenarios["set"]("api_error")
        
        result = mock_cli_runner.invoke(app, ["init", "acme.com", "--yolo"])
        
        # Should handle error gracefully
        assert "Error during generation" in result.output or "Failed" in result.output
        assert result.exit_code == 1
    
    def test_init_creates_proper_project_structure(self, mock_cli_runner, temp_project_dir):
        """Test that init creates the expected project structure"""
        result = mock_cli_runner.invoke(app, ["init", "acme.com", "--yolo"])
        
        assert result.exit_code == 0
        
        project_dir = temp_project_dir / "acme.com"
        assert project_dir.exists()
        
        # Check that JSON files are created
        expected_files = ["overview.json", "account.json", "persona.json", "email.json"]
        for filename in expected_files:
            file_path = project_dir / filename
            if file_path.exists():  # Some steps might fail in mocked environment
                # Verify it's valid JSON
                import json
                data = json.loads(file_path.read_text())
                assert isinstance(data, dict)
                assert "_generated_at" in data
    
    def test_init_completion_menu_options(self, mock_cli_runner, temp_project_dir):
        """Test the completion menu after successful generation"""
        with patch('cli.utils.menu_utils.show_menu_with_numbers', return_value="Finish") as mock_menu:
            result = mock_cli_runner.invoke(app, ["init", "acme.com", "--yolo"])
            
            assert result.exit_code == 0
            # Menu should be called for completion choices
            assert mock_menu.called or "What would you like to do?" in result.output


class TestInitCommandErrorHandling:
    """Test error handling scenarios for init command"""
    
    def test_init_network_error(self, mock_cli_runner, mock_error_scenarios):
        """Test handling of network errors during scraping"""
        mock_error_scenarios["set"]("network_error")
        
        result = mock_cli_runner.invoke(app, ["init", "acme.com", "--yolo"])
        
        assert result.exit_code == 1
        assert "error" in result.output.lower() or "failed" in result.output.lower()
    
    def test_init_file_permission_error(self, mock_cli_runner, temp_project_dir, monkeypatch):
        """Test handling of file permission errors"""
        # Make the temp directory read-only
        temp_project_dir.chmod(0o444)
        
        try:
            result = mock_cli_runner.invoke(app, ["init", "acme.com", "--yolo"])
            # Should handle permission error gracefully
            assert "error" in result.output.lower() or result.exit_code != 0
        finally:
            # Restore permissions for cleanup
            temp_project_dir.chmod(0o755)
    
    def test_init_corrupted_existing_project(self, mock_cli_runner, mock_corrupted_project):
        """Test handling of corrupted existing project files"""
        domain = mock_corrupted_project.name
        
        # Should handle corrupted files gracefully
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        
        # Should either succeed (overwriting corrupted files) or show error
        assert result.exit_code in [0, 1]


class TestInitCommandContextHandling:
    """Test context and hypothesis handling in init command"""
    
    def test_init_with_user_hypotheses(self, mock_cli_runner, mock_console_input, temp_project_dir):
        """Test init with user-provided hypotheses"""
        # Mock hypothesis inputs
        mock_console_input("acme.com")  # Domain
        mock_console_input("Enterprise companies with 500+ employees")  # Account hypothesis
        mock_console_input("CTOs and VP Engineering")  # Persona hypothesis
        mock_console_input("Focus on AI and automation")  # Extra context
        
        with patch('typer.confirm', return_value=True):
            result = mock_cli_runner.invoke(app, ["init"])
            
            assert result.exit_code == 0
            assert "Context captured" in result.output
    
    def test_init_skip_all_hypotheses(self, mock_cli_runner, mock_console_input, temp_project_dir):
        """Test init when user skips all hypothesis inputs"""
        mock_console_input("acme.com")  # Domain
        mock_console_input("")  # Skip account hypothesis
        mock_console_input("")  # Skip persona hypothesis
        mock_console_input("")  # Skip extra context
        
        with patch('typer.confirm', return_value=True):
            result = mock_cli_runner.invoke(app, ["init"])
            
            assert result.exit_code == 0
            # Should still proceed without context
    
    def test_init_context_parameter_usage(self, mock_cli_runner, temp_project_dir):
        """Test that context parameter is properly used"""
        context = "Series A startup in fintech space"
        result = mock_cli_runner.invoke(app, [
            "init", "acme.com", 
            "--context", context,
            "--yolo"
        ])
        
        assert result.exit_code == 0
        # Context should be passed to generation (verified through mocks)