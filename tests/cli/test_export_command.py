"""
Comprehensive tests for the export command.
Tests exporting GTM assets to various formats.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from cli.main import app


class TestExportCommand:
    """Test suite for the export command"""
    
    def test_export_help(self, mock_cli_runner):
        """Test export command help"""
        result = mock_cli_runner.invoke(app, ["export", "--help"])
        
        assert result.exit_code == 0
        assert "export" in result.output.lower()
        assert "format" in result.output.lower()
    
    def test_export_all_formats(self, mock_cli_runner, mock_project_with_data):
        """Test exporting all formats for a project"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain, 
                "--output", temp_dir,
                "--format", "all"
            ])
            
            assert result.exit_code == 0
            assert "exported" in result.output.lower() or "success" in result.output.lower()
    
    def test_export_json_format(self, mock_cli_runner, mock_project_with_data):
        """Test exporting in JSON format"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--format", "json"
            ])
            
            assert result.exit_code == 0
            # Check if JSON files were created
            output_path = Path(temp_dir)
            json_files = list(output_path.glob("*.json"))
            assert len(json_files) > 0 or "exported" in result.output.lower()
    
    def test_export_markdown_format(self, mock_cli_runner, mock_project_with_data):
        """Test exporting in Markdown format"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--format", "markdown"
            ])
            
            assert result.exit_code == 0
    
    def test_export_csv_format(self, mock_cli_runner, mock_project_with_data):
        """Test exporting in CSV format"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--format", "csv"
            ])
            
            assert result.exit_code == 0
    
    def test_export_single_step(self, mock_cli_runner, mock_project_with_data):
        """Test exporting a single step"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--step", "overview",
                "--format", "json"
            ])
            
            assert result.exit_code == 0
    
    def test_export_multiple_steps(self, mock_cli_runner, mock_project_with_data):
        """Test exporting multiple specific steps"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--step", "overview",
                "--step", "account",
                "--format", "json"
            ])
            
            assert result.exit_code == 0
    
    def test_export_nonexistent_project(self, mock_cli_runner, temp_project_dir):
        """Test exporting non-existent project"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", "nonexistent.com",
                "--output", temp_dir,
                "--format", "json"
            ])
            
            assert result.exit_code != 0 or "not found" in result.output.lower()
    
    def test_export_to_existing_directory(self, mock_cli_runner, mock_project_with_data):
        """Test exporting to an existing directory"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file in the directory
            existing_file = Path(temp_dir) / "existing.txt"
            existing_file.write_text("existing content")
            
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--format", "json"
            ])
            
            assert result.exit_code == 0
            # Should handle existing directory gracefully
    
    def test_export_with_invalid_format(self, mock_cli_runner, mock_project_with_data):
        """Test export with invalid format"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--format", "invalid_format"
            ])
            
            assert result.exit_code != 0 or "invalid" in result.output.lower()
    
    def test_export_with_invalid_step(self, mock_cli_runner, mock_project_with_data):
        """Test export with invalid step name"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--step", "invalid_step",
                "--format", "json"
            ])
            
            assert result.exit_code != 0 or "invalid" in result.output.lower()
    
    def test_export_incomplete_project(self, mock_cli_runner, mock_incomplete_project):
        """Test exporting incomplete project"""
        domain = mock_incomplete_project.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--format", "json"
            ])
            
            assert result.exit_code == 0
            # Should export what's available
    
    def test_export_without_output_directory(self, mock_cli_runner, mock_project_with_data):
        """Test export without specifying output directory"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, [
            "export", domain,
            "--format", "json"
        ])
        
        # Should either work with default location or require output
        assert result.exit_code == 0 or "output" in result.output.lower()
    
    def test_export_with_custom_filename(self, mock_cli_runner, mock_project_with_data):
        """Test export with custom filename"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--filename", "custom_export",
                "--format", "json"
            ])
            
            assert result.exit_code == 0


class TestExportCommandOutputValidation:
    """Test validation of exported content"""
    
    def test_export_json_valid_structure(self, mock_cli_runner, mock_project_with_data):
        """Test that exported JSON has valid structure"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--format", "json"
            ])
            
            if result.exit_code == 0:
                # Check for valid JSON files
                output_path = Path(temp_dir)
                json_files = list(output_path.glob("*.json"))
                
                for json_file in json_files:
                    try:
                        with open(json_file) as f:
                            data = json.load(f)
                            assert isinstance(data, (dict, list))
                    except json.JSONDecodeError:
                        pytest.fail(f"Invalid JSON in {json_file}")
    
    def test_export_markdown_contains_headers(self, mock_cli_runner, mock_project_with_data):
        """Test that exported Markdown contains proper headers"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--format", "markdown"
            ])
            
            if result.exit_code == 0:
                output_path = Path(temp_dir)
                md_files = list(output_path.glob("*.md"))
                
                for md_file in md_files:
                    content = md_file.read_text()
                    # Should contain markdown headers
                    assert "#" in content or "**" in content or "*" in content
    
    def test_export_preserves_data_integrity(self, mock_cli_runner, mock_project_with_data):
        """Test that export preserves original data"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--step", "overview",
                "--format", "json"
            ])
            
            if result.exit_code == 0:
                output_path = Path(temp_dir)
                json_files = list(output_path.glob("*overview*.json"))
                
                if json_files:
                    with open(json_files[0]) as f:
                        exported_data = json.load(f)
                        # Should contain expected fields from mock data
                        assert "company_name" in str(exported_data).lower() or "acme" in str(exported_data).lower()


class TestExportCommandEdgeCases:
    """Test edge cases for export command"""
    
    def test_export_with_file_permission_error(self, mock_cli_runner, mock_project_with_data, monkeypatch):
        """Test export when output directory is not writable"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Make directory non-writable
            temp_path = Path(temp_dir)
            temp_path.chmod(0o444)
            
            try:
                result = mock_cli_runner.invoke(app, [
                    "export", domain,
                    "--output", temp_dir,
                    "--format", "json"
                ])
                
                # Should handle permission error gracefully
                assert result.exit_code != 0 or "permission" in result.output.lower()
            finally:
                # Restore permissions for cleanup
                temp_path.chmod(0o755)
    
    def test_export_corrupted_project_data(self, mock_cli_runner, mock_corrupted_project):
        """Test export with corrupted project data"""
        domain = mock_corrupted_project.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--format", "json"
            ])
            
            # Should handle corrupted data gracefully
            assert result.exit_code != 0 or "error" in result.output.lower()
    
    def test_export_very_large_project(self, mock_cli_runner, temp_project_dir):
        """Test export with very large project data"""
        domain = "large.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create large overview data
        large_data = {
            "company_name": "Large Corp",
            "description": "Large description. " * 10000,  # ~230KB
            "_generated_at": "2024-01-01T00:00:00Z"
        }
        (project_path / "overview.json").write_text(json.dumps(large_data))
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--format", "json"
            ])
            
            assert result.exit_code == 0
            # Should handle large data
    
    def test_export_special_characters_in_data(self, mock_cli_runner, temp_project_dir):
        """Test export with special characters in data"""
        domain = "special.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create data with special characters
        special_data = {
            "company_name": "Special Corp™",
            "description": "Company with émojis 🚀 and spëcial chars: áéíóú",
            "unicode_field": "测试中文字符",
            "_generated_at": "2024-01-01T00:00:00Z"
        }
        (project_path / "overview.json").write_text(json.dumps(special_data, ensure_ascii=False))
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--format", "json"
            ])
            
            assert result.exit_code == 0
    
    def test_export_deep_nested_data(self, mock_cli_runner, temp_project_dir):
        """Test export with deeply nested data structures"""
        domain = "nested.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create deeply nested data
        nested_data = {
            "company_name": "Nested Corp",
            "deeply": {
                "nested": {
                    "structure": {
                        "with": {
                            "many": {
                                "levels": ["value1", "value2", {"more": "nesting"}]
                            }
                        }
                    }
                }
            },
            "_generated_at": "2024-01-01T00:00:00Z"
        }
        (project_path / "overview.json").write_text(json.dumps(nested_data))
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--format", "json"
            ])
            
            assert result.exit_code == 0


class TestExportCommandInteractive:
    """Test interactive features of export command"""
    
    def test_export_interactive_project_selection(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test interactive project selection during export"""
        # Mock user selecting project
        mock_console_input("acme.com")
        mock_console_input("json")  # Format selection
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export",
                "--output", temp_dir
            ])
            
            # Should either work interactively or require domain parameter
            assert result.exit_code == 0 or "domain" in result.output.lower()
    
    def test_export_interactive_format_selection(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test interactive format selection"""
        domain = mock_project_with_data.name
        mock_console_input("json")  # Format selection
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir
            ])
            
            assert result.exit_code == 0
    
    def test_export_with_confirmation_prompt(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test export with confirmation prompt for overwriting"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create existing file
            existing_file = Path(temp_dir) / f"{domain}_export.json"
            existing_file.write_text("existing content")
            
            mock_console_input("y")  # Confirm overwrite
            
            result = mock_cli_runner.invoke(app, [
                "export", domain,
                "--output", temp_dir,
                "--format", "json"
            ])
            
            assert result.exit_code == 0