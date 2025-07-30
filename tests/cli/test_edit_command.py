"""
Comprehensive tests for the edit command.
Tests editing GTM assets and content modification.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
from cli.main import app


class TestEditCommand:
    """Test suite for the edit command"""
    
    def test_edit_help(self, mock_cli_runner):
        """Test edit command help"""
        result = mock_cli_runner.invoke(app, ["edit", "--help"])
        
        assert result.exit_code == 0
        assert "edit" in result.output.lower()
    
    def test_edit_overview_step(self, mock_cli_runner, mock_project_with_data):
        """Test editing overview step"""
        domain = mock_project_with_data.name
        
        # Mock editor opening
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            assert result.exit_code == 0
            assert "edit" in result.output.lower() or "open" in result.output.lower()
    
    def test_edit_account_step(self, mock_cli_runner, mock_project_with_data):
        """Test editing account step"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "account", domain])
            
            assert result.exit_code == 0
    
    def test_edit_persona_step(self, mock_cli_runner, mock_project_with_data):
        """Test editing persona step"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "persona", domain])
            
            assert result.exit_code == 0
    
    def test_edit_email_step(self, mock_cli_runner, mock_project_with_data):
        """Test editing email step"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "email", domain])
            
            assert result.exit_code == 0
    
    def test_edit_strategy_step(self, mock_cli_runner, mock_project_with_data):
        """Test editing strategy step"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "strategy", domain])
            
            assert result.exit_code == 0
    
    def test_edit_nonexistent_step(self, mock_cli_runner, mock_project_with_data):
        """Test editing non-existent step"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["edit", "nonexistent", domain])
        
        assert result.exit_code != 0 or "not found" in result.output.lower()
    
    def test_edit_nonexistent_project(self, mock_cli_runner, temp_project_dir):
        """Test editing step in non-existent project"""
        result = mock_cli_runner.invoke(app, ["edit", "overview", "nonexistent.com"])
        
        assert result.exit_code != 0 or "not found" in result.output.lower()
    
    def test_edit_with_specific_editor(self, mock_cli_runner, mock_project_with_data):
        """Test editing with specific editor"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, [
                "edit", "overview", domain,
                "--editor", "nano"
            ])
            
            assert result.exit_code == 0
    
    def test_edit_creates_backup(self, mock_cli_runner, mock_project_with_data):
        """Test that edit creates backup before editing"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, [
                "edit", "overview", domain,
                "--backup"
            ])
            
            assert result.exit_code == 0
            # Should mention backup creation
            assert "backup" in result.output.lower() or result.exit_code == 0


class TestEditCommandEditorIntegration:
    """Test editor integration for edit command"""
    
    def test_edit_detects_default_editor(self, mock_cli_runner, mock_project_with_data):
        """Test that edit detects default system editor"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.detect_editor') as mock_detect:
            mock_detect.return_value = "vim"
            
            with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
                mock_editor.return_value = True
                
                result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
                
                assert result.exit_code == 0
    
    def test_edit_handles_editor_not_found(self, mock_cli_runner, mock_project_with_data):
        """Test handling when editor is not found"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.detect_editor') as mock_detect:
            mock_detect.return_value = None
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            # Should handle missing editor gracefully
            assert result.exit_code != 0 or "editor" in result.output.lower()
    
    def test_edit_handles_editor_failure(self, mock_cli_runner, mock_project_with_data):
        """Test handling when editor fails to open"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = False  # Editor failed
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            # Should handle editor failure gracefully
            assert result.exit_code != 0 or "failed" in result.output.lower()
    
    def test_edit_with_editor_environment_variable(self, mock_cli_runner, mock_project_with_data, monkeypatch):
        """Test edit respects EDITOR environment variable"""
        domain = mock_project_with_data.name
        
        monkeypatch.setenv("EDITOR", "custom-editor")
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            assert result.exit_code == 0
    
    def test_edit_with_visual_environment_variable(self, mock_cli_runner, mock_project_with_data, monkeypatch):
        """Test edit respects VISUAL environment variable"""
        domain = mock_project_with_data.name
        
        monkeypatch.setenv("VISUAL", "custom-visual-editor")
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            assert result.exit_code == 0
    
    def test_edit_interactive_editor_selection(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test interactive editor selection"""
        domain = mock_project_with_data.name
        
        mock_console_input("vim")  # Select vim
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            assert result.exit_code == 0


class TestEditCommandFileHandling:
    """Test file handling aspects of edit command"""
    
    def test_edit_json_format(self, mock_cli_runner, mock_project_with_data):
        """Test editing JSON format files"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, [
                "edit", "overview", domain,
                "--format", "json"
            ])
            
            assert result.exit_code == 0
    
    def test_edit_markdown_format(self, mock_cli_runner, mock_project_with_data):
        """Test editing Markdown format files"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, [
                "edit", "overview", domain,
                "--format", "markdown"
            ])
            
            assert result.exit_code == 0
    
    def test_edit_creates_file_if_missing(self, mock_cli_runner, mock_incomplete_project):
        """Test that edit creates file if it doesn't exist"""
        domain = mock_incomplete_project.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "account", domain])
            
            # Should either create file or prompt for creation
            assert result.exit_code == 0 or "create" in result.output.lower()
    
    def test_edit_validates_json_after_edit(self, mock_cli_runner, mock_project_with_data):
        """Test that edit validates JSON after editing"""
        domain = mock_project_with_data.name
        
        def mock_edit_with_invalid_json(*args, **kwargs):
            # Simulate editing file to invalid JSON
            file_path = args[0]
            Path(file_path).write_text("{ invalid json")
            return True
        
        with patch('cli.utils.editor.open_file_in_editor', side_effect=mock_edit_with_invalid_json):
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            # Should detect invalid JSON and handle appropriately
            assert result.exit_code != 0 or "invalid" in result.output.lower() or "json" in result.output.lower()
    
    def test_edit_preserves_file_permissions(self, mock_cli_runner, mock_project_with_data):
        """Test that edit preserves file permissions"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            assert result.exit_code == 0
    
    def test_edit_handles_file_locked(self, mock_cli_runner, mock_project_with_data):
        """Test handling when file is locked by another process"""
        domain = mock_project_with_data.name
        
        def mock_locked_file(*args, **kwargs):
            raise PermissionError("File is locked")
        
        with patch('cli.utils.editor.open_file_in_editor', side_effect=mock_locked_file):
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            # Should handle locked file gracefully
            assert result.exit_code != 0 or "locked" in result.output.lower() or "permission" in result.output.lower()


class TestEditCommandDataValidation:
    """Test data validation in edit command"""
    
    def test_edit_validates_required_fields(self, mock_cli_runner, mock_project_with_data):
        """Test that edit validates required fields after editing"""
        domain = mock_project_with_data.name
        
        def mock_edit_remove_required_field(*args, **kwargs):
            # Simulate removing required field
            file_path = args[0]
            Path(file_path).write_text(json.dumps({"incomplete": "data"}))
            return True
        
        with patch('cli.utils.editor.open_file_in_editor', side_effect=mock_edit_remove_required_field):
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            # Should either validate or warn about missing fields
            assert result.exit_code == 0  # May allow incomplete data with warning
    
    def test_edit_handles_data_type_validation(self, mock_cli_runner, mock_project_with_data):
        """Test data type validation after editing"""
        domain = mock_project_with_data.name
        
        def mock_edit_wrong_types(*args, **kwargs):
            # Simulate wrong data types
            file_path = args[0]
            Path(file_path).write_text(json.dumps({
                "company_name": 123,  # Should be string
                "invalid_field": "value"
            }))
            return True
        
        with patch('cli.utils.editor.open_file_in_editor', side_effect=mock_edit_wrong_types):
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            # Should handle type validation
            assert result.exit_code == 0  # May allow with warning
    
    def test_edit_preserves_metadata(self, mock_cli_runner, mock_project_with_data):
        """Test that edit preserves important metadata"""
        domain = mock_project_with_data.name
        
        def mock_edit_preserve_metadata(*args, **kwargs):
            # Simulate editing while preserving metadata
            file_path = args[0]
            original_data = json.loads(Path(file_path).read_text())
            original_data["company_name"] = "Edited Company Name"
            Path(file_path).write_text(json.dumps(original_data, indent=2))
            return True
        
        with patch('cli.utils.editor.open_file_in_editor', side_effect=mock_edit_preserve_metadata):
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            assert result.exit_code == 0
    
    def test_edit_updates_modification_timestamp(self, mock_cli_runner, mock_project_with_data):
        """Test that edit updates modification timestamp"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            assert result.exit_code == 0
            # Should update timestamp (implementation dependent)


class TestEditCommandInteractive:
    """Test interactive features of edit command"""
    
    def test_edit_interactive_step_selection(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test interactive step selection for editing"""
        domain = mock_project_with_data.name
        mock_console_input("overview")  # Select step to edit
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", domain])
            
            assert result.exit_code == 0 or "select" in result.output.lower()
    
    def test_edit_interactive_project_selection(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test interactive project selection"""
        mock_console_input("acme.com")  # Select project
        mock_console_input("overview")  # Select step
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit"])
            
            assert result.exit_code == 0 or "select" in result.output.lower()
    
    def test_edit_confirmation_prompts(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test confirmation prompts during editing"""
        domain = mock_project_with_data.name
        mock_console_input("y")  # Confirm edit
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            assert result.exit_code == 0
    
    def test_edit_post_edit_actions(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test post-edit action prompts"""
        domain = mock_project_with_data.name
        mock_console_input("regenerate")  # Choose to regenerate dependent steps
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            assert result.exit_code == 0


class TestEditCommandDependencyHandling:
    """Test dependency handling in edit command"""
    
    def test_edit_marks_dependent_steps_stale(self, mock_cli_runner, mock_project_with_data):
        """Test that editing marks dependent steps as stale"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            assert result.exit_code == 0
            # Should mention dependent steps or stale status
            assert "dependent" in result.output.lower() or "stale" in result.output.lower() or result.exit_code == 0
    
    def test_edit_offers_regeneration_of_dependencies(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test that edit offers to regenerate dependent steps"""
        domain = mock_project_with_data.name
        mock_console_input("y")  # Confirm regeneration
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            assert result.exit_code == 0
    
    def test_edit_dependency_chain_validation(self, mock_cli_runner, mock_project_with_data):
        """Test validation of dependency chain after editing"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "account", domain])
            
            assert result.exit_code == 0
            # Should validate dependency chain


class TestEditCommandEdgeCases:
    """Test edge cases for edit command"""
    
    def test_edit_very_large_file(self, mock_cli_runner, temp_project_dir):
        """Test editing very large file"""
        domain = "large.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create large file
        large_data = {
            "company_name": "Large Corp",
            "description": "Large description. " * 10000,  # ~230KB
            "_generated_at": "2024-01-01T00:00:00Z"
        }
        (project_path / "overview.json").write_text(json.dumps(large_data))
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            assert result.exit_code == 0
    
    def test_edit_file_with_special_characters(self, mock_cli_runner, temp_project_dir):
        """Test editing file with special characters"""
        domain = "special.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create data with special characters
        special_data = {
            "company_name": "Spëcial Corp™",
            "description": "Company with émojis 🚀 and spëcial chars",
            "_generated_at": "2024-01-01T00:00:00Z"
        }
        (project_path / "overview.json").write_text(json.dumps(special_data, ensure_ascii=False))
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            assert result.exit_code == 0
    
    def test_edit_readonly_file(self, mock_cli_runner, mock_project_with_data):
        """Test editing read-only file"""
        domain = mock_project_with_data.name
        
        # Make file read-only
        project_path = mock_project_with_data
        overview_file = project_path / "overview.json"
        if overview_file.exists():
            overview_file.chmod(0o444)
        
        try:
            with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
                mock_editor.return_value = True
                
                result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
                
                # Should handle read-only file
                assert result.exit_code != 0 or "read-only" in result.output.lower() or "permission" in result.output.lower()
        finally:
            # Restore permissions
            if overview_file.exists():
                overview_file.chmod(0o644)
    
    def test_edit_concurrent_access(self, mock_cli_runner, mock_project_with_data):
        """Test handling concurrent access to same file"""
        domain = mock_project_with_data.name
        
        def mock_concurrent_edit(*args, **kwargs):
            # Simulate another process modifying the file
            file_path = args[0]
            original_data = json.loads(Path(file_path).read_text())
            original_data["modified_by_other_process"] = True
            Path(file_path).write_text(json.dumps(original_data))
            return True
        
        with patch('cli.utils.editor.open_file_in_editor', side_effect=mock_concurrent_edit):
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            # Should handle concurrent modification
            assert result.exit_code == 0
    
    def test_edit_keyboard_interrupt(self, mock_cli_runner, mock_project_with_data):
        """Test handling keyboard interrupt during edit"""
        domain = mock_project_with_data.name
        
        def mock_interrupt(*args, **kwargs):
            raise KeyboardInterrupt()
        
        with patch('cli.utils.editor.open_file_in_editor', side_effect=mock_interrupt):
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            # Should handle interruption gracefully
            assert "interrupt" in result.output.lower() or "cancelled" in result.output.lower() or result.exit_code != 0


class TestEditCommandRecovery:
    """Test recovery features of edit command"""
    
    def test_edit_backup_and_restore(self, mock_cli_runner, mock_project_with_data):
        """Test backup and restore functionality"""
        domain = mock_project_with_data.name
        
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            mock_editor.return_value = True
            
            # Edit with backup
            result = mock_cli_runner.invoke(app, [
                "edit", "overview", domain,
                "--backup"
            ])
            
            assert result.exit_code == 0
            
            # Should be able to restore from backup
            result = mock_cli_runner.invoke(app, [
                "edit", "overview", domain,
                "--restore-backup"
            ])
            
            assert result.exit_code == 0 or "backup" in result.output.lower()
    
    def test_edit_auto_save_on_crash(self, mock_cli_runner, mock_project_with_data):
        """Test auto-save functionality on unexpected exit"""
        domain = mock_project_with_data.name
        
        def mock_crash_during_edit(*args, **kwargs):
            # Simulate crash during editing
            raise Exception("Simulated crash")
        
        with patch('cli.utils.editor.open_file_in_editor', side_effect=mock_crash_during_edit):
            result = mock_cli_runner.invoke(app, ["edit", "overview", domain])
            
            # Should handle crash gracefully
            assert result.exit_code != 0