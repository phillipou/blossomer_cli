# Blossomer GTM CLI Test Suite

This directory contains a comprehensive test suite for the Blossomer GTM CLI. **All tests are designed to run without making real API calls or incurring costs.**

## 🚨 Important: Zero Cost Testing

**ALL TESTS USE MOCKED API CALLS** - No real API requests are made to:
- OpenAI/Anthropic APIs
- Firecrawl web scraping service  
- TensorBlock Forge API
- Any other external paid services

If you see real API calls during testing, **STOP IMMEDIATELY** and fix the mocks.

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and mocks
├── cli/                        # CLI-specific tests
│   ├── test_init_command.py    # Init command tests
│   ├── test_show_command.py    # Show command tests
│   ├── test_other_commands.py  # Edit, export, list commands
│   ├── test_services.py        # Service layer tests
│   ├── test_utilities.py       # Utility function tests
│   ├── test_integration.py     # Integration workflow tests
│   ├── test_e2e.py            # End-to-end scenario tests
│   └── test_error_handling.py  # Error handling tests
├── run_tests.py               # Test runner script
├── README.md                  # This file
└── pytest.ini                # Pytest configuration
```

## Test Categories

### Unit Tests
- **Purpose**: Test individual components in isolation
- **Speed**: Fast (< 1 second per test)
- **Coverage**: Commands, services, utilities
- **Files**: `test_*_command.py`, `test_services.py`, `test_utilities.py`

### Integration Tests  
- **Purpose**: Test component interactions and workflows
- **Speed**: Medium (1-5 seconds per test)
- **Coverage**: Complete user workflows, data flow
- **Files**: `test_integration.py`

### End-to-End Tests
- **Purpose**: Test complete user scenarios
- **Speed**: Slower (5-15 seconds per test)
- **Coverage**: Full CLI usage patterns
- **Files**: `test_e2e.py`

### Error Handling Tests
- **Purpose**: Test failure scenarios and recovery
- **Speed**: Medium (1-5 seconds per test)
- **Coverage**: API errors, file system errors, input validation
- **Files**: `test_error_handling.py`

## Running Tests

### Quick Start
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
python tests/run_tests.py

# Or use pytest directly
pytest tests/cli/
```

### Test Runner Options
```bash
# Run specific test categories
python tests/run_tests.py --mode unit          # Unit tests only
python tests/run_tests.py --mode integration   # Integration tests only
python tests/run_tests.py --mode e2e          # End-to-end tests only
python tests/run_tests.py --mode error        # Error handling tests only

# Run fast tests (excludes slow tests)
python tests/run_tests.py --mode fast

# Run smoke tests (basic functionality)
python tests/run_tests.py --mode smoke

# Generate coverage report
python tests/run_tests.py --mode coverage

# Generate HTML test report
python tests/run_tests.py --mode report

# Run code quality checks
python tests/run_tests.py --mode lint
```

### Direct Pytest Usage
```bash
# Run all CLI tests
pytest tests/cli/ -v

# Run specific test file
pytest tests/cli/test_init_command.py -v

# Run specific test class
pytest tests/cli/test_init_command.py::TestInitCommand -v

# Run specific test method
pytest tests/cli/test_init_command.py::TestInitCommand::test_init_yolo_mode_new_domain -v

# Run tests with coverage
pytest tests/cli/ --cov=cli --cov=app --cov-report=html

# Run tests matching pattern
pytest tests/cli/ -k "test_init" -v

# Run tests with markers
pytest tests/cli/ -m "not slow" -v
```

## Mock Strategy

### Comprehensive Mocking
The test suite uses comprehensive mocking to avoid all external API calls:

```python
# All LLM API calls are mocked
@pytest.fixture(autouse=True) 
def mock_all_external_calls(monkeypatch, mock_llm_responses):
    """Automatically mock all external API calls"""
    # Mock LLM service
    async def mock_llm_generate(prompt, model=None, **kwargs):
        # Returns appropriate mock response based on prompt content
        if "company overview" in prompt.lower():
            return json.dumps(mock_llm_responses["overview"])
        # ... more conditions
    
    monkeypatch.setattr("cli.services.llm_service.LLMClient.generate", mock_llm_generate)
    monkeypatch.setattr("app.services.website_scraper.scrape_website", mock_firecrawl)
```

### Smart Mock Responses
Mocks return realistic data that matches the expected schema:

```python
mock_llm_responses = {
    "overview": {
        "company_name": "Acme Corporation",
        "description": "Leading provider of enterprise automation software",
        # ... complete realistic data
        "_generated_at": "2024-01-01T00:00:00Z"
    }
    # ... responses for all steps
}
```

### File System Mocking
Tests use temporary directories to avoid polluting the real file system:

```python
@pytest.fixture
def temp_project_dir(tmp_path, monkeypatch):
    """Create temporary project directory for tests"""
    project_dir = tmp_path / "gtm_projects"
    project_dir.mkdir()
    
    # Mock the project storage to use temp directory
    monkeypatch.setattr("cli.services.project_storage.PROJECT_ROOT", project_dir)
    
    return project_dir
```

## Test Data

### Mock Project Data
Tests use consistent mock data that represents realistic GTM content:

- **Company Overview**: Complete business analysis with products, value props
- **Target Account**: Detailed firmographics and behavioral attributes  
- **Buyer Persona**: Demographics, psychographics, pain points
- **Email Campaign**: Multi-email sequences with subjects and CTAs
- **Strategic Plan**: Complete GTM strategy with frameworks and metrics

### Test Scenarios
Tests cover various scenarios:

- **Happy Path**: Successful generation and viewing
- **Error Cases**: API failures, network issues, file problems
- **Edge Cases**: Invalid inputs, corrupted data, missing files
- **User Workflows**: First-time users, returning users, power users
- **Performance**: Large projects, many projects, timeouts

## Writing New Tests

### Test Structure
Follow this pattern for new tests:

```python
class TestFeatureName:
    """Test suite for specific feature"""
    
    def test_happy_path_scenario(self, mock_cli_runner, temp_project_dir):
        """Test the main success scenario"""
        result = mock_cli_runner.invoke(app, ["command", "args"])
        
        assert result.exit_code == 0
        assert "expected output" in result.output
        
    def test_error_scenario(self, mock_cli_runner, mock_error_scenarios):
        """Test error handling"""
        mock_error_scenarios["set"]("api_error")
        
        result = mock_cli_runner.invoke(app, ["command", "args"])
        
        assert result.exit_code == 1
        assert "error message" in result.output
```

### Naming Conventions
- Test files: `test_*.py`  
- Test classes: `Test*`
- Test methods: `test_*`
- Use descriptive names: `test_init_yolo_mode_new_domain`

### Assertions
Use clear, specific assertions:

```python
# Good - specific checks
assert result.exit_code == 0
assert "Company Overview" in result.output
assert project_dir.exists()

# Avoid - vague checks  
assert result  # Too vague
assert "success" in result.output.lower()  # Too broad
```

### Mock Usage  
Leverage existing fixtures:

```python
def test_with_mocks(self, mock_cli_runner, mock_project_with_data, mock_error_scenarios):
    """Use existing fixtures for consistent testing"""
    # Test implementation
```

## Debugging Tests

### Running Single Tests
```bash
# Run single test with verbose output
pytest tests/cli/test_init_command.py::TestInitCommand::test_init_yolo_mode_new_domain -v -s

# Add debugging output
pytest tests/cli/test_init_command.py::TestInitCommand::test_init_yolo_mode_new_domain -v -s --tb=long
```

### Common Issues

1. **Real API Calls**: If tests make real API calls, check mock setup in `conftest.py`
2. **File Permissions**: Tests may fail if temp directories have wrong permissions
3. **Mock Data**: Ensure mock responses match expected schema
4. **Async Issues**: Use `@pytest.mark.asyncio` for async tests

### Test Output
Tests provide clear output:
- ✅ Success indicators  
- ❌ Failure indicators
- 🧪 Test categories
- 📊 Coverage reports

## Coverage Goals

- **Unit Tests**: 80%+ coverage
- **Integration Tests**: 70%+ coverage  
- **Critical Paths**: 100% coverage
- **Error Handling**: All error scenarios covered

## Continuous Integration

Tests are designed to run in CI/CD environments:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pip install -r requirements-test.txt
    python tests/run_tests.py --mode all --no-mock-check
```

## Performance Benchmarks

Tests include performance checks:
- Full workflow: < 15 seconds (mocked)
- Unit tests: < 1 second each
- Show commands: < 2 seconds
- File operations: < 1 second

## Contributing

When adding new features:

1. **Write tests first** (TDD approach)
2. **Ensure all mocks work** - no real API calls
3. **Test happy path and error cases**
4. **Add integration test for workflows**  
5. **Update this README** if needed

## Questions?

- Check existing tests for patterns
- Review `conftest.py` for available fixtures
- Look at mock strategies in similar tests
- Ask maintainers for guidance

---

🧪 **Remember**: These tests ensure the CLI works correctly without costing money on API calls. Keep the mocks comprehensive and realistic!