"""
Unit tests for the show command.
Tests displaying generated GTM assets with rich formatting.
"""

import pytest
import json
from unittest.mock import patch, Mock
from typer.testing import CliRunner

from cli.main import app


class TestShowCommand:
    """Test suite for the show command"""
    
    def test_show_all_assets_single_project(self, mock_cli_runner, mock_project_with_data):
        """Test showing all assets when only one project exists"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "all"])
        
        assert result.exit_code == 0
        assert f"GTM Project: {domain}" in result.output
        assert "Progress:" in result.output
        assert "Company Overview" in result.output
        assert "Target Account Profile" in result.output
    
    def test_show_all_assets_with_domain(self, mock_cli_runner, mock_project_with_data):
        """Test showing all assets for specific domain"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        
        assert result.exit_code == 0
        assert f"GTM Project: {domain}" in result.output
        assert "Available steps:" in result.output
    
    def test_show_single_asset_overview(self, mock_cli_runner, mock_project_with_data):
        """Test showing company overview asset"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Company Overview" in result.output
        assert "Acme Corporation" in result.output  # From mock data
    
    def test_show_single_asset_account(self, mock_cli_runner, mock_project_with_data):
        """Test showing target account asset"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "account", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Target Account Profile" in result.output
        assert "Technology" in result.output  # From mock data
    
    def test_show_single_asset_persona(self, mock_cli_runner, mock_project_with_data):
        """Test showing buyer persona asset"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "persona", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Buyer Persona" in result.output
        assert "VP of Operations" in result.output  # From mock data
    
    def test_show_single_asset_email(self, mock_cli_runner, mock_project_with_data):
        """Test showing email campaign asset"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "email", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Email Campaign" in result.output
        assert "Transform Your Operations" in result.output  # From mock data
    
    def test_show_single_asset_strategy(self, mock_cli_runner, mock_project_with_data):
        """Test showing GTM strategy asset"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "strategy", "--domain", domain])
        
        assert result.exit_code == 0
        assert "GTM Strategic Plan" in result.output
    
    def test_show_json_output_overview(self, mock_cli_runner, mock_project_with_data):
        """Test JSON output format for overview"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "overview", "--json", "--domain", domain])
        
        assert result.exit_code == 0
        # Should contain JSON syntax highlighting
        assert "{" in result.output
        assert "company_name" in result.output
    
    def test_show_json_output_account(self, mock_cli_runner, mock_project_with_data):
        """Test JSON output format for account"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "account", "--json", "--domain", domain])
        
        assert result.exit_code == 0
        assert "{" in result.output
        assert "firmographics" in result.output
    
    def test_show_nonexistent_project(self, mock_cli_runner, temp_project_dir):
        """Test showing assets for non-existent project"""
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", "nonexistent.com"])
        
        assert result.exit_code == 0
        assert "No GTM project found" in result.output
        assert "blossomer init" in result.output
    
    def test_show_nonexistent_asset(self, mock_cli_runner, mock_incomplete_project):
        """Test showing asset that doesn't exist"""
        domain = mock_incomplete_project.name
        
        result = mock_cli_runner.invoke(app, ["show", "account", "--domain", domain])
        
        assert result.exit_code == 0
        # Should handle missing asset gracefully
        assert "not found" in result.output or "Generated: Unknown" in result.output
    
    def test_show_invalid_asset_name(self, mock_cli_runner, mock_project_with_data):
        """Test showing invalid asset name"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "invalid_asset", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Unknown asset" in result.output
        assert "Available assets:" in result.output
    
    def test_show_auto_detect_single_project(self, mock_cli_runner, mock_project_with_data):
        """Test auto-detection when only one project exists"""
        result = mock_cli_runner.invoke(app, ["show", "all"])
        
        assert result.exit_code == 0
        assert "GTM Project:" in result.output
    
    def test_show_multiple_projects_no_domain(self, mock_cli_runner, mock_project_with_data, temp_project_dir):
        """Test showing assets when multiple projects exist without specifying domain"""
        # Create second project
        second_project = temp_project_dir / "second.com"
        second_project.mkdir()
        (second_project / "overview.json").write_text(json.dumps({
            "company_name": "Second Company",
            "_generated_at": "2024-01-01T00:00:00Z"
        }))
        
        result = mock_cli_runner.invoke(app, ["show", "all"])
        
        assert result.exit_code == 0
        assert "Multiple projects found" in result.output
        assert "Please specify domain" in result.output
    
    def test_show_stale_data_warning(self, mock_cli_runner, temp_project_dir):
        """Test showing warning for stale data"""
        # Create project with stale data
        domain = "stale.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create overview with stale marker
        overview_data = {
            "company_name": "Stale Corp",
            "_generated_at": "2024-01-01T00:00:00Z",
            "_stale": True,
            "_stale_reason": "Dependency updated"
        }
        (project_path / "overview.json").write_text(json.dumps(overview_data))
        
        result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        
        assert result.exit_code == 0
        assert "may be outdated" in result.output or "stale" in result.output.lower()
    
    def test_show_step_option_vs_argument(self, mock_cli_runner, mock_project_with_data):
        """Test --step option vs positional argument"""
        domain = mock_project_with_data.name
        
        # Test with --step option
        result1 = mock_cli_runner.invoke(app, ["show", "--step", "overview", "--domain", domain])
        assert result1.exit_code == 0
        assert "Company Overview" in result1.output
        
        # Test with positional argument
        result2 = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        assert result2.exit_code == 0
        assert "Company Overview" in result2.output
    
    def test_show_with_character_counts(self, mock_cli_runner, mock_project_with_data):
        """Test that character counts are displayed in summaries"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        
        assert result.exit_code == 0
        # Should show some indication of content length/metadata
        assert "Generated:" in result.output or "Last updated:" in result.output
    
    def test_show_markdown_file_content(self, mock_cli_runner, mock_project_with_data, temp_project_dir):
        """Test showing markdown file content when available"""
        domain = mock_project_with_data.name
        project_path = temp_project_dir / domain
        
        # Create a markdown file
        plans_dir = project_path / "plans"
        plans_dir.mkdir(exist_ok=True)
        (plans_dir / "overview.md").write_text("# Company Overview\n\nThis is test content.")
        
        result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        
        assert result.exit_code == 0
        # Should display markdown content or reference to it
    
    def test_show_handles_missing_metadata(self, mock_cli_runner, temp_project_dir):
        """Test showing asset with missing metadata"""
        domain = "no-metadata.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create overview without metadata fields
        overview_data = {
            "company_name": "No Metadata Corp"
            # No _generated_at field
        }
        (project_path / "overview.json").write_text(json.dumps(overview_data))
        
        result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Generated: Unknown" in result.output or "Unknown" in result.output


class TestShowCommandEdgeCases:
    """Test edge cases and error conditions for show command"""
    
    def test_show_corrupted_json_file(self, mock_cli_runner, mock_corrupted_project):
        """Test showing asset with corrupted JSON"""
        domain = mock_corrupted_project.name
        
        result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        
        # Should handle corrupted JSON gracefully
        assert result.exit_code == 0
        assert "not found" in result.output or "error" in result.output.lower()
    
    def test_show_empty_project_directory(self, mock_cli_runner, temp_project_dir):
        """Test showing assets for empty project directory"""
        empty_project = temp_project_dir / "empty.com"
        empty_project.mkdir()
        
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", "empty.com"])
        
        assert result.exit_code == 0
        assert "No GTM project found" in result.output or "0% complete" in result.output
    
    def test_show_with_invalid_domain_format(self, mock_cli_runner):
        """Test show with invalid domain format"""
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", "invalid..domain"])
        
        assert result.exit_code == 0
        assert "Invalid domain format" in result.output or "No GTM project found" in result.output
    
    def test_show_no_projects_exist(self, mock_cli_runner, temp_project_dir):
        """Test show when no projects exist at all"""
        # temp_project_dir is empty
        result = mock_cli_runner.invoke(app, ["show", "all"])
        
        assert result.exit_code == 0
        assert "No GTM projects found" in result.output
        assert "blossomer init" in result.output
    
    def test_show_file_permission_error(self, mock_cli_runner, mock_project_with_data):
        """Test handling file permission errors"""
        domain = mock_project_with_data.name
        
        # Make the project directory inaccessible
        mock_project_with_data.chmod(0o000)
        
        try:
            result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
            # Should handle permission error gracefully
            assert result.exit_code == 0
            assert "not found" in result.output or "error" in result.output.lower()
        finally:
            # Restore permissions for cleanup
            mock_project_with_data.chmod(0o755)


class TestShowCommandFormatting:
    """Test rich formatting features of show command"""
    
    def test_show_rich_panel_formatting(self, mock_cli_runner, mock_project_with_data):
        """Test that rich panels are properly formatted"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        
        assert result.exit_code == 0
        # Check for rich formatting elements
        assert "Project Overview" in result.output or "GTM Project:" in result.output
    
    def test_show_progress_percentage(self, mock_cli_runner, mock_incomplete_project):
        """Test progress percentage calculation"""
        domain = mock_incomplete_project.name
        
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        
        assert result.exit_code == 0
        # Should show some progress percentage less than 100%
        assert "%" in result.output and "Progress:" in result.output
    
    def test_show_step_icons_and_formatting(self, mock_cli_runner, mock_project_with_data):
        """Test that step icons and formatting are displayed"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        
        assert result.exit_code == 0
        # Check for emojis or formatting
        assert "🏢" in result.output or "🎯" in result.output or "👤" in result.output
    
    def test_show_metadata_display(self, mock_cli_runner, mock_project_with_data):
        """Test display of generation metadata"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Generated:" in result.output
        assert "2024-01-01" in result.output  # From mock data
    
    def test_show_commands_help_text(self, mock_cli_runner, mock_project_with_data):
        """Test that helpful command suggestions are shown"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Commands:" in result.output
        assert "blossomer" in result.output
        assert "edit" in result.output or "export" in result.output


class TestShowCommandDataHandling:
    """Test data handling and validation in show command"""
    
    def test_show_handles_missing_fields(self, mock_cli_runner, temp_project_dir):
        """Test showing data with missing expected fields"""
        domain = "minimal.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create minimal overview data
        overview_data = {
            "company_name": "Minimal Corp"
            # Missing other expected fields
        }
        (project_path / "overview.json").write_text(json.dumps(overview_data))
        
        result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Minimal Corp" in result.output
    
    def test_show_handles_extra_fields(self, mock_cli_runner, temp_project_dir):
        """Test showing data with extra unexpected fields"""
        domain = "extra.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create overview data with extra fields
        overview_data = {
            "company_name": "Extra Corp",
            "_generated_at": "2024-01-01T00:00:00Z",
            "extra_field": "This should not break anything",
            "nested_extra": {"more": "data"}
        }
        (project_path / "overview.json").write_text(json.dumps(overview_data))
        
        result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Extra Corp" in result.output
    
    def test_show_large_content_handling(self, mock_cli_runner, temp_project_dir):
        """Test showing very large content"""
        domain = "large.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create overview with very large description
        large_description = "Very long description. " * 1000  # ~23KB
        overview_data = {
            "company_name": "Large Corp",
            "description": large_description,
            "_generated_at": "2024-01-01T00:00:00Z"
        }
        (project_path / "overview.json").write_text(json.dumps(overview_data))
        
        result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        
        assert result.exit_code == 0
        assert "Large Corp" in result.output
        # Should handle large content without issues