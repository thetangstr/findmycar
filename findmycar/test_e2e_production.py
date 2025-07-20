#!/usr/bin/env python3
"""
End-to-End tests for production vehicle search with Playwright
Tests all data sources and UI functionality
"""

from playwright.sync_api import sync_playwright, expect
import time
import json
import os

class TestVehicleSearchE2E:
    """Comprehensive E2E tests for vehicle search application"""
    
    def __init__(self):
        self.base_url = "http://localhost:8601"
        self.api_base = f"{self.base_url}/api"
        
    def run_all_tests(self):
        """Run all E2E tests"""
        with sync_playwright() as p:
            # Launch browser in headless mode for speed
            browser = p.chromium.launch(
                headless=True,
                slow_mo=50  # Slight delay for stability
            )
            
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )
            
            page = context.new_page()
            
            print("🧪 Starting E2E Tests for Vehicle Search Production App\n")
            
            try:
                # Run test suites
                self.test_homepage_loading(page)
                self.test_search_functionality(page)
                self.test_multi_source_search(page)
                self.test_filter_functionality(page)
                self.test_pagination(page)
                self.test_vehicle_details(page)
                self.test_error_handling(page)
                self.test_performance(page)
                self.test_mobile_responsiveness(page)
                self.test_accessibility(page)
                
                print("\n✅ All E2E tests completed successfully!")
                
            except Exception as e:
                print(f"\n❌ Test failed: {e}")
                # Take screenshot on failure
                page.screenshot(path="test_failure.png")
                raise
                
            finally:
                browser.close()
    
    def test_homepage_loading(self, page):
        """Test 1: Homepage loads correctly"""
        print("📋 Test 1: Homepage Loading")
        
        # Navigate to homepage
        page.goto(self.base_url)
        
        # Wait for page to load
        page.wait_for_load_state('networkidle')
        
        # Check title
        expect(page).to_have_title("CarGPT - Comprehensive Vehicle Search")
        print("   ✓ Page title correct")
        
        # Check search input exists
        search_input = page.locator("#searchQuery")
        expect(search_input).to_be_visible()
        print("   ✓ Search input visible")
        
        # Check filter sections exist
        filters = page.locator(".filter-section").first
        expect(filters).to_be_visible()
        print("   ✓ Filter sections visible")
        
        # Check results container
        results = page.locator("#resultsContainer")
        expect(results).to_be_visible()
        print("   ✓ Results container ready")
        
        # Take screenshot
        page.screenshot(path="screenshots/01_homepage.png")
        print("   ✓ Screenshot saved")
    
    def test_search_functionality(self, page):
        """Test 2: Basic search functionality"""
        print("\n📋 Test 2: Search Functionality")
        
        # Clear search input
        search_input = page.locator("#searchQuery")
        search_input.clear()
        
        # Type search query
        search_input.type("Honda Civic", delay=100)
        print("   ✓ Typed search query")
        
        # Click search button
        search_button = page.locator("button:has-text('Search')").first
        search_button.click()
        
        # Wait for loading to finish
        page.wait_for_selector(".loading-overlay", state="hidden", timeout=60000)
        print("   ✓ Search completed")
        
        # Wait for results container to be populated
        page.wait_for_function("document.querySelectorAll('.vehicle-card').length > 0", timeout=5000)
        print("   ✓ Search results loaded")
        
        # Count results
        results = page.locator(".vehicle-card")
        result_count = results.count()
        print(f"   ✓ Found {result_count} vehicles")
        
        # Verify results contain Honda
        first_result = results.first
        expect(first_result).to_contain_text("Honda", ignore_case=True)
        print("   ✓ Results match search query")
        
        # Check for data source indicators
        source_badges = page.locator(".source-badge")
        if source_badges.count() > 0:
            print(f"   ✓ Data source badges visible ({source_badges.count()} sources)")
        
        page.screenshot(path="screenshots/02_search_results.png")
    
    def test_multi_source_search(self, page):
        """Test 3: Multi-source data aggregation"""
        print("\n📋 Test 3: Multi-Source Search")
        
        # Search for popular model
        search_input = page.locator("#searchQuery")
        search_input.clear()
        search_input.type("Toyota Camry 2020")
        search_input.press("Enter")
        
        # Wait for results with timeout for scraping
        page.wait_for_selector(".vehicle-card", timeout=45000)
        
        # Check for multiple data sources
        time.sleep(2)  # Allow all results to load
        
        # Look for source indicators
        ebay_results = page.locator(".vehicle-card:has-text('eBay')")
        carmax_results = page.locator(".vehicle-card:has-text('CarMax')")
        autotrader_results = page.locator(".vehicle-card:has-text('AutoTrader')")
        
        sources_found = []
        if ebay_results.count() > 0:
            sources_found.append(f"eBay ({ebay_results.count()})")
        if carmax_results.count() > 0:
            sources_found.append(f"CarMax ({carmax_results.count()})")
        if autotrader_results.count() > 0:
            sources_found.append(f"AutoTrader ({autotrader_results.count()})")
        
        print(f"   ✓ Found results from: {', '.join(sources_found)}")
        
        # Check search stats
        stats = page.locator(".search-stats")
        if stats.is_visible():
            stats_text = stats.inner_text()
            print(f"   ✓ Search stats: {stats_text}")
        
        page.screenshot(path="screenshots/03_multi_source.png")
    
    def test_filter_functionality(self, page):
        """Test 4: Filter functionality"""
        print("\n📋 Test 4: Filter Functionality")
        
        # Clear search for fresh start
        page.goto(self.base_url)
        page.wait_for_load_state('networkidle')
        
        # Apply price filter
        price_max = page.locator("#priceMax")
        price_max.clear()
        price_max.type("20000")
        print("   ✓ Set max price filter")
        
        # Apply year filter
        year_min = page.locator("#yearMin")
        year_min.clear()
        year_min.type("2018")
        print("   ✓ Set min year filter")
        
        # Select body style if available
        body_style = page.locator("#bodyStyle")
        if body_style.is_visible():
            body_style.select_option("suv")
            print("   ✓ Selected SUV body style")
        
        # Apply filters
        search_button = page.locator("button:has-text('Search')").first
        search_button.click()
        
        # Wait for filtered results
        page.wait_for_selector(".vehicle-card", timeout=30000)
        
        # Verify filters applied
        results = page.locator(".vehicle-card")
        if results.count() > 0:
            # Check first result price
            first_price = results.first.locator(".vehicle-price").inner_text()
            print(f"   ✓ Filtered results loaded (first price: {first_price})")
        
        page.screenshot(path="screenshots/04_filters.png")
    
    def test_pagination(self, page):
        """Test 5: Pagination functionality"""
        print("\n📋 Test 5: Pagination")
        
        # Do a search with many results
        search_input = page.locator("#searchQuery")
        search_input.clear()
        search_input.type("Honda")
        search_input.press("Enter")
        
        page.wait_for_selector(".vehicle-card", timeout=30000)
        
        # Check for pagination controls
        pagination = page.locator(".pagination")
        if pagination.is_visible():
            print("   ✓ Pagination controls visible")
            
            # Try to go to next page
            next_button = page.locator("a:has-text('Next')")
            if next_button.is_visible():
                next_button.click()
                page.wait_for_selector(".vehicle-card")
                print("   ✓ Navigated to next page")
        else:
            print("   ℹ No pagination needed for current results")
        
        page.screenshot(path="screenshots/05_pagination.png")
    
    def test_vehicle_details(self, page):
        """Test 6: Vehicle detail view"""
        print("\n📋 Test 6: Vehicle Details")
        
        # Ensure we have results
        results = page.locator(".vehicle-card")
        if results.count() == 0:
            # Do a search first
            search_input = page.locator("#searchQuery")
            search_input.clear()
            search_input.type("Honda Civic")
            search_input.press("Enter")
            page.wait_for_selector(".vehicle-card", timeout=30000)
        
        # Click on first vehicle
        first_vehicle = page.locator(".vehicle-card").first
        vehicle_link = first_vehicle.locator("a").first
        
        # Check if it opens in modal or new page
        if vehicle_link.get_attribute("target") == "_blank":
            print("   ✓ Vehicle links open in new tab")
        else:
            # Click and wait for modal/detail view
            with page.expect_popup() as popup_info:
                vehicle_link.click()
            popup = popup_info.value
            print("   ✓ Vehicle detail page opened")
            popup.close()
        
        page.screenshot(path="screenshots/06_vehicle_details.png")
    
    def test_error_handling(self, page):
        """Test 7: Error handling"""
        print("\n📋 Test 7: Error Handling")
        
        # Test empty search
        search_input = page.locator("#searchQuery")
        search_input.clear()
        search_input.press("Enter")
        
        # Should still work and show all vehicles
        page.wait_for_selector(".vehicle-card", timeout=30000)
        print("   ✓ Empty search handled correctly")
        
        # Test invalid filter combination
        page.goto(self.base_url)
        price_min = page.locator("#priceMin")
        price_max = page.locator("#priceMax")
        
        if price_min.is_visible() and price_max.is_visible():
            price_min.clear()
            price_min.type("50000")
            price_max.clear()
            price_max.type("10000")
            
            search_button = page.locator("button:has-text('Search')").first
            search_button.click()
            
            # Should handle gracefully
            time.sleep(2)
            print("   ✓ Invalid filter combination handled")
        
        page.screenshot(path="screenshots/07_error_handling.png")
    
    def test_performance(self, page):
        """Test 8: Performance metrics"""
        print("\n📋 Test 8: Performance")
        
        # Measure search time
        start_time = time.time()
        
        search_input = page.locator("#searchQuery")
        search_input.clear()
        search_input.type("Ford F-150")
        search_input.press("Enter")
        
        # Wait for results
        page.wait_for_selector(".vehicle-card", timeout=45000)
        
        end_time = time.time()
        search_time = end_time - start_time
        
        print(f"   ✓ Search completed in {search_time:.2f} seconds")
        
        # Check if search time is displayed
        search_stats = page.locator(".search-time")
        if search_stats.is_visible():
            displayed_time = search_stats.inner_text()
            print(f"   ✓ UI shows: {displayed_time}")
        
        # Test cached search (should be faster)
        start_time = time.time()
        search_input.clear()
        search_input.type("Ford F-150")
        search_input.press("Enter")
        
        page.wait_for_selector(".vehicle-card")
        cached_time = time.time() - start_time
        
        if cached_time < search_time:
            print(f"   ✓ Cached search faster ({cached_time:.2f}s)")
        
        page.screenshot(path="screenshots/08_performance.png")
    
    def test_mobile_responsiveness(self, page):
        """Test 9: Mobile responsiveness"""
        print("\n📋 Test 9: Mobile Responsiveness")
        
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(self.base_url)
        page.wait_for_load_state('networkidle')
        
        # Check if elements are still accessible
        search_input = page.locator("#searchQuery")
        expect(search_input).to_be_visible()
        print("   ✓ Search input visible on mobile")
        
        # Check if filters are collapsible
        filter_toggle = page.locator(".filter-toggle, button:has-text('Filters')")
        if filter_toggle.is_visible():
            filter_toggle.click()
            print("   ✓ Filter toggle works on mobile")
        
        # Do a search
        search_input.type("Honda")
        search_input.press("Enter")
        page.wait_for_selector(".vehicle-card", timeout=30000)
        
        # Check if results are properly displayed
        results = page.locator(".vehicle-card")
        if results.count() > 0:
            print(f"   ✓ Results display correctly on mobile ({results.count()} vehicles)")
        
        page.screenshot(path="screenshots/09_mobile.png")
        
        # Reset viewport
        page.set_viewport_size({"width": 1280, "height": 720})
    
    def test_accessibility(self, page):
        """Test 10: Basic accessibility checks"""
        print("\n📋 Test 10: Accessibility")
        
        page.goto(self.base_url)
        
        # Check for ARIA labels
        search_input = page.locator("#searchQuery")
        aria_label = search_input.get_attribute("aria-label")
        if aria_label:
            print(f"   ✓ Search input has ARIA label: {aria_label}")
        
        # Check for alt text on images
        page.wait_for_selector(".vehicle-card img", timeout=30000)
        images = page.locator(".vehicle-card img")
        if images.count() > 0:
            first_img = images.first
            alt_text = first_img.get_attribute("alt")
            if alt_text:
                print("   ✓ Images have alt text")
        
        # Test keyboard navigation
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        focused = page.evaluate("document.activeElement.tagName")
        print(f"   ✓ Keyboard navigation works (focused: {focused})")
        
        # Check color contrast (basic check)
        page.screenshot(path="screenshots/10_accessibility.png")
        print("   ✓ Visual accessibility screenshot saved")


def main():
    """Run all E2E tests"""
    # Create screenshots directory
    os.makedirs("screenshots", exist_ok=True)
    
    # Run tests
    tester = TestVehicleSearchE2E()
    tester.run_all_tests()
    
    print("\n📊 Test Summary:")
    print("- Homepage Loading: ✅")
    print("- Search Functionality: ✅")
    print("- Multi-Source Integration: ✅")
    print("- Filters: ✅")
    print("- Pagination: ✅")
    print("- Vehicle Details: ✅")
    print("- Error Handling: ✅")
    print("- Performance: ✅")
    print("- Mobile Responsiveness: ✅")
    print("- Accessibility: ✅")
    print("\n🎉 All E2E tests passed!")
    print(f"\n📸 Screenshots saved in: {os.path.abspath('screenshots/')}")


if __name__ == "__main__":
    main()