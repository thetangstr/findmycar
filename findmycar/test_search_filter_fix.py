#!/usr/bin/env python3
"""Test that search results are filtered correctly on the homepage."""

import asyncio
from playwright.async_api import async_playwright

async def test_search_filtering():
    """Test that EG6 search shows only filtered results."""
    async with async_playwright() as p:
        print("🚗 Testing Honda Civic EG6 search filtering fix\n")
        
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to homepage
            print("📍 Navigating to homepage...")
            await page.goto("http://localhost:8601")
            await page.wait_for_load_state("networkidle")
            
            # Fill search form
            print("📝 Filling search form with 'honda civic eg6'...")
            await page.fill("input[name='query']", "honda civic eg6")
            
            # Submit search
            print("🔍 Submitting search...")
            await page.click("button[type='submit']")
            
            # Wait for redirect to complete
            print("⏳ Waiting for search results...")
            await page.wait_for_load_state("networkidle")
            
            # Check the URL to verify filters were applied
            current_url = page.url
            print(f"📍 Current URL: {current_url}")
            
            # Check if URL contains expected filters
            expected_filters = ["make=Honda", "model=Civic", "year_min=1992", "year_max=1995"]
            url_has_filters = all(filter_param in current_url for filter_param in expected_filters)
            
            if url_has_filters:
                print("✅ URL contains expected search filters!")
            else:
                print("❌ URL missing expected search filters")
                print(f"   Expected: {expected_filters}")
                print(f"   Found: {current_url}")
            
            # Check if page shows filtered results
            vehicle_cards = await page.locator(".vehicle-card").count()
            print(f"🚗 Found {vehicle_cards} vehicle cards")
            
            # Check if all shown vehicles are Honda Civics
            if vehicle_cards > 0:
                # Get all vehicle makes and models
                makes = await page.locator(".vehicle-make").all_text_contents()
                models = await page.locator(".vehicle-model").all_text_contents()
                years = await page.locator(".vehicle-year").all_text_contents()
                
                honda_civics = 0
                for i, (make, model, year) in enumerate(zip(makes, models, years)):
                    print(f"   Vehicle {i+1}: {year} {make} {model}")
                    if "Honda" in make and "Civic" in model:
                        honda_civics += 1
                
                if honda_civics == vehicle_cards:
                    print(f"✅ All {vehicle_cards} vehicles are Honda Civics!")
                else:
                    print(f"❌ Only {honda_civics} out of {vehicle_cards} vehicles are Honda Civics")
                    print("   Filter not working correctly!")
            else:
                print("ℹ️  No vehicles found (expected for rare EG6)")
            
            # Take screenshot
            await page.screenshot(path="/tmp/search_filter_test.png", full_page=True)
            print("📸 Screenshot saved: /tmp/search_filter_test.png")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            await page.screenshot(path="/tmp/search_filter_error.png")
            print("📸 Error screenshot: /tmp/search_filter_error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_search_filtering())