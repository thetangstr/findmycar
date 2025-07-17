#!/usr/bin/env python3
"""Test the EG6 search after fixing the bug."""

import asyncio
from playwright.async_api import async_playwright

async def test_eg6_search_fixed():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("🌐 Loading CarGPT...")
            await page.goto("http://localhost:8601", wait_until="networkidle")
            
            # Find and fill search
            search = await page.query_selector('input[name="query"]')
            await search.fill("honda civic eg6")
            print("✅ Entered: honda civic eg6")
            
            # Submit search
            await page.press('input[name="query"]', 'Enter')
            print("🚀 Search submitted")
            
            # Wait for completion
            print("⏳ Waiting for results...")
            await page.wait_for_timeout(10000)  # Wait 10 seconds
            
            # Check for error
            error = await page.query_selector(".alert-danger")
            if error:
                text = await error.text_content()
                print(f"❌ Error: {text}")
            else:
                print("✅ No error found!")
                
            # Check for success message
            success = await page.query_selector(".alert-success")
            if success:
                text = await success.text_content()
                print(f"✅ Success: {text}")
                
            # Check for vehicles
            vehicles = await page.query_selector_all(".vehicle-card")
            print(f"📊 Vehicles displayed: {len(vehicles)}")
            
            # Get current URL
            url = page.url
            print(f"📍 Final URL: {url}")
            
            # Take screenshot
            await page.screenshot(path="/tmp/eg6_search_fixed.png", full_page=True)
            print("📸 Screenshot: /tmp/eg6_search_fixed.png")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            await page.wait_for_timeout(3000)
            await browser.close()

print("Testing EG6 search after fix...\n")
asyncio.run(test_eg6_search_fixed())