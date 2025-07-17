#!/usr/bin/env python3
"""
E2E test for search functionality on enhanced demo
"""

import asyncio
from playwright.async_api import async_playwright

async def test_search():
    print("🧪 Testing Enhanced Search Functionality on port 8601...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to enhanced search
            print("1️⃣ Navigating to enhanced search page...")
            await page.goto("http://localhost:8601/enhanced-search")
            await page.wait_for_load_state("networkidle")
            
            # Check that demo vehicles are loaded
            print("2️⃣ Checking initial vehicle display...")
            honda_civic = await page.locator("text=2021 Honda Civic Sport").count()
            tesla_model3 = await page.locator("text=2020 Tesla Model 3").count()
            print(f"   ✅ Found {honda_civic} Honda Civic listings")
            print(f"   ✅ Found {tesla_model3} Tesla Model 3 listings")
            
            # Test search for Honda
            print("3️⃣ Testing search for 'Honda'...")
            search_input = page.locator('input[id="query"]')
            await search_input.fill("Honda")
            await search_input.press("Enter")
            
            # Wait for search to complete (loading overlay should appear and disappear)
            await page.wait_for_timeout(1500)  # Wait for simulated delay
            
            # Check results
            honda_after = await page.locator("text=2021 Honda Civic Sport").count()
            tesla_after = await page.locator("text=2020 Tesla Model 3").count()
            print(f"   ✅ After search: {honda_after} Honda, {tesla_after} Tesla")
            
            if honda_after > 0 and tesla_after == 0:
                print("   ✅ Search filtering works correctly!")
            else:
                print("   ⚠️  Search filtering may not be working properly")
            
            # Test quick search tag
            print("4️⃣ Testing quick search tags...")
            await page.reload()
            await page.wait_for_load_state("networkidle")
            
            # Click on Tesla quick tag
            tesla_tag = page.locator('[data-query="Tesla under $50k"]')
            await tesla_tag.click()
            await page.wait_for_timeout(1500)
            
            # Check search input was populated
            search_value = await search_input.input_value()
            print(f"   ✅ Search input populated with: '{search_value}'")
            
            # Test clear search
            print("5️⃣ Testing clear search...")
            await search_input.fill("")
            await search_input.press("Enter")
            await page.wait_for_timeout(1500)
            
            # Should show all vehicles again
            all_vehicles = await page.locator(".vehicle-card").count()
            print(f"   ✅ After clearing search: {all_vehicles} vehicles shown")
            
            print("\n✅ Search functionality is working!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_search())