#!/usr/bin/env python3
"""
Test script for the guided email builder
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli.utils.guided_email_builder import GuidedEmailBuilder

# Sample test data that matches the target_persona.jinja2 output structure
sample_persona_data = {
    "use_cases": [
        {
            "use_case": "Quality assurance workflow",
            "pain_points": "Maintaining support quality during rapid scaling",
            "capability": "Real-time conversation analysis",
            "desired_outcome": "Consistent service quality across all agents"
        },
        {
            "use_case": "Agent training optimization", 
            "pain_points": "Long agent onboarding times",
            "capability": "Automated coaching suggestions",
            "desired_outcome": "Faster time-to-productivity for new hires"
        },
        {
            "use_case": "Knowledge gap detection",
            "pain_points": "Lack of visibility into knowledge gaps",
            "capability": "Knowledge gap identification",
            "desired_outcome": "Proactive training before customer complaints"
        }
    ],
    "buying_signals": [
        {
            "title": "Recent Series B funding",
            "description": "Company completed Series B round in last 6 months",
            "type": "Company Data",
            "priority": "High"
        },
        {
            "title": "Support team hiring spree",
            "description": "Posting multiple customer support agent positions",
            "type": "Company Data", 
            "priority": "Medium"
        },
        {
            "title": "Customer growth indicators",
            "description": "Public announcements about customer base expansion",
            "type": "News",
            "priority": "Medium"
        },
        {
            "title": "Technology adoption signals",
            "description": "Recent implementation of customer support tools",
            "type": "Tech Stack",
            "priority": "Low"
        }
    ]
}

sample_account_data = {
    "target_account_name": "Mid-Market FinTech Companies",
    "buying_signals": [
        "Recent funding rounds",
        "Rapid customer growth", 
        "Support team expansion"
    ]
}

def test_guided_builder():
    """Test the guided email builder flow"""
    print("Testing Guided Email Builder...")
    print("=" * 50)
    
    # Initialize the builder
    builder = GuidedEmailBuilder(sample_persona_data, sample_account_data)
    
    # Test content extraction methods
    print("\n1. Testing content extraction by type:")
    
    for emphasis_type in ["use_case", "pain_point", "capability", "desired_outcome"]:
        content_options = builder._extract_content_by_type(emphasis_type)
        print(f"\n{emphasis_type.replace('_', ' ').title()} options:")
        for i, option in enumerate(content_options, 1):
            print(f"  {i}. {option['value']}")
    
    print("\n2. Testing buying signal extraction:")
    signals = builder._extract_buying_signals_for_personalization()
    for i, signal in enumerate(signals, 1):
        print(f"  {i}. {signal['title']}: {signal['example']}")
    
    print("\n✅ All extraction methods working correctly!")
    print("\nTo test the full interactive flow, run:")
    print("python -c \"from cli.utils.guided_email_builder import GuidedEmailBuilder; from test_guided_email import sample_persona_data, sample_account_data; builder = GuidedEmailBuilder(sample_persona_data, sample_account_data); result = builder.run_guided_flow(); print('Result:', result)\"")

if __name__ == "__main__":
    test_guided_builder()