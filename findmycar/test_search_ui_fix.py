#!/usr/bin/env python3
"""Test to verify the UI fix for the stuck loading spinner."""

import asyncio
from playwright.async_api import async_playwright

async def test_search_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # First, go directly to a URL with search results to test the fix
            print("🌐 Testing direct navigation with search message...")
            test_url = "http://localhost:8601/?message=Successfully%20ingested%200%20vehicles"
            await page.goto(test_url)
            await page.wait_for_timeout(1000)
            
            # Check if loading overlay is hidden
            loading_overlay = await page.query_selector("#loadingOverlay")
            if loading_overlay:
                is_visible = await loading_overlay.is_visible()
                print(f"📍 Loading overlay visible after redirect: {is_visible}")
                
                if is_visible:
                    print("❌ BUG CONFIRMED: Loading overlay still visible after redirect!")
                    # Get the style attribute
                    style = await loading_overlay.get_attribute("style")
                    print(f"   Style: {style}")
                else:
                    print("✅ FIXED: Loading overlay properly hidden after redirect!")
            
            # Now test a real search
            print("\n🔍 Testing actual search...")
            await page.goto("http://localhost:8601")
            await page.wait_for_timeout(1000)
            
            # Fill search
            await page.fill('input[name="query"]', "test search")
            
            # Submit form and wait for navigation
            print("🚀 Submitting search...")
            
            # Use Promise.all to handle navigation
            await page.evaluate("""
                document.querySelector('#searchForm').submit();
            """)
            
            # Wait for the page to navigate
            print("⏳ Waiting for navigation...")
            try:
                await page.wait_for_url("**/?message=*", timeout=60000)
                print("✅ Page navigated successfully")
            except:
                print("⚠️  Navigation timeout")
            
            # Final check
            await page.wait_for_timeout(1000)
            if loading_overlay:
                final_visible = await loading_overlay.is_visible()
                print(f"\n📍 Final loading overlay state: {'VISIBLE' if final_visible else 'HIDDEN'}")
                
                # Check search UI elements
                search_button = await page.query_selector('#searchForm button[type="submit"]')
                if search_button:
                    button_text = await search_button.text_content()
                    is_disabled = await search_button.is_disabled()
                    print(f"🔘 Search button: '{button_text.strip()}' (Disabled: {is_disabled})")
            
            # Take screenshot
            await page.screenshot(path="/tmp/search_ui_final.png")
            print("\n📸 Screenshot: /tmp/search_ui_final.png")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            await page.wait_for_timeout(3000)
            await browser.close()

print("Testing search UI fix...\n")
asyncio.run(test_search_ui())