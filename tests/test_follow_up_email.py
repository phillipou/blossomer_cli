"""Test follow-up email generation functionality"""

import asyncio
import json
from pathlib import Path

# Test by manually calling the LLM with our updated prompt
async def test_follow_up_email_generation():
    """Test that follow-up emails are generated correctly"""
    
    # Import required modules
    from app.core.llm.base import LLMClient
    from app.core.llm.factory import LLMFactory
    from app.prompts.runner import TemplateRunner
    from app.prompts.models import EmailGenerationPromptVars
    
    # Create LLM client
    llm_client = LLMFactory.create("openai")
    
    # Create template runner
    runner = TemplateRunner(llm_client)
    
    # Test data
    test_vars = EmailGenerationPromptVars(
        company_context={
            "company_name": "TestCo",
            "description": "We help companies automate their sales outreach",
            "capabilities": ["Email automation", "Lead scoring", "CRM integration"]
        },
        target_account={
            "target_account_name": "Mid-market SaaS companies",
            "target_account_description": "Growing SaaS companies with 50-200 employees"
        },
        target_persona={
            "target_persona_name": "VP of Sales",
            "use_cases": [
                {
                    "use_case": "Outbound automation",
                    "pain_points": "Manual outreach is time-consuming",
                    "capability": "Automated email sequences",
                    "desired_outcome": "10x outreach volume"
                }
            ]
        },
        preferences={
            "use_case": "Outbound automation",
            "emphasis": "pain-point",
            "opening_line": "not-personalized",
            "cta_setting": "meeting",
            "template": "blossomer"
        }
    )
    
    # Expected response structure
    response_model = {
        "subjects": {
            "primary": str,
            "alternatives": list
        },
        "full_email_body": str,
        "email_body_breakdown": list,
        "writing_process": dict,
        "follow_up_email": {
            "subject": str,
            "body": str,
            "wait_days": int
        },
        "metadata": dict
    }
    
    # Run the template
    result = await runner.run(
        template_name="email_generation_blossomer",
        prompt_vars=test_vars,
        response_model=response_model
    )
    
    # Verify follow-up email was generated
    assert "follow_up_email" in result, "Follow-up email not found in response"
    
    follow_up = result["follow_up_email"]
    assert "subject" in follow_up, "Follow-up email missing subject"
    assert "body" in follow_up, "Follow-up email missing body"
    assert "wait_days" in follow_up, "Follow-up email missing wait_days"
    
    # Verify follow-up email constraints
    assert len(follow_up["subject"].split()) <= 4, "Follow-up subject too long"
    assert len(follow_up["body"].split()) <= 60, "Follow-up body exceeds 60 words"
    assert 3 <= follow_up["wait_days"] <= 7, "Wait days outside 3-7 range"
    
    # Verify follow-up doesn't contain platitudes
    platitudes = ["following up", "circling back", "making sure this hit your inbox"]
    body_lower = follow_up["body"].lower()
    for platitude in platitudes:
        assert platitude not in body_lower, f"Follow-up contains platitude: {platitude}"
    
    print("\n✅ Follow-up email generation test passed!")
    print(f"\nFollow-up email subject: {follow_up['subject']}")
    print(f"Follow-up email body ({len(follow_up['body'].split())} words):")
    print(follow_up['body'])
    print(f"\nWait days: {follow_up['wait_days']}")
    
    return True


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_follow_up_email_generation())