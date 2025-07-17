#!/usr/bin/env python3
"""Test the search functionality with Playwright MCP."""

import asyncio
from playwright.async_api import async_playwright
import time

async def test_search_feature():
    async with async_playwright() as p:
        # Launch browser in headed mode so we can see what's happening
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("🌐 Navigating to CarGPT...")
            await page.goto("http://localhost:8601", wait_until="networkidle")
            
            # Take initial screenshot
            await page.screenshot(path="/tmp/cargpt_homepage.png")
            print("📸 Homepage screenshot: /tmp/cargpt_homepage.png")
            
            # Find the search input
            search_input = await page.query_selector('input[name="query"]')
            if not search_input:
                print("❌ Search input not found!")
                return
                
            print("✅ Found search input")
            
            # Type a search query
            search_query = "Honda Civic Type R"
            print(f"🔍 Entering search query: '{search_query}'")
            await search_input.fill(search_query)
            
            # Take screenshot with filled search
            await page.screenshot(path="/tmp/search_filled.png")
            print("📸 Search filled screenshot: /tmp/search_filled.png")
            
            # Find and click the search button
            search_button = await page.query_selector('button[type="submit"]')
            if search_button:
                print("🚀 Clicking search button...")
                await search_button.click()
            else:
                print("🚀 Submitting form...")
                await page.press('input[name="query"]', 'Enter')
            
            # Wait for navigation and results
            print("⏳ Waiting for search results...")
            try:
                # Wait for either success message or vehicle cards
                await page.wait_for_selector(".alert-success, .vehicle-card", timeout=30000)
                
                # Check for success message
                success_msg = await page.query_selector(".alert-success")
                if success_msg:
                    msg_text = await success_msg.text_content()
                    print(f"✅ Success message: {msg_text}")
                
                # Wait a bit for page to fully load
                await page.wait_for_timeout(2000)
                
                # Count vehicle cards
                vehicle_cards = await page.query_selector_all(".vehicle-card")
                print(f"📊 Found {len(vehicle_cards)} vehicle listings")
                
                # Take screenshot of results
                await page.screenshot(path="/tmp/search_results.png", full_page=True)
                print("📸 Results screenshot: /tmp/search_results.png")
                
                # Analyze first few results
                if vehicle_cards:
                    print("\n🚗 First 3 vehicles found:")
                    for i, card in enumerate(vehicle_cards[:3]):
                        # Get title
                        title_elem = await card.query_selector("h5, .card-title")
                        title = await title_elem.text_content() if title_elem else "Unknown"
                        
                        # Get price
                        price_elem = await card.query_selector(".price, .listing-price")
                        price = await price_elem.text_content() if price_elem else "No price"
                        
                        # Get source
                        source_elem = await card.query_selector(".data-source, .platform-badge")
                        source = await source_elem.text_content() if source_elem else "Unknown source"
                        
                        print(f"  {i+1}. {title.strip()}")
                        print(f"     💰 {price.strip()}")
                        print(f"     📍 {source.strip()}")
                
                # Test filters
                print("\n🔧 Testing filters...")
                
                # Try price filter
                min_price = await page.query_selector('input[name="price_min"]')
                max_price = await page.query_selector('input[name="price_max"]')
                
                if min_price and max_price:
                    await min_price.fill("20000")
                    await max_price.fill("40000")
                    print("💰 Set price range: $20,000 - $40,000")
                    
                    # Submit search again
                    await page.press('input[name="query"]', 'Enter')
                    await page.wait_for_timeout(3000)
                    
                    filtered_cards = await page.query_selector_all(".vehicle-card")
                    print(f"📊 After filtering: {len(filtered_cards)} vehicles")
                
            except Exception as e:
                print(f"❌ Error during search: {e}")
                await page.screenshot(path="/tmp/search_error.png")
                print("📸 Error screenshot: /tmp/search_error.png")
                
        finally:
            print("\n🎬 Test complete! Browser will close in 5 seconds...")
            await page.wait_for_timeout(5000)
            await browser.close()

if __name__ == "__main__":
    print("🚀 Starting CarGPT Search Test with Playwright\n")
    asyncio.run(test_search_feature())