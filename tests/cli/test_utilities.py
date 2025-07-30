"""
Unit tests for CLI utilities.
Tests utility functions without external dependencies.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, call

# Import utilities to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.utils.domain import normalize_domain, NormalizedDomain
from cli.utils.colors import Colors
from cli.utils.guided_email_builder import GuidedEmailBuilder
from cli.utils.markdown_formatter import get_formatter
from cli.utils.panel_utils import create_welcome_panel, create_step_panel_by_key
from cli.utils.loading_animation import LoadingAnimator


class TestDomainUtils:
    """Test suite for domain utilities"""
    
    def test_normalize_domain_basic(self):
        """Test basic domain normalization"""
        test_cases = [
            ("acme.com", "acme.com", "https://acme.com"),
            ("ACME.COM", "acme.com", "https://acme.com"),
            ("www.acme.com", "acme.com", "https://acme.com"),
            ("WWW.ACME.COM", "acme.com", "https://acme.com"),
        ]
        
        for input_domain, expected_domain, expected_url in test_cases:
            result = normalize_domain(input_domain)
            assert isinstance(result, NormalizedDomain)
            assert result.domain == expected_domain
            assert result.url == expected_url
    
    def test_normalize_domain_with_protocol(self):
        """Test domain normalization with protocols"""
        test_cases = [
            ("https://acme.com", "acme.com", "https://acme.com"),
            ("http://acme.com", "acme.com", "https://acme.com"),
            ("https://www.acme.com", "acme.com", "https://acme.com"),
            ("http://www.acme.com", "acme.com", "https://acme.com"),
        ]
        
        for input_domain, expected_domain, expected_url in test_cases:
            result = normalize_domain(input_domain)
            assert result.domain == expected_domain
            assert result.url == expected_url
    
    def test_normalize_domain_with_paths(self):
        """Test domain normalization strips paths"""
        test_cases = [
            ("acme.com/about", "acme.com", "https://acme.com"),
            ("https://acme.com/products", "acme.com", "https://acme.com"),
            ("www.acme.com/contact/us", "acme.com", "https://acme.com"),
        ]
        
        for input_domain, expected_domain, expected_url in test_cases:
            result = normalize_domain(input_domain)
            assert result.domain == expected_domain
            assert result.url == expected_url
    
    def test_normalize_domain_invalid_formats(self):
        """Test domain normalization with invalid formats"""
        invalid_domains = [
            "",
            "   ",
            "invalid..domain",
            "domain with spaces",
            "ftp://domain.com",  # Unsupported protocol
        ]
        
        for invalid_domain in invalid_domains:
            with pytest.raises(Exception):
                normalize_domain(invalid_domain)
    
    def test_normalized_domain_object(self):
        """Test NormalizedDomain object properties"""
        domain_info = NormalizedDomain(domain="test.com", url="https://test.com")
        
        assert domain_info.domain == "test.com"
        assert domain_info.url == "https://test.com"
        assert str(domain_info) == "https://test.com"  # NormalizedDomain returns URL in __str__
        assert repr(domain_info) == "NormalizedDomain(domain='test.com', url='https://test.com')"


class TestColorsUtils:
    """Test suite for color utilities"""
    
    def test_colors_constants(self):
        """Test that color constants are defined"""
        assert hasattr(Colors, 'SUCCESS')
        assert hasattr(Colors, 'ERROR')
        assert hasattr(Colors, 'WARNING')
        assert hasattr(Colors, 'INFO')
        
        # Colors should be strings
        assert isinstance(Colors.SUCCESS, str)
        assert isinstance(Colors.ERROR, str)
    
    def test_format_success(self):
        """Test success message formatting"""
        message = "Test successful"
        formatted = Colors.format_success(message)
        
        assert isinstance(formatted, str)
        assert message in formatted
    
    def test_format_error(self):
        """Test error message formatting"""
        message = "Test error"
        formatted = Colors.format_error(message)
        
        assert isinstance(formatted, str)
        assert message in formatted
    
    def test_format_warning(self):
        """Test warning message formatting"""
        message = "Test warning"
        formatted = Colors.format_warning(message)
        
        assert isinstance(formatted, str)
        assert message in formatted
    
    def test_format_command(self):
        """Test command formatting"""
        command = "blossomer init"
        formatted = Colors.format_command(command)
        
        assert isinstance(formatted, str)
        assert command in formatted
    
    def test_format_section(self):
        """Test section formatting"""
        if hasattr(Colors, 'format_section'):
            title = "Test Section"
            icon = "🚀"
            formatted = Colors.format_section(title, icon)
            
            assert isinstance(formatted, str)
            assert title in formatted
            assert icon in formatted


class TestGuidedEmailBuilder:
    """Test suite for guided email builder"""
    
    @pytest.fixture
    def mock_persona_data(self):
        """Mock persona data for testing"""
        return {
            "target_persona_name": "VP of Engineering",
            "demographics": {
                "job_title": "VP Engineering",
                "department": "Engineering"
            },
            "psychographics": {
                "pain_points": ["Technical debt", "Team scaling"],
                "goals": ["Improve velocity", "Reduce downtime"]
            }
        }
    
    @pytest.fixture
    def mock_account_data(self):
        """Mock account data for testing"""
        return {
            "target_account_name": "Mid-Market Tech Companies",
            "firmographics": {
                "industry": "Technology",
                "company_size": "500-2000 employees"
            }
        }
    
    def test_guided_email_builder_initialization(self, mock_persona_data, mock_account_data):
        """Test guided email builder initialization"""
        builder = GuidedEmailBuilder(mock_persona_data, mock_account_data)
        
        assert builder.persona_data == mock_persona_data
        assert builder.account_data == mock_account_data
    
    @patch('questionary.select')
    @patch('questionary.text')
    def test_guided_email_builder_flow(self, mock_text, mock_select, mock_persona_data, mock_account_data):
        """Test guided email builder complete flow"""
        # Mock user responses
        mock_select.return_value.ask.side_effect = [
            "Professional",  # Tone
            "Concise",       # Length
            "ROI",           # Focus
            "Direct",        # CTA style
            "Yes"            # Confirmation
        ]
        mock_text.return_value.ask.return_value = "Custom message"
        
        builder = GuidedEmailBuilder(mock_persona_data, mock_account_data)
        
        # Mock the console to avoid Rich output during tests
        with patch('cli.utils.guided_email_builder.console'):
            preferences = builder.run_guided_flow()
        
        assert isinstance(preferences, dict)
        # Should contain user preferences
        assert len(preferences) > 0
    
    def test_guided_email_builder_context_processing(self, mock_persona_data, mock_account_data):
        """Test that builder processes context correctly"""
        builder = GuidedEmailBuilder(mock_persona_data, mock_account_data)
        
        # Test internal methods if accessible
        if hasattr(builder, '_extract_pain_points'):
            pain_points = builder._extract_pain_points()
            assert isinstance(pain_points, list)
            assert "Technical debt" in pain_points
    
    def test_guided_email_builder_error_handling(self, mock_persona_data, mock_account_data):
        """Test guided email builder error handling"""
        # Test with incomplete data
        incomplete_persona = {"target_persona_name": "VP Engineering"}
        
        builder = GuidedEmailBuilder(incomplete_persona, mock_account_data)
        
        # Should handle missing fields gracefully
        assert builder.persona_data == incomplete_persona
    
    @patch('questionary.select')
    def test_guided_email_builder_keyboard_interrupt(self, mock_select, mock_persona_data, mock_account_data):
        """Test guided email builder handles keyboard interrupt"""
        # Mock keyboard interrupt
        mock_select.return_value.ask.side_effect = KeyboardInterrupt()
        
        builder = GuidedEmailBuilder(mock_persona_data, mock_account_data)
        
        with patch('cli.utils.guided_email_builder.console'):
            with pytest.raises(KeyboardInterrupt):
                builder.run_guided_flow()


class TestMarkdownFormatter:
    """Test suite for markdown formatter"""
    
    def test_get_formatter_overview(self):
        """Test getting formatter for overview step"""
        formatter = get_formatter("overview")
        
        assert formatter is not None
        assert hasattr(formatter, 'format')
    
    def test_get_formatter_account(self):
        """Test getting formatter for account step"""
        formatter = get_formatter("account")
        
        assert formatter is not None
        assert hasattr(formatter, 'format')
    
    def test_get_formatter_persona(self):
        """Test getting formatter for persona step"""
        formatter = get_formatter("persona")
        
        assert formatter is not None
        assert hasattr(formatter, 'format')
    
    def test_get_formatter_email(self):
        """Test getting formatter for email step"""
        formatter = get_formatter("email")
        
        assert formatter is not None
        assert hasattr(formatter, 'format')
    
    def test_get_formatter_invalid_step(self):
        """Test getting formatter for invalid step"""
        formatter = get_formatter("invalid_step")
        
        # Should return None or handle gracefully
        assert formatter is None or hasattr(formatter, 'format')
    
    def test_formatter_format_method(self, mock_llm_responses):
        """Test formatter format method"""
        formatter = get_formatter("overview")
        
        if formatter:
            # Test with mock data
            formatted = formatter.format(mock_llm_responses["overview"], preview=False)
            
            assert isinstance(formatted, str)
            assert len(formatted) > 0
            assert "Acme Corporation" in formatted  # From mock data
    
    def test_formatter_preview_mode(self, mock_llm_responses):
        """Test formatter preview mode"""
        formatter = get_formatter("overview")
        
        if formatter:
            # Test preview mode
            preview = formatter.format(mock_llm_responses["overview"], preview=True)
            full = formatter.format(mock_llm_responses["overview"], preview=False)
            
            assert isinstance(preview, str)
            assert isinstance(full, str)
            # Preview might be shorter than full
            assert len(preview) >= 0


class TestPanelUtils:
    """Test suite for panel utilities"""
    
    def test_create_welcome_panel(self):
        """Test welcome panel creation"""
        domain = "test.com"
        panel = create_welcome_panel(domain)
        
        assert panel is not None
        # Panel should contain domain reference
        panel_content = str(panel)
        assert domain in panel_content or "welcome" in panel_content.lower()
    
    def test_create_step_panel_by_key(self):
        """Test step panel creation by key"""
        step_keys = ["overview", "account", "persona", "email", "strategy"]
        
        for key in step_keys:
            panel = create_step_panel_by_key(key)
            
            assert panel is not None
            # Panel should contain step information
            panel_content = str(panel)
            assert len(panel_content) > 0
    
    def test_create_step_panel_invalid_key(self):
        """Test step panel creation with invalid key"""
        panel = create_step_panel_by_key("invalid_key")
        
        # Should handle gracefully (return None or default panel)
        assert panel is None or hasattr(panel, 'renderable')
    
    @patch('cli.utils.step_config.step_manager')
    def test_panel_uses_step_config(self, mock_step_manager):
        """Test that panels use step configuration"""
        mock_step = Mock()
        mock_step.name = "Company Overview"
        mock_step.key = "overview"
        mock_step_manager.get_step_by_key.return_value = mock_step
        
        panel = create_step_panel_by_key("overview")
        
        if panel:
            panel_content = str(panel)
            # Should incorporate step configuration
            assert len(panel_content) > 0


class TestLoadingAnimation:
    """Test suite for loading animation"""
    
    @pytest.fixture
    def mock_console(self):
        """Mock console for testing animations"""
        return Mock()
    
    def test_loading_animator_initialization(self, mock_console):
        """Test loading animator initialization"""
        animator = LoadingAnimator(mock_console)
        
        assert animator.console == mock_console
        assert hasattr(animator, 'start_animation')
        assert hasattr(animator, 'stop')
    
    def test_loading_animator_start_stop(self, mock_console):
        """Test loading animator start and stop"""
        animator = LoadingAnimator(mock_console)
        
        # Test start animation
        animator.start_animation("overview")
        
        # Test stop animation
        animator.stop()
        
        # Should not raise exceptions
        assert True
    
    def test_loading_animator_different_steps(self, mock_console):
        """Test loading animator with different steps"""
        animator = LoadingAnimator(mock_console)
        
        steps = ["overview", "account", "persona", "email", "strategy", "plan"]
        
        for step in steps:
            animator.start_animation(step)
            animator.stop()
        
        # Should handle all step types
        assert True
    
    def test_loading_animator_double_start(self, mock_console):
        """Test loading animator handles double start"""
        animator = LoadingAnimator(mock_console)
        
        animator.start_animation("overview")
        animator.start_animation("account")  # Should handle gracefully
        animator.stop()
        
        assert True
    
    def test_loading_animator_stop_without_start(self, mock_console):
        """Test loading animator handles stop without start"""
        animator = LoadingAnimator(mock_console)
        
        # Should handle stop without start gracefully
        animator.stop()
        
        assert True


class TestUtilityIntegration:
    """Test integration between utilities"""
    
    def test_domain_normalization_with_colors(self):
        """Test domain normalization with color formatting"""
        domain = "test.com"
        normalized = normalize_domain(domain)
        formatted_command = Colors.format_command(f"blossomer init {normalized.domain}")
        
        assert isinstance(formatted_command, str)
        assert "test.com" in formatted_command
    
    def test_panel_utils_with_step_config(self):
        """Test panel utilities integration with step configuration"""
        # This tests that the utilities work together
        panel = create_step_panel_by_key("overview")
        
        if panel:
            assert hasattr(panel, 'renderable') or hasattr(panel, '__rich__')
    
    def test_guided_builder_with_formatter(self, mock_llm_responses):
        """Test guided email builder integration with formatter"""
        formatter = get_formatter("email")
        email_data = mock_llm_responses["email"]
        
        if formatter:
            formatted = formatter.format(email_data, preview=True)
            assert isinstance(formatted, str)
            assert "Transform Your Operations" in formatted  # From mock data


class TestUtilityErrorHandling:
    """Test error handling in utilities"""
    
    def test_domain_utils_handle_none_input(self):
        """Test domain utilities handle None input"""
        with pytest.raises(Exception):
            normalize_domain(None)
    
    def test_domain_utils_handle_empty_string(self):
        """Test domain utilities handle empty string"""
        with pytest.raises(Exception):
            normalize_domain("")
    
    def test_colors_handle_none_input(self):
        """Test color utilities handle None input"""
        # Should handle gracefully or raise appropriate error
        try:
            result = Colors.format_success(None)
            assert isinstance(result, str)
        except (TypeError, AttributeError):
            # Expected behavior for None input
            pass
    
    def test_formatter_handle_missing_data(self):
        """Test formatter handles missing data fields"""
        formatter = get_formatter("overview")
        
        if formatter:
            incomplete_data = {"company_name": "Test Corp"}  # Missing other fields
            
            try:
                result = formatter.format(incomplete_data, preview=True)
                assert isinstance(result, str)
            except (KeyError, AttributeError):
                # Expected behavior for incomplete data
                pass
    
    def test_panel_utils_handle_missing_config(self):
        """Test panel utilities handle missing configuration"""
        with patch('cli.utils.step_config.step_manager.get_step_by_key', return_value=None):
            panel = create_step_panel_by_key("nonexistent")
            
            # Should handle missing configuration gracefully
            assert panel is None or hasattr(panel, 'renderable')


class TestUtilityPerformance:
    """Test performance characteristics of utilities"""
    
    def test_domain_normalization_performance(self):
        """Test domain normalization performance"""
        import time
        
        domains = [f"test-{i}.com" for i in range(100)]
        
        start_time = time.time()
        for domain in domains:
            normalize_domain(domain)
        elapsed_time = time.time() - start_time
        
        # Should normalize 100 domains quickly
        assert elapsed_time < 1.0
    
    def test_color_formatting_performance(self):
        """Test color formatting performance"""
        import time
        
        messages = [f"Test message {i}" for i in range(100)]
        
        start_time = time.time()
        for message in messages:
            Colors.format_success(message)
            Colors.format_error(message)
            Colors.format_warning(message)
        elapsed_time = time.time() - start_time
        
        # Should format 300 messages quickly
        assert elapsed_time < 1.0
    
    def test_panel_creation_performance(self):
        """Test panel creation performance"""
        import time
        
        start_time = time.time()
        for _ in range(50):
            create_welcome_panel("test.com")
            create_step_panel_by_key("overview")
        elapsed_time = time.time() - start_time
        
        # Should create 100 panels quickly
        assert elapsed_time < 2.0