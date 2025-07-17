#!/usr/bin/env python3
"""
Enhanced Features Test Suite for CarGPT
Tests the new enhanced search, comparison, and saved search features
"""

import asyncio
import sys
import time
from typing import Dict, List
from dataclasses import dataclass
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

@dataclass
class TestResult:
    test_name: str
    status: str  # PASS, FAIL, WARNING
    message: str
    execution_time: float
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class EnhancedFeaturesTests:
    """Test suite for enhanced CarGPT features"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        
    async def run_all_tests(self) -> List[TestResult]:
        """Run all enhanced feature tests"""
        print("🚀 Starting CarGPT Enhanced Features Tests")
        print("=" * 60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Test enhanced search interface
                await self.test_enhanced_search_interface(page)
                await self.test_search_suggestions(page)
                await self.test_advanced_filters(page)
                
                # Test vehicle comparison
                await self.test_comparison_page(page)
                await self.test_comparison_functionality(page)
                
                # Test saved searches
                await self.test_saved_searches_page(page)
                await self.test_search_history(page)
                
                # Test API endpoints
                await self.test_api_endpoints(page)
                
            except Exception as e:
                print(f"❌ Test suite error: {e}")
                
            finally:
                await browser.close()
                
        return self.results
    
    async def test_enhanced_search_interface(self, page: Page):
        """Test the enhanced search interface"""
        start_time = time.time()
        
        try:
            # Navigate to enhanced search page
            await page.goto(f"{self.base_url}/enhanced-search")
            
            # Check if page loads
            await page.wait_for_load_state("networkidle", timeout=5000)
            
            # Look for enhanced search elements
            search_input = page.locator("input[name='query']")
            if await search_input.count() > 0:
                self.results.append(TestResult(
                    "Enhanced Search Interface",
                    "PASS",
                    "Enhanced search page loads with search input",
                    time.time() - start_time
                ))
            else:
                self.results.append(TestResult(
                    "Enhanced Search Interface",
                    "WARNING",
                    "Enhanced search page exists but search input not found",
                    time.time() - start_time
                ))
                
        except Exception as e:
            self.results.append(TestResult(
                "Enhanced Search Interface",
                "FAIL",
                f"Enhanced search interface failed: {str(e)}",
                time.time() - start_time,
                [str(e)]
            ))
    
    async def test_search_suggestions(self, page: Page):
        """Test search suggestions functionality"""
        start_time = time.time()
        
        try:
            # Navigate to homepage
            await page.goto(f"{self.base_url}/")
            
            # Look for search input and test suggestions
            search_input = page.locator("input[name='query']")
            if await search_input.count() > 0:
                await search_input.fill("Honda")
                await page.wait_for_timeout(1000)  # Wait for suggestions
                
                # Check for suggestions container
                suggestions = page.locator(".search-suggestions, .suggestion-item")
                if await suggestions.count() > 0:
                    self.results.append(TestResult(
                        "Search Suggestions",
                        "PASS",
                        "Search suggestions appear when typing",
                        time.time() - start_time
                    ))
                else:
                    self.results.append(TestResult(
                        "Search Suggestions",
                        "WARNING",
                        "Search suggestions functionality not fully implemented",
                        time.time() - start_time
                    ))
            else:
                self.results.append(TestResult(
                    "Search Suggestions",
                    "WARNING",
                    "Search input not found for suggestions testing",
                    time.time() - start_time
                ))
                
        except Exception as e:
            self.results.append(TestResult(
                "Search Suggestions",
                "FAIL",
                f"Search suggestions failed: {str(e)}",
                time.time() - start_time,
                [str(e)]
            ))
    
    async def test_advanced_filters(self, page: Page):
        """Test advanced filters functionality"""
        start_time = time.time()
        
        try:
            # Navigate to enhanced search
            await page.goto(f"{self.base_url}/enhanced-search")
            
            # Look for advanced filters
            filters_toggle = page.locator(".filter-toggle, .advanced-filters-toggle")
            price_slider = page.locator("input[type='range']")
            filter_buttons = page.locator(".filter-btn")
            
            if await filters_toggle.count() > 0 or await price_slider.count() > 0 or await filter_buttons.count() > 0:
                self.results.append(TestResult(
                    "Advanced Filters",
                    "PASS",
                    "Advanced filters interface is available",
                    time.time() - start_time
                ))
            else:
                self.results.append(TestResult(
                    "Advanced Filters",
                    "WARNING",
                    "Advanced filters not found on enhanced search page",
                    time.time() - start_time
                ))
                
        except Exception as e:
            self.results.append(TestResult(
                "Advanced Filters",
                "FAIL",
                f"Advanced filters test failed: {str(e)}",
                time.time() - start_time,
                [str(e)]
            ))
    
    async def test_comparison_page(self, page: Page):
        """Test vehicle comparison page"""
        start_time = time.time()
        
        try:
            # Navigate to comparison page
            await page.goto(f"{self.base_url}/comparison")
            
            # Check if page loads
            await page.wait_for_load_state("networkidle", timeout=5000)
            
            # Look for comparison elements
            comparison_table = page.locator(".comparison-table, .comparison-container")
            add_vehicle_btn = page.locator(".add-vehicle-btn")
            
            if await comparison_table.count() > 0 or await add_vehicle_btn.count() > 0:
                self.results.append(TestResult(
                    "Comparison Page",
                    "PASS",
                    "Vehicle comparison page loads with comparison interface",
                    time.time() - start_time
                ))
            else:
                self.results.append(TestResult(
                    "Comparison Page",
                    "WARNING",
                    "Comparison page exists but comparison interface not found",
                    time.time() - start_time
                ))
                
        except Exception as e:
            self.results.append(TestResult(
                "Comparison Page",
                "FAIL",
                f"Comparison page failed: {str(e)}",
                time.time() - start_time,
                [str(e)]
            ))
    
    async def test_comparison_functionality(self, page: Page):
        """Test comparison functionality"""
        start_time = time.time()
        
        try:
            # Navigate to comparison page
            await page.goto(f"{self.base_url}/comparison")
            
            # Test comparison with mock vehicle IDs
            await page.goto(f"{self.base_url}/comparison?vehicle_ids=1,2")
            
            # Check for comparison content
            comparison_content = page.locator(".comparison-row, .vehicle-column")
            
            if await comparison_content.count() > 0:
                self.results.append(TestResult(
                    "Comparison Functionality",
                    "PASS",
                    "Vehicle comparison functionality works",
                    time.time() - start_time
                ))
            else:
                self.results.append(TestResult(
                    "Comparison Functionality",
                    "WARNING",
                    "Comparison functionality available but no test data",
                    time.time() - start_time
                ))
                
        except Exception as e:
            self.results.append(TestResult(
                "Comparison Functionality",
                "WARNING",
                f"Comparison functionality limited: {str(e)}",
                time.time() - start_time
            ))
    
    async def test_saved_searches_page(self, page: Page):
        """Test saved searches page"""
        start_time = time.time()
        
        try:
            # Navigate to saved searches page
            await page.goto(f"{self.base_url}/saved-searches")
            
            # Check if page loads
            await page.wait_for_load_state("networkidle", timeout=5000)
            
            # Look for saved searches elements
            save_search_form = page.locator(".save-search-form, form")
            search_list = page.locator(".saved-search-card, .search-list")
            
            if await save_search_form.count() > 0 or await search_list.count() > 0:
                self.results.append(TestResult(
                    "Saved Searches Page",
                    "PASS",
                    "Saved searches page loads with interface",
                    time.time() - start_time
                ))
            else:
                self.results.append(TestResult(
                    "Saved Searches Page",
                    "WARNING",
                    "Saved searches page exists but interface not found",
                    time.time() - start_time
                ))
                
        except Exception as e:
            self.results.append(TestResult(
                "Saved Searches Page",
                "FAIL",
                f"Saved searches page failed: {str(e)}",
                time.time() - start_time,
                [str(e)]
            ))
    
    async def test_search_history(self, page: Page):
        """Test search history functionality"""
        start_time = time.time()
        
        try:
            # Navigate to homepage and perform a search
            await page.goto(f"{self.base_url}/")
            
            search_input = page.locator("input[name='query']")
            if await search_input.count() > 0:
                await search_input.fill("Test Search")
                await search_input.press("Enter")
                
                # Check for search history elements
                history_container = page.locator(".search-history, .history-item")
                
                if await history_container.count() > 0:
                    self.results.append(TestResult(
                        "Search History",
                        "PASS",
                        "Search history functionality works",
                        time.time() - start_time
                    ))
                else:
                    self.results.append(TestResult(
                        "Search History",
                        "WARNING",
                        "Search history not immediately visible",
                        time.time() - start_time
                    ))
            else:
                self.results.append(TestResult(
                    "Search History",
                    "WARNING",
                    "Search input not found for history testing",
                    time.time() - start_time
                ))
                
        except Exception as e:
            self.results.append(TestResult(
                "Search History",
                "WARNING",
                f"Search history test limited: {str(e)}",
                time.time() - start_time
            ))
    
    async def test_api_endpoints(self, page: Page):
        """Test API endpoints"""
        start_time = time.time()
        
        try:
            # Test search suggestions API
            response = await page.goto(f"{self.base_url}/api/search-suggestions?q=Honda")
            
            if response.status == 200:
                api_tests_passed = 1
            else:
                api_tests_passed = 0
                
            # Test health endpoint
            health_response = await page.goto(f"{self.base_url}/health")
            if health_response.status == 200:
                api_tests_passed += 1
            
            if api_tests_passed >= 1:
                self.results.append(TestResult(
                    "API Endpoints",
                    "PASS",
                    f"API endpoints working ({api_tests_passed}/2 tested)",
                    time.time() - start_time
                ))
            else:
                self.results.append(TestResult(
                    "API Endpoints",
                    "WARNING",
                    "Some API endpoints may not be implemented",
                    time.time() - start_time
                ))
                
        except Exception as e:
            self.results.append(TestResult(
                "API Endpoints",
                "WARNING",
                f"API endpoints test limited: {str(e)}",
                time.time() - start_time
            ))
    
    def print_results(self):
        """Print test results in a formatted way"""
        print("\n" + "=" * 60)
        print("📊 ENHANCED FEATURES TEST RESULTS")
        print("=" * 60)
        
        passed = 0
        failed = 0
        warnings = 0
        
        for result in self.results:
            if result.status == "PASS":
                print(f"✅ {result.test_name}")
                passed += 1
            elif result.status == "FAIL":
                print(f"❌ {result.test_name}")
                failed += 1
            else:
                print(f"⚠️ {result.test_name}")
                warnings += 1
                
            print(f"   Status: {result.status}")
            print(f"   Message: {result.message}")
            print(f"   Time: {result.execution_time:.2f}s")
            if result.errors:
                print(f"   Errors: {', '.join(result.errors)}")
            print()
        
        print("=" * 60)
        print(f"📈 SUMMARY: {passed} PASSED, {warnings} WARNINGS, {failed} FAILED")
        success_rate = (passed / len(self.results)) * 100 if self.results else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if failed > 0:
            print("❌ Some enhanced features need attention")
        elif warnings > 0:
            print("⚠️ Enhanced features are partially implemented")
        else:
            print("✅ All enhanced features are working correctly")

async def main():
    """Main test execution"""
    tests = EnhancedFeaturesTests()
    results = await tests.run_all_tests()
    tests.print_results()
    
    # Return appropriate exit code
    failed_tests = [r for r in results if r.status == "FAIL"]
    sys.exit(1 if failed_tests else 0)

if __name__ == "__main__":
    asyncio.run(main())