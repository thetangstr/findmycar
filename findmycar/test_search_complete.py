#!/usr/bin/env python3
"""Complete test of search functionality with Playwright."""

import asyncio
from playwright.async_api import async_playwright

async def test_complete_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("🌐 Loading CarGPT homepage...")
            await page.goto("http://localhost:8601", wait_until="networkidle")
            print("✅ Homepage loaded")
            
            # Check initial state
            loading_overlay = await page.query_selector("#loadingOverlay")
            if loading_overlay:
                is_visible = await loading_overlay.is_visible()
                print(f"📍 Loading overlay visible: {is_visible}")
            
            # Count initial vehicles
            initial_vehicles = await page.query_selector_all(".vehicle-card")
            print(f"📊 Initial vehicles shown: {len(initial_vehicles)}")
            
            # Find search input
            search_input = await page.query_selector('input[name="query"]')
            if not search_input:
                print("❌ Search input not found!")
                return
                
            # Enter search query
            search_query = "honda civic eg6"
            print(f"\n🔍 Entering search: '{search_query}'")
            await search_input.fill(search_query)
            
            # Take screenshot before search
            await page.screenshot(path="/tmp/before_search_new.png")
            print("📸 Screenshot: /tmp/before_search_new.png")
            
            # Find and click search button
            search_button = await page.query_selector('#searchForm button[type="submit"]')
            if search_button:
                print("🚀 Clicking search button...")
                await search_button.click()
            else:
                print("🚀 Submitting form...")
                await page.press('input[name="query"]', 'Enter')
            
            # Monitor what happens during search
            print("\n⏳ Monitoring search progress...")
            
            # Wait a moment to see if loading overlay appears
            await page.wait_for_timeout(1000)
            
            # Check if loading overlay is shown
            if loading_overlay:
                is_visible = await loading_overlay.is_visible()
                if is_visible:
                    print("✅ Loading overlay appeared")
                    
                    # Check for progress indicators
                    progress_text = await page.query_selector("#loadingOverlay .text-center")
                    if progress_text:
                        text = await progress_text.text_content()
                        print(f"📊 Progress text: {text[:100]}...")
            
            # Wait for navigation or completion
            print("\n⏳ Waiting for search to complete...")
            try:
                # Wait for either navigation or timeout
                await page.wait_for_url("**/\\?message=*", timeout=60000)
                print("✅ Page redirected with message")
            except:
                print("⚠️  No redirect detected within timeout")
            
            # Check final state
            print("\n📊 Final state check:")
            
            # Check URL
            final_url = page.url
            print(f"📍 Final URL: {final_url}")
            
            # Check if loading overlay is hidden
            if loading_overlay:
                is_visible = await loading_overlay.is_visible()
                print(f"📍 Loading overlay visible: {is_visible}")
                if is_visible:
                    print("❌ Loading overlay still visible - this is the bug!")
                else:
                    print("✅ Loading overlay properly hidden")
            
            # Check for success/error messages
            alerts = await page.query_selector_all(".alert")
            for alert in alerts:
                text = await alert.text_content()
                classes = await alert.get_attribute("class")
                if "alert-success" in classes:
                    print(f"✅ Success: {text.strip()}")
                elif "alert-danger" in classes:
                    print(f"❌ Error: {text.strip()}")
                else:
                    print(f"📢 Alert: {text.strip()}")
            
            # Count final vehicles
            final_vehicles = await page.query_selector_all(".vehicle-card")
            print(f"📊 Vehicles displayed: {len(final_vehicles)}")
            
            # Check search button state
            if search_button:
                is_disabled = await search_button.is_disabled()
                button_text = await search_button.text_content()
                print(f"🔘 Search button - Disabled: {is_disabled}, Text: {button_text.strip()}")
            
            # Take final screenshot
            await page.screenshot(path="/tmp/after_search_complete.png", full_page=True)
            print("\n📸 Final screenshot: /tmp/after_search_complete.png")
            
            # Summary
            print("\n📋 Summary:")
            if "message=" in final_url:
                print("✅ Search completed and redirected properly")
            if loading_overlay and not await loading_overlay.is_visible():
                print("✅ Loading overlay properly hidden after search")
            else:
                print("❌ Loading overlay issue detected")
                
        except Exception as e:
            print(f"\n❌ Test error: {e}")
            await page.screenshot(path="/tmp/test_error.png")
            
        finally:
            print("\n🎬 Test complete! Browser will close in 5 seconds...")
            await page.wait_for_timeout(5000)
            await browser.close()

print("🚗 Testing complete search functionality\n")
asyncio.run(test_complete_search())