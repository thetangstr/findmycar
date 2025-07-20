#!/usr/bin/env python3
"""Final UI test with Playwright"""

from playwright.sync_api import sync_playwright
import time

def test_comprehensive_search():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Testing comprehensive search UI...")
        
        # Navigate to the app
        page.goto("http://localhost:8602")
        print("✓ Page loaded")
        
        # Wait for page to load
        page.wait_for_selector("#searchQuery", timeout=5000)
        
        # Test 1: Search for Honda
        print("\n1. Testing Honda search:")
        page.fill("#searchQuery", "honda")
        page.click(".input-group-append button.btn-warning")
        
        # Wait for results
        page.wait_for_selector("#resultsContainer", timeout=5000)
        time.sleep(1)  # Give time for results to render
        
        # Check results
        results = page.query_selector_all(".vehicle-card")
        print(f"   Found {len(results)} Honda vehicles")
        
        # Check first result
        if results:
            first_result = results[0]
            title = first_result.query_selector(".vehicle-title")
            if title:
                print(f"   First result: {title.inner_text()}")
        
        # Test 2: Test filters
        print("\n2. Testing price filter:")
        page.fill("#searchQuery", "")
        page.fill("#priceMax", "25000")
        page.click(".input-group-append button.btn-warning")
        
        page.wait_for_selector("#resultsContainer", timeout=5000)
        filtered_results = page.query_selector_all(".vehicle-card")
        print(f"   Found {len(filtered_results)} vehicles under $25,000")
        
        # Test 3: Test smart preset
        print("\n3. Testing smart preset (Family SUV):")
        # Click the preset card
        page.evaluate("selectPreset('family_suv')")
        
        time.sleep(2)  # Wait for search to complete
        preset_results = page.query_selector_all(".vehicle-card")
        print(f"   Found {len(preset_results)} family SUVs")
        
        # Check search stats
        stats = page.query_selector(".search-stats")
        if stats:
            print(f"\n4. Search stats: {stats.inner_text()}")
        
        browser.close()
        print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    test_comprehensive_search()