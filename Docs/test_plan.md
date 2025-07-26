# Blossomer GTM CLI Test Plan

## Overview
This document outlines a comprehensive test plan for the Blossomer GTM CLI tool. The tests are organized by functionality and priority, covering unit tests, integration tests, and end-to-end scenarios.

## 🚨 Critical Testing Principle: Zero LLM Costs
**All tests MUST mock LLM and external API calls.** No test should ever make real API calls that incur costs. This includes:
- OpenAI/Anthropic API calls
- Firecrawl web scraping API
- TensorBlock Forge API
- Any other external paid services

Every test file should include comprehensive mocking fixtures to simulate these services.

## Test Categories

### 1. Unit Tests

#### 1.1 Command Tests (`tests/cli/test_commands.py`)
Test individual CLI commands in isolation.

**Priority: High**

##### `test_init_command.py`
- [ ] Test domain validation and normalization
- [ ] Test API key validation (missing keys should show setup instructions)
- [ ] Test interactive mode flow (domain prompt, context questions)
- [ ] Test YOLO mode (skip all interactions)
- [ ] Test handling existing projects (menu choices)
- [ ] Test keyboard interrupt handling (Ctrl+C)
- [ ] Test invalid domain formats
- [ ] Test step-by-step generation success
- [ ] Test error recovery and resume functionality

##### `test_show_command.py`
- [ ] Test showing all assets for a project
- [ ] Test showing individual assets (overview, account, persona, email, strategy)
- [ ] Test JSON output format
- [ ] Test auto-detection of current project
- [ ] Test handling multiple projects (domain required)
- [ ] Test handling non-existent projects
- [ ] Test stale data warnings
- [ ] Test character count displays

##### `test_edit_command.py`
- [ ] Test opening files in system editor
- [ ] Test editor detection (VS Code, vim, nano)
- [ ] Test handling missing files
- [ ] Test domain auto-detection

##### `test_export_command.py`
- [ ] Test exporting all assets
- [ ] Test exporting individual assets
- [ ] Test custom output paths
- [ ] Test default naming conventions
- [ ] Test markdown formatting

##### `test_list_command.py`
- [ ] Test listing all projects
- [ ] Test filtering by domain
- [ ] Test empty project list
- [ ] Test project metadata display

#### 1.2 Service Tests (`tests/cli/test_services.py`)
Test CLI-specific services.

**Priority: High**

##### `test_gtm_generation_service.py`
- [ ] Test company overview generation
- [ ] Test target account generation with dependencies
- [ ] Test target persona generation with dependencies
- [ ] Test email campaign generation (automatic and guided)
- [ ] Test strategic plan generation
- [ ] Test force regeneration flag
- [ ] Test stale data marking
- [ ] Test dependency validation

##### `test_project_storage.py`
- [ ] Test project directory creation
- [ ] Test saving step data
- [ ] Test loading step data
- [ ] Test metadata management
- [ ] Test listing projects
- [ ] Test file path generation
- [ ] Test stale data tracking
- [ ] Test error handling for corrupted files

#### 1.3 Utility Tests (`tests/cli/test_utils.py`)
Test utility functions and helpers.

**Priority: Medium**

##### `test_domain_utils.py`
- [ ] Test domain normalization
- [ ] Test URL validation
- [ ] Test various domain formats (http://, https://, www., etc.)
- [ ] Test invalid domains

##### `test_guided_email_builder.py`
- [ ] Test 5-step flow navigation
- [ ] Test context preservation between steps
- [ ] Test menu choices and validation
- [ ] Test preview generation
- [ ] Test skipping steps

##### `test_markdown_formatter.py`
- [ ] Test formatting for each content type
- [ ] Test preview mode truncation
- [ ] Test character counting
- [ ] Test rich formatting

##### `test_panel_utils.py`
- [ ] Test welcome panel creation
- [ ] Test step panel creation
- [ ] Test status panel creation
- [ ] Test completion panel creation

##### `test_loading_animation.py`
- [ ] Test animation start/stop
- [ ] Test step-specific messages
- [ ] Test timing display

### 2. Integration Tests

#### 2.1 Workflow Tests (`tests/cli/test_integration.py`)
Test complete user workflows.

**Priority: High**

##### `test_new_project_flow.py`
- [ ] Test complete 5-step generation for new domain
- [ ] Test with user context provided
- [ ] Test with hypotheses captured
- [ ] Test interruption and resume
- [ ] Test final menu choices (view/edit/finish)

##### `test_existing_project_flow.py`
- [ ] Test resuming from different steps
- [ ] Test regenerating specific steps
- [ ] Test handling stale dependencies
- [ ] Test skipping to specific steps

##### `test_guided_email_flow.py`
- [ ] Test complete guided email builder flow
- [ ] Test with missing dependencies
- [ ] Test preference capture and application
- [ ] Test preview and edit functionality

##### `test_export_flow.py`
- [ ] Test exporting after generation
- [ ] Test various export formats
- [ ] Test file organization

### 3. End-to-End Tests

#### 3.1 Full CLI Tests (`tests/cli/test_e2e.py`)
Test complete CLI usage scenarios.

**Priority: High**

##### `test_complete_workflow.py`
- [ ] Test: `blossomer init acme.com`
- [ ] Test: `blossomer show all`
- [ ] Test: `blossomer edit strategy`
- [ ] Test: `blossomer export all`

##### `test_resume_workflow.py`
- [ ] Test interrupting during generation
- [ ] Test resuming with `blossomer init acme.com`
- [ ] Test regenerating stale steps

##### `test_yolo_mode.py`
- [ ] Test: `blossomer init acme.com --yolo`
- [ ] Test automatic generation without prompts

### 4. Error Handling Tests

#### 4.1 API Error Tests (`tests/cli/test_error_handling.py`)
Test handling of API failures.

**Priority: Medium**

- [ ] Test network timeout handling
- [ ] Test API rate limit handling
- [ ] Test invalid API responses
- [ ] Test missing API keys
- [ ] Test LLM service errors

#### 4.2 File System Tests
Test file system error scenarios.

- [ ] Test permission errors
- [ ] Test disk space errors
- [ ] Test corrupted JSON files
- [ ] Test missing project directories

### 5. Performance Tests

#### 5.1 Timing Tests (`tests/cli/test_performance.py`)
Test performance characteristics.

**Priority: Low**

- [ ] Test generation timeouts (40s limit)
- [ ] Test animation performance
- [ ] Test file I/O performance with large projects

### 6. UI/UX Tests

#### 6.1 Terminal Display Tests (`tests/cli/test_display.py`)
Test terminal output formatting.

**Priority: Medium**

- [ ] Test color output (with and without --no-color)
- [ ] Test panel formatting
- [ ] Test progress indicators
- [ ] Test menu styling
- [ ] Test immersive mode behavior

### 7. Mock/Fixture Requirements

#### 7.1 Mock LLM Responses (`tests/fixtures/mock_responses/`)
- [ ] Company overview responses
- [ ] Target account responses
- [ ] Target persona responses
- [ ] Email campaign responses
- [ ] Strategic plan responses
- [ ] Error responses

#### 7.2 Sample Projects (`tests/fixtures/sample_projects/`)
- [ ] Complete project with all steps
- [ ] Partial project (missing steps)
- [ ] Project with stale data
- [ ] Corrupted project files

## Test Implementation Guidelines

### IMPORTANT: No Real LLM Calls
**All LLM service calls MUST be mocked to avoid costs.** Every test should use mock responses instead of making actual API calls.

### Test Structure
```python
# Example test structure with mocked LLM
import pytest
from typer.testing import CliRunner
from cli.main import app
from unittest.mock import patch, AsyncMock

runner = CliRunner()

@patch('cli.services.llm_service.LLMClient.generate')
@patch('app.services.web_content_service.WebContentService.fetch_website_content')
def test_init_new_domain(mock_fetch, mock_llm):
    """Test initializing a new domain project"""
    # Mock web scraping
    mock_fetch.return_value = {"content": "Mocked website content"}
    
    # Mock LLM responses
    mock_llm.return_value = AsyncMock(return_value={
        "company_name": "Acme Corp",
        "description": "Test company description"
    })
    
    result = runner.invoke(app, ["init", "acme.com", "--yolo"])
    assert result.exit_code == 0
    assert "Company Overview" in result.output
    assert mock_llm.called  # Verify LLM was called
    assert mock_fetch.called  # Verify web scraping was called
```

### Comprehensive Mocking Strategy

#### 1. Mock LLM Service Calls
```python
@pytest.fixture
def mock_llm_responses():
    """Provide mock responses for all LLM calls"""
    return {
        "overview": {
            "company_name": "Test Company",
            "description": "A test software company",
            "product_description": "Test product description",
            "value_proposition": "Test value prop",
            "_generated_at": "2024-01-01T00:00:00Z"
        },
        "account": {
            "target_account_name": "Enterprise Tech Companies",
            "firmographics": {
                "industry": "Technology",
                "company_size": "1000-5000 employees"
            },
            "_generated_at": "2024-01-01T00:00:00Z"
        },
        "persona": {
            "target_persona_name": "VP of Engineering",
            "demographics": {
                "job_title": "VP Engineering",
                "seniority": "VP Level"
            },
            "_generated_at": "2024-01-01T00:00:00Z"
        },
        "email": {
            "subjects": {"primary": "Transform Your Engineering Workflow"},
            "primary_email": {"subject": "Test", "body": "Test email"},
            "_generated_at": "2024-01-01T00:00:00Z"
        },
        "strategy": {
            "content": "# GTM Strategic Plan\n\nTest strategy content...",
            "_generated_at": "2024-01-01T00:00:00Z"
        }
    }

@pytest.fixture(autouse=True)
def mock_all_llm_calls(monkeypatch, mock_llm_responses):
    """Automatically mock all LLM service calls"""
    async def mock_generate_overview(*args, **kwargs):
        return mock_llm_responses["overview"]
    
    async def mock_generate_account(*args, **kwargs):
        return mock_llm_responses["account"]
    
    async def mock_generate_persona(*args, **kwargs):
        return mock_llm_responses["persona"]
    
    async def mock_generate_email(*args, **kwargs):
        return mock_llm_responses["email"]
    
    async def mock_generate_strategy(*args, **kwargs):
        return mock_llm_responses["strategy"]
    
    # Mock all service methods
    monkeypatch.setattr(
        "cli.services.product_overview_service.generate_product_overview_service",
        mock_generate_overview
    )
    monkeypatch.setattr(
        "cli.services.target_account_service.generate_target_account_profile",
        mock_generate_account
    )
    # ... continue for all services
```

#### 2. Mock External API Calls
```python
@pytest.fixture
def mock_external_apis(monkeypatch):
    """Mock all external API calls (Firecrawl, etc.)"""
    def mock_firecrawl(*args, **kwargs):
        return {
            "content": "Mocked website content",
            "title": "Test Company",
            "description": "Test description"
        }
    
    monkeypatch.setattr(
        "app.services.website_scraper.scrape_website",
        mock_firecrawl
    )
```

#### 3. Mock File System for Tests
```python
@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project directory for tests"""
    project_dir = tmp_path / "gtm_projects"
    project_dir.mkdir()
    return project_dir

@pytest.fixture
def mock_project_storage(monkeypatch, temp_project_dir):
    """Mock project storage to use temp directory"""
    monkeypatch.setattr(
        "cli.services.project_storage.PROJECT_ROOT",
        temp_project_dir
    )
```

### Test Data Management
- Use fixtures for consistent mock responses
- Create response factories for different scenarios
- Use temporary directories for file operations
- Clean up is automatic with pytest tmp_path

## Mock Response Examples

### Complete Mock Setup for Integration Tests
```python
# tests/conftest.py - Shared fixtures for all tests
import pytest
from pathlib import Path
import json

@pytest.fixture
def mock_firecrawl_response():
    """Mock Firecrawl API response"""
    return {
        "content": """
        <h1>Acme Corporation</h1>
        <p>Leading provider of enterprise software solutions.</p>
        <h2>Our Products</h2>
        <p>AcmeFlow - Workflow automation platform</p>
        <p>AcmeSync - Real-time data synchronization</p>
        """,
        "metadata": {
            "title": "Acme Corporation - Enterprise Software",
            "description": "Transform your business with Acme"
        }
    }

@pytest.fixture
def mock_llm_service(monkeypatch):
    """Mock the entire LLM service to return predefined responses"""
    from unittest.mock import AsyncMock
    
    async def mock_llm_call(prompt, model=None, **kwargs):
        # Return different responses based on prompt content
        if "company overview" in prompt.lower():
            return json.dumps({
                "company_name": "Acme Corporation",
                "description": "Enterprise software solutions provider",
                "product_description": "AcmeFlow and AcmeSync platforms",
                "value_proposition": "Streamline operations with AI"
            })
        elif "target account" in prompt.lower():
            return json.dumps({
                "target_account_name": "Mid-Market Tech Companies",
                "firmographics": {
                    "industry": "Technology",
                    "company_size": "500-2000 employees",
                    "revenue_range": "$50M-$500M"
                }
            })
        # Add more conditions as needed
        return json.dumps({"default": "response"})
    
    mock = AsyncMock(side_effect=mock_llm_call)
    monkeypatch.setattr("cli.services.llm_service.LLMClient.generate", mock)
    return mock

@pytest.fixture
def sample_project_data():
    """Complete project data for testing"""
    return {
        "overview": {
            "company_name": "Acme Corporation",
            "description": "Leading enterprise software provider",
            "product_description": "Workflow automation and data sync",
            "value_proposition": "10x productivity gains",
            "_generated_at": "2024-01-01T00:00:00Z"
        },
        "account": {
            "target_account_name": "Growth-Stage SaaS Companies",
            "firmographics": {
                "industry": "Software",
                "company_size": "200-1000 employees",
                "revenue_range": "$20M-$200M",
                "growth_rate": ">40% YoY"
            },
            "_generated_at": "2024-01-01T00:00:00Z"
        },
        "persona": {
            "target_persona_name": "VP of Engineering",
            "demographics": {
                "job_title": "VP Engineering",
                "department": "Engineering",
                "seniority": "VP",
                "team_size": "50-200"
            },
            "psychographics": {
                "pain_points": ["Technical debt", "Team scaling"],
                "goals": ["Improve velocity", "Reduce downtime"]
            },
            "_generated_at": "2024-01-01T00:00:00Z"
        }
    }
```

### Testing Different Scenarios
```python
# tests/cli/test_error_scenarios.py
@pytest.fixture
def mock_llm_timeout(monkeypatch):
    """Mock LLM timeout scenario"""
    import asyncio
    
    async def timeout_response(*args, **kwargs):
        await asyncio.sleep(45)  # Exceed 40s timeout
        return {}
    
    monkeypatch.setattr(
        "cli.services.llm_service.LLMClient.generate",
        timeout_response
    )

@pytest.fixture
def mock_llm_error(monkeypatch):
    """Mock LLM API error"""
    async def error_response(*args, **kwargs):
        raise Exception("API rate limit exceeded")
    
    monkeypatch.setattr(
        "cli.services.llm_service.LLMClient.generate",
        error_response
    )

@pytest.fixture
def mock_corrupted_project(temp_project_dir):
    """Create a project with corrupted JSON"""
    project_path = temp_project_dir / "acme.com"
    project_path.mkdir()
    
    # Write corrupted JSON
    (project_path / "overview.json").write_text("{corrupted json")
    
    return project_path
```

## Test Execution Plan

### Phase 1: Core Functionality (Week 1)
1. Command tests (init, show, export)
2. Service tests (generation, storage)
3. Basic integration tests

### Phase 2: Advanced Features (Week 2)
1. Guided email builder tests
2. Error handling tests
3. UI/UX tests

### Phase 3: Polish (Week 3)
1. End-to-end tests
2. Performance tests
3. Edge case coverage

## Coverage Goals
- Unit test coverage: 80%+
- Integration test coverage: 70%+
- Critical path coverage: 100%

## CI/CD Integration
```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest tests/ -v --cov=cli --cov=app
```

## Test Environment Requirements
- Python 3.11+
- Mock API keys for testing
- Temporary file system access
- Terminal emulation for display tests

## Success Criteria
- All tests pass consistently
- No flaky tests
- Clear error messages on failures
- Fast test execution (<5 minutes total)
- Comprehensive coverage of user scenarios