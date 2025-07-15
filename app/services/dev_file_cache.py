"""
dev_file_cache.py - Simple file-based cache for development environments.

This utility provides two levels of caching:
1.  **Raw Scrape Cache**: Caches the full, raw JSON output from scraping services like Firecrawl.
    This avoids hitting the scraping API repeatedly for the same URL.
2.  **Processed Content Cache**: Caches the clean, text-only content after it has been
    processed by the content preprocessing pipeline. This avoids running the (potentially slow)
    pipeline on the same raw content multiple times.

Both caches are keyed by a hash of the URL and are only active in non-production environments.
"""

import os
import hashlib
import json
import urllib.parse
from typing import Optional, Dict, Any

# Cache for raw website scrape results (JSON objects from Firecrawl)
RAW_SCRAPE_CACHE_DIR = os.path.join(os.path.dirname(__file__), "../../dev_cache/website_scrapes")

# Cache for cleaned, processed content (plain text ready for LLM)
PROCESSED_CONTENT_CACHE_DIR = os.path.join(os.path.dirname(__file__), "../../dev_cache/processed_content")


def canonicalize_url_for_cache(url: str) -> str:
    """Canonicalize URL for consistent cache keys across URL variations."""
    url = url.strip().lower()
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urllib.parse.urlparse(url)
    
    netloc = parsed.netloc
    if netloc.endswith(":443") and parsed.scheme == "https":
        netloc = netloc[:-4]
    elif netloc.endswith(":80") and parsed.scheme == "http":
        netloc = netloc[:-3]
    
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    
    return f"https://{netloc}{path}"


def _url_to_filename(url: str, cache_dir: str) -> str:
    """Hash the canonicalized URL to a filename for a specific cache directory."""
    canonical_url = canonicalize_url_for_cache(url)
    h = hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()
    return os.path.join(cache_dir, f"{h}.json")


# --- Raw Scrape Cache ---

def load_cached_scrape(url: str) -> Optional[Dict[str, Any]]:
    """Load a cached raw scrape result (JSON dict) for a URL."""
    os.makedirs(RAW_SCRAPE_CACHE_DIR, exist_ok=True)
    fname = _url_to_filename(url, RAW_SCRAPE_CACHE_DIR)

    if os.path.exists(fname):
        try:
            with open(fname, "r") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"[DEV CACHE] Error loading raw scrape cache file {fname}: {e}")
            return None
    return None


def save_scrape_to_cache(url: str, data: Dict[str, Any]) -> None:
    """Save a raw scrape result (JSON dict) to the cache."""
    os.makedirs(RAW_SCRAPE_CACHE_DIR, exist_ok=True)
    fname = _url_to_filename(url, RAW_SCRAPE_CACHE_DIR)
    try:
        with open(fname, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"[DEV CACHE] Error saving raw scrape cache file {fname}: {e}")


# --- Processed Content Cache ---

def load_processed_from_cache(url: str) -> Optional[str]:
    """Load cached processed content (plain text) for a URL."""
    os.makedirs(PROCESSED_CONTENT_CACHE_DIR, exist_ok=True)
    fname = _url_to_filename(url, PROCESSED_CONTENT_CACHE_DIR)

    if os.path.exists(fname):
        try:
            with open(fname, "r") as f:
                return f.read()
        except IOError as e:
            print(f"[DEV CACHE] Error loading processed cache file {fname}: {e}")
            return None
    return None


def save_processed_to_cache(url: str, content: str) -> None:
    """Save processed content (plain text) to the cache."""
    os.makedirs(PROCESSED_CONTENT_CACHE_DIR, exist_ok=True)
    fname = _url_to_filename(url, PROCESSED_CONTENT_CACHE_DIR)
    try:
        with open(fname, "w") as f:
            f.write(content)
    except IOError as e:
        print(f"[DEV CACHE] Error saving processed cache file {fname}: {e}")
