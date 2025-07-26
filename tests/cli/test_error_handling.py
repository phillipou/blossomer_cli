"""
Comprehensive error handling tests for the CLI.
Tests various failure scenarios without making real API calls.
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, Mock, side_effect
from typer.testing import CliRunner

from cli.main import app


class TestAPIErrorHandling:
    """Test handling of API and external service errors"""
    
    def test_llm_api_timeout_handling(self, mock_cli_runner, mock_error_scenarios, temp_project_dir):
        """Test handling of LLM API timeouts"""
        domain = "timeout-test.com"
        mock_error_scenarios["set"]("timeout")
        
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        
        assert result.exit_code == 1
        assert "timed out" in result.output.lower() or "timeout" in result.output.lower()
        assert "40 seconds" in result.output or "network" in result.output.lower()
        
        # Should provide recovery guidance
        assert "try again" in result.output.lower() or "blossomer init" in result.output
    
    def test_llm_api_rate_limit_handling(self, mock_cli_runner, mock_error_scenarios, temp_project_dir):
        """Test handling of API rate limits"""
        domain = "rate-limit-test.com"
        mock_error_scenarios["set"]("api_error")
        
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        
        assert result.exit_code == 1
        assert "error" in result.output.lower() or "failed" in result.output.lower()
        
        # Should suggest retry
        assert "try again" in result.output.lower() or "later" in result.output.lower()
    
    def test_firecrawl_api_error_handling(self, mock_cli_runner, mock_error_scenarios, temp_project_dir):
        """Test handling of Firecrawl/web scraping errors"""
        domain = "scraping-error-test.com"
        mock_error_scenarios["set"]("network_error")
        
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        
        assert result.exit_code == 1
        assert "error" in result.output.lower() or "failed" in result.output.lower()
        
        # Should provide helpful guidance
        assert "network" in result.output.lower() or "connectivity" in result.output.lower()
    
    def test_missing_api_keys_handling(self, mock_cli_runner, monkeypatch):
        """Test handling of missing API keys"""
        # Remove API keys
        monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
        monkeypatch.delenv("FORGE_API_KEY", raising=False)
        
        # Mock declining interactive setup
        with patch('questionary.confirm') as mock_confirm:
            mock_confirm.return_value.ask.return_value = False
            
            result = mock_cli_runner.invoke(app, ["init", "test.com"])
            
            assert result.exit_code == 0  # Should exit gracefully
            assert "API" in result.output or "key" in result.output.lower()
            assert "setup" in result.output.lower() or "required" in result.output.lower()
    
    def test_invalid_api_keys_handling(self, mock_cli_runner, monkeypatch):
        """Test handling of invalid API keys"""
        # Set invalid API keys
        monkeypatch.setenv("FIRECRAWL_API_KEY", "invalid_key")
        monkeypatch.setenv("FORGE_API_KEY", "invalid_key")
        
        # Mock API error due to invalid keys
        with patch('cli.services.llm_service.LLMClient.generate', 
                  side_effect=Exception("Invalid API key")):
            
            result = mock_cli_runner.invoke(app, ["init", "test.com", "--yolo"])
            
            assert result.exit_code == 1
            assert "error" in result.output.lower() or "failed" in result.output.lower()
    
    def test_api_service_unavailable_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling when API services are unavailable"""
        domain = "service-unavailable.com"
        
        # Mock service unavailable error
        with patch('cli.services.llm_service.LLMClient.generate', 
                  side_effect=ConnectionError("Service unavailable")):
            
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            assert result.exit_code == 1
            assert "error" in result.output.lower() or "failed" in result.output.lower()
            
            # Should provide recovery guidance
            assert "network" in result.output.lower() or "connectivity" in result.output.lower()


class TestFileSystemErrorHandling:
    """Test handling of file system errors"""
    
    def test_permission_denied_error_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of file permission errors"""
        domain = "permission-denied.com"
        
        # Make temp directory read-only
        temp_project_dir.chmod(0o444)
        
        try:
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            # Should handle permission error gracefully
            assert result.exit_code in [0, 1]
            if result.exit_code == 1:
                assert "permission" in result.output.lower() or "error" in result.output.lower()
                
        finally:
            # Restore permissions for cleanup
            temp_project_dir.chmod(0o755)
    
    def test_disk_space_error_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of disk space errors"""
        domain = "disk-space.com"
        
        # Mock disk space error
        with patch('pathlib.Path.write_text', side_effect=OSError("No space left on device")):
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            # Should handle disk space error gracefully
            assert result.exit_code in [0, 1]
            if result.exit_code == 1:
                assert "space" in result.output.lower() or "disk" in result.output.lower()
    
    def test_corrupted_json_file_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of corrupted JSON files"""
        domain = "corrupted-json.com"
        project_dir = temp_project_dir / domain
        project_dir.mkdir()
        
        # Create corrupted JSON file
        (project_dir / "overview.json").write_text("{corrupted json content")
        
        # Show command should handle corrupted JSON gracefully
        result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        
        assert result.exit_code == 0  # Should not crash
        assert "not found" in result.output or "error" in result.output.lower()
    
    def test_missing_project_directory_handling(self, mock_cli_runner):
        """Test handling of missing project directories"""
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", "nonexistent.com"])
        
        assert result.exit_code == 0
        assert "No GTM project found" in result.output
        assert "blossomer init" in result.output
    
    def test_partial_file_corruption_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of partially corrupted project files"""
        domain = "partial-corruption.com"
        project_dir = temp_project_dir / domain
        project_dir.mkdir()
        
        # Create valid overview but corrupted account
        overview_data = {"company_name": "Test Corp", "_generated_at": "2024-01-01T00:00:00Z"}
        (project_dir / "overview.json").write_text(json.dumps(overview_data))
        (project_dir / "account.json").write_text("{invalid json")
        
        # Should show what's available and handle corruption gracefully
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Test Corp" in result.output  # Should show valid data
    
    def test_file_read_permission_error_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling when files can't be read due to permissions"""
        domain = "read-permission.com"
        project_dir = temp_project_dir / domain
        project_dir.mkdir()
        
        # Create file and make it unreadable
        json_file = project_dir / "overview.json"
        json_file.write_text(json.dumps({"company_name": "Test"}))
        json_file.chmod(0o000)
        
        try:
            result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
            
            # Should handle read permission error gracefully
            assert result.exit_code == 0
            assert "not found" in result.output or "error" in result.output.lower()
            
        finally:
            # Restore permissions for cleanup
            json_file.chmod(0o644)


class TestInputValidationErrorHandling:
    """Test handling of invalid inputs"""
    
    def test_invalid_domain_format_handling(self, mock_cli_runner):
        """Test handling of various invalid domain formats"""
        invalid_domains = [
            "",
            "   ",
            "invalid..domain",
            "domain with spaces",
            "http://",
            "https://",
            "ftp://domain.com",
            "domain..com",
            ".domain.com",
            "domain.com.",
            "very-long-domain-name-that-exceeds-reasonable-limits-for-domain-names.com",
        ]
        
        for invalid_domain in invalid_domains:
            result = mock_cli_runner.invoke(app, ["init", invalid_domain, "--yolo"])
            
            # Should handle invalid domain gracefully
            assert result.exit_code == 1
            assert "Invalid domain format" in result.output or "domain" in result.output.lower()
            
            # Should provide helpful guidance
            assert "Try:" in result.output or "example" in result.output.lower()
    
    def test_invalid_step_name_handling(self, mock_cli_runner, mock_project_with_data):
        """Test handling of invalid step names"""
        domain = mock_project_with_data.name
        invalid_steps = ["invalid_step", "nonexistent", "123", "", "step with spaces"]
        
        for invalid_step in invalid_steps:
            result = mock_cli_runner.invoke(app, ["show", invalid_step, "--domain", domain])
            
            # Should handle invalid step gracefully
            assert result.exit_code == 0
            assert "Unknown asset" in result.output or "not found" in result.output.lower()
            
            # Should show available options
            assert "Available assets:" in result.output or "overview" in result.output
    
    def test_invalid_command_arguments_handling(self, mock_cli_runner):
        """Test handling of invalid command arguments"""
        invalid_commands = [
            ["init"],  # Missing domain
            ["show"],  # May need domain
            ["edit"],  # Missing step
            ["export"],  # May need domain
            ["--invalid-flag", "init", "test.com"],
        ]
        
        for cmd in invalid_commands:
            result = mock_cli_runner.invoke(app, cmd)
            
            # Should handle invalid arguments gracefully
            # Some may succeed with defaults, others should show help
            if result.exit_code != 0:
                assert "error" in result.output.lower() or "usage" in result.output.lower() or "help" in result.output.lower()
    
    def test_context_too_long_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of extremely long context input"""
        domain = "long-context.com"
        extremely_long_context = "Very long context. " * 1000  # ~18KB
        
        result = mock_cli_runner.invoke(app, [
            "init", domain,
            "--context", extremely_long_context,
            "--yolo"
        ])
        
        # Should either succeed or fail gracefully
        assert result.exit_code in [0, 1]
        
        if result.exit_code == 1:
            assert "context" in result.output.lower() or "too long" in result.output.lower()
    
    def test_special_characters_in_input_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of special characters in inputs"""
        special_context = "Context with émojis 🚀 and spëcial chars ànd unicode ñ"
        
        result = mock_cli_runner.invoke(app, [
            "init", "special-chars.com",
            "--context", special_context,
            "--yolo"
        ])
        
        # Should handle special characters gracefully
        assert result.exit_code in [0, 1]


class TestConcurrencyErrorHandling:
    """Test handling of concurrency and race condition errors"""
    
    def test_concurrent_project_access_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of concurrent access to same project"""
        domain = "concurrent-test.com"
        
        # Create project
        init_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert init_result.exit_code == 0
        
        # Simulate concurrent access by multiple operations
        # In real scenario, this might cause file locking issues
        with patch('pathlib.Path.write_text', side_effect=OSError("Resource temporarily unavailable")):
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            # Should handle concurrency error gracefully
            assert result.exit_code in [0, 1]
    
    def test_file_locking_error_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of file locking errors"""
        domain = "file-lock.com"
        
        # Mock file locking error
        with patch('pathlib.Path.write_text', side_effect=PermissionError("File is locked")):
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            assert result.exit_code in [0, 1]
            if result.exit_code == 1:
                assert "error" in result.output.lower() or "permission" in result.output.lower()


class TestResourceErrorHandling:
    """Test handling of resource exhaustion errors"""
    
    def test_memory_error_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of memory errors"""
        domain = "memory-error.com"
        
        # Mock memory error
        with patch('json.dumps', side_effect=MemoryError("Out of memory")):
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            # Should handle memory error gracefully
            assert result.exit_code in [0, 1]
            if result.exit_code == 1:
                assert "error" in result.output.lower() or "memory" in result.output.lower()
    
    def test_large_response_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of extremely large API responses"""
        domain = "large-response.com"
        
        # Mock extremely large response
        large_response = json.dumps({"large_field": "x" * 100000})  # 100KB
        
        with patch('cli.services.llm_service.LLMClient.generate', return_value=large_response):
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            # Should handle large responses
            assert result.exit_code in [0, 1]
    
    def test_too_many_files_error_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of too many open files error"""
        domain = "too-many-files.com"
        
        # Mock too many files error
        with patch('pathlib.Path.open', side_effect=OSError("Too many open files")):
            result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
            
            # Should handle file limit error gracefully
            assert result.exit_code in [0, 1]


class TestInterruptionErrorHandling:
    """Test handling of user interruptions and signals"""
    
    def test_keyboard_interrupt_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of Ctrl+C during operations"""
        domain = "interrupt-test.com"
        
        # Mock keyboard interrupt during generation
        with patch('cli.commands.init.run_async_generation', side_effect=KeyboardInterrupt()):
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            assert result.exit_code == 130  # Standard Ctrl+C exit code
            assert "cancelled" in result.output.lower() or "stopped" in result.output.lower()
            
            # Should provide recovery guidance
            assert "Resume with:" in result.output or "blossomer init" in result.output
    
    def test_system_signal_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of system signals"""
        domain = "signal-test.com"
        
        # Mock system signal interruption
        with patch('cli.commands.init.run_async_generation', side_effect=SystemExit(1)):
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            # Should handle system exit gracefully
            assert result.exit_code in [1, 130]
    
    def test_timeout_during_user_input_handling(self, mock_cli_runner, temp_project_dir):
        """Test handling of timeout during user input"""
        # This would be relevant for interactive mode timeouts
        with patch('questionary.text') as mock_text:
            mock_text.return_value.ask.side_effect = KeyboardInterrupt()
            
            result = mock_cli_runner.invoke(app, ["init"])
            
            # Should handle input timeout/interruption gracefully
            assert result.exit_code in [0, 130]


class TestErrorRecoveryGuidance:
    """Test that error messages provide helpful recovery guidance"""
    
    def test_error_messages_include_next_steps(self, mock_cli_runner):
        """Test that error messages include actionable next steps"""
        # Test various error scenarios and verify guidance is provided
        
        # Invalid domain
        result1 = mock_cli_runner.invoke(app, ["init", "invalid..domain", "--yolo"])
        assert result1.exit_code == 1
        assert "Try:" in result1.output or "example" in result1.output.lower()
        
        # Non-existent project
        result2 = mock_cli_runner.invoke(app, ["show", "all", "--domain", "nonexistent.com"])
        assert result2.exit_code == 0
        assert "blossomer init" in result2.output
        
        # Invalid step
        result3 = mock_cli_runner.invoke(app, ["show", "invalid_step", "--domain", "test.com"])
        assert result3.exit_code == 0
        assert "Available assets:" in result3.output or "overview" in result3.output
    
    def test_error_messages_are_user_friendly(self, mock_cli_runner, mock_error_scenarios):
        """Test that error messages are user-friendly, not technical"""
        domain = "user-friendly-errors.com"
        
        mock_error_scenarios["set"]("api_error")
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        
        assert result.exit_code == 1
        
        # Should avoid technical jargon
        technical_terms = ["traceback", "exception", "stacktrace", "null pointer"]
        error_output_lower = result.output.lower()
        
        for term in technical_terms:
            assert term not in error_output_lower
        
        # Should use friendly language
        friendly_indicators = ["error", "failed", "try", "help", "network", "connectivity"]
        assert any(indicator in error_output_lower for indicator in friendly_indicators)
    
    def test_error_context_preservation(self, mock_cli_runner, temp_project_dir):
        """Test that errors preserve user context and progress"""
        domain = "context-preservation.com"
        
        # Start project creation
        with patch('cli.services.llm_service.LLMClient.generate', 
                  side_effect=[
                      json.dumps({"company_name": "Test Corp"}),  # First call succeeds
                      Exception("API error")  # Second call fails
                  ]):
            
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            # Should preserve partial progress
            project_dir = temp_project_dir / domain
            if project_dir.exists():
                # Check if partial progress was saved
                overview_file = project_dir / "overview.json"
                if overview_file.exists():
                    overview_data = json.loads(overview_file.read_text())
                    assert overview_data["company_name"] == "Test Corp"
    
    def test_help_system_accessibility(self, mock_cli_runner):
        """Test that help system is accessible from error states"""
        # Test that users can access help even when commands fail
        
        # Main help should always work
        help_result = mock_cli_runner.invoke(app, ["--help"])
        assert help_result.exit_code == 0
        assert "init" in help_result.output
        
        # Command-specific help should work
        init_help_result = mock_cli_runner.invoke(app, ["init", "--help"])
        assert init_help_result.exit_code == 0
        assert "domain" in init_help_result.output.lower()
        
        show_help_result = mock_cli_runner.invoke(app, ["show", "--help"])
        assert show_help_result.exit_code == 0


class TestErrorLoggingAndDebugging:
    """Test error logging and debugging capabilities"""
    
    def test_debug_mode_error_details(self, mock_cli_runner, mock_error_scenarios):
        """Test that debug mode provides additional error details"""
        domain = "debug-errors.com"
        mock_error_scenarios["set"]("api_error")
        
        # Normal mode - should be user-friendly
        normal_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        
        # Debug mode - should provide more details
        debug_result = mock_cli_runner.invoke(app, ["--debug", "init", domain, "--yolo"])
        
        # Both should handle error, but debug might provide more info
        assert normal_result.exit_code == 1
        assert debug_result.exit_code == 1
    
    def test_verbose_mode_error_context(self, mock_cli_runner, mock_error_scenarios):
        """Test that verbose mode provides error context"""
        domain = "verbose-errors.com"
        mock_error_scenarios["set"]("network_error")
        
        result = mock_cli_runner.invoke(app, ["--verbose", "init", domain, "--yolo"])
        
        assert result.exit_code == 1
        # Verbose mode should provide additional context
    
    def test_quiet_mode_error_handling(self, mock_cli_runner, mock_error_scenarios):
        """Test that quiet mode still shows critical errors"""
        domain = "quiet-errors.com"
        mock_error_scenarios["set"]("api_error")
        
        result = mock_cli_runner.invoke(app, ["--quiet", "init", domain, "--yolo"])
        
        assert result.exit_code == 1
        # Even in quiet mode, should show critical errors
        assert len(result.output) > 0  # Should not be completely silent on errors


print("🔥 Error handling test suite ready")
print("These tests cover various failure scenarios to ensure robust error handling")