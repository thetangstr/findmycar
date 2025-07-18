#!/usr/bin/env python3
"""Test current search behavior to understand the toast issue."""

import asyncio
from playwright.async_api import async_playwright

async def test_search_behavior():
    """Test search behavior to identify toast source."""
    
    async with async_playwright() as p:
        print("🧪 Testing search behavior to identify toast issue\n")
        
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"[CONSOLE] {msg.type()}: {msg.text()}"))
        
        try:
            # Navigate to homepage
            print("📍 Navigating to homepage...")
            await page.goto("http://localhost:8601")
            await page.wait_for_load_state("networkidle")
            
            # Check if async search is enabled
            async_enabled = await page.is_checked("#useAsyncSearch")
            print(f"🔄 Async search enabled: {async_enabled}")
            
            # Fill search form
            print("📝 Filling search form with 'honda civic eg6'...")
            await page.fill("input[name='query']", "honda civic eg6")
            
            # Take screenshot before search
            await page.screenshot(path="/tmp/before_search.png")
            
            # Submit search and monitor network/console
            print("🔍 Submitting search...")
            
            # Listen for any network responses
            responses = []
            def handle_response(response):
                responses.append(f"{response.status()} {response.url()}")
                print(f"[NETWORK] {response.status()} {response.url()}")
            
            page.on("response", handle_response)
            
            # Click search button
            await page.click("button[type='submit']")
            
            # Wait a bit to see what happens
            await page.wait_for_timeout(3000)
            
            # Take screenshot after search start
            await page.screenshot(path="/tmp/after_search_start.png")
            
            # Check current URL
            current_url = page.url
            print(f"📍 Current URL: {current_url}")
            
            # Look for any toast/notification elements
            print("🔍 Looking for toast/notification elements...")
            
            # Check for common toast selectors
            toast_selectors = [
                ".toast", ".alert", ".notification", ".message", 
                "[class*='toast']", "[class*='alert']", "[class*='notification']",
                ".semi-transparent", ".overlay"
            ]
            
            for selector in toast_selectors:
                try:
                    elements = await page.locator(selector).count()
                    if elements > 0:
                        print(f"  Found {elements} elements with selector: {selector}")
                        # Get text content
                        for i in range(elements):
                            text = await page.locator(selector).nth(i).text_content()
                            print(f"    Element {i}: {text}")
                except:
                    pass
            
            # Check for any dynamically created elements
            print("🔍 Checking for dynamically created elements...")
            
            # Wait for any async operations to complete
            await page.wait_for_timeout(5000)
            
            # Check if we're on progress page
            if "/search/async" in current_url or "progress" in current_url:
                print("✅ Successfully redirected to progress page")
            else:
                print("❌ Still on homepage or unknown page")
            
            # Take final screenshot
            await page.screenshot(path="/tmp/search_final.png", full_page=True)
            print("📸 Screenshots saved: /tmp/before_search.png, /tmp/after_search_start.png, /tmp/search_final.png")
            
            # Print all network responses
            print("\n📡 Network responses:")
            for response in responses:
                print(f"  {response}")
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            await page.screenshot(path="/tmp/search_error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_search_behavior())