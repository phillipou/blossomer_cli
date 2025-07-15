#!/usr/bin/env python3
"""
Tests for domain normalization and validation utilities.
"""

import sys
from pathlib import Path

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.utils.domain import normalize_domain


def test_domain_normalization():
    """Test domain normalization utility"""
    print("📋 Testing domain normalization...")
    
    test_cases = [
        ("acme.com", "acme.com", "https://acme.com"),
        ("https://acme.com", "acme.com", "https://acme.com"),
        ("www.acme.com", "acme.com", "https://acme.com"),
        ("http://www.acme.com/about", "acme.com", "https://acme.com")
    ]
    
    for input_domain, expected_domain, expected_url in test_cases:
        result = normalize_domain(input_domain)
        assert result.domain == expected_domain, f"Expected domain {expected_domain}, got {result.domain}"
        assert result.url == expected_url, f"Expected URL {expected_url}, got {result.url}"
        print(f"  ✓ {input_domain} → {result.url}")
    
    print("  ✅ Domain normalization working correctly\n")


if __name__ == "__main__":
    test_domain_normalization()
    print("🎉 All domain utility tests passed!")