#!/usr/bin/env python3
"""
Populate website content cache for evaluation test URLs.
This will use Firecrawl credits once, then cache content for future evaluations.
"""

import sys
import os
import csv

# Add current working directory to path (should be project root)
sys.path.insert(0, os.getcwd())

from app.services.web_content_service import WebContentService

def populate_cache_for_test_urls() -> None:
    """Populate cache for all test URLs in our dataset."""

    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "test_cases.csv"
    )
    url_list = []
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row.get("input_website_url", "").strip()
            if url:
                url_list.append(url)
    test_urls = sorted(set(url_list))
    
    web_service = WebContentService()
    
    print("🚀 Populating website content cache for evaluation...")
    print(f"📝 Processing {len(test_urls)} URLs...")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n[{i}/{len(test_urls)}] Processing: {url}")
        
        try:
            # This will scrape if not cached, or return cached content
            result = web_service.get_content_for_llm(url)
            
            if result and result.get("processed_content"):
                content_length = len(result["processed_content"])
                print(f"✅ Cached content: {content_length} characters")
            else:
                print("❌ Failed to get content")
                
        except Exception as e:
            print(f"❌ Error processing {url}: {e}")
    
    print("\n🎉 Cache population complete!")
    print("💡 Future evaluations will use cached content (no additional Firecrawl credits)")

if __name__ == "__main__":
    populate_cache_for_test_urls()