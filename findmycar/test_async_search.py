#!/usr/bin/env python3
"""Test the async search with real-time progress updates."""

import asyncio
import json
import websockets
from playwright.async_api import async_playwright

async def test_async_search():
    """Test async search with WebSocket progress tracking."""
    
    async with async_playwright() as p:
        print("🚀 Testing async search with real-time progress updates\n")
        
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to homepage
            print("📍 Navigating to homepage...")
            await page.goto("http://localhost:8601")
            await page.wait_for_load_state("networkidle")
            
            # Ensure async search is enabled
            print("✅ Ensuring async search is enabled...")
            await page.check("#useAsyncSearch")
            
            # Fill search form
            print("📝 Filling search form with 'honda civic eg6'...")
            await page.fill("input[name='query']", "honda civic eg6")
            
            # Submit search
            print("🔍 Submitting async search...")
            await page.click("button[type='submit']")
            
            # Wait for redirect to progress page
            print("⏳ Waiting for progress page...")
            await page.wait_for_url("**/search/async*", timeout=10000)
            
            # Check if progress page loaded
            progress_title = await page.locator("h2").first.text_content()
            print(f"📄 Progress page loaded: {progress_title}")
            
            # Wait for search to complete (look for completed status)
            print("⏳ Waiting for search to complete...")
            await page.wait_for_selector("#overall-status.status-completed", timeout=60000)
            
            # Check final status
            final_status = await page.locator("#overall-status").text_content()
            print(f"✅ Search completed with status: {final_status}")
            
            # Check if results redirect appears
            redirect_notice = await page.locator("#redirect-notice").is_visible()
            if redirect_notice:
                print("✅ Redirect notice appeared")
                
                # Wait for auto-redirect or click manual redirect
                try:
                    await page.wait_for_url("**/make=Honda**", timeout=5000)
                    print("✅ Auto-redirected to results page")
                except:
                    print("⚠️ Auto-redirect didn't work, clicking manual redirect...")
                    await page.click("#view-results-btn")
                    await page.wait_for_load_state("networkidle")
            
            # Verify results page
            current_url = page.url
            print(f"📍 Final URL: {current_url}")
            
            # Check if results are filtered
            if "make=Honda" in current_url and "model=Civic" in current_url:
                print("✅ Results page has correct filters!")
                
                # Check vehicle count
                vehicle_count = await page.locator(".vehicle-card").count()
                print(f"🚗 Found {vehicle_count} vehicles")
                
                if vehicle_count > 0:
                    # Check if vehicles are Honda Civics
                    first_vehicle = await page.locator(".vehicle-card").first
                    make_text = await first_vehicle.locator(".card-title").text_content()
                    print(f"📋 First vehicle: {make_text}")
                    
                    if "Honda" in make_text and "Civic" in make_text:
                        print("✅ Vehicles are correctly filtered!")
                    else:
                        print("❌ Vehicles are not correctly filtered")
                else:
                    print("ℹ️ No vehicles found (expected for rare EG6s)")
            else:
                print("❌ Results page doesn't have correct filters")
            
            # Take screenshot
            await page.screenshot(path="/tmp/async_search_test.png", full_page=True)
            print("📸 Screenshot saved: /tmp/async_search_test.png")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            await page.screenshot(path="/tmp/async_search_error.png")
            print("📸 Error screenshot: /tmp/async_search_error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_async_search())