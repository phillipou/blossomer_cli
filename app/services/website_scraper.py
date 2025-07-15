import os
import urllib.parse
import socket
import requests
import logging
import re
from urllib import robotparser
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from app.services.dev_file_cache import (
    load_cached_scrape,
    save_scrape_to_cache,
    load_processed_from_cache,
    save_processed_to_cache,
)
import time

# Import debug utility for conditional debug printing
try:
    from cli.utils.debug import debug_print
except ImportError:
    # Fallback if running outside CLI context
    debug_print = print

load_dotenv()

logger = logging.getLogger(__name__)

try:
    from firecrawl import FirecrawlApp, ScrapeOptions
except ImportError:
    FirecrawlApp = None  # type: ignore
    ScrapeOptions = None  # type: ignore

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")


def normalize_url(url: str) -> str:
    """
    Normalize a URL by adding http:// if no scheme is present.
    Basic validation without network calls.
    """
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme:
        url = "http://" + url
        parsed = urllib.parse.urlparse(url)

    # Basic validation
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
    if not parsed.netloc:
        raise ValueError("URL missing network location (domain)")
    if "." not in parsed.netloc:
        raise ValueError("URL netloc must contain a dot (e.g., example.com)")

    return url


def clean_text_for_llm(text: str) -> str:
    """
    Final text cleaning for LLM consumption.

    Firecrawl's .content field already provides well-structured markdown,
    so we focus on removing noise while preserving the good structure.

    - Remove URLs and links
    - Remove excessive whitespace
    - Remove navigation elements
    - Remove contact forms and boilerplate
    - Preserve structured content (headers, lists, paragraphs)
    """
    # Remove URLs and markdown links
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    text = re.sub(url_pattern, "", text)
    # Convert [text](url) to just text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove common navigation and boilerplate patterns
    nav_patterns = [
        r"Skip to (?:main )?content",
        r"Home\s+About\s+(?:Services|Products)\s+Contact",
        r"Menu\s+Toggle",
        r"Search\s+for:",
        r"Cookie Policy",
        r"Privacy Policy",
        r"Terms of Service",
        r"All rights reserved",
        r"Copyright ©.*",
        r"Follow us on",
        r"Subscribe to our newsletter",
        r"Sign up for updates",
    ]
    for pattern in nav_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Remove contact form patterns
    text = re.sub(r"Email\*?\s+Name\*?\s+Message\*?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Your email address\*?", "", text, flags=re.IGNORECASE)

    # Remove social media links and handles
    text = re.sub(r"@\w+", "", text)  # Remove @handles
    text = re.sub(r"#\w+", "", text)  # Remove #hashtags

    # Clean up whitespace (preserve paragraph breaks)
    text = re.sub(r"\n{3,}", "\n\n", text)  # Max 2 consecutive newlines
    text = re.sub(r" {2,}", " ", text)  # Multiple spaces to single space
    text = re.sub(r"\t+", " ", text)  # Tabs to spaces

    # Remove empty lines with just spaces
    lines = text.split("\n")
    cleaned_lines = [line.rstrip() for line in lines if line.strip()]
    text = "\n".join(cleaned_lines)

    return text.strip()


def process_raw_content(content: str, html: str) -> str:
    """
    Process raw Firecrawl content into clean text suitable for LLM consumption.

    Args:
        content (str): Markdown content from Firecrawl
        html (str): HTML content from Firecrawl (unused, but kept for signature consistency)

    Returns:
        str: Clean, processed text with boilerplate removed
    """
    return clean_text_for_llm(content)


def get_processed_website_content(url: str) -> str:
    """
    Get processed website content, using cache if available.
    """
    cached_content = load_processed_from_cache(url)
    if cached_content:
        return cached_content

    raw_content = extract_website_content(url)
    processed_content = process_raw_content(
        raw_content.get("content", ""), raw_content.get("html", "")
    )
    save_processed_to_cache(url, processed_content)
    return processed_content


def validate_url(url: str, user_agent: str = "BlossomerBot") -> dict:
    """
    Validate a website URL for syntax, reachability, and robots.txt compliance.
    Returns a dict with validation results.
    """
    t_total0 = time.monotonic()

    result: dict[str, Any] = {
        "is_valid": False,
        "reason": None,
        "reachable": False,
        "robots_allowed": None,
        "http_status": None,
        "final_url": None,
    }

    # 1. Normalize and parse URL
    t_parse0 = time.monotonic()
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme:
        url = "http://" + url  # Default to http if missing
        parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        result["reason"] = f"Invalid URL scheme: {parsed.scheme}"
        return result
    if not parsed.netloc:
        result["reason"] = "URL missing network location (domain)"
        return result
    # Stricter check: netloc must contain at least one dot (e.g., example.com)
    if "." not in parsed.netloc:
        result["reason"] = "URL netloc must contain a dot (e.g., example.com)"
        return result
    t_parse1 = time.monotonic()
    debug_print(f"[TIMING] URL parsing took {t_parse1 - t_parse0:.3f}s")

    # 2. DNS resolution
    t_dns0 = time.monotonic()
    if not parsed.hostname:
        result["reason"] = "URL missing hostname for DNS resolution"
        return result
    try:
        socket.gethostbyname(parsed.hostname)
    except Exception as e:
        result["reason"] = f"DNS resolution failed: {e}"
        return result
    t_dns1 = time.monotonic()
    debug_print(f"[TIMING] DNS resolution took {t_dns1 - t_dns0:.3f}s")

    # 3. HTTP reachability
    t_http0 = time.monotonic()
    try:
        resp = requests.head(
            url,
            allow_redirects=True,
            timeout=5,
            headers={"User-Agent": user_agent},
        )
        result["http_status"] = resp.status_code
        result["final_url"] = resp.url
        if resp.status_code >= 400:
            result["reason"] = f"HTTP error: {resp.status_code}"
            return result
        result["reachable"] = True
    except Exception as e:
        result["reason"] = f"HTTP request failed: {e}"
        return result
    t_http1 = time.monotonic()
    debug_print(f"[TIMING] HTTP HEAD request took {t_http1 - t_http0:.3f}s")

    # 4. robots.txt compliance
    t_robots0 = time.monotonic()
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        allowed = rp.can_fetch(user_agent, url)
        result["robots_allowed"] = allowed
        if not allowed:
            result["reason"] = "Blocked by robots.txt"
            return result
    except Exception as e:
        logger.warning(f"robots.txt fetch failed for {robots_url}: {e}")
        # If robots.txt is missing/unreachable, default to allow
        result["robots_allowed"] = True
    t_robots1 = time.monotonic()
    debug_print(f"[TIMING] robots.txt check took {t_robots1 - t_robots0:.3f}s")

    result["is_valid"] = True

    t_total1 = time.monotonic()
    debug_print(f"[TIMING] Total URL validation took {t_total1 - t_total0:.3f}s")

    return result


def firecrawl_scrape_url(
    url: str, formats: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Scrape a single web page using Firecrawl and return LLM-ready data as a dict.
    """
    if FirecrawlApp is None:
        raise ImportError(
            "firecrawl-py SDK is not installed. Run 'poetry add firecrawl-py'."
        )
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        logger.error("FIRECRAWL_API_KEY is not set in the environment.")
        raise ValueError("FIRECRAWL_API_KEY is required.")
    app = FirecrawlApp(api_key=api_key)
    if formats is None:
        formats = ["markdown", "html"]
    try:
        scrape_result = app.scrape_url(url, formats=formats)
        return scrape_result.model_dump()
    except Exception as e:
        logger.error(f"Firecrawl scrape_url failed: {e}")
        raise ValueError(f"Firecrawl scrape_url failed: {e}")


def firecrawl_crawl_site(
    url: str,
    limit: int = 5,
    formats: Optional[List[str]] = None,
    only_main_content: bool = True,
    wait_for: int = 1000,
) -> Dict[str, Any]:
    """
    Crawl a website and all accessible subpages using Firecrawl. Returns a dict.
    Args:
        url (str): The root URL to crawl.
        limit (int): Max number of pages to crawl.
        formats (Optional[List[str]]): Output formats, e.g., ['markdown', 'html'].
        only_main_content (bool): If True, extract only the main content of each page.
        wait_for (int): Milliseconds to wait for dynamic content to load.
    Returns:
        Dict[str, Any]: Firecrawl crawl result as a dict.
    """
    if FirecrawlApp is None or ScrapeOptions is None:
        raise ImportError(
            "firecrawl-py SDK is not installed. Run 'poetry add firecrawl-py'."
        )
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        logger.error("FIRECRAWL_API_KEY is not set in the environment.")
        raise ValueError("FIRECRAWL_API_KEY is required.")
    app = FirecrawlApp(api_key=api_key)
    if formats is None:
        formats = ["markdown", "html"]
    try:
        scrape_options = ScrapeOptions(
            formats=formats,
            onlyMainContent=only_main_content,
            waitFor=wait_for,
        )
        crawl_result = app.crawl_url(url, limit=limit, scrape_options=scrape_options)
        return crawl_result.model_dump()
    except Exception as e:
        logger.error(f"Firecrawl crawl_url failed: {e}")
        raise ValueError(f"Firecrawl crawl_url failed: {e}")


def extract_website_content(
    url: str,
    crawl: bool = False,
    crawl_limit: int = 5,
    formats: Optional[List[str]] = None,
    only_main_content: bool = True,
    wait_for: int = 1000,
    return_processed: bool = False,
) -> Dict[str, Any]:
    """
    Validate the URL and extract (but do not store) website content using Firecrawl. Returns a dict.
    Args:
        url (str): The URL to process.
        crawl (bool): If True, crawl all accessible subpages. If False, scrape only the main page.
        crawl_limit (int): Max number of pages to crawl (if crawl=True).
        formats (Optional[List[str]]): Output formats, e.g., ['markdown', 'html'].
        only_main_content (bool): If True, extract only the main content of each page (crawl mode).
        wait_for (int): Milliseconds to wait for dynamic content to load (crawl mode).
        return_processed (bool): If True, return processed content.
    Returns:
        Dict[str, Any]: Structured result with validation, content, and metadata.
    """
    if return_processed:
        cached_processed = load_processed_from_cache(url)
        if cached_processed:
            return {
                "url": url,
                "processed_content": cached_processed,
                "from_cache": True,
            }

    # Use file-based cache in development (not in production)
    if os.getenv("ENV") != "production":
        t_cache0 = time.monotonic()
        cached = load_cached_scrape(url)
        t_cache1 = time.monotonic()
        if cached is not None:
            # Validate cache structure
            if "content" not in cached or "html" not in cached:
                debug_print(
                    f"[DEV CACHE] Cache for {url} missing 'content' or 'html'. "
                    "Forcing fresh scrape."
                )
                cached = None
            elif not cached["content"] and not cached["html"]:
                debug_print(
                    f"[DEV CACHE] Cache for {url} has empty 'content' and 'html'. "
                    "Forcing fresh scrape."
                )
                cached = None
            else:
                cache_time = t_cache1 - t_cache0
                debug_print(
                    f"[DEV CACHE] Cache hit for URL: {url} (retrieval took {cache_time:.2f}s)"
                )
                cached["from_cache"] = True
                return cached
        else:
            debug_print(
                f"[DEV CACHE] Cache miss for URL: {url} (check took {t_cache1 - t_cache0:.2f}s)"
            )

    t_scrape0 = time.monotonic()

    # Step 1: URL Normalization (fast, no network calls)
    t_normalize0 = time.monotonic()
    url = normalize_url(url)
    t_normalize1 = time.monotonic()
    debug_print(f"[TIMING] URL normalization took {t_normalize1 - t_normalize0:.3f}s")

    if formats is None:
        formats = ["markdown", "html"]

    # Step 2: Firecrawl API Call
    t_firecrawl0 = time.monotonic()
    if crawl:
        crawl_result = firecrawl_crawl_site(
            url,
            limit=crawl_limit,
            formats=formats,
            only_main_content=only_main_content,
            wait_for=wait_for,
        )
        # Concatenate all markdown and html from crawled pages
        content = "\n\n".join(
            [page.get("markdown", "") for page in crawl_result.get("data", [])]
        )
        html = "\n\n".join(
            [page.get("html", "") for page in crawl_result.get("data", [])]
        )
        metadata = crawl_result.get("metadata", {})
    else:
        scrape_result = firecrawl_scrape_url(url, formats=formats)
        content = scrape_result.get("markdown", "")
        html = scrape_result.get("html", "")
        metadata = scrape_result.get("metadata", {})
    t_firecrawl1 = time.monotonic()
    debug_print(f"[TIMING] Firecrawl API call took {t_firecrawl1 - t_firecrawl0:.2f}s")

    # Step 3: Content processing
    t_processing0 = time.monotonic()
    processed_content = None
    if return_processed:
        processed_content = process_raw_content(content, html)
        save_processed_to_cache(url, processed_content)

    t_scrape1 = time.monotonic()
    t_processing1 = time.monotonic()
    debug_print(f"[TIMING] Content processing took {t_processing1 - t_processing0:.2f}s")
    debug_print(
        f"[TIMING] Total fresh scrape for URL: {url} took {t_scrape1 - t_scrape0:.2f}s"
    )

    result = {
        "url": url,
        "content": content,
        "html": html,
        "metadata": metadata,
        "crawl": crawl,
        "from_cache": False,
    }
    if processed_content:
        result["processed_content"] = processed_content

    if os.getenv("ENV") != "production":
        save_scrape_to_cache(url, result)
    return result


if __name__ == "__main__":
    from pprint import pprint

    # Example 1: Single page scrape
    url = "https://plandex.ai/"
    try:
        print("=== Single Page Scrape ===")
        result = extract_website_content(url, crawl=False, return_processed=True)
        pprint(result)
    except Exception as e:
        print(f"Single page scrape failed: {e}")

    # Example 2: Multi-page crawl (up to 5 pages)
    try:
        print("\n=== Multi-Page Crawl ===")
        crawl_result = extract_website_content(url, crawl=True, crawl_limit=2)
        pprint(crawl_result)
    except Exception as e:
        print(f"Multi-page crawl failed: {e}")
