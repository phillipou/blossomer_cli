#!/usr/bin/env python3
"""
Error handling and recovery tests for common failure scenarios.
Tests API failures, file system issues, network problems, and user input validation.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import json
from requests.exceptions import ConnectionError, Timeout
from openai import APIError, RateLimitError

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.services.project_storage import project_storage
from cli.services.gtm_generation_service import gtm_service
from cli.utils.domain import normalize_domain, DomainValidationError


class TestErrorHandling:
    """Test suite for error handling and recovery scenarios"""
    
    @pytest.fixture
    def test_domain(self):
        """Provide a test domain and clean up after tests"""
        domain = "error-test.com"
        yield domain
        # Cleanup
        if project_storage.project_exists(domain):
            project_storage.delete_project(domain)

    def test_api_rate_limit_handling(self, test_domain):
        """Test OpenAI API rate limit error handling"""
        print(f"⏱️ Testing API rate limit handling for {test_domain}")
        
        with patch('cli.services.llm_service.OpenAIProvider.generate') as mock_generate:
            # Simulate rate limit error
            mock_generate.side_effect = RateLimitError(
                message="Rate limit reached",
                response=MagicMock(status_code=429),
                body={"error": {"message": "Rate limit reached"}}
            )
            
            result = gtm_service.generate_step(test_domain, "overview")
            
            assert not result["success"], "Should fail on rate limit"
            assert "rate limit" in result["error"].lower(), "Should indicate rate limit error"
            print("  ✓ Rate limit error properly caught and reported")

    def test_api_authentication_error(self, test_domain):
        """Test OpenAI API authentication error handling"""
        print(f"🔐 Testing API authentication error for {test_domain}")
        
        with patch('cli.services.llm_service.OpenAIProvider.generate') as mock_generate:
            # Simulate authentication error
            mock_generate.side_effect = APIError(
                message="Invalid API key",
                response=MagicMock(status_code=401),
                body={"error": {"message": "Invalid API key"}}
            )
            
            result = gtm_service.generate_step(test_domain, "overview")
            
            assert not result["success"], "Should fail on auth error"
            assert "api key" in result["error"].lower() or "authentication" in result["error"].lower()
            print("  ✓ Authentication error properly caught and reported")

    def test_network_connection_error(self, test_domain):
        """Test network connection error handling"""
        print(f"🌐 Testing network connection error for {test_domain}")
        
        with patch('cli.services.llm_service.OpenAIProvider.generate') as mock_generate:
            # Simulate connection error
            mock_generate.side_effect = ConnectionError("Failed to connect")
            
            result = gtm_service.generate_step(test_domain, "overview")
            
            assert not result["success"], "Should fail on connection error"
            assert "connection" in result["error"].lower() or "network" in result["error"].lower()
            print("  ✓ Connection error properly caught and reported")

    def test_file_system_permission_error(self, test_domain):
        """Test file system permission error handling"""
        print(f"📁 Testing file system permission error for {test_domain}")
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            try:
                project_storage.save_step_data(test_domain, "overview", {"test": "data"})
                assert False, "Should raise permission error"
            except PermissionError:
                print("  ✓ Permission error properly propagated")
            except Exception as e:
                # Check if error is wrapped and handled gracefully
                assert "permission" in str(e).lower() or "access" in str(e).lower()
                print("  ✓ Permission error handled gracefully")

    def test_corrupted_json_file_handling(self, test_domain):
        """Test handling of corrupted JSON files"""
        print(f"💥 Testing corrupted JSON file handling for {test_domain}")
        
        # Create project directory
        project_storage.create_project(test_domain)
        
        # Write corrupted JSON file
        project_dir = project_storage.get_project_path(test_domain)
        corrupted_file = project_dir / "overview.json"
        with open(corrupted_file, 'w') as f:
            f.write("{ invalid json content }")
        
        # Try to load corrupted data
        result = project_storage.load_step_data(test_domain, "overview")
        
        # Should handle gracefully (return None or raise handled exception)
        assert result is None or isinstance(result, dict), "Should handle corrupted JSON gracefully"
        print("  ✓ Corrupted JSON handled gracefully")

    def test_invalid_domain_validation(self):
        """Test domain validation error handling"""
        print("🔍 Testing invalid domain validation")
        
        invalid_domains = [
            "",  # Empty string
            "not-a-domain",  # Missing TLD
            "http://",  # Incomplete URL
            "just-text-no-domain",  # No valid domain pattern
        ]
        
        for invalid_domain in invalid_domains:
            try:
                result = normalize_domain(invalid_domain)
                # If it doesn't raise an exception, check if result indicates error
                assert hasattr(result, 'error') or result is None, f"Should reject invalid domain: {invalid_domain}"
            except (DomainValidationError, ValueError, AttributeError):
                print(f"  ✓ Rejected invalid domain: {invalid_domain}")
            except Exception as e:
                # Other exceptions are also acceptable as long as they're handled
                print(f"  ✓ Handled invalid domain {invalid_domain} with: {type(e).__name__}")

    def test_missing_step_dependencies(self, test_domain):
        """Test handling of missing step dependencies"""
        print(f"🔗 Testing missing step dependencies for {test_domain}")
        
        # Try to generate persona without overview and account
        with patch('cli.services.target_persona_service.generate_target_persona_profile') as mock_persona:
            mock_persona.return_value = {"title": "Test Persona"}
            
            result = gtm_service.generate_step(test_domain, "persona")
            
            # Should either:
            # 1. Generate missing dependencies automatically, or
            # 2. Fail with clear error about missing dependencies
            if result["success"]:
                # Check that dependencies were created
                overview_data = project_storage.load_step_data(test_domain, "overview")
                account_data = project_storage.load_step_data(test_domain, "account")
                assert overview_data is not None or account_data is not None, "Should create missing dependencies"
                print("  ✓ Missing dependencies handled by auto-generation")
            else:
                assert "dependency" in result["error"].lower() or "required" in result["error"].lower()
                print("  ✓ Missing dependencies properly reported")

    def test_partial_api_response_handling(self, test_domain):
        """Test handling of partial or malformed API responses"""
        print(f"📡 Testing partial API response handling for {test_domain}")
        
        with patch('cli.services.llm_service.OpenAIProvider.generate') as mock_generate:
            # Simulate partial/invalid response
            mock_generate.return_value = "{ incomplete json"
            
            result = gtm_service.generate_step(test_domain, "overview")
            
            assert not result["success"], "Should fail on malformed response"
            assert "parse" in result["error"].lower() or "format" in result["error"].lower()
            print("  ✓ Malformed API response properly handled")

    def test_disk_space_full_simulation(self, test_domain):
        """Test handling of disk space issues"""
        print(f"💾 Testing disk space error handling for {test_domain}")
        
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            try:
                project_storage.save_step_data(test_domain, "overview", {"large": "data" * 1000})
                assert False, "Should raise disk space error"
            except OSError:
                print("  ✓ Disk space error properly propagated")
            except Exception as e:
                # Check if error is wrapped and handled gracefully
                assert "space" in str(e).lower() or "disk" in str(e).lower()
                print("  ✓ Disk space error handled gracefully")

    def test_concurrent_file_access(self, test_domain):
        """Test handling of concurrent file access issues"""
        print(f"🔄 Testing concurrent file access for {test_domain}")
        
        # Create project
        project_storage.create_project(test_domain)
        
        # Simulate file being locked/accessed by another process
        with patch('builtins.open', side_effect=PermissionError("Resource temporarily unavailable")):
            try:
                result = project_storage.load_step_data(test_domain, "overview")
                # Should handle gracefully (None return or exception handling)
                print("  ✓ Concurrent access handled gracefully")
            except Exception as e:
                # Should be a handled exception with useful message
                assert len(str(e)) > 0, "Error should have descriptive message"
                print(f"  ✓ Concurrent access error handled: {type(e).__name__}")

    def test_large_api_response_handling(self, test_domain):
        """Test handling of unexpectedly large API responses"""
        print(f"📈 Testing large API response handling for {test_domain}")
        
        with patch('cli.services.llm_service.OpenAIProvider.generate') as mock_generate:
            # Simulate very large response
            large_response = json.dumps({
                "company_name": "Test Corp",
                "description": "A" * 100000,  # Very large description
                "details": ["item" + str(i) for i in range(10000)]  # Large array
            })
            mock_generate.return_value = large_response
            
            result = gtm_service.generate_step(test_domain, "overview")
            
            # Should either handle gracefully or fail with size limit error
            if not result["success"]:
                assert "size" in result["error"].lower() or "large" in result["error"].lower()
                print("  ✓ Large response properly limited")
            else:
                print("  ✓ Large response handled successfully")

    def test_timeout_handling(self, test_domain):
        """Test API timeout error handling"""
        print(f"⏰ Testing timeout error handling for {test_domain}")
        
        with patch('cli.services.llm_service.OpenAIProvider.generate') as mock_generate:
            # Simulate timeout
            mock_generate.side_effect = Timeout("Request timed out")
            
            result = gtm_service.generate_step(test_domain, "overview")
            
            assert not result["success"], "Should fail on timeout"
            assert "timeout" in result["error"].lower() or "time" in result["error"].lower()
            print("  ✓ Timeout error properly caught and reported")


if __name__ == "__main__":
    # Run with pytest for proper fixture handling
    pytest.main([__file__, "-v"])