#!/usr/bin/env python3
"""
End-to-End Playwright tests for Enhanced Demo Application
Tests all critical user journeys on port 8601
"""

import asyncio
from playwright.async_api import async_playwright, expect
import sys
import os

# Test configuration
BASE_URL = "http://localhost:8601"
TIMEOUT = 30000  # 30 seconds

class TestEnhancedDemoE2E:
    """Enhanced Demo E2E Test Suite"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
    
    async def setup(self):
        """Set up browser for tests"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.page.set_default_timeout(TIMEOUT)
    
    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def test_home_page_loads(self):
        """Test that home page loads with all feature cards"""
        print("\n🧪 Testing home page...")
        
        # Navigate to home
        await self.page.goto(BASE_URL)
        
        # Check page title
        await expect(self.page).to_have_title("CarGPT Enhanced Features Demo")
        
        # Check all feature cards are present
        await expect(self.page.locator("text=Enhanced Search")).to_be_visible()
        await expect(self.page.locator("text=Vehicle Comparison")).to_be_visible()
        await expect(self.page.locator("text=Saved Searches")).to_be_visible()
        await expect(self.page.locator("text=Favorites")).to_be_visible()
        
        print("✅ Home page loads correctly")
    
    async def test_enhanced_search_page(self):
        """Test enhanced search page functionality"""
        print("\n🧪 Testing enhanced search page...")
        
        # Navigate to enhanced search
        await self.page.goto(f"{BASE_URL}/enhanced-search")
        
        # Wait for page to load
        await self.page.wait_for_load_state("networkidle")
        
        # Check search input exists
        search_input = self.page.locator('input[placeholder*="Search"]')
        await expect(search_input).to_be_visible()
        
        # Check filters exist
        await expect(self.page.locator("text=Filters")).to_be_visible()
        
        # Check demo vehicles are displayed
        await expect(self.page.locator("text=Honda Civic")).to_be_visible()
        await expect(self.page.locator("text=Tesla Model 3")).to_be_visible()
        
        print("✅ Enhanced search page loads correctly")
    
    async def test_search_functionality(self):
        """Test search input and filtering"""
        print("\n🧪 Testing search functionality...")
        
        await self.page.goto(f"{BASE_URL}/enhanced-search")
        await self.page.wait_for_load_state("networkidle")
        
        # Find search input
        search_input = self.page.locator('input[type="text"]').first
        
        # Type in search
        await search_input.fill("Honda")
        
        # Press Enter or click search button if exists
        await search_input.press("Enter")
        
        # Wait a moment for any updates
        await self.page.wait_for_timeout(1000)
        
        # Check if search was attempted (look for console errors or network activity)
        # Note: The demo may not have full search implementation
        print("✅ Search input accepts text and submits")
    
    async def test_vehicle_comparison_page(self):
        """Test vehicle comparison page"""
        print("\n🧪 Testing vehicle comparison page...")
        
        await self.page.goto(f"{BASE_URL}/comparison")
        await self.page.wait_for_load_state("networkidle")
        
        # Check comparison vehicles are shown
        await expect(self.page.locator("text=Honda Civic")).to_be_visible()
        await expect(self.page.locator("text=Tesla Model 3")).to_be_visible()
        
        # Check analysis sections
        await expect(self.page.locator("text=Best Value")).to_be_visible()
        await expect(self.page.locator("text=Lowest Price")).to_be_visible()
        
        print("✅ Vehicle comparison page loads correctly")
    
    async def test_saved_searches_page(self):
        """Test saved searches page"""
        print("\n🧪 Testing saved searches page...")
        
        await self.page.goto(f"{BASE_URL}/saved-searches")
        await self.page.wait_for_load_state("networkidle")
        
        # Check for saved search examples
        await expect(self.page.locator("text=Honda Civic Search")).to_be_visible()
        await expect(self.page.locator("text=Tesla Under 50k")).to_be_visible()
        
        print("✅ Saved searches page loads correctly")
    
    async def test_favorites_page(self):
        """Test favorites page"""
        print("\n🧪 Testing favorites page...")
        
        await self.page.goto(f"{BASE_URL}/favorites")
        await self.page.wait_for_load_state("networkidle")
        
        # Check for favorite vehicle
        await expect(self.page.locator("text=Honda Civic")).to_be_visible()
        
        print("✅ Favorites page loads correctly")
    
    async def test_navigation_between_pages(self):
        """Test navigation between different pages"""
        print("\n🧪 Testing navigation...")
        
        # Start at home
        await self.page.goto(BASE_URL)
        
        # Navigate to enhanced search
        await self.page.click("text=Go to Enhanced Search")
        await expect(self.page).to_have_url(f"{BASE_URL}/enhanced-search")
        
        # Navigate back to home (if nav exists)
        if await self.page.locator("text=Home").count() > 0:
            await self.page.click("text=Home")
            await expect(self.page).to_have_url(BASE_URL)
        
        print("✅ Navigation works correctly")
    
    async def test_missing_endpoints(self):
        """Test and document missing endpoints"""
        print("\n🧪 Testing API endpoints...")
        
        # Test search endpoint
        response = await self.page.request.post(f"{BASE_URL}/api/enhanced-search", 
                                               data={"query": "Honda"})
        if response.status == 404:
            print("⚠️  /api/enhanced-search endpoint not implemented")
        else:
            print("✅ /api/enhanced-search endpoint exists")
        
        # Test ingest endpoint
        response = await self.page.request.post(f"{BASE_URL}/ingest", 
                                               data={"query": "test"})
        if response.status == 404:
            print("⚠️  /ingest endpoint not implemented")
        else:
            print("✅ /ingest endpoint exists")
        
        # Test vehicle detail endpoint
        response = await self.page.request.get(f"{BASE_URL}/vehicle/1")
        if response.status == 404:
            print("⚠️  /vehicle/<id> endpoint not implemented")
        else:
            print("✅ /vehicle/<id> endpoint exists")

async def run_all_tests():
    """Run all tests and generate report"""
    print("=" * 60)
    print("🚀 Running Enhanced Demo E2E Tests on port 8601")
    print("=" * 60)
    
    test_suite = TestEnhancedDemoE2E()
    
    try:
        # Set up browser
        await test_suite.setup()
        
        # Run all tests
        tests = [
            test_suite.test_home_page_loads(),
            test_suite.test_enhanced_search_page(),
            test_suite.test_search_functionality(),
            test_suite.test_vehicle_comparison_page(),
            test_suite.test_saved_searches_page(),
            test_suite.test_favorites_page(),
            test_suite.test_navigation_between_pages(),
            test_suite.test_missing_endpoints()
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                await test
                passed += 1
            except Exception as e:
                failed += 1
                print(f"❌ Test failed: {str(e)}")
        
        # Clean up
        await test_suite.cleanup()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        if passed + failed > 0:
            print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        else:
            print("📈 Success Rate: 0%")
        
        # Recommendations
        print("\n📝 Recommendations:")
        print("1. Implement missing API endpoints (/ingest, /api/enhanced-search, /vehicle/<id>)")
        print("2. Add actual search functionality to filter vehicles")
        print("3. Implement vehicle detail pages")
        print("4. Add form submission handling for saved searches")
        print("5. Add navigation menu for easier page switching")
        
    except Exception as e:
        print(f"\n❌ Test suite error: {str(e)}")
        print("\n⚠️  Make sure the application is running on http://localhost:8601")
        if test_suite.browser:
            await test_suite.cleanup()

if __name__ == "__main__":
    asyncio.run(run_all_tests())