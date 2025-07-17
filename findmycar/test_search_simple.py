#!/usr/bin/env python3
"""Simple test to verify search functionality."""

import asyncio
from playwright.async_api import async_playwright

async def test_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("🌐 Loading CarGPT homepage...")
            await page.goto("http://localhost:8601")
            
            # Check page loaded
            title = await page.title()
            print(f"✅ Page loaded: {title}")
            
            # Count initial vehicles
            initial_cards = await page.query_selector_all(".vehicle-card")
            print(f"📊 Initial vehicles displayed: {len(initial_cards)}")
            
            # Find search form
            search_input = await page.query_selector('input[name="query"]')
            if not search_input:
                print("❌ Search input not found")
                return
            
            # Search for Honda
            print("\n🔍 Testing search for 'Honda'...")
            await search_input.fill("Honda")
            
            # Submit form
            await page.evaluate("""
                document.querySelector('form').submit();
            """)
            
            # Wait for response
            print("⏳ Waiting for search results...")
            await page.wait_for_timeout(3000)
            
            # Check URL
            current_url = page.url
            print(f"📍 Current URL: {current_url}")
            
            # Check for success message
            alert = await page.query_selector(".alert")
            if alert:
                alert_text = await alert.text_content()
                print(f"📢 Alert message: {alert_text.strip()}")
            
            # Count vehicles after search
            result_cards = await page.query_selector_all(".vehicle-card")
            print(f"📊 Vehicles after search: {len(result_cards)}")
            
            # Check if results are different
            if len(result_cards) != len(initial_cards):
                print("✅ Search results updated!")
            else:
                print("⚠️  Results count unchanged")
            
            # Sample a vehicle if available
            if result_cards:
                first = result_cards[0]
                title_elem = await first.query_selector("h5")
                if title_elem:
                    vehicle_title = await title_elem.text_content()
                    print(f"\n🚗 Sample vehicle: {vehicle_title}")
                    
                    # Check if it's a Honda
                    if "Honda" in vehicle_title:
                        print("✅ Search filter working - found Honda vehicle")
                    else:
                        print(f"⚠️  Vehicle doesn't match search term")
                        
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="/tmp/error.png")
            
        finally:
            await browser.close()

print("Starting CarGPT Search Test\n")
asyncio.run(test_search())
print("\nTest complete!")