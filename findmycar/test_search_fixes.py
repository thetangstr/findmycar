#!/usr/bin/env python3
"""Test the search fixes for async mode and toast messages."""

import asyncio
from playwright.async_api import async_playwright

async def test_search_fixes():
    """Test that async search and improved messages work."""
    
    async with async_playwright() as p:
        print("🧪 Testing search fixes\n")
        
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Enable console logging
        def handle_console(msg):
            print(f"[CONSOLE] {msg.text}")
        page.on("console", handle_console)
        
        try:
            # Navigate to homepage
            print("📍 Navigating to homepage...")
            await page.goto("http://localhost:8601")
            await page.wait_for_load_state("networkidle")
            
            # Verify async search is enabled by default
            async_enabled = await page.is_checked("#useAsyncSearch")
            print(f"✅ Async search enabled: {async_enabled}")
            
            # Fill search form
            print("📝 Filling search form...")
            await page.fill("input[name='query']", "honda civic eg6")
            
            # Take screenshot before search
            await page.screenshot(path="/tmp/before_search_fixed.png")
            
            # Submit search
            print("🔍 Submitting search...")
            await page.click("button[type='submit']")
            
            # Wait for navigation
            await page.wait_for_timeout(2000)
            
            # Check current URL
            current_url = page.url
            print(f"📍 Current URL: {current_url}")
            
            if async_enabled:
                # Should be on progress page if async worked
                if "search" in current_url.lower() or "progress" in current_url.lower():
                    print("✅ Successfully using async search mode")
                    
                    # Wait for search to complete
                    try:
                        await page.wait_for_selector("text=Completed", timeout=60000)
                        print("✅ Search completed")
                    except:
                        print("⚠️ Search still running or no completion indicator")
                    
                    # Take screenshot of progress page
                    await page.screenshot(path="/tmp/async_progress.png")
                    
                else:
                    print("❌ Async search didn't redirect to progress page")
            else:
                # Should be on homepage with results
                if "message=" in current_url:
                    print("✅ Sync search completed with message")
                else:
                    print("❌ Sync search didn't show results")
            
            # Wait for final results
            await page.wait_for_timeout(3000)
            
            # Take final screenshot
            await page.screenshot(path="/tmp/search_results_fixed.png", full_page=True)
            
            # Check for improved messages
            page_content = await page.content()
            if "Found" in page_content and "saved" in page_content:
                print("✅ Improved message format detected")
            else:
                print("❌ Old message format still being used")
            
            # Check if results show correct filtering
            try:
                # Look for vehicle count
                vehicle_count_text = await page.locator("text=/\\d+ vehicles found/").first.text_content()
                if "2 vehicles found" in vehicle_count_text:
                    print("✅ Correct filtering: 2 vehicles found")
                else:
                    print(f"❌ Incorrect filtering: {vehicle_count_text}")
            except:
                print("⚠️ Could not find vehicle count")
            
            print("\n📸 Screenshots saved:")
            print("  - /tmp/before_search_fixed.png")
            print("  - /tmp/async_progress.png (if async)")
            print("  - /tmp/search_results_fixed.png")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            await page.screenshot(path="/tmp/search_fixes_error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_search_fixes())