#!/usr/bin/env python3
"""Test the search functionality to verify it returns real data."""

import asyncio
from playwright.async_api import async_playwright
import json

async def test_search_functionality():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to the application
            print("📍 Navigating to http://localhost:8601")
            await page.goto("http://localhost:8601", wait_until="networkidle")
            
            # Take a screenshot of the initial page
            await page.screenshot(path="/tmp/homepage.png")
            print("📸 Screenshot saved: /tmp/homepage.png")
            
            # Find the search form
            search_form = await page.query_selector("#searchForm")
            if not search_form:
                print("❌ Search form not found!")
                return
            
            # Look for the main search input
            search_input = await page.query_selector('input[name="query"]')
            if not search_input:
                # Try other selectors
                search_input = await page.query_selector('input#query')
            
            if search_input:
                print("🔍 Found search input box")
                await search_input.fill("Honda Civic under 25000")
                await page.screenshot(path="/tmp/search_filled.png")
                print("📸 Screenshot with search query: /tmp/search_filled.png")
            else:
                print("❌ No search input found!")
                return
            
            # Submit the form
            print("🚀 Submitting search...")
            
            # Listen for network responses
            responses = []
            page.on("response", lambda response: responses.append(response))
            
            # Submit form and wait for navigation
            await page.evaluate("document.querySelector('#searchForm').submit()")
            
            # Wait for results or timeout
            try:
                await page.wait_for_selector(".vehicle-card, .car-card, .listing", timeout=30000)
                print("✅ Search results loaded!")
                
                # Take screenshot of results
                await page.screenshot(path="/tmp/search_results.png", full_page=True)
                print("📸 Results screenshot: /tmp/search_results.png")
                
                # Count results
                results = await page.query_selector_all(".vehicle-card, .car-card, .listing")
                print(f"📊 Found {len(results)} vehicle listings")
                
                # Check if results contain real data
                if results:
                    first_result = results[0]
                    text_content = await first_result.text_content()
                    print(f"\n🚗 First result preview:\n{text_content[:200]}...")
                    
                    # Check for price information
                    price_element = await first_result.query_selector("[class*='price']")
                    if price_element:
                        price = await price_element.text_content()
                        print(f"💰 Price found: {price}")
                    
                    # Check data source
                    source_element = await first_result.query_selector("[class*='source'], [class*='platform']")
                    if source_element:
                        source = await source_element.text_content()
                        print(f"📍 Data source: {source}")
                
                # Check API calls made
                print(f"\n🌐 Network requests made: {len(responses)}")
                for response in responses[-10:]:  # Last 10 requests
                    if "api" in response.url or "search" in response.url:
                        print(f"  - {response.status} {response.url}")
                
            except Exception as e:
                print(f"⏱️ Timeout or error waiting for results: {e}")
                await page.screenshot(path="/tmp/search_error.png")
                print("📸 Error screenshot: /tmp/search_error.png")
                
                # Check page content
                content = await page.content()
                if "error" in content.lower():
                    print("❌ Error message found on page")
                elif "no results" in content.lower():
                    print("📭 No results found message")
                else:
                    print("🤔 Unknown state - check screenshots")
                    
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_search_functionality())