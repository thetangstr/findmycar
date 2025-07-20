#!/usr/bin/env python3
"""Test comprehensive search UI with Playwright"""

import asyncio
from playwright.async_api import async_playwright
import json

async def test_comprehensive_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("1. Loading comprehensive search page...")
        await page.goto("http://localhost:8602")
        await page.wait_for_load_state('networkidle')
        
        # Take screenshot of initial page
        await page.screenshot(path="comprehensive_search_initial.png")
        print("✓ Screenshot saved: comprehensive_search_initial.png")
        
        # Check if page loaded properly
        title = await page.title()
        print(f"✓ Page title: {title}")
        
        # Check for any console errors
        page.on("console", lambda msg: print(f"Console: {msg.type()}: {msg.text()}"))
        
        print("\n2. Testing basic search...")
        # Try a simple search
        search_input = page.locator("#searchQuery")
        await search_input.fill("honda")
        
        # Click search button (be more specific)
        search_button = page.locator(".input-group-append button.btn-warning")
        await search_button.click()
        
        # Wait for results
        await page.wait_for_timeout(3000)
        
        # Take screenshot after search
        await page.screenshot(path="comprehensive_search_after.png")
        print("✓ Screenshot saved: comprehensive_search_after.png")
        
        # Check results
        try:
            results_text = await page.locator("#resultCount").text_content()
            print(f"✓ Results found: {results_text}")
        except:
            print("❌ Could not find result count")
        
        # Try API directly
        print("\n3. Testing API directly...")
        api_response = await page.evaluate("""
            async () => {
                const response = await fetch('/api/search/v2?query=honda');
                return await response.json();
            }
        """)
        
        print(f"API Response: {json.dumps(api_response, indent=2)}")
        
        # Check for vehicles in the response
        if 'vehicles' in api_response:
            print(f"\n✓ Total vehicles from API: {api_response.get('total', 0)}")
            if api_response['vehicles']:
                print("Sample vehicle:")
                print(json.dumps(api_response['vehicles'][0], indent=2))
        
        # Test filters
        print("\n4. Testing filters...")
        
        # Test body style filter
        suv_filter = page.locator("[data-value='suv']")
        await suv_filter.click()
        await page.wait_for_timeout(500)
        
        # Apply filters
        apply_button = page.locator("button:has-text('Apply Filters')")
        await apply_button.click()
        await page.wait_for_timeout(2000)
        
        # Check filtered results
        try:
            filtered_count = await page.locator("#resultCount").text_content()
            print(f"✓ SUV filter results: {filtered_count}")
        except:
            print("❌ Could not find filtered result count")
        
        await page.screenshot(path="comprehensive_search_filtered.png")
        print("✓ Screenshot saved: comprehensive_search_filtered.png")
        
        # Keep browser open for 5 seconds
        await page.wait_for_timeout(5000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_comprehensive_search())