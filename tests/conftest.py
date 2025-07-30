"""
Shared test fixtures for the Blossomer GTM CLI test suite.
This file contains all mock fixtures to avoid LLM API costs.
"""

import pytest
import json
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

# Add CLI modules to path for imports
import sys
cli_root = Path(__file__).parent.parent
sys.path.insert(0, str(cli_root))


@pytest.fixture
def mock_api_keys(monkeypatch):
    """Mock API keys to be present for tests"""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test_firecrawl_key")
    monkeypatch.setenv("FORGE_API_KEY", "test_forge_key")


@pytest.fixture
def temp_project_dir(tmp_path, monkeypatch):
    """Create temporary project directory for tests"""
    project_dir = tmp_path / "gtm_projects"
    project_dir.mkdir()
    
    # Mock the ProjectStorage class to use temp directory
    original_init = None
    try:
        from cli.services.project_storage import ProjectStorage
        original_init = ProjectStorage.__init__
        
        def mock_init(self, base_dir="gtm_projects"):
            original_init(self, str(project_dir))
        
        monkeypatch.setattr(ProjectStorage, "__init__", mock_init)
    except ImportError:
        pass  # Service might not exist
    
    return project_dir


@pytest.fixture
def mock_llm_responses():
    """Provide realistic mock responses for all LLM calls"""
    return {
        "overview": {
            "company_name": "Acme Corporation",
            "description": "Leading provider of enterprise automation software",
            "product_description": "AcmeFlow - Workflow automation platform for enterprises",
            "value_proposition": "Reduce manual work by 80% with intelligent automation",
            "target_market": "Enterprise companies with 500+ employees",
            "business_model": "SaaS subscription with professional services",
            "key_differentiators": ["AI-powered automation", "Enterprise security", "Custom integrations"],
            "capabilities": ["Workflow automation", "Process optimization", "System integration", "Analytics reporting"],
            "_generated_at": "2024-01-01T00:00:00Z"
        },
        "account": {
            "target_account_name": "Mid-Market Technology Companies",
            "firmographics": {
                "industry": "Technology",
                "company_size": "500-2000 employees",
                "revenue_range": "$50M-$500M",
                "growth_stage": "Growth stage",
                "geography": "North America, Europe"
            },
            "technographics": {
                "tech_stack": ["Salesforce", "HubSpot", "AWS", "Microsoft"],
                "digital_maturity": "High"
            },
            "behavioral_attributes": {
                "buying_process": "Committee-based with 6-month cycles",
                "decision_criteria": ["ROI", "Security", "Scalability"]
            },
            "_generated_at": "2024-01-01T00:00:00Z"
        },
        "persona": {
            "target_persona_name": "VP of Operations",
            "demographics": {
                "job_title": "VP Operations",
                "department": "Operations",
                "seniority": "VP",
                "team_size": "20-50",
                "tenure": "3-7 years"
            },
            "psychographics": {
                "pain_points": [
                    "Manual processes causing delays",
                    "Lack of visibility into operations",
                    "Scaling challenges"
                ],
                "goals": [
                    "Improve operational efficiency",
                    "Reduce manual work",
                    "Enable team to focus on strategy"
                ],
                "motivations": ["Process optimization", "Team productivity"],
                "concerns": ["Implementation complexity", "Change management"]
            },
            "communication_preferences": {
                "channels": ["Email", "LinkedIn", "Industry events"],
                "content_types": ["Case studies", "ROI calculators", "Webinars"],
                "messaging_tone": "Professional, data-driven"
            },
            "_generated_at": "2024-01-01T00:00:00Z"
        },
        "email": {
            "subjects": {
                "primary": "Transform Your Operations with Intelligent Automation",
                "alternatives": [
                    "Reduce Manual Work by 80% - See How",
                    "VP Operations: Your Automation Solution is Here"
                ]
            },
            "full_email_body": "Hi {{first_name}},\n\nI notice {{company}} is scaling rapidly in the tech space. Many VPs of Operations at similar companies are struggling with manual processes that slow down growth.\n\nAcmeFlow has helped companies like yours reduce manual work by 80% while improving visibility across operations.\n\nWould you be interested in a 15-minute conversation about how we could help {{company}} scale more efficiently?\n\nBest regards,\n[Your Name]",
            "email_body_breakdown": [
                {"text": "Hi {{first_name}},", "type": "greeting"},
                {"text": "I notice {{company}} is scaling rapidly in the tech space. Many VPs of Operations at similar companies are struggling with manual processes that slow down growth.", "type": "pain-point"},
                {"text": "AcmeFlow has helped companies like yours reduce manual work by 80% while improving visibility across operations.", "type": "solution"},
                {"text": "Would you be interested in a 15-minute conversation about how we could help {{company}} scale more efficiently?", "type": "cta"},
                {"text": "Best regards,\n[Your Name]", "type": "signature"}
            ],
            "writing_process": {
                "target_persona": "VP of Operations",
                "key_pain_points": "Manual processes and scaling challenges",
                "value_props_used": "80% reduction in manual work and improved operational visibility",
                "call_to_action_type": "Soft meeting request"
            },
            "metadata": {
                "word_count": 65,
                "reading_time_seconds": 15,
                "personalization_fields": ["first_name", "company"],
                "tone": "Professional, consultative",
                "generated_at": "2024-01-01T00:00:00Z",
                "generation_id": "test-email-gen-123",
                "confidence": "high",
                "personalization_level": "medium"
            },
            "_generated_at": "2024-01-01T00:00:00Z"
        },
        "strategy": {
            "content": """# GTM Strategic Plan for Acme Corporation

## Executive Summary
Comprehensive go-to-market strategy targeting mid-market technology companies with VP-level operations leaders.

## Target Market Analysis
### Primary Target: Mid-Market Technology Companies
- **Size**: 500-2000 employees
- **Revenue**: $50M-$500M annually
- **Growth Stage**: Scaling rapidly
- **Geographic Focus**: North America, Europe

## Buyer Persona Profile
### VP of Operations
- **Primary Decision Maker**: Yes
- **Budget Authority**: $100K+ annually
- **Key Pain Points**: Manual processes, scaling challenges
- **Success Metrics**: Operational efficiency, team productivity

## Lead Scoring Framework

### Account Scoring (Total: 100 points)
1. **Company Size** (25 points)
   - 500-1000 employees: 25 points
   - 1000-2000 employees: 20 points
   - 2000+ employees: 15 points

2. **Industry Fit** (25 points)
   - Technology/Software: 25 points
   - Financial Services: 20 points
   - Healthcare: 15 points

3. **Technology Stack** (25 points)
   - Uses Salesforce + HubSpot: 25 points
   - Uses one of Salesforce/HubSpot: 15 points
   - Uses competing CRM: 10 points

4. **Growth Indicators** (25 points)
   - Recent funding/IPO: 25 points
   - Rapid hiring: 20 points
   - Market expansion: 15 points

### Contact Scoring (Total: 100 points)
1. **Title Match** (40 points)
   - VP Operations: 40 points
   - Director Operations: 30 points
   - Operations Manager: 20 points

2. **Department** (20 points)
   - Operations: 20 points
   - IT/Technology: 15 points
   - Other: 10 points

3. **Seniority** (20 points)
   - VP level: 20 points
   - Director level: 15 points
   - Manager level: 10 points

4. **Team Size** (20 points)
   - 20+ reports: 20 points
   - 10-20 reports: 15 points
   - 5-10 reports: 10 points

## Tool Stack Recommendations

### 1. Sales Intelligence & Prospecting
- **Primary**: Apollo.io
- **Alternative**: ZoomInfo
- **Purpose**: Account discovery and contact identification

### 2. CRM & Pipeline Management
- **Primary**: HubSpot Sales Hub
- **Alternative**: Salesforce
- **Purpose**: Lead tracking and opportunity management

### 3. Email Automation & Outreach
- **Primary**: Outreach.io
- **Alternative**: SalesLoft
- **Purpose**: Multi-touch email campaigns

### 4. Social Selling
- **Primary**: LinkedIn Sales Navigator
- **Purpose**: Social research and engagement

### 5. Content Management
- **Primary**: Highspot
- **Alternative**: Seismic
- **Purpose**: Sales collateral management

### 6. Video Outreach
- **Primary**: Vidyard
- **Alternative**: Loom
- **Purpose**: Personalized video messages

### 7. Meeting Scheduling
- **Primary**: Calendly
- **Alternative**: Chili Piper
- **Purpose**: Frictionless meeting booking

### 8. Conversation Intelligence
- **Primary**: Gong
- **Alternative**: Chorus
- **Purpose**: Call analysis and coaching

### 9. Sales Analytics
- **Primary**: Tableau
- **Alternative**: Power BI
- **Purpose**: Performance tracking and insights

## Email Methodology Framework

### The IMPACT Method
1. **I**ntroduce: Brief, relevant introduction
2. **M**ention: Specific company/industry insight
3. **P**roblem: Acknowledge their likely challenges
4. **A**dvantage: Present your solution's value
5. **C**all-to-action: Clear next step
6. **T**hank: Professional closing

### Email Sequence Structure
1. **Email 1**: Problem awareness + soft introduction
2. **Email 2**: Social proof + case study
3. **Email 3**: Value proposition + ROI focus
4. **Email 4**: Urgency + final opportunity
5. **Email 5**: Break-up email with future follow-up

## Key Metrics & Interpretation

### Pipeline Metrics
- **Lead-to-Opportunity Rate**: Target 15-20%
- **Opportunity-to-Customer Rate**: Target 25-30%
- **Average Deal Size**: Target $150K annually
- **Sales Cycle Length**: Target 4-6 months

### Activity Metrics
- **Emails Sent per Rep per Day**: 50-75
- **Calls Made per Rep per Day**: 20-30
- **LinkedIn Messages per Week**: 25-35
- **Meetings Booked per Week**: 5-8

### Quality Metrics
- **Email Open Rate**: Target 25-30%
- **Email Reply Rate**: Target 3-5%
- **Meeting Show Rate**: Target 75-80%
- **Demo Conversion Rate**: Target 40-50%

## Implementation Timeline

### Month 1: Foundation
- Set up tool stack and integrations
- Create initial prospect lists
- Develop email templates and sequences
- Train sales team on methodology

### Month 2: Launch
- Begin outbound campaigns
- Start tracking metrics
- Iterate on messaging based on responses
- Book initial meetings

### Month 3: Optimize
- Analyze performance data
- Refine targeting criteria
- Optimize email sequences
- Scale successful campaigns

### Month 4+: Scale
- Expand successful campaigns
- Add new channels (social, events)
- Develop partner programs
- Implement account-based marketing

## Success Criteria
- Generate 50+ qualified leads per month
- Achieve 15% lead-to-opportunity conversion
- Book 20+ sales meetings per month
- Close 5+ deals per quarter

This strategic plan provides a comprehensive framework for successful go-to-market execution targeting your ideal customer profile.""",
            "_generated_at": "2024-01-01T00:00:00Z"
        }
    }


@pytest.fixture
def mock_firecrawl_response():
    """Mock Firecrawl API response for website scraping"""
    return {
        "content": """
        <html>
        <head>
            <title>Acme Corporation - Enterprise Automation</title>
            <meta name="description" content="Transform your business with intelligent automation">
        </head>
        <body>
            <h1>Acme Corporation</h1>
            <p>Leading provider of enterprise automation software for mid-market companies.</p>
            
            <h2>Our Products</h2>
            <div class="product">
                <h3>AcmeFlow</h3>
                <p>Workflow automation platform that reduces manual work by 80%</p>
            </div>
            
            <div class="product">
                <h3>AcmeSync</h3>
                <p>Real-time data synchronization across enterprise systems</p>
            </div>
            
            <h2>Why Choose Acme</h2>
            <ul>
                <li>AI-powered intelligent automation</li>
                <li>Enterprise-grade security and compliance</li>
                <li>Custom integrations with your existing tools</li>
                <li>24/7 support and professional services</li>
            </ul>
            
            <h2>Customer Success</h2>
            <p>Over 500 enterprise customers trust Acme to streamline their operations.</p>
        </body>
        </html>
        """,
        "metadata": {
            "title": "Acme Corporation - Enterprise Automation",
            "description": "Transform your business with intelligent automation",
            "keywords": ["automation", "enterprise", "workflow", "productivity"]
        },
        "success": True
    }


@pytest.fixture(autouse=True)
def mock_all_external_calls(monkeypatch, mock_llm_responses, mock_firecrawl_response, mock_api_keys):
    """Automatically mock all external API calls to prevent costs"""
    
    # Mock LLM service calls
    async def mock_llm_generate(prompt=None, system_prompt: str = None, response_model=None, **kwargs):
        """Smart mock that returns appropriate response based on prompt content"""
        # Handle both generate and generate_structured_output calls
        if prompt is None:
            prompt = system_prompt or ""
        
        # Handle different types of prompt input (string, LLMRequest object, etc.)
        if hasattr(prompt, 'lower'):
            prompt_lower = prompt.lower()
        elif hasattr(prompt, 'prompt'):
            prompt_lower = prompt.prompt.lower()
        elif hasattr(prompt, '__str__'):
            prompt_lower = str(prompt).lower()
        else:
            prompt_lower = ""
        
        # Check for email-related keywords first (more specific)
        if any(word in prompt_lower for word in ["email", "campaign", "outreach", "subject", "message", "writing"]):
            response_data = mock_llm_responses["email"]
        elif any(word in prompt_lower for word in ["company", "overview", "business", "product"]):
            response_data = mock_llm_responses["overview"]
        elif any(word in prompt_lower for word in ["account", "target", "firmographic"]):
            response_data = mock_llm_responses["account"]
        elif any(word in prompt_lower for word in ["persona", "buyer", "demographic"]):
            response_data = mock_llm_responses["persona"]
        elif any(word in prompt_lower for word in ["strategy", "plan", "gtm"]):
            # Strategy returns a response object with text attribute
            strategy_response = Mock()
            strategy_response.text = mock_llm_responses["strategy"]["content"]
            return strategy_response
        else:
            response_data = {"default": "mock response"}
        
        # If response_model is provided (structured output), return the data as-is
        # Otherwise return JSON string for compatibility
        if response_model:
            return response_data
        else:
            return json.dumps(response_data)
    
    # Mock all LLM service paths
    mock_llm = AsyncMock(side_effect=mock_llm_generate)
    
    # Mock LLM client methods that are actually used
    mock_client = Mock()
    mock_client.generate = mock_llm
    mock_client.generate_structured_output = mock_llm
    
    # Mock the singleton function to return our mock client
    try:
        monkeypatch.setattr("cli.services.llm_singleton.get_llm_client", lambda **kwargs: mock_client)
    except (ImportError, AttributeError):
        pass  # Service might not exist
    
    # Mock app services without importing them directly
    try:
        import app.services.llm_service
        monkeypatch.setattr("app.services.llm_service.LLMClient.generate", mock_llm)
    except ImportError:
        # App service isn't available in CLI test environment - that's OK
        pass
    
    # Mock Firecrawl website scraping
    def mock_firecrawl_scrape(*args, **kwargs):
        return mock_firecrawl_response
    
    # Mock the actual functions that exist
    monkeypatch.setattr("app.services.website_scraper.firecrawl_scrape_url", mock_firecrawl_scrape)
    monkeypatch.setattr("app.services.website_scraper.get_processed_website_content", 
                       lambda url: mock_firecrawl_response["content"])
    
    # Mock web content service if it exists
    try:
        monkeypatch.setattr("app.services.web_content_service.WebContentService.fetch_website_content", 
                           lambda self, url: mock_firecrawl_response)
    except AttributeError:
        pass  # Service might not exist
    
    # Mock any other external API calls
    monkeypatch.setattr("requests.get", Mock(return_value=Mock(json=lambda: mock_firecrawl_response)))
    monkeypatch.setattr("requests.post", Mock(return_value=Mock(json=lambda: mock_firecrawl_response)))
    
    return mock_llm


@pytest.fixture
def sample_project_data(mock_llm_responses):
    """Complete project data for testing existing projects"""
    return mock_llm_responses


@pytest.fixture
def mock_project_with_data(temp_project_dir, sample_project_data):
    """Create a complete mock project with all steps"""
    domain = "acme.com"
    project_path = temp_project_dir / domain
    project_path.mkdir()
    
    # Create JSON files for each step
    for step, data in sample_project_data.items():
        if step != "strategy":  # Strategy is stored differently
            json_path = project_path / f"{step}.json"
            json_path.write_text(json.dumps(data, indent=2))
    
    # Create metadata file
    metadata = {
        "domain": domain,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "steps_completed": ["overview", "account", "persona", "email", "strategy"],
        "version": "1.0"
    }
    (project_path / ".metadata.json").write_text(json.dumps(metadata, indent=2))
    
    return project_path


@pytest.fixture
def mock_incomplete_project(temp_project_dir):
    """Create a mock project with only some steps completed"""
    domain = "incomplete.com"
    project_path = temp_project_dir / domain
    project_path.mkdir()
    
    # Only create overview step
    overview_data = {
        "company_name": "Incomplete Corp",
        "description": "Test company",
        "_generated_at": "2024-01-01T00:00:00Z"
    }
    (project_path / "overview.json").write_text(json.dumps(overview_data, indent=2))
    
    # Create metadata
    metadata = {
        "domain": domain,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "steps_completed": ["overview"],
        "version": "1.0"
    }
    (project_path / ".metadata.json").write_text(json.dumps(metadata, indent=2))
    
    return project_path


@pytest.fixture
def mock_corrupted_project(temp_project_dir):
    """Create a project with corrupted JSON files"""
    domain = "corrupted.com"
    project_path = temp_project_dir / domain
    project_path.mkdir()
    
    # Write corrupted JSON
    (project_path / "overview.json").write_text("{corrupted json content")
    
    return project_path


@pytest.fixture
def mock_cli_runner():
    """Create a Typer CLI runner for testing commands"""
    from typer.testing import CliRunner
    return CliRunner()


@pytest.fixture
def mock_console_input(monkeypatch):
    """Mock console input for interactive tests"""
    inputs = []
    
    def mock_input(prompt=""):
        if inputs:
            return inputs.pop(0)
        return ""
    
    def mock_questionary_text(question, **kwargs):
        mock_result = Mock()
        mock_result.ask = Mock(return_value=inputs.pop(0) if inputs else "test_input")
        return mock_result
    
    def mock_questionary_select(question, choices, **kwargs):
        mock_result = Mock()
        mock_result.ask = Mock(return_value=choices[0] if choices else "default")
        return mock_result
    
    def mock_questionary_confirm(question, **kwargs):
        mock_result = Mock()
        mock_result.ask = Mock(return_value=True)
        return mock_result
    
    monkeypatch.setattr("builtins.input", mock_input)
    monkeypatch.setattr("questionary.text", mock_questionary_text)
    monkeypatch.setattr("questionary.select", mock_questionary_select)
    monkeypatch.setattr("questionary.confirm", mock_questionary_confirm)
    
    def add_input(value):
        inputs.append(value)
    
    return add_input


@pytest.fixture
def mock_error_scenarios(monkeypatch):
    """Fixture for testing error handling scenarios"""
    scenarios = {}
    
    def set_scenario(name: str):
        if name == "timeout":
            async def timeout_response(*args, **kwargs):
                import asyncio
                await asyncio.sleep(45)  # Exceed timeout
                return {}
            monkeypatch.setattr("cli.services.llm_service.LLMClient.generate", timeout_response)
            
        elif name == "api_error":
            async def error_response(*args, **kwargs):
                raise Exception("API rate limit exceeded")
            monkeypatch.setattr("cli.services.llm_service.LLMClient.generate", error_response)
            
        elif name == "network_error":
            def network_error(*args, **kwargs):
                raise ConnectionError("Network unreachable")
            monkeypatch.setattr("app.services.website_scraper.scrape_website", network_error)
    
    scenarios["set"] = set_scenario
    return scenarios


# Test data factories for creating test objects
@pytest.fixture
def create_test_domain():
    """Factory for creating test domain objects"""
    def _create(domain_name="test.com"):
        from cli.utils.domain import NormalizedDomain
        return NormalizedDomain(domain=domain_name, url=f"https://{domain_name}")
    return _create


@pytest.fixture
def create_test_project():
    """Factory for creating test project data"""
    def _create(domain="test.com", steps=None):
        if steps is None:
            steps = ["overview", "account", "persona", "email", "strategy"]
        
        project_data = {}
        for step in steps:
            if step == "overview":
                project_data[step] = {
                    "company_name": f"Test Company for {domain}",
                    "description": "Test description",
                    "_generated_at": "2024-01-01T00:00:00Z"
                }
            elif step == "account":
                project_data[step] = {
                    "target_account_name": "Test Accounts",
                    "firmographics": {"industry": "Technology"},
                    "_generated_at": "2024-01-01T00:00:00Z"
                }
            # Add other steps as needed
        
        return project_data
    return _create