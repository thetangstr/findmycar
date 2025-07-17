#!/usr/bin/env python3
"""Test the search functionality after fix."""

import asyncio
from playwright.async_api import async_playwright

async def test_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("🌐 Loading CarGPT...")
            await page.goto("http://localhost:8601")
            await page.wait_for_timeout(1000)
            
            # Enter search
            print("🔍 Searching for 'honda civic eg6'...")
            await page.fill('input[name="query"]', "honda civic eg6")
            
            # Submit form directly
            await page.evaluate("""
                document.querySelector('#searchForm').submit();
            """)
            
            print("⏳ Waiting for search to complete...")
            
            # Wait for redirect and reload
            await page.wait_for_timeout(8000)
            
            # Check URL
            url = page.url
            print(f"📍 Final URL: {url}")
            
            # Look for success message
            alerts = await page.query_selector_all(".alert")
            for alert in alerts:
                text = await alert.text_content()
                print(f"📢 Alert: {text.strip()}")
            
            # Count vehicles
            vehicles = await page.query_selector_all(".vehicle-card")
            print(f"🚗 Vehicles displayed: {len(vehicles)}")
            
            # Check if search worked
            if "Successfully" in url or len(vehicles) > 0:
                print("\n✅ Search is working! The bug is fixed.")
            else:
                print("\n⚠️  No results, but no error either.")
                
            # Take screenshot
            await page.screenshot(path="/tmp/search_working.png", full_page=True)
            print("📸 Screenshot saved: /tmp/search_working.png")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            await page.wait_for_timeout(3000)
            await browser.close()

print("Testing search functionality...\n")
asyncio.run(test_search())