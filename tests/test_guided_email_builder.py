#!/usr/bin/env python3
"""
Integration tests for the guided email builder (4-step interactive flow).
Tests the complete email generation pipeline with user selections.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.utils.guided_email_builder import GuidedEmailBuilder
from cli.services.project_storage import project_storage


class TestGuidedEmailBuilder:
    """Test suite for the guided email builder"""
    
    @pytest.fixture
    def test_domain(self):
        """Provide a test domain and clean up after tests"""
        domain = "guided-email-test.com"
        yield domain
        # Cleanup
        if project_storage.project_exists(domain):
            project_storage.delete_project(domain)
    
    @pytest.fixture
    def sample_persona_data(self):
        """Sample persona data for testing"""
        return {
            "title": "VP of Engineering",
            "use_cases": [
                {
                    "use_case": "Automated testing workflows",
                    "pain_point": "Manual testing bottlenecks", 
                    "capability": "AI-powered test generation",
                    "desired_outcome": "Faster release cycles"
                },
                {
                    "use_case": "Code quality monitoring",
                    "pain_point": "Inconsistent code reviews",
                    "capability": "Automated code analysis", 
                    "desired_outcome": "Higher code quality"
                }
            ],
            "buying_signals": [
                {
                    "title": "Recent Series B funding",
                    "description": "Growth stage companies with fresh capital"
                },
                {
                    "title": "Hiring spree activity",
                    "description": "Rapidly expanding engineering teams"
                }
            ]
        }
    
    @pytest.fixture
    def guided_builder(self, test_domain, sample_persona_data):
        """Create a guided email builder with test data"""
        # Create project and save persona data
        project_storage.create_project(test_domain)
        project_storage.save_step_data(test_domain, "persona", sample_persona_data)
        
        return GuidedEmailBuilder(test_domain)

    def test_guided_builder_initialization(self, guided_builder, sample_persona_data):
        """Test guided email builder initialization"""
        print("🚀 Testing guided email builder initialization")
        
        assert guided_builder.domain is not None, "Domain should be set"
        assert guided_builder.persona_data is not None, "Persona data should be loaded"
        assert len(guided_builder.persona_data["use_cases"]) == 2, "Should load use cases"
        assert len(guided_builder.persona_data["buying_signals"]) == 2, "Should load buying signals"
        print("  ✓ Guided builder initialized with persona data")

    def test_step1_emphasis_selection(self, guided_builder):
        """Test step 1: emphasis selection"""
        print("📋 Testing step 1: emphasis selection")
        
        with patch('questionary.select') as mock_select:
            mock_select.return_value.ask.return_value = "2. Pain Point: Focus on challenges they're experiencing"
            
            result = guided_builder.run_step_1()
            
            assert result["emphasis"] == "pain_point", "Should select pain point emphasis"
            mock_select.assert_called_once()
            print("  ✓ Step 1: Pain point emphasis selected")

    def test_step2_content_selection_pain_point(self, guided_builder):
        """Test step 2: content selection for pain point emphasis"""
        print("🎯 Testing step 2: pain point content selection")
        
        # Set emphasis from step 1
        guided_builder.selections["emphasis"] = "pain_point"
        
        with patch('questionary.select') as mock_select:
            mock_select.return_value.ask.return_value = "1. Manual testing bottlenecks"
            
            result = guided_builder.run_step_2()
            
            assert result["selected_content"]["type"] == "pain_point", "Should be pain point type"
            assert "manual testing" in result["selected_content"]["value"].lower(), "Should contain selected pain point"
            print("  ✓ Step 2: Pain point content selected")

    def test_step2_content_selection_use_case(self, guided_builder):
        """Test step 2: content selection for use case emphasis"""
        print("⚙️ Testing step 2: use case content selection")
        
        # Set emphasis from step 1
        guided_builder.selections["emphasis"] = "use_case"
        
        with patch('questionary.select') as mock_select:
            mock_select.return_value.ask.return_value = "2. Code quality monitoring"
            
            result = guided_builder.run_step_2()
            
            assert result["selected_content"]["type"] == "use_case", "Should be use case type"
            assert "code quality" in result["selected_content"]["value"].lower(), "Should contain selected use case"
            print("  ✓ Step 2: Use case content selected")

    def test_step2_custom_instructions(self, guided_builder):
        """Test step 2: custom instructions option"""
        print("✏️ Testing step 2: custom instructions")
        
        guided_builder.selections["emphasis"] = "pain_point"
        
        with patch('questionary.select') as mock_select_option, \
             patch('questionary.text') as mock_text:
            mock_select_option.return_value.ask.return_value = "3. Other (specify custom instructions to the LLM)"
            mock_text.return_value.ask.return_value = "Focus on scalability challenges during rapid growth"
            
            result = guided_builder.run_step_2()
            
            assert result["selected_content"]["custom"] == True, "Should be marked as custom"
            assert "scalability challenges" in result["selected_content"]["custom_instructions"], "Should contain custom instructions"
            print("  ✓ Step 2: Custom instructions handled correctly")

    def test_step3_personalization_selection(self, guided_builder):
        """Test step 3: personalization selection"""
        print("🎨 Testing step 3: personalization selection")
        
        with patch('questionary.select') as mock_select:
            mock_select.return_value.ask.return_value = "1. Recent Series B funding"
            
            result = guided_builder.run_step_3()
            
            assert result["personalization"]["type"] == "buying_signal", "Should be buying signal type"
            assert "series b" in result["personalization"]["title"].lower(), "Should contain Series B reference"
            print("  ✓ Step 3: Series B personalization selected")

    def test_step3_custom_personalization(self, guided_builder):
        """Test step 3: custom personalization option"""
        print("🔧 Testing step 3: custom personalization")
        
        with patch('questionary.select') as mock_select_option, \
             patch('questionary.text') as mock_text:
            mock_select_option.return_value.ask.return_value = "3. Other (specify custom instructions to the LLM)"
            mock_text.return_value.ask.return_value = "Reference their recent product launch announcement"
            
            result = guided_builder.run_step_3()
            
            assert result["personalization"]["custom"] == True, "Should be marked as custom"
            assert "product launch" in result["personalization"]["custom_instructions"], "Should contain custom instructions"
            print("  ✓ Step 3: Custom personalization handled correctly")

    def test_step4_cta_selection(self, guided_builder):
        """Test step 4: call-to-action selection"""
        print("📞 Testing step 4: CTA selection")
        
        with patch('questionary.select') as mock_select:
            mock_select.return_value.ask.return_value = "1. Ask for a meeting (e.g. \"Worth a quick 15-min call next week?\")"
            
            result = guided_builder.run_step_4()
            
            assert result["call_to_action"]["type"] == "meeting", "Should be meeting type"
            assert result["call_to_action"]["intent"] == "schedule_meeting", "Should have correct intent"
            print("  ✓ Step 4: Meeting CTA selected")

    def test_step4_custom_cta(self, guided_builder):
        """Test step 4: custom CTA option"""
        print("📝 Testing step 4: custom CTA")
        
        with patch('questionary.select') as mock_select_option, \
             patch('questionary.text') as mock_text:
            mock_select_option.return_value.ask.return_value = "6. Other (write your own custom CTA)"
            mock_text.return_value.ask.return_value = "Should I send over our technical implementation guide?"
            
            result = guided_builder.run_step_4()
            
            assert result["call_to_action"]["custom"] == True, "Should be marked as custom"
            assert "implementation guide" in result["call_to_action"]["text"], "Should contain custom CTA text"
            print("  ✓ Step 4: Custom CTA handled correctly")

    def test_complete_guided_flow(self, guided_builder):
        """Test the complete 4-step guided flow"""
        print("🔄 Testing complete guided flow")
        
        # Mock all user selections
        selections = [
            "2. Pain Point: Focus on challenges they're experiencing",  # Step 1
            "1. Manual testing bottlenecks",  # Step 2
            "1. Recent Series B funding",  # Step 3
            "1. Ask for a meeting (e.g. \"Worth a quick 15-min call next week?\")"  # Step 4
        ]
        
        with patch('questionary.select') as mock_select:
            mock_select.return_value.ask.side_effect = selections
            
            result = guided_builder.run_complete_flow()
            
            # Verify all selections are captured
            assert result["guided_mode"] == True, "Should be in guided mode"
            assert result["emphasis"] == "pain_point", "Should have pain point emphasis"
            assert result["selected_content"]["type"] == "pain_point", "Should have pain point content"
            assert result["personalization"]["type"] == "buying_signal", "Should have buying signal personalization"
            assert result["call_to_action"]["type"] == "meeting", "Should have meeting CTA"
            
            print("  ✓ Complete guided flow executed successfully")

    def test_edge_case_missing_persona_data(self, test_domain):
        """Test guided builder with missing persona data"""
        print("⚠️ Testing edge case: missing persona data")
        
        # Create project without persona data
        project_storage.create_project(test_domain)
        
        try:
            guided_builder = GuidedEmailBuilder(test_domain)
            
            # Should either handle gracefully or use defaults
            assert guided_builder.persona_data is not None, "Should provide default persona data"
            print("  ✓ Missing persona data handled with defaults")
        except Exception as e:
            # Should be a handled exception with clear message
            assert "persona" in str(e).lower() or "missing" in str(e).lower()
            print(f"  ✓ Missing persona data properly reported: {type(e).__name__}")

    def test_email_generation_with_guided_selections(self, guided_builder):
        """Test email generation using guided selections"""
        print("✉️ Testing email generation with guided selections")
        
        # Set up complete guided selections
        guided_selections = {
            "guided_mode": True,
            "emphasis": "pain_point",
            "selected_content": {
                "type": "pain_point",
                "value": "Manual testing bottlenecks",
                "description": "Time-consuming manual testing processes",
                "custom": False
            },
            "personalization": {
                "type": "buying_signal",
                "title": "Recent Series B funding",
                "example": "Growth stage companies with fresh capital",
                "custom": False
            },
            "call_to_action": {
                "type": "meeting",
                "text": "Worth a quick 15-min call next week?",
                "intent": "schedule_meeting",
                "custom": False
            }
        }
        
        with patch('cli.services.email_generation_service.generate_email_campaign_service') as mock_email_gen:
            mock_email_gen.return_value = {
                "subject": "manual testing bottlenecks post-series b?",
                "body": "Hi {{FirstName}},\n\nCongrats on the Series B! Manual testing bottlenecks often become critical at your scale.\n\nWorth a quick 15-min call next week?",
                "alternatives": ["testing automation for {{Company}}?"]
            }
            
            result = guided_builder.generate_email_with_selections(guided_selections)
            
            assert result["success"] == True, "Email generation should succeed"
            assert "manual testing" in result["data"]["subject"].lower(), "Should reflect guided selections"
            
            # Verify guided mode variables were passed to email service
            call_args = mock_email_gen.call_args[1]  # keyword arguments
            assert call_args["guided_mode"] == True, "Should pass guided mode flag"
            assert call_args["emphasis"] == "pain_point", "Should pass emphasis selection"
            
            print("  ✓ Email generation with guided selections successful")

    def test_dynamic_option_extraction(self, guided_builder, sample_persona_data):
        """Test dynamic extraction of options from persona data"""
        print("📊 Testing dynamic option extraction")
        
        # Test use case extraction
        use_cases = guided_builder._extract_use_case_options()
        assert len(use_cases) == 2, "Should extract 2 use cases"
        assert "Automated testing workflows" in use_cases[0], "Should contain first use case"
        
        # Test pain point extraction
        pain_points = guided_builder._extract_pain_point_options()
        assert len(pain_points) == 2, "Should extract 2 pain points"
        assert "Manual testing bottlenecks" in pain_points[0], "Should contain first pain point"
        
        # Test buying signals extraction
        buying_signals = guided_builder._extract_buying_signals()
        assert len(buying_signals) == 2, "Should extract 2 buying signals"
        assert "Recent Series B funding" in buying_signals[0]["title"], "Should contain first buying signal"
        
        print("  ✓ Dynamic option extraction working correctly")


if __name__ == "__main__":
    # Run with pytest for proper fixture handling
    pytest.main([__file__, "-v"])