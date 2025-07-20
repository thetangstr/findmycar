#!/usr/bin/env python3
"""Test production UI with live eBay data"""

from playwright.sync_api import sync_playwright
import time

def test_production_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser for demo
        page = browser.new_page()
        
        print("=== Testing Production UI with Live eBay Data ===\n")
        
        # Navigate to production app
        page.goto("http://localhost:8603")
        print("✓ Page loaded")
        
        # Wait for search input
        page.wait_for_selector("#searchQuery", timeout=5000)
        
        # Test 1: Search for specific model
        print("\n1. Searching for 'Honda Civic 2015'...")
        page.fill("#searchQuery", "Honda Civic 2015")
        page.click(".input-group-append button")
        
        # Wait for results  
        page.wait_for_selector("#resultsContainer", timeout=10000)
        time.sleep(2)  # Wait for all results to load
        
        # Count results
        results = page.query_selector_all(".vehicle-card")
        print(f"   Found {len(results)} vehicles")
        
        # Check for live data indicator
        live_indicators = page.query_selector_all(".badge.badge-success:has-text('LIVE')")
        print(f"   Live results: {len(live_indicators)}")
        
        # Test 2: Price filter
        print("\n2. Applying price filter (max $15,000)...")
        page.fill("#priceMax", "15000")
        page.click(".input-group-append button")
        
        time.sleep(2)
        filtered_results = page.query_selector_all(".vehicle-card")
        print(f"   Filtered results: {len(filtered_results)}")
        
        # Test 3: Check vehicle details
        print("\n3. Checking vehicle details...")
        if results:
            # Click first result
            first_card = page.query_selector(".vehicle-card")
            if first_card:
                # Get details
                title = first_card.query_selector(".vehicle-title")
                price = first_card.query_selector(".vehicle-price")
                source = first_card.query_selector(".text-muted small")
                
                if title and price:
                    print(f"   First vehicle: {title.inner_text()}")
                    print(f"   Price: {price.inner_text()}")
                    if source:
                        print(f"   Source: {source.inner_text()}")
        
        # Test 4: Search stats
        print("\n4. Search statistics:")
        stats = page.query_selector(".search-stats")
        if stats:
            print(f"   {stats.inner_text()}")
        
        # Show sources used
        source_info = page.query_selector("small:has-text('Sources:')")
        if source_info:
            print(f"   {source_info.inner_text()}")
        
        print("\n5. Taking screenshot...")
        page.screenshot(path="production_search_results.png", full_page=True)
        print("   Screenshot saved as production_search_results.png")
        
        # Keep browser open for 5 seconds to see results
        print("\n✅ Production UI test complete! Keeping browser open for 5 seconds...")
        time.sleep(5)
        
        browser.close()

if __name__ == "__main__":
    test_production_ui()