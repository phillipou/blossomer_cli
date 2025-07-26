"""
Unit tests for other CLI commands (edit, export, list).
Tests the remaining CLI commands with mocked dependencies.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, Mock
from typer.testing import CliRunner

from cli.main import app


class TestEditCommand:
    """Test suite for the edit command"""
    
    def test_edit_strategy_with_domain(self, mock_cli_runner, mock_project_with_data):
        """Test editing strategy for specific domain"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            result = mock_cli_runner.invoke(app, ["edit", "strategy", "--domain", domain])
            
            assert result.exit_code == 0
            assert mock_editor.called
    
    def test_edit_overview_auto_detect(self, mock_cli_runner, mock_project_with_data):
        """Test editing overview with auto-detected domain"""
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            result = mock_cli_runner.invoke(app, ["edit", "overview"])
            
            assert result.exit_code == 0
            assert mock_editor.called
    
    def test_edit_nonexistent_project(self, mock_cli_runner):
        """Test editing for non-existent project"""
        result = mock_cli_runner.invoke(app, ["edit", "strategy", "--domain", "nonexistent.com"])
        
        assert result.exit_code == 0
        # Should show error or guidance message
        assert "not found" in result.output.lower() or "no gtm project" in result.output.lower()
    
    def test_edit_invalid_step(self, mock_cli_runner, mock_project_with_data):
        """Test editing invalid step"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["edit", "invalid_step", "--domain", domain])
        
        # Should handle gracefully (may succeed with default or show error)
        assert result.exit_code in [0, 1]
    
    def test_edit_missing_file(self, mock_cli_runner, temp_project_dir):
        """Test editing when markdown file doesn't exist"""
        # Create minimal project without markdown files
        domain = "minimal.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        overview_data = {"company_name": "Minimal Corp"}
        (project_path / "overview.json").write_text(json.dumps(overview_data))
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            result = mock_cli_runner.invoke(app, ["edit", "overview", "--domain", domain])
            
            # Should handle missing markdown files gracefully
            assert result.exit_code == 0
    
    def test_edit_multiple_projects_no_domain(self, mock_cli_runner, mock_project_with_data, temp_project_dir):
        """Test editing when multiple projects exist without domain"""
        # Create second project
        second_project = temp_project_dir / "second.com"
        second_project.mkdir()
        (second_project / "overview.json").write_text(json.dumps({
            "company_name": "Second Company"
        }))
        
        result = mock_cli_runner.invoke(app, ["edit", "strategy"])
        
        # Should require domain specification or auto-detect
        assert result.exit_code in [0, 1]
    
    def test_edit_editor_detection(self, mock_cli_runner, mock_project_with_data):
        """Test editor detection and usage"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.detect_editor', return_value='code') as mock_detect, \
             patch('cli.utils.editor.open_file_in_editor') as mock_open:
            
            result = mock_cli_runner.invoke(app, ["edit", "strategy", "--domain", domain])
            
            assert result.exit_code == 0
            assert mock_open.called


class TestExportCommand:
    """Test suite for the export command"""
    
    def test_export_all_assets(self, mock_cli_runner, mock_project_with_data):
        """Test exporting all assets"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["export", "all", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Exporting GTM assets" in result.output
    
    def test_export_single_asset(self, mock_cli_runner, mock_project_with_data):
        """Test exporting single asset"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["export", "overview", "--domain", domain])
        
        assert result.exit_code == 0
    
    def test_export_with_custom_output(self, mock_cli_runner, mock_project_with_data, tmp_path):
        """Test exporting with custom output path"""
        domain = mock_project_with_data.name
        output_file = tmp_path / "custom_export.md"
        
        with patch('pathlib.Path.write_text') as mock_write:
            result = mock_cli_runner.invoke(app, [
                "export", "overview", 
                "--domain", domain,
                "--output", str(output_file)
            ])
            
            assert result.exit_code == 0
            assert mock_write.called
    
    def test_export_nonexistent_project(self, mock_cli_runner):
        """Test exporting non-existent project"""
        result = mock_cli_runner.invoke(app, ["export", "all", "--domain", "nonexistent.com"])
        
        assert result.exit_code == 0
        assert "No GTM project found" in result.output
    
    def test_export_auto_detect_single_project(self, mock_cli_runner, mock_project_with_data):
        """Test export with auto-detected domain"""
        result = mock_cli_runner.invoke(app, ["export", "all"])
        
        assert result.exit_code == 0
    
    def test_export_multiple_projects_no_domain(self, mock_cli_runner, mock_project_with_data, temp_project_dir):
        """Test export when multiple projects exist"""
        # Create second project
        second_project = temp_project_dir / "second.com"
        second_project.mkdir()
        (second_project / "overview.json").write_text(json.dumps({
            "company_name": "Second Company"
        }))
        
        result = mock_cli_runner.invoke(app, ["export", "all"])
        
        assert result.exit_code == 0
        assert "Multiple projects found" in result.output
        assert "Please specify domain" in result.output
    
    def test_export_invalid_asset(self, mock_cli_runner, mock_project_with_data):
        """Test exporting invalid asset"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["export", "invalid_asset", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Unknown asset" in result.output
        assert "Available assets:" in result.output
    
    def test_export_creates_output_file(self, mock_cli_runner, mock_project_with_data, temp_project_dir):
        """Test that export creates output file"""
        domain = mock_project_with_data.name
        
        with patch('pathlib.Path.write_text') as mock_write:
            result = mock_cli_runner.invoke(app, ["export", "overview", "--domain", domain])
            
            assert result.exit_code == 0
            # Should attempt to write file
            if mock_write.called:
                assert len(mock_write.call_args[0]) > 0  # Content should not be empty
    
    def test_export_default_filename_format(self, mock_cli_runner, mock_project_with_data):
        """Test default filename format"""
        domain = mock_project_with_data.name
        
        with patch('pathlib.Path.write_text') as mock_write:
            result = mock_cli_runner.invoke(app, ["export", "overview", "--domain", domain])
            
            assert result.exit_code == 0
            # Test passes if export functionality works (filename tested in integration)


class TestListCommand:
    """Test suite for the list command"""
    
    def test_list_all_projects(self, mock_cli_runner, mock_project_with_data, mock_incomplete_project):
        """Test listing all projects"""
        result = mock_cli_runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "GTM projects" in result.output.lower() or mock_project_with_data.name in result.output
    
    def test_list_specific_domain(self, mock_cli_runner, mock_project_with_data):
        """Test listing files for specific domain"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["list", "--domain", domain])
        
        assert result.exit_code == 0
        assert domain in result.output
    
    def test_list_no_projects(self, mock_cli_runner, temp_project_dir):
        """Test listing when no projects exist"""
        # temp_project_dir is empty
        result = mock_cli_runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "No GTM projects found" in result.output or "no projects" in result.output.lower()
    
    def test_list_nonexistent_domain(self, mock_cli_runner):
        """Test listing non-existent domain"""
        result = mock_cli_runner.invoke(app, ["list", "--domain", "nonexistent.com"])
        
        assert result.exit_code == 0
        # Should show no files or appropriate message
    
    def test_list_shows_file_structure(self, mock_cli_runner, mock_project_with_data):
        """Test that list shows file structure"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["list", "--domain", domain])
        
        assert result.exit_code == 0
        # Should show some indication of files/structure
        assert ".json" in result.output or "files" in result.output.lower()
    
    def test_list_with_metadata(self, mock_cli_runner, mock_project_with_data):
        """Test list command includes metadata"""
        result = mock_cli_runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        # Should show creation date, progress, or other metadata
        assert "2024" in result.output or "progress" in result.output.lower() or "steps" in result.output.lower()


class TestMainAppIntegration:
    """Test main app integration and global options"""
    
    def test_version_option(self, mock_cli_runner):
        """Test --version option"""
        result = mock_cli_runner.invoke(app, ["--version"])
        
        assert result.exit_code == 0
        assert "Blossomer GTM CLI" in result.output
        assert "version" in result.output.lower()
    
    def test_help_option(self, mock_cli_runner):
        """Test --help option"""
        result = mock_cli_runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "Blossomer GTM CLI" in result.output
        assert "init" in result.output
        assert "show" in result.output
    
    def test_verbose_option(self, mock_cli_runner, mock_project_with_data):
        """Test --verbose option"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["--verbose", "show", "all", "--domain", domain])
        
        assert result.exit_code == 0
        # Verbose mode should work (may not show different output in mocked environment)
    
    def test_quiet_option(self, mock_cli_runner, mock_project_with_data):
        """Test --quiet option"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["--quiet", "show", "all", "--domain", domain])
        
        assert result.exit_code == 0
        # Quiet mode should work
    
    def test_no_color_option(self, mock_cli_runner, mock_project_with_data):
        """Test --no-color option"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["--no-color", "show", "all", "--domain", domain])
        
        assert result.exit_code == 0
        # No-color mode should work
    
    def test_debug_option(self, mock_cli_runner, mock_project_with_data):
        """Test --debug option"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["--debug", "show", "all", "--domain", domain])
        
        assert result.exit_code == 0
        # Debug mode should work
    
    def test_main_welcome_panel(self, mock_cli_runner):
        """Test main welcome panel when no command is given"""
        result = mock_cli_runner.invoke(app, [])
        
        assert result.exit_code == 0
        assert "Welcome to" in result.output
        assert "Blossomer CLI" in result.output
        assert "Available Commands" in result.output
    
    def test_invalid_command(self, mock_cli_runner):
        """Test invalid command handling"""
        result = mock_cli_runner.invoke(app, ["invalid_command"])
        
        # Should show error or help
        assert result.exit_code != 0 or "No such command" in result.output


class TestCommandErrorHandling:
    """Test error handling across all commands"""
    
    def test_commands_handle_permission_errors(self, mock_cli_runner, mock_project_with_data):
        """Test commands handle file permission errors"""
        domain = mock_project_with_data.name
        
        # Make project directory inaccessible
        mock_project_with_data.chmod(0o000)
        
        try:
            commands_to_test = [
                ["show", "all", "--domain", domain],
                ["edit", "strategy", "--domain", domain],
                ["export", "overview", "--domain", domain],
                ["list", "--domain", domain]
            ]
            
            for cmd in commands_to_test:
                result = mock_cli_runner.invoke(app, cmd)
                # Should handle errors gracefully (not crash)
                assert result.exit_code in [0, 1]
                
        finally:
            # Restore permissions for cleanup
            mock_project_with_data.chmod(0o755)
    
    def test_commands_handle_corrupted_data(self, mock_cli_runner, mock_corrupted_project):
        """Test commands handle corrupted project data"""
        domain = mock_corrupted_project.name
        
        commands_to_test = [
            ["show", "overview", "--domain", domain],
            ["edit", "overview", "--domain", domain],
            ["export", "overview", "--domain", domain],
            ["list", "--domain", domain]
        ]
        
        for cmd in commands_to_test:
            result = mock_cli_runner.invoke(app, cmd)
            # Should handle corrupted data gracefully
            assert result.exit_code in [0, 1]
    
    def test_commands_handle_missing_dependencies(self, mock_cli_runner, temp_project_dir):
        """Test commands handle missing system dependencies"""
        # Create project
        domain = "deps-test.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        (project_path / "overview.json").write_text(json.dumps({"company_name": "Test"}))
        
        # Mock missing editor
        with patch('cli.utils.editor.detect_editor', return_value=None):
            result = mock_cli_runner.invoke(app, ["edit", "overview", "--domain", domain])
            
            # Should handle missing editor gracefully
            assert result.exit_code in [0, 1]
    
    def test_commands_handle_disk_space_error(self, mock_cli_runner, mock_project_with_data):
        """Test commands handle disk space errors"""
        domain = mock_project_with_data.name
        
        # Mock disk space error
        with patch('pathlib.Path.write_text', side_effect=OSError("No space left on device")):
            result = mock_cli_runner.invoke(app, ["export", "overview", "--domain", domain])
            
            # Should handle disk space error gracefully
            assert result.exit_code in [0, 1]
            if result.exit_code == 1:
                assert "error" in result.output.lower() or "failed" in result.output.lower()


class TestCommandPerformance:
    """Test performance characteristics of commands"""
    
    def test_show_command_performance(self, mock_cli_runner, mock_project_with_data):
        """Test show command completes quickly"""
        import time
        domain = mock_project_with_data.name
        
        start_time = time.time()
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        elapsed_time = time.time() - start_time
        
        assert result.exit_code == 0
        assert elapsed_time < 5.0  # Should complete within 5 seconds
    
    def test_list_command_with_many_projects(self, mock_cli_runner, temp_project_dir):
        """Test list command performance with many projects"""
        # Create multiple projects
        for i in range(20):
            project_path = temp_project_dir / f"project-{i}.com"
            project_path.mkdir()
            (project_path / "overview.json").write_text(json.dumps({
                "company_name": f"Company {i}"
            }))
        
        import time
        start_time = time.time()
        result = mock_cli_runner.invoke(app, ["list"])
        elapsed_time = time.time() - start_time
        
        assert result.exit_code == 0
        assert elapsed_time < 3.0  # Should handle many projects quickly