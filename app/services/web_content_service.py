"""
Web Content Service - High-level interface for website content extraction.

Provides a clean API for getting website content with dual caching:
1. Raw Firecrawl response cache
2. Processed text cache ready for LLM consumption
"""

from typing import Dict, Any, Optional
from app.services.website_scraper import (
    extract_website_content,
    process_raw_content,
)
from app.services.dev_file_cache import (
    load_processed_from_cache,
    save_processed_to_cache,
)
import time
import os
import re
from dataclasses import dataclass


@dataclass
class WebContentConfig:
    """Configuration for web content processing."""

    # Cache settings
    enable_caching: bool = os.getenv("ENV") != "production"
    cache_ttl_hours: int = int(os.getenv("WEB_CACHE_TTL_HOURS", "24"))

    # Processing settings
    min_content_length: int = int(os.getenv("MIN_CONTENT_LENGTH", "50"))
    max_content_length: int = int(os.getenv("MAX_CONTENT_LENGTH", "5000"))

    # Firecrawl settings
    enable_crawling: bool = os.getenv("ENABLE_SITE_CRAWLING", "false").lower() == "true"
    max_crawl_pages: int = int(os.getenv("MAX_CRAWL_PAGES", "5"))

    # Quality thresholds
    min_quality_score: int = int(os.getenv("MIN_QUALITY_SCORE", "20"))
    min_word_count: int = int(os.getenv("MIN_WORD_COUNT", "100"))


class WebContentService:
    """Service for extracting and caching website content."""

    def __init__(self, config: Optional[WebContentConfig] = None):
        self.config = config or WebContentConfig()

    def get_content_for_llm(
        self, url: str, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get processed website content optimized for LLM consumption.

        Args:
            url (str): Website URL to scrape
            force_refresh (bool): Skip cache and force fresh scrape

        Returns:
            Dict containing:
            - processed_content: Clean text for LLM
            - metadata: Scraping metadata
            - cache_status: "processed_hit" | "raw_hit" | "fresh_scrape"
        """
        if not self.config.enable_caching:
            force_refresh = True

        # Check processed cache first (unless force refresh)
        if not force_refresh:
            cached_processed = load_processed_from_cache(url)
            if cached_processed:
                return {
                    "processed_content": cached_processed,
                    "cache_status": "processed_hit",
                    "metadata": {"source": "processed_cache"},
                    "processed_content_length": len(cached_processed),
                }

        # Get raw content (may hit raw cache or call Firecrawl)
        raw_result = extract_website_content(url)

        # Process the content
        processed_content = process_raw_content(
            content=raw_result.get("content", ""), html=raw_result.get("html", "")
        )

        # Cache processed content
        if self.config.enable_caching:
            save_processed_to_cache(url, processed_content)

        cache_status = "raw_hit" if raw_result.get("from_cache") else "fresh_scrape"

        return {
            "processed_content": processed_content,
            "cache_status": cache_status,
            "metadata": raw_result.get("metadata", {}),
            "raw_content_length": len(raw_result.get("content", "")),
            "processed_content_length": len(processed_content),
        }

    @staticmethod
    def analyze_content_quality(processed_content: str) -> Dict[str, Any]:
        """
        Analyze the quality of processed content for LLM consumption.

        Returns metrics about content richness, structure, and suitability.
        """
        # Basic metrics
        word_count = len(processed_content.split())
        char_count = len(processed_content)

        # Structure detection
        headers = len(re.findall(r"^#+\s", processed_content, re.MULTILINE))
        lists = len(re.findall(r"^\s*[-*+]\s", processed_content, re.MULTILINE))
        paragraphs = len(re.findall(r"\n\s*\n", processed_content))

        # Content type detection
        has_product_info = bool(
            re.search(
                r"(features?|benefits?|pricing|solutions?)",
                processed_content,
                re.IGNORECASE,
            )
        )
        has_company_info = bool(
            re.search(
                r"(about|company|team|mission|founded)",
                processed_content,
                re.IGNORECASE,
            )
        )
        has_contact_info = bool(
            re.search(
                r"(contact|email|phone|address)", processed_content, re.IGNORECASE
            )
        )

        # Quality assessment
        quality_score = min(100, (word_count / 10) + (headers * 5) + (lists * 2))

        return {
            "word_count": word_count,
            "char_count": char_count,
            "structure": {"headers": headers, "lists": lists, "paragraphs": paragraphs},
            "content_types": {
                "has_product_info": has_product_info,
                "has_company_info": has_company_info,
                "has_contact_info": has_contact_info,
            },
            "quality_score": quality_score,
            "is_sufficient": quality_score > 20 and word_count > 100,
        }

    @staticmethod
    def debug_content_pipeline(url: str) -> Dict[str, Any]:
        """
        Debug the content processing pipeline for a URL.
        Shows cache status, processing steps, and content quality.
        """
        debug_info = {"url": url, "timestamp": time.time(), "steps": []}

        # Step 1: Check processed cache
        start_time = time.monotonic()
        cached_processed = load_processed_from_cache(url)
        cache_check_time = time.monotonic() - start_time

        debug_info["steps"].append(
            {
                "step": "processed_cache_check",
                "duration_ms": cache_check_time * 1000,
                "result": "hit" if cached_processed else "miss",
                "content_length": len(cached_processed) if cached_processed else 0,
            }
        )

        if cached_processed:
            debug_info["content_quality"] = WebContentService.analyze_content_quality(
                cached_processed
            )
            return debug_info

        # Step 2: Get raw content
        start_time = time.monotonic()
        raw_result = extract_website_content(url)
        raw_fetch_time = time.monotonic() - start_time

        debug_info["steps"].append(
            {
                "step": "raw_content_fetch",
                "duration_ms": raw_fetch_time * 1000,
                "cache_status": "hit" if raw_result.get("from_cache") else "fresh",
                "raw_content_length": len(raw_result.get("content", "")),
                "html_length": len(raw_result.get("html", "")),
            }
        )

        # Step 3: Process content
        start_time = time.monotonic()
        processed = process_raw_content(
            content=raw_result.get("content", ""), html=raw_result.get("html", "")
        )
        process_time = time.monotonic() - start_time

        debug_info["steps"].append(
            {
                "step": "content_processing",
                "duration_ms": process_time * 1000,
                "processed_length": len(processed),
                "compression_ratio": len(processed)
                / max(len(raw_result.get("content", "")), 1),
            }
        )

        debug_info["content_quality"] = WebContentService.analyze_content_quality(
            processed
        )

        return debug_info
