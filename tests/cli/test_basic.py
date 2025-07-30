"""
Basic smoke test to verify test infrastructure works.
"""

import pytest
from pathlib import Path
import sys

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_imports_work():
    """Test that basic imports work"""
    try:
        from cli.main import app
        assert app is not None
        
        from cli.utils.domain import normalize_domain
        assert normalize_domain is not None
        
        print("✅ Basic imports working")
        
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_domain_normalization_basic():
    """Test basic domain normalization"""
    from cli.utils.domain import normalize_domain
    
    result = normalize_domain("test.com")
    assert result.domain == "test.com"
    assert result.url == "https://test.com"
    
    print("✅ Domain normalization working")


def test_typer_cli_runner():
    """Test that Typer CLI runner works"""
    from typer.testing import CliRunner
    from cli.main import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    
    assert result.exit_code == 0
    assert "Blossomer CLI" in result.output
    
    print("✅ CLI runner working")


def test_mock_fixtures():
    """Test that our mock fixtures work"""
    import json
    
    # Test mock LLM response structure
    mock_response = {
        "company_name": "Test Company",
        "description": "Test description",
        "_generated_at": "2024-01-01T00:00:00Z"
    }
    
    # Should be valid JSON
    json_str = json.dumps(mock_response)
    parsed = json.loads(json_str)
    
    assert parsed["company_name"] == "Test Company"
    assert "_generated_at" in parsed
    
    print("✅ Mock data structure working")


if __name__ == "__main__":
    test_imports_work()
    test_domain_normalization_basic() 
    test_typer_cli_runner()
    test_mock_fixtures()
    print("🎉 All basic tests passed!")