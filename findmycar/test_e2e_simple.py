#!/usr/bin/env python3
"""
Simple E2E test to verify production search
"""

from playwright.sync_api import sync_playwright
import time

def test_simple_search():
    """Test basic search functionality"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("🧪 Simple E2E Test")
        
        # Go to homepage
        page.goto("http://localhost:8601")
        print("✅ Homepage loaded")
        
        # Take screenshot
        page.screenshot(path="test_homepage.png")
        
        # Type search
        search_input = page.locator("#searchQuery")
        search_input.type("Honda")
        print("✅ Typed search query")
        
        # Click search
        search_button = page.locator("button:has-text('Search')").first
        search_button.click()
        print("✅ Clicked search button")
        
        # Wait a bit
        time.sleep(5)
        
        # Take screenshot
        page.screenshot(path="test_search_results.png")
        
        # Check what's on the page
        page_content = page.content()
        
        # Look for any results
        if "vehicle" in page_content.lower() or "honda" in page_content.lower():
            print("✅ Found vehicle content on page")
        else:
            print("❌ No vehicle content found")
        
        # Check for specific elements
        vehicle_elements = [
            ".vehicle-card",
            ".car-result", 
            ".listing-card",
            "[data-vehicle]",
            ".result-item"
        ]
        
        found_element = None
        for selector in vehicle_elements:
            try:
                if page.locator(selector).count() > 0:
                    found_element = selector
                    break
            except:
                pass
        
        if found_element:
            print(f"✅ Found results using selector: {found_element}")
            count = page.locator(found_element).count()
            print(f"   Total results: {count}")
        else:
            print("❌ No result elements found")
            
        browser.close()

if __name__ == "__main__":
    test_simple_search()