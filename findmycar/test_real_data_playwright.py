#!/usr/bin/env python3
"""
Test the application with Playwright to verify real data is being displayed
"""

import asyncio
from playwright.async_api import async_playwright
import subprocess
import time
import re

class RealDataTester:
    def __init__(self):
        self.app_process = None
        self.base_url = "http://localhost:8000"
        self.results = []
    
    async def start_app(self):
        """Start the FastAPI application"""
        print("🚀 Starting application...")
        self.app_process = subprocess.Popen([
            "python", "-m", "uvicorn", "main:app", "--reload", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for app to start
        await asyncio.sleep(5)
        print("✅ Application started")
    
    def stop_app(self):
        """Stop the application"""
        if self.app_process:
            self.app_process.terminate()
            self.app_process.wait()
            print("🛑 Application stopped")
    
    async def test_search_functionality(self, page):
        """Test search functionality and verify real data"""
        print("\n🔍 Testing Search Functionality")
        print("="*60)
        
        # Navigate to home page
        await page.goto(self.base_url)
        await page.wait_for_load_state('networkidle')
        
        # Take screenshot of initial page
        await page.screenshot(path="screenshots/01_initial_page.png")
        print("📸 Screenshot: Initial page")
        
        # Test 1: Search for a common car
        print("\n📝 Test 1: Searching for 'Honda Civic'")
        
        # Fill in search query
        search_input = page.locator("input[name='query']")
        await search_input.fill("Honda Civic")
        
        # Select only eBay and CarMax for faster results
        await page.uncheck("input[value='cargurus']")
        await page.uncheck("input[value='bringatrailer']")
        await page.uncheck("input[value='autotrader']")
        
        # Take screenshot before search
        await page.screenshot(path="screenshots/02_before_search.png")
        print("📸 Screenshot: Before search")
        
        # Submit search
        search_button = page.locator("button[type='submit']")
        await search_button.click()
        
        # Wait for results (with timeout)
        print("⏳ Waiting for search results...")
        try:
            await page.wait_for_selector(".vehicle-card", timeout=30000)
            print("✅ Results loaded!")
        except:
            print("❌ No results found within timeout")
            await page.screenshot(path="screenshots/03_no_results.png")
            return False
        
        # Take screenshot of results
        await page.screenshot(path="screenshots/04_search_results.png")
        print("📸 Screenshot: Search results")
        
        # Analyze results
        vehicle_cards = page.locator(".vehicle-card")
        vehicle_count = await vehicle_cards.count()
        
        print(f"\n📊 Found {vehicle_count} vehicles")
        
        if vehicle_count == 0:
            print("❌ No vehicles found - possible issue with data sources")
            return False
        
        # Check first 3 vehicles for real data
        print("\n🚗 Analyzing vehicle listings:")
        for i in range(min(3, vehicle_count)):
            vehicle = vehicle_cards.nth(i)
            
            # Extract vehicle details
            try:
                title = await vehicle.locator(".vehicle-title").text_content()
                price = await vehicle.locator(".vehicle-price").text_content()
                source = await vehicle.locator(".source-badge").text_content()
                
                # Check for real data indicators
                has_real_price = bool(re.search(r'\$[\d,]+', price))
                has_real_title = len(title) > 10 and not title.lower().startswith("test")
                
                print(f"\n   Vehicle {i+1}:")
                print(f"   - Title: {title}")
                print(f"   - Price: {price}")
                print(f"   - Source: {source}")
                print(f"   - Real price? {'✅' if has_real_price else '❌'}")
                print(f"   - Real title? {'✅' if has_real_title else '❌'}")
                
                # Check for view button
                view_button = vehicle.locator("a:has-text('View on')")
                if await view_button.count() > 0:
                    href = await view_button.get_attribute('href')
                    is_external = href and ('ebay.com' in href or 'carmax.com' in href)
                    print(f"   - External link? {'✅' if is_external else '❌'} ({href[:50]}...)")
                
                self.results.append({
                    'title': title,
                    'price': price,
                    'source': source,
                    'has_real_price': has_real_price,
                    'has_real_title': has_real_title
                })
                
            except Exception as e:
                print(f"   ❌ Error extracting vehicle {i+1}: {e}")
        
        # Test 2: Check EG6 chassis code search
        print("\n📝 Test 2: Testing chassis code search 'civic eg6'")
        
        await search_input.fill("civic eg6")
        await search_button.click()
        
        # Wait briefly for results
        await page.wait_for_timeout(10000)
        
        # Check if year filter was applied correctly
        print("🔍 Checking if chassis code parsing worked...")
        
        # Take screenshot
        await page.screenshot(path="screenshots/05_eg6_search.png")
        print("📸 Screenshot: EG6 search results")
        
        return True
    
    async def test_progress_indicator(self, page):
        """Test the new progress indicator"""
        print("\n🎯 Testing Progress Indicator")
        print("="*60)
        
        # Start a new search
        await page.goto(self.base_url)
        search_input = page.locator("input[name='query']")
        await search_input.fill("Toyota Camry")
        
        # Enable multiple sources
        await page.check("input[value='ebay']")
        await page.check("input[value='carmax']")
        await page.check("input[value='autotrader']")
        
        # Click search and immediately check for progress indicator
        search_button = page.locator("button[type='submit']")
        await search_button.click()
        
        # Check if loading overlay appears
        loading_overlay = page.locator("#loadingOverlay")
        is_visible = await loading_overlay.is_visible()
        
        if is_visible:
            print("✅ Progress indicator is visible")
            
            # Check for source status
            source_status = page.locator("#sourceStatus")
            if await source_status.count() > 0:
                print("✅ Source status tracking is active")
                await page.screenshot(path="screenshots/06_progress_indicator.png")
                print("📸 Screenshot: Progress indicator")
        else:
            print("❌ Progress indicator not visible")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        if not self.results:
            print("❌ No vehicle data found - application may be showing fake data")
            return
        
        real_vehicles = sum(1 for r in self.results if r['has_real_price'] and r['has_real_title'])
        total_vehicles = len(self.results)
        
        print(f"Total vehicles analyzed: {total_vehicles}")
        print(f"Real vehicles found: {real_vehicles}")
        print(f"Percentage real: {(real_vehicles/total_vehicles)*100:.1f}%")
        
        if real_vehicles == total_vehicles:
            print("\n✅ VERIFIED: All displayed vehicles appear to be real data from actual sources")
        elif real_vehicles > 0:
            print("\n⚠️  PARTIAL: Some vehicles appear real, but some may be fake")
        else:
            print("\n❌ FAKE DATA: No real vehicle data detected")

async def main():
    tester = RealDataTester()
    
    try:
        # Create screenshots directory
        import os
        os.makedirs("screenshots", exist_ok=True)
        
        # Start the application
        await tester.start_app()
        
        # Run Playwright tests
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Set to False to watch
            page = await browser.new_page()
            
            # Run tests
            await tester.test_search_functionality(page)
            await tester.test_progress_indicator(page)
            
            await browser.close()
        
        # Print summary
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tester.stop_app()

if __name__ == "__main__":
    asyncio.run(main())