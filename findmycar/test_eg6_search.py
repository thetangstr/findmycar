#!/usr/bin/env python3
"""Test the EG6 search with Playwright to capture the error."""

import asyncio
from playwright.async_api import async_playwright

async def test_eg6_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Set up console logging
        page.on("console", lambda msg: print(f"🖥️  Console: {msg.text}"))
        
        # Set up response listener
        responses = []
        def handle_response(response):
            if '/ingest' in response.url:
                responses.append({
                    'url': response.url,
                    'status': response.status,
                    'ok': response.ok
                })
        page.on("response", handle_response)
        
        try:
            print("🌐 Navigating to CarGPT...")
            await page.goto("http://localhost:8601", wait_until="networkidle")
            await page.wait_for_timeout(1000)
            
            # Find search input
            search_input = await page.query_selector('input[name="query"]')
            if not search_input:
                print("❌ Search input not found!")
                return
                
            print("✅ Found search input")
            
            # Enter search query
            search_query = "honda civic eg6"
            print(f"🔍 Entering search: '{search_query}'")
            await search_input.fill(search_query)
            await page.wait_for_timeout(500)
            
            # Take screenshot before search
            await page.screenshot(path="/tmp/before_search.png")
            print("📸 Screenshot: /tmp/before_search.png")
            
            # Submit search
            print("🚀 Submitting search...")
            await page.press('input[name="query"]', 'Enter')
            
            # Wait for toast notifications
            print("⏳ Waiting for search progress...")
            await page.wait_for_timeout(3000)
            
            # Check for progress toasts
            toasts = await page.query_selector_all(".toast, .alert-info")
            if toasts:
                print(f"📊 Found {len(toasts)} progress notifications")
                for toast in toasts[:3]:
                    text = await toast.text_content()
                    print(f"   📌 {text.strip()}")
            
            # Wait for search to complete or error
            print("⏳ Waiting for search completion...")
            try:
                # Wait for either error or success
                await page.wait_for_selector(".alert-danger, .vehicle-card", timeout=60000)
            except:
                print("⏱️ Timeout waiting for results")
            
            # Take screenshot after search
            await page.screenshot(path="/tmp/after_search.png", full_page=True)
            print("📸 Screenshot: /tmp/after_search.png")
            
            # Check for error message
            error_alert = await page.query_selector(".alert-danger")
            if error_alert:
                error_text = await error_alert.text_content()
                print(f"❌ Error found: {error_text.strip()}")
            
            # Check HTTP responses
            print(f"\n🌐 HTTP Responses to /ingest:")
            for resp in responses:
                print(f"   - Status: {resp['status']} {'✅' if resp['ok'] else '❌'}")
            
            # Check if spinner is still visible
            spinner = await page.query_selector(".spinner-border:visible, .fa-spinner:visible")
            if spinner:
                print("🔄 Search spinner still visible")
            
            # Check for vehicle results
            vehicles = await page.query_selector_all(".vehicle-card")
            print(f"\n📊 Vehicles found: {len(vehicles)}")
            
            # Get page content for debugging
            page_text = await page.text_content("body")
            if "Internal Server Error" in page_text:
                print("⚠️  'Internal Server Error' found in page")
            if "500" in page_text:
                print("⚠️  HTTP 500 error found in page")
                
        except Exception as e:
            print(f"❌ Test error: {e}")
            await page.screenshot(path="/tmp/error_state.png")
            
        finally:
            print("\n🎬 Test complete! Browser will close in 5 seconds...")
            await page.wait_for_timeout(5000)
            await browser.close()

print("🚗 Testing 'honda civic eg6' search\n")
asyncio.run(test_eg6_search())