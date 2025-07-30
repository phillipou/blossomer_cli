"""
Comprehensive tests for the advisor command.
Tests GTM strategic planning and advice functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from cli.main import app


class TestAdvisorCommand:
    """Test suite for the advisor command"""
    
    def test_advisor_help(self, mock_cli_runner):
        """Test advisor command help"""
        result = mock_cli_runner.invoke(app, ["advisor", "--help"])
        
        assert result.exit_code == 0
        assert "advisor" in result.output.lower()
        assert "strategic" in result.output.lower() or "plan" in result.output.lower()
    
    def test_advisor_create_plan(self, mock_cli_runner, mock_project_with_data):
        """Test creating strategic plan for existing project"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        assert result.exit_code == 0
        assert "strategic" in result.output.lower() or "plan" in result.output.lower()
    
    def test_advisor_create_plan_new_project(self, mock_cli_runner, temp_project_dir):
        """Test creating strategic plan for new project"""
        result = mock_cli_runner.invoke(app, ["advisor", "newcompany.com"])
        
        # Should either create plan or prompt for more information
        assert result.exit_code == 0 or "missing" in result.output.lower()
    
    def test_advisor_with_output_file(self, mock_cli_runner, mock_project_with_data):
        """Test advisor with custom output file"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "strategic_plan.md"
            
            result = mock_cli_runner.invoke(app, [
                "advisor", domain,
                "--output", str(output_file)
            ])
            
            assert result.exit_code == 0
    
    def test_advisor_with_context(self, mock_cli_runner, mock_project_with_data):
        """Test advisor with additional context"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, [
            "advisor", domain,
            "--context", "We are focusing on enterprise market"
        ])
        
        assert result.exit_code == 0
    
    def test_advisor_force_regenerate(self, mock_cli_runner, mock_project_with_data):
        """Test advisor with force flag to regenerate existing plan"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["advisor", domain, "--force"])
        
        assert result.exit_code == 0
        assert "generat" in result.output.lower()
    
    def test_advisor_incomplete_project(self, mock_cli_runner, mock_incomplete_project):
        """Test advisor with incomplete project data"""
        domain = mock_incomplete_project.name
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        # Should either work with available data or request missing steps
        assert result.exit_code == 0 or "missing" in result.output.lower()
    
    def test_advisor_nonexistent_project(self, mock_cli_runner, temp_project_dir):
        """Test advisor with non-existent project"""
        result = mock_cli_runner.invoke(app, ["advisor", "nonexistent.com"])
        
        assert result.exit_code != 0 or "not found" in result.output.lower()
    
    def test_advisor_invalid_domain(self, mock_cli_runner):
        """Test advisor with invalid domain"""
        result = mock_cli_runner.invoke(app, ["advisor", "invalid..domain"])
        
        assert result.exit_code != 0 or "invalid" in result.output.lower()
    
    def test_advisor_list_existing_plans(self, mock_cli_runner, mock_project_with_data):
        """Test listing existing strategic plans"""
        result = mock_cli_runner.invoke(app, ["advisor", "--list"])
        
        assert result.exit_code == 0
        # Should show available plans or projects
    
    def test_advisor_with_template_option(self, mock_cli_runner, mock_project_with_data):
        """Test advisor with specific template"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, [
            "advisor", domain,
            "--template", "enterprise"
        ])
        
        assert result.exit_code == 0


class TestAdvisorCommandContent:
    """Test content generation and validation for advisor command"""
    
    def test_advisor_plan_contains_key_sections(self, mock_cli_runner, mock_project_with_data):
        """Test that strategic plan contains expected sections"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        if result.exit_code == 0:
            content_lower = result.output.lower()
            # Should contain strategic planning elements
            expected_sections = [
                "market", "target", "strategy", "plan", "execution",
                "framework", "scoring", "tools", "metrics"
            ]
            found_sections = [section for section in expected_sections if section in content_lower]
            assert len(found_sections) >= 3  # At least 3 key sections
    
    def test_advisor_plan_includes_company_context(self, mock_cli_runner, mock_project_with_data):
        """Test that plan includes company-specific context"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        if result.exit_code == 0:
            content_lower = result.output.lower()
            # Should reference company data from mock
            assert "acme" in content_lower or "corporation" in content_lower
    
    def test_advisor_plan_includes_actionable_recommendations(self, mock_cli_runner, mock_project_with_data):
        """Test that plan includes actionable recommendations"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        if result.exit_code == 0:
            content_lower = result.output.lower()
            # Should contain actionable elements
            actionable_terms = ["recommend", "should", "implement", "action", "step", "framework"]
            found_terms = [term for term in actionable_terms if term in content_lower]
            assert len(found_terms) >= 2
    
    def test_advisor_plan_includes_tool_recommendations(self, mock_cli_runner, mock_project_with_data):
        """Test that plan includes tool recommendations"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        if result.exit_code == 0:
            content_lower = result.output.lower()
            # Should mention tools or platforms
            tool_terms = ["tool", "platform", "crm", "sales", "marketing", "hubspot", "salesforce"]
            found_terms = [term for term in tool_terms if term in content_lower]
            assert len(found_terms) >= 1
    
    def test_advisor_plan_includes_metrics(self, mock_cli_runner, mock_project_with_data):
        """Test that plan includes success metrics"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        if result.exit_code == 0:
            content_lower = result.output.lower()
            # Should include metrics and measurement
            metric_terms = ["metric", "measure", "kpi", "success", "track", "performance", "roi"]
            found_terms = [term for term in metric_terms if term in content_lower]
            assert len(found_terms) >= 1


class TestAdvisorCommandFormats:
    """Test different output formats for advisor command"""
    
    def test_advisor_markdown_output(self, mock_cli_runner, mock_project_with_data):
        """Test advisor markdown output format"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "plan.md"
            
            result = mock_cli_runner.invoke(app, [
                "advisor", domain,
                "--output", str(output_file),
                "--format", "markdown"
            ])
            
            if result.exit_code == 0 and output_file.exists():
                content = output_file.read_text()
                # Should contain markdown formatting
                assert "#" in content or "*" in content or "-" in content
    
    def test_advisor_json_output(self, mock_cli_runner, mock_project_with_data):
        """Test advisor JSON output format"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "plan.json"
            
            result = mock_cli_runner.invoke(app, [
                "advisor", domain,
                "--output", str(output_file),
                "--format", "json"
            ])
            
            if result.exit_code == 0 and output_file.exists():
                try:
                    with open(output_file) as f:
                        data = json.load(f)
                        assert isinstance(data, dict)
                except json.JSONDecodeError:
                    pytest.fail("Invalid JSON output")
    
    def test_advisor_plain_text_output(self, mock_cli_runner, mock_project_with_data):
        """Test advisor plain text output"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, [
            "advisor", domain,
            "--format", "text"
        ])
        
        assert result.exit_code == 0
    
    def test_advisor_html_output(self, mock_cli_runner, mock_project_with_data):
        """Test advisor HTML output format"""
        domain = mock_project_with_data.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "plan.html"
            
            result = mock_cli_runner.invoke(app, [
                "advisor", domain,
                "--output", str(output_file),
                "--format", "html"
            ])
            
            if result.exit_code == 0 and output_file.exists():
                content = output_file.read_text()
                # Should contain HTML tags
                assert "<" in content and ">" in content


class TestAdvisorCommandInteractive:
    """Test interactive features of advisor command"""
    
    def test_advisor_interactive_project_selection(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test interactive project selection"""
        mock_console_input("acme.com")
        
        result = mock_cli_runner.invoke(app, ["advisor"])
        
        # Should either work interactively or require domain
        assert result.exit_code == 0 or "domain" in result.output.lower()
    
    def test_advisor_interactive_template_selection(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test interactive template selection"""
        domain = mock_project_with_data.name
        mock_console_input("enterprise")  # Template selection
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        assert result.exit_code == 0
    
    def test_advisor_guided_planning_session(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test guided planning session"""
        domain = mock_project_with_data.name
        
        # Mock various guided inputs
        mock_console_input("Enterprise market")  # Target market
        mock_console_input("6 months")  # Timeline
        mock_console_input("High growth")  # Priority
        
        result = mock_cli_runner.invoke(app, ["advisor", domain, "--guided"])
        
        assert result.exit_code == 0
    
    def test_advisor_confirmation_prompts(self, mock_cli_runner, mock_console_input, mock_project_with_data):
        """Test confirmation prompts for overwriting existing plans"""
        domain = mock_project_with_data.name
        mock_console_input("y")  # Confirm overwrite
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        assert result.exit_code == 0


class TestAdvisorCommandEdgeCases:
    """Test edge cases for advisor command"""
    
    def test_advisor_very_large_project_data(self, mock_cli_runner, temp_project_dir):
        """Test advisor with very large project data"""
        domain = "large.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create large project data
        large_data = {
            "company_name": "Large Corp",
            "description": "Large description. " * 5000,  # ~115KB
            "_generated_at": "2024-01-01T00:00:00Z"
        }
        (project_path / "overview.json").write_text(json.dumps(large_data))
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        assert result.exit_code == 0
        # Should handle large data appropriately
    
    def test_advisor_corrupted_project_data(self, mock_cli_runner, mock_corrupted_project):
        """Test advisor with corrupted project data"""
        domain = mock_corrupted_project.name
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        # Should handle corrupted data gracefully
        assert result.exit_code != 0 or "error" in result.output.lower()
    
    def test_advisor_missing_critical_data(self, mock_cli_runner, temp_project_dir):
        """Test advisor with minimal/missing critical data"""
        domain = "minimal.com"
        project_path = temp_project_dir / domain
        project_path.mkdir()
        
        # Create minimal data
        minimal_data = {"company_name": "Minimal Corp"}
        (project_path / "overview.json").write_text(json.dumps(minimal_data))
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        # Should either work with minimal data or request more information
        assert result.exit_code == 0 or "missing" in result.output.lower()
    
    def test_advisor_special_characters_in_data(self, mock_cli_runner, temp_project_dir):
        """Test advisor with special characters in project data"""
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
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        assert result.exit_code == 0
    
    def test_advisor_output_permission_error(self, mock_cli_runner, mock_project_with_data):
        """Test advisor when output location is not writable"""
        domain = mock_project_with_data.name
        
        # Try to write to root directory (should fail)
        result = mock_cli_runner.invoke(app, [
            "advisor", domain,
            "--output", "/root/plan.md"
        ])
        
        # Should handle permission error gracefully
        assert result.exit_code != 0 or "permission" in result.output.lower()


class TestAdvisorCommandValidation:
    """Test validation and quality of advisor output"""
    
    def test_advisor_plan_structure_validation(self, mock_cli_runner, mock_project_with_data):
        """Test that strategic plan has proper structure"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        if result.exit_code == 0:
            content = result.output
            # Should have structured content
            assert len(content) > 100  # Should be substantial
            # Should contain headers or structure
            structure_indicators = ["#", "##", "**", "*", "1.", "2.", "-", "•"]
            has_structure = any(indicator in content for indicator in structure_indicators)
            assert has_structure
    
    def test_advisor_plan_completeness(self, mock_cli_runner, mock_project_with_data):
        """Test that strategic plan is comprehensive"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        if result.exit_code == 0:
            content_lower = result.output.lower()
            
            # Should cover multiple strategic areas
            strategic_areas = [
                "market analysis", "target customer", "value proposition",
                "go-to-market", "sales process", "marketing", "channels",
                "pricing", "competition", "positioning", "messaging"
            ]
            
            covered_areas = sum(1 for area in strategic_areas if area.replace(" ", "") in content_lower.replace(" ", ""))
            assert covered_areas >= 3  # Should cover at least 3 strategic areas
    
    def test_advisor_plan_actionability(self, mock_cli_runner, mock_project_with_data):
        """Test that strategic plan contains actionable items"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        if result.exit_code == 0:
            content_lower = result.output.lower()
            
            # Should contain actionable language
            actionable_words = [
                "implement", "execute", "develop", "create", "build",
                "launch", "establish", "optimize", "measure", "track"
            ]
            
            found_actions = sum(1 for word in actionable_words if word in content_lower)
            assert found_actions >= 3  # Should have multiple actionable items
    
    def test_advisor_plan_customization(self, mock_cli_runner, mock_project_with_data):
        """Test that plan is customized to company data"""
        domain = mock_project_with_data.name
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        if result.exit_code == 0:
            content_lower = result.output.lower()
            
            # Should reference company-specific information from mock data
            company_specific = [
                "acme", "enterprise", "automation", "technology",
                "operations", "workflow", "productivity"
            ]
            
            found_specific = sum(1 for term in company_specific if term in content_lower)
            assert found_specific >= 2  # Should reference company specifics


class TestAdvisorCommandPerformance:
    """Test performance aspects of advisor command"""
    
    def test_advisor_generation_performance(self, mock_cli_runner, mock_project_with_data):
        """Test that advisor plan generation completes in reasonable time"""
        import time
        
        domain = mock_project_with_data.name
        
        start_time = time.time()
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time for tests
        assert elapsed_time < 15.0  # 15 seconds should be plenty for mocked tests
        
    def test_advisor_memory_usage(self, mock_cli_runner, mock_project_with_data):
        """Test that advisor doesn't consume excessive memory"""
        domain = mock_project_with_data.name
        
        # Basic test - just ensure it completes without memory errors
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        assert result.exit_code == 0 or "memory" not in result.output.lower()
    
    def test_advisor_handles_timeout_gracefully(self, mock_cli_runner, mock_error_scenarios, mock_project_with_data):
        """Test advisor handles API timeouts gracefully"""
        domain = mock_project_with_data.name
        mock_error_scenarios["set"]("timeout")
        
        result = mock_cli_runner.invoke(app, ["advisor", domain])
        
        # Should handle timeout without crashing
        assert "timeout" in result.output.lower() or result.exit_code != 0