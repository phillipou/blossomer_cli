#!/usr/bin/env python3
"""
Integration tests for the complete 5-step GTM flow.
Tests the end-to-end pipeline: overview → account → persona → email → plan
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.services.project_storage import project_storage
from cli.services.gtm_generation_service import gtm_service


class TestGTMFlowIntegration:
    """Integration tests for the complete GTM flow"""
    
    @pytest.fixture
    def test_domain(self):
        """Provide a test domain and clean up after tests"""
        domain = "gtm-flow-test.com"
        yield domain
        # Cleanup
        if project_storage.project_exists(domain):
            project_storage.delete_project(domain)
    
    @pytest.fixture
    def mock_llm_responses(self):
        """Mock LLM responses for all 5 steps"""
        return {
            "overview": {
                "company_name": "Test Corp",
                "description": "AI-powered testing platform",
                "product_category": "B2B SaaS",
                "cli_summary": {
                    "title": "AI-powered testing platform",
                    "key_points": ["B2B SaaS platform", "Automated testing", "Enterprise focus"],
                    "metrics": {"category": "B2B SaaS", "model": "Usage-based"}
                }
            },
            "account": {
                "target_name": "Mid-Market Tech Companies",
                "company_size": "100-500 employees",
                "geography": "North America",
                "cli_summary": {
                    "title": "Mid-Market Tech Companies",
                    "key_points": ["100-500 employees", "North America focus", "Tech industry"],
                    "metrics": {"size": "100-500", "revenue": "$10M-$50M"}
                }
            },
            "persona": {
                "title": "VP of Engineering",
                "use_cases": [
                    {
                        "use_case": "Automated testing workflows",
                        "pain_point": "Manual testing bottlenecks",
                        "capability": "AI-powered test generation",
                        "desired_outcome": "Faster release cycles"
                    }
                ],
                "buying_signals": [
                    {"title": "Recent Series B funding", "description": "Growth stage funding"}
                ],
                "cli_summary": {
                    "title": "VP of Engineering",
                    "key_points": ["Technical decision maker", "Focus on automation", "Quality concerns"],
                    "metrics": {"team_size": "15-30", "reports_to": "CTO"}
                }
            },
            "email": {
                "subject": "automated testing bottlenecks?",
                "body": "Hi {{FirstName}},\n\nNoticed your Series B - congrats! Testing bottlenecks often become critical at your scale.\n\nWorth a quick chat?",
                "alternatives": ["testing automation for {{Company}}?"],
                "cli_summary": {
                    "title": "Pain Point Email Campaign",
                    "key_points": ["Series B personalization", "Testing bottlenecks focus", "Meeting CTA"],
                    "metrics": {"emphasis": "pain_point", "cta": "meeting"}
                }
            },
            "plan": {
                "execution_plan": {
                    "week_1": ["Build target list", "Set up tools"],
                    "week_2": ["Find contacts", "Verify emails"],
                    "week_3": ["Launch campaign", "Monitor metrics"],
                    "week_4": ["Optimize and scale"]
                },
                "cli_summary": {
                    "title": "30-day GTM Execution Plan",
                    "key_points": ["4-week timeline", "Tool stack setup", "Campaign optimization"],
                    "metrics": {"timeline": "30 days", "expected_meetings": "2-3"}
                }
            }
        }

    def test_complete_gtm_flow(self, test_domain, mock_llm_responses):
        """Test the complete 5-step GTM flow"""
        print(f"🧪 Testing complete GTM flow for {test_domain}")
        
        # Mock all generation services
        with patch('cli.services.product_overview_service.generate_product_overview_service') as mock_overview, \
             patch('cli.services.target_account_service.generate_target_account_profile') as mock_account, \
             patch('cli.services.target_persona_service.generate_target_persona_profile') as mock_persona, \
             patch('cli.services.email_generation_service.generate_email_campaign_service') as mock_email, \
             patch('cli.services.gtm_plan_service.generate_gtm_plan_service') as mock_plan:
            
            # Configure mock returns
            mock_overview.return_value = mock_llm_responses["overview"]
            mock_account.return_value = mock_llm_responses["account"]
            mock_persona.return_value = mock_llm_responses["persona"]
            mock_email.return_value = mock_llm_responses["email"]
            mock_plan.return_value = mock_llm_responses["plan"]
            
            # Step 1: Generate company overview
            overview_result = gtm_service.generate_step(test_domain, "overview", context="Test context")
            assert overview_result["success"], "Overview generation should succeed"
            assert overview_result["data"]["company_name"] == "Test Corp"
            print("  ✓ Step 1: Company overview generated")
            
            # Step 2: Generate target account
            account_result = gtm_service.generate_step(test_domain, "account")
            assert account_result["success"], "Account generation should succeed"
            assert account_result["data"]["target_name"] == "Mid-Market Tech Companies"
            print("  ✓ Step 2: Target account generated")
            
            # Step 3: Generate buyer persona
            persona_result = gtm_service.generate_step(test_domain, "persona")
            assert persona_result["success"], "Persona generation should succeed"
            assert persona_result["data"]["title"] == "VP of Engineering"
            print("  ✓ Step 3: Buyer persona generated")
            
            # Step 4: Generate email campaign
            email_result = gtm_service.generate_step(test_domain, "email")
            assert email_result["success"], "Email generation should succeed"
            assert "automated testing bottlenecks" in email_result["data"]["subject"]
            print("  ✓ Step 4: Email campaign generated")
            
            # Step 5: Generate GTM plan
            plan_result = gtm_service.generate_step(test_domain, "plan")
            assert plan_result["success"], "Plan generation should succeed"
            assert "execution_plan" in plan_result["data"]
            print("  ✓ Step 5: GTM plan generated")
            
            # Verify project completion
            status = gtm_service.get_project_status(test_domain)
            assert status["progress_percentage"] == 100.0, "Project should be 100% complete"
            assert len(status["completed_steps"]) == 5, "All 5 steps should be completed"
            print(f"  ✓ Project completion: {status['progress_percentage']}%")

    def test_step_dependencies(self, test_domain, mock_llm_responses):
        """Test that steps are generated in correct dependency order"""
        print(f"🔗 Testing step dependencies for {test_domain}")
        
        with patch('cli.services.target_account_service.generate_target_account_profile') as mock_account:
            mock_account.return_value = mock_llm_responses["account"]
            
            # Try to generate account without overview (should fail or create overview first)
            result = gtm_service.generate_step(test_domain, "account")
            
            # Verify that overview was created as a dependency
            overview_data = project_storage.load_step_data(test_domain, "overview")
            assert overview_data is not None, "Overview should be created as dependency"
            print("  ✓ Missing dependencies are automatically generated")

    def test_stale_data_regeneration(self, test_domain, mock_llm_responses):
        """Test that dependent steps are marked stale when prerequisites change"""
        print(f"🚨 Testing stale data regeneration for {test_domain}")
        
        # Create project with complete pipeline
        project_storage.create_project(test_domain)
        for step, data in mock_llm_responses.items():
            project_storage.save_step_data(test_domain, step, data)
        
        # Regenerate overview (should mark dependents as stale)
        new_overview = {**mock_llm_responses["overview"], "company_name": "Updated Corp"}
        stale_steps = project_storage.mark_steps_stale(test_domain, "overview")
        project_storage.save_step_data(test_domain, "overview", new_overview)
        
        expected_stale = ["account", "persona", "email", "plan"]
        assert stale_steps == expected_stale, f"Expected {expected_stale} to be stale"
        
        # Verify stale marking
        for step in expected_stale:
            step_data = project_storage.load_step_data(test_domain, step)
            assert step_data.get("_stale", False), f"Step {step} should be marked stale"
        
        print(f"  ✓ {len(stale_steps)} dependent steps marked stale")

    def test_project_status_tracking(self, test_domain, mock_llm_responses):
        """Test project status tracking throughout the flow"""
        print(f"📊 Testing project status tracking for {test_domain}")
        
        # Initial status
        status = gtm_service.get_project_status(test_domain)
        assert not status["exists"], "Project should not exist initially"
        
        # Create project
        project_storage.create_project(test_domain)
        status = gtm_service.get_project_status(test_domain)
        assert status["exists"], "Project should exist after creation"
        assert status["progress_percentage"] == 0.0, "Should be 0% complete"
        
        # Add steps incrementally
        for i, (step, data) in enumerate(mock_llm_responses.items(), 1):
            project_storage.save_step_data(test_domain, step, data)
            status = gtm_service.get_project_status(test_domain)
            expected_progress = (i / 5) * 100
            assert status["progress_percentage"] == expected_progress, f"Should be {expected_progress}% after step {i}"
            print(f"  ✓ After {step}: {status['progress_percentage']}% complete")


if __name__ == "__main__":
    # Run with pytest for proper fixture handling
    pytest.main([__file__, "-v"])