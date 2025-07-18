"""
Domain normalization and validation utilities.
"""

import re
from urllib.parse import urlparse
from typing import NamedTuple


class NormalizedDomain(NamedTuple):
    """
    Represents a normalized domain with both clean name and full URL.
    
    Attributes:
        domain: Clean domain name (e.g., "acme.com")
        url: Full HTTPS URL (e.g., "https://acme.com")
    """
    domain: str
    url: str
    
    def __str__(self) -> str:
        """Return the full URL when converting to string"""
        return self.url


def normalize_domain(domain_input: str) -> NormalizedDomain:
    """
    Normalize various domain formats to a consistent format.
    
    Args:
        domain_input: User input (acme.com, www.acme.com, https://acme.com/about, etc.)
        
    Returns:
        NormalizedDomain with clean domain name and full HTTPS URL
    """
    # Strip whitespace
    domain_input = domain_input.strip()
    
    # If it already has a protocol, parse it
    if domain_input.startswith(('http://', 'https://')):
        parsed = urlparse(domain_input)
        domain = parsed.netloc
        
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return NormalizedDomain(domain, f"https://{domain}")
    
    # If it starts with www., remove it
    if domain_input.startswith('www.'):
        domain_input = domain_input[4:]
    
    # Remove any path components (e.g., "acme.com/about" -> "acme.com")
    if '/' in domain_input:
        domain_input = domain_input.split('/')[0]
    
    # Basic domain validation
    if not is_valid_domain_format(domain_input):
        raise ValueError(f"Invalid domain format: {domain_input}")
    
    return NormalizedDomain(domain_input, f"https://{domain_input}")


def is_valid_domain_format(domain: str) -> bool:
    """
    Basic domain format validation.
    
    Args:
        domain: Domain to validate (e.g., "acme.com")
        
    Returns:
        True if domain format looks valid
    """
    # Basic regex for domain validation
    # Allows: letters, numbers, hyphens, and dots
    # Must have at least one dot
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    
    if not re.match(pattern, domain):
        return False
    
    # Must have at least one dot (TLD)
    if '.' not in domain:
        return False
    
    # Can't start or end with hyphen or dot
    if domain.startswith(('-', '.')) or domain.endswith(('-', '.')):
        return False
    
    return True


def get_project_name(domain: str) -> str:
    """
    Convert domain to a safe project directory name.
    
    Args:
        domain: Clean domain name (e.g., "acme.com")
        
    Returns:
        Safe directory name (e.g., "acme.com")
    """
    # For now, just return the domain as-is
    # In the future, we might want to sanitize special characters
    return domain


# Examples for testing
if __name__ == "__main__":
    test_domains = [
        "acme.com",
        "www.acme.com", 
        "https://acme.com",
        "https://www.acme.com/about",
        "http://example.org/path/to/page",
        "sub.domain.co.uk"
    ]
    
    for test in test_domains:
        try:
            result = normalize_domain(test)
            print(f"{test:<30} -> {result.domain:<20} | {result.url}")
        except ValueError as e:
            print(f"{test:<30} -> ERROR: {e}")