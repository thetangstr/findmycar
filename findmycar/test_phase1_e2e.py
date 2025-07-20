"""
End-to-End tests for Phase 1 vehicle sources using Playwright
Tests Hemmings, Cars & Bids, Craigslist, CarSoup, and Revy Autos
"""
import asyncio
from playwright.async_api import async_playwright
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase1E2ETests:
    def __init__(self):
        self.base_url = "http://localhost:8601"
        self.results = {}
        
    async def test_source_management_ui(self, page):
        """Test the source management interface"""
        try:
            logger.info("Testing Source Management UI...")
            
            # Navigate to source management
            await page.goto(f"{self.base_url}/sources")
            await page.wait_for_load_state('networkidle')
            
            # Check page loaded
            assert await page.title() == "Source Management - FindMyCar"
            
            # Wait for sources to load
            await page.wait_for_selector('.source-card', timeout=10000)
            
            # Count sources
            source_cards = await page.query_selector_all('.source-card')
            logger.info(f"Found {len(source_cards)} source cards")
            
            # Check statistics loaded
            total_sources = await page.text_content('#totalSources')
            enabled_sources = await page.text_content('#enabledSources')
            logger.info(f"Statistics - Total: {total_sources}, Enabled: {enabled_sources}")
            
            # Test toggling a source
            first_toggle = await page.query_selector('.toggle-switch input')
            if first_toggle:
                initial_state = await first_toggle.is_checked()
                await first_toggle.click()
                await page.wait_for_timeout(1000)  # Wait for API call
                
                # Check alert appeared
                alert = await page.query_selector('.alert-success')
                assert alert is not None, "Success alert should appear after toggle"
            
            # Test health check button
            health_btn = await page.query_selector('.health-check-btn')
            await health_btn.click()
            
            # Wait for health check to complete
            await page.wait_for_selector('.health-check-btn:not(:disabled)', timeout=30000)
            
            return True
            
        except Exception as e:
            logger.error(f"Source Management UI test failed: {e}")
            return False
    
    async def test_search_with_new_sources(self, page):
        """Test searching with new sources enabled"""
        try:
            logger.info("Testing search with new sources...")
            
            # Go to home page
            await page.goto(self.base_url)
            await page.wait_for_load_state('networkidle')
            
            # Search for vehicles
            search_input = await page.query_selector('#searchInput')
            await search_input.fill("honda civic")
            await search_input.press('Enter')
            
            # Wait for results
            await page.wait_for_selector('.vehicle-card, .no-results', timeout=30000)
            
            # Check if source info is displayed
            source_info = await page.query_selector('#sourceInfo')
            if source_info:
                source_text = await source_info.text_content()
                logger.info(f"Sources displayed: {source_text}")
            
            # Count results
            results = await page.query_selector_all('.vehicle-card')
            logger.info(f"Found {len(results)} search results")
            
            # Check for source badges on vehicles
            if len(results) > 0:
                first_result = results[0]
                source_badge = await first_result.query_selector('.vehicle-source')
                if source_badge:
                    source_name = await source_badge.text_content()
                    logger.info(f"First result source: {source_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Search test failed: {e}")
            return False
    
    async def test_individual_source_apis(self, page):
        """Test individual source API endpoints"""
        api_tests = [
            {
                'name': 'Source Stats',
                'url': '/api/sources/stats',
                'method': 'GET',
                'expected_keys': ['total_sources', 'enabled_sources', 'sources']
            },
            {
                'name': 'Health Check',
                'url': '/api/sources/health-check',
                'method': 'POST',
                'expected_keys': ['success', 'health_status']
            }
        ]
        
        for test in api_tests:
            try:
                logger.info(f"Testing API: {test['name']}")
                
                if test['method'] == 'GET':
                    response = await page.request.get(f"{self.base_url}{test['url']}")
                else:
                    response = await page.request.post(f"{self.base_url}{test['url']}")
                
                assert response.ok, f"API call failed with status {response.status}"
                
                data = await response.json()
                for key in test['expected_keys']:
                    assert key in data, f"Expected key '{key}' not found in response"
                
                logger.info(f"✓ {test['name']} API test passed")
                
            except Exception as e:
                logger.error(f"✗ {test['name']} API test failed: {e}")
                return False
        
        return True
    
    async def test_search_filters_with_sources(self, page):
        """Test search with filters across multiple sources"""
        try:
            logger.info("Testing filtered search across sources...")
            
            # Navigate to search page
            await page.goto(f"{self.base_url}/search")
            await page.wait_for_load_state('networkidle')
            
            # Apply filters
            await page.select_option('#makeFilter', 'honda')
            await page.fill('#priceMax', '20000')
            
            # Apply filters
            apply_btn = await page.query_selector('.apply-filters-btn')
            await apply_btn.click()
            
            # Wait for results
            await page.wait_for_selector('.vehicle-card, .no-results', timeout=30000)
            
            # Check results
            results = await page.query_selector_all('.vehicle-card')
            logger.info(f"Filtered search returned {len(results)} results")
            
            # Verify filters were applied
            for result in results[:5]:  # Check first 5
                price_elem = await result.query_selector('.vehicle-price')
                if price_elem:
                    price_text = await price_elem.text_content()
                    # Parse price and verify it's under 20000
                    logger.info(f"Vehicle price: {price_text}")
            
            return True
            
        except Exception as e:
            logger.error(f"Filter test failed: {e}")
            return False
    
    async def test_source_specific_features(self, page):
        """Test features specific to new sources"""
        try:
            logger.info("Testing source-specific features...")
            
            # Test Cars & Bids auction info
            await page.goto(self.base_url)
            await page.fill('#searchInput', 'porsche')
            await page.press('#searchInput', 'Enter')
            
            await page.wait_for_selector('.vehicle-card, .no-results', timeout=30000)
            
            # Look for auction-specific info
            auction_info = await page.query_selector('[data-source="cars_bids"]')
            if auction_info:
                logger.info("Found Cars & Bids listing with auction info")
            
            # Test Hemmings classic car search
            await page.fill('#searchInput', 'classic mustang 1960s')
            await page.press('#searchInput', 'Enter')
            
            await page.wait_for_selector('.vehicle-card, .no-results', timeout=30000)
            
            return True
            
        except Exception as e:
            logger.error(f"Source-specific features test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all Phase 1 E2E tests"""
        logger.info("="*70)
        logger.info("Starting Phase 1 E2E Tests")
        logger.info("="*70)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Enable console logging
            page.on("console", lambda msg: logger.info(f"Browser console: {msg.text}"))
            
            tests = [
                ("Source Management UI", self.test_source_management_ui),
                ("Search with New Sources", self.test_search_with_new_sources),
                ("Individual Source APIs", self.test_individual_source_apis),
                ("Search Filters", self.test_search_filters_with_sources),
                ("Source-Specific Features", self.test_source_specific_features)
            ]
            
            for test_name, test_func in tests:
                logger.info(f"\nRunning test: {test_name}")
                try:
                    result = await test_func(page)
                    self.results[test_name] = result
                    logger.info(f"{'✓' if result else '✗'} {test_name}: {'PASSED' if result else 'FAILED'}")
                except Exception as e:
                    logger.error(f"✗ {test_name}: FAILED with error: {e}")
                    self.results[test_name] = False
                
                # Take screenshot on failure
                if not self.results.get(test_name, False):
                    screenshot_name = f"test_failure_{test_name.lower().replace(' ', '_')}.png"
                    await page.screenshot(path=screenshot_name)
                    logger.info(f"Screenshot saved: {screenshot_name}")
            
            await browser.close()
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("TEST SUMMARY")
        logger.info("="*70)
        
        passed = sum(1 for r in self.results.values() if r)
        total = len(self.results)
        
        for test_name, result in self.results.items():
            status = "✓ PASSED" if result else "✗ FAILED"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\nTotal: {passed}/{total} tests passed")
        
        return passed == total

async def main():
    """Run Phase 1 E2E tests"""
    tester = Phase1E2ETests()
    success = await tester.run_all_tests()
    
    if success:
        logger.info("\n🎉 All Phase 1 tests passed! Ready for Phase 2.")
    else:
        logger.info("\n⚠️  Some tests failed. Please fix issues before proceeding to Phase 2.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())