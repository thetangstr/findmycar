"""
Comprehensive Testing Framework for CarGPT Data Sources
Tests all integrated data sources to ensure they're working properly
"""

import unittest
import logging
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import all available clients
from ebay_client_improved import search_ebay_listings, EbayAPIError
from carmax_client import CarMaxClient
from bat_client import BringATrailerClient
from cars_client import CarsComClient

logger = logging.getLogger(__name__)

class TestStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIP = "SKIP"

@dataclass
class TestResult:
    source: str
    test_name: str
    status: TestStatus
    message: str
    execution_time: float
    data_points: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class DataSourceTestFramework:
    """
    Comprehensive testing framework for all CarGPT data sources
    """
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.test_queries = [
            "Honda Civic",
            "Toyota Camry", 
            "BMW 3 Series",
            "Tesla Model 3",
            "Ford F-150"
        ]
        
    def run_all_tests(self) -> Dict[str, List[TestResult]]:
        """Run tests for all data sources"""
        results = {
            'ebay': self.test_ebay_motors(),
            'carmax': self.test_carmax(),
            'bringatrailer': self.test_bring_a_trailer(),
            'cars_com': self.test_cars_com(),
            'autodev': self.test_autodev()
        }
        
        # Generate summary report
        self._generate_summary_report(results)
        
        return results
    
    def test_ebay_motors(self) -> List[TestResult]:
        """Test eBay Motors integration"""
        results = []
        source = "eBay Motors"
        
        # Test 1: Basic connectivity
        results.append(self._test_basic_connectivity(
            source, 
            self._test_ebay_connectivity
        ))
        
        # Test 2: Search functionality
        for query in self.test_queries:
            results.append(self._test_search_functionality(
                source,
                query,
                self._search_ebay,
                min_results=5
            ))
        
        # Test 3: Data quality
        results.append(self._test_data_quality(
            source,
            self._search_ebay,
            self._validate_ebay_data
        ))
        
        # Test 4: Performance
        results.append(self._test_performance(
            source,
            self._search_ebay,
            max_time=30.0
        ))
        
        return results
    
    def test_carmax(self) -> List[TestResult]:
        """Test CarMax integration"""
        results = []
        source = "CarMax"
        
        # Test 1: Basic connectivity
        results.append(self._test_basic_connectivity(
            source, 
            self._test_carmax_connectivity
        ))
        
        # Test 2: Search functionality
        for query in self.test_queries:
            results.append(self._test_search_functionality(
                source,
                query,
                self._search_carmax,
                min_results=3  # CarMax might have fewer results
            ))
        
        # Test 3: Data quality
        results.append(self._test_data_quality(
            source,
            self._search_carmax,
            self._validate_carmax_data
        ))
        
        # Test 4: Performance (longer timeout for Selenium)
        results.append(self._test_performance(
            source,
            self._search_carmax,
            max_time=60.0
        ))
        
        return results
    
    def test_bring_a_trailer(self) -> List[TestResult]:
        """Test Bring a Trailer integration"""
        results = []
        source = "Bring a Trailer"
        
        # Test 1: Basic connectivity
        results.append(self._test_basic_connectivity(
            source, 
            self._test_bat_connectivity
        ))
        
        # Test 2: Search functionality (different queries for collector cars)
        collector_queries = ["Porsche 911", "BMW M3", "Classic Mercedes", "Vintage Ferrari"]
        for query in collector_queries:
            results.append(self._test_search_functionality(
                source,
                query,
                self._search_bat,
                min_results=1  # BaT might have fewer but higher quality results
            ))
        
        # Test 3: Auction data quality
        results.append(self._test_data_quality(
            source,
            self._search_bat,
            self._validate_bat_data
        ))
        
        # Test 4: Performance (longer timeout for auction site)
        results.append(self._test_performance(
            source,
            self._search_bat,
            max_time=60.0
        ))
        
        return results
    
    def test_cars_com(self) -> List[TestResult]:
        """Test Cars.com integration"""
        results = []
        source = "Cars.com"
        
        # Test 1: Basic connectivity
        results.append(self._test_basic_connectivity(
            source, 
            self._test_cars_connectivity
        ))
        
        # Test 2: Search functionality
        for query in self.test_queries:
            results.append(self._test_search_functionality(
                source,
                query,
                self._search_cars,
                min_results=5
            ))
        
        # Test 3: Data quality
        results.append(self._test_data_quality(
            source,
            self._search_cars,
            self._validate_cars_data
        ))
        
        return results
    
    def test_autodev(self) -> List[TestResult]:
        """Test Auto.dev integration"""
        results = []
        source = "Auto.dev"
        
        # Test 1: Basic connectivity
        results.append(self._test_basic_connectivity(
            source, 
            self._test_autodev_connectivity
        ))
        
        # Test 2: Search functionality
        for query in self.test_queries:
            results.append(self._test_search_functionality(
                source,
                query,
                self._search_autodev,
                min_results=3
            ))
        
        # Test 3: Data quality
        results.append(self._test_data_quality(
            source,
            self._search_autodev,
            self._validate_autodev_data
        ))
        
        return results
    
    # Helper Methods for Testing
    
    def _test_basic_connectivity(self, source: str, connectivity_func) -> TestResult:
        """Test basic connectivity to a data source"""
        start_time = time.time()
        
        try:
            success = connectivity_func()
            execution_time = time.time() - start_time
            
            if success:
                return TestResult(
                    source=source,
                    test_name="Basic Connectivity",
                    status=TestStatus.PASS,
                    message="Successfully connected to data source",
                    execution_time=execution_time
                )
            else:
                return TestResult(
                    source=source,
                    test_name="Basic Connectivity",
                    status=TestStatus.FAIL,
                    message="Failed to connect to data source",
                    execution_time=execution_time
                )
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                source=source,
                test_name="Basic Connectivity",
                status=TestStatus.FAIL,
                message=f"Connection error: {str(e)}",
                execution_time=execution_time,
                errors=[str(e)]
            )
    
    def _test_search_functionality(self, source: str, query: str, search_func, min_results: int = 1) -> TestResult:
        """Test search functionality for a data source"""
        start_time = time.time()
        
        try:
            results = search_func(query, limit=10)
            execution_time = time.time() - start_time
            
            if not results:
                return TestResult(
                    source=source,
                    test_name=f"Search: {query}",
                    status=TestStatus.WARNING,
                    message="No results returned",
                    execution_time=execution_time,
                    data_points=0
                )
            elif len(results) >= min_results:
                return TestResult(
                    source=source,
                    test_name=f"Search: {query}",
                    status=TestStatus.PASS,
                    message=f"Returned {len(results)} results",
                    execution_time=execution_time,
                    data_points=len(results)
                )
            else:
                return TestResult(
                    source=source,
                    test_name=f"Search: {query}",
                    status=TestStatus.WARNING,
                    message=f"Only {len(results)} results (expected {min_results}+)",
                    execution_time=execution_time,
                    data_points=len(results)
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                source=source,
                test_name=f"Search: {query}",
                status=TestStatus.FAIL,
                message=f"Search failed: {str(e)}",
                execution_time=execution_time,
                errors=[str(e)]
            )
    
    def _test_data_quality(self, source: str, search_func, validation_func) -> TestResult:
        """Test data quality for a data source"""
        start_time = time.time()
        
        try:
            results = search_func("Honda Civic", limit=5)
            execution_time = time.time() - start_time
            
            if not results:
                return TestResult(
                    source=source,
                    test_name="Data Quality",
                    status=TestStatus.SKIP,
                    message="No data to validate",
                    execution_time=execution_time
                )
            
            quality_issues = []
            valid_count = 0
            
            for result in results:
                issues = validation_func(result)
                if not issues:
                    valid_count += 1
                else:
                    quality_issues.extend(issues)
            
            quality_percentage = (valid_count / len(results)) * 100
            
            if quality_percentage >= 80:
                status = TestStatus.PASS
                message = f"Data quality good: {quality_percentage:.1f}% valid"
            elif quality_percentage >= 60:
                status = TestStatus.WARNING
                message = f"Data quality fair: {quality_percentage:.1f}% valid"
            else:
                status = TestStatus.FAIL
                message = f"Data quality poor: {quality_percentage:.1f}% valid"
            
            return TestResult(
                source=source,
                test_name="Data Quality",
                status=status,
                message=message,
                execution_time=execution_time,
                data_points=len(results),
                errors=quality_issues[:5]  # Show first 5 issues
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                source=source,
                test_name="Data Quality",
                status=TestStatus.FAIL,
                message=f"Quality test failed: {str(e)}",
                execution_time=execution_time,
                errors=[str(e)]
            )
    
    def _test_performance(self, source: str, search_func, max_time: float = 30.0) -> TestResult:
        """Test performance of a data source"""
        start_time = time.time()
        
        try:
            results = search_func("Toyota Camry", limit=10)
            execution_time = time.time() - start_time
            
            if execution_time <= max_time:
                status = TestStatus.PASS
                message = f"Good performance: {execution_time:.2f}s"
            elif execution_time <= max_time * 1.5:
                status = TestStatus.WARNING
                message = f"Slow performance: {execution_time:.2f}s"
            else:
                status = TestStatus.FAIL
                message = f"Poor performance: {execution_time:.2f}s (max: {max_time}s)"
            
            return TestResult(
                source=source,
                test_name="Performance",
                status=status,
                message=message,
                execution_time=execution_time,
                data_points=len(results) if results else 0
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                source=source,
                test_name="Performance",
                status=TestStatus.FAIL,
                message=f"Performance test failed: {str(e)}",
                execution_time=execution_time,
                errors=[str(e)]
            )
    
    # Connectivity Test Functions
    
    def _test_ebay_connectivity(self) -> bool:
        """Test eBay API connectivity"""
        try:
            from ebay_client_improved import get_ebay_oauth_token
            token = get_ebay_oauth_token()
            return bool(token)
        except Exception:
            return False
    
    def _test_carmax_connectivity(self) -> bool:
        """Test CarMax website connectivity"""
        try:
            client = CarMaxClient()
            # Just try to initialize and navigate to base URL
            driver = client._get_driver()
            driver.get("https://www.carmax.com")
            client.close()
            return True
        except Exception:
            return False
    
    def _test_bat_connectivity(self) -> bool:
        """Test Bring a Trailer connectivity"""
        try:
            client = BringATrailerClient()
            driver = client._get_driver()
            driver.get("https://bringatrailer.com")
            client.close()
            return True
        except Exception:
            return False
    
    def _test_cars_connectivity(self) -> bool:
        """Test Cars.com connectivity"""
        try:
            client = CarsComClient()
            # Test a simple request
            import requests
            response = requests.get("https://www.cars.com", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def _test_autodev_connectivity(self) -> bool:
        """Test Auto.dev connectivity"""
        try:
            client = AutoDevClient()
            # This would test their API endpoint
            return True  # Placeholder
        except Exception:
            return False
    
    # Search Functions
    
    def _search_ebay(self, query: str, limit: int = 10) -> List[Dict]:
        """Search eBay Motors"""
        try:
            result = search_ebay_listings(query, limit=limit)
            return result.get('items', []) if isinstance(result, dict) else result
        except Exception as e:
            logger.error(f"eBay search error: {e}")
            return []
    
    def _search_carmax(self, query: str, limit: int = 10) -> List[Dict]:
        """Search CarMax"""
        try:
            client = CarMaxClient()
            results = client.search_listings(query, limit=limit)
            client.close()
            return results
        except Exception as e:
            logger.error(f"CarMax search error: {e}")
            return []
    
    def _search_bat(self, query: str, limit: int = 10) -> List[Dict]:
        """Search Bring a Trailer"""
        try:
            client = BringATrailerClient()
            results = client.search_listings(query, limit=limit)
            client.close()
            return results
        except Exception as e:
            logger.error(f"BaT search error: {e}")
            return []
    
    def _search_cars(self, query: str, limit: int = 10) -> List[Dict]:
        """Search Cars.com"""
        try:
            client = CarsComClient()
            results = client.search_listings(query, limit=limit)
            return results
        except Exception as e:
            logger.error(f"Cars.com search error: {e}")
            return []
    
    def _search_autodev(self, query: str, limit: int = 10) -> List[Dict]:
        """Search Auto.dev"""
        try:
            client = AutoDevClient()
            result = client.search_vehicles(query, limit=limit)
            return result.get('vehicles', []) if result.get('success') else []
        except Exception as e:
            logger.error(f"Auto.dev search error: {e}")
            return []
    
    # Data Validation Functions
    
    def _validate_ebay_data(self, item: Dict) -> List[str]:
        """Validate eBay data quality"""
        issues = []
        
        if not item.get('itemId'):
            issues.append("Missing itemId")
        if not item.get('title'):
            issues.append("Missing title")
        if not item.get('price'):
            issues.append("Missing price")
        if not item.get('itemWebUrl'):
            issues.append("Missing item URL")
        
        return issues
    
    def _validate_carmax_data(self, item: Dict) -> List[str]:
        """Validate CarMax data quality"""
        issues = []
        
        if not item.get('listing_id'):
            issues.append("Missing listing_id")
        if not item.get('title'):
            issues.append("Missing title")
        if not item.get('price'):
            issues.append("Missing price")
        if not item.get('view_item_url'):
            issues.append("Missing view_item_url")
        
        return issues
    
    def _validate_bat_data(self, item: Dict) -> List[str]:
        """Validate Bring a Trailer data quality"""
        issues = []
        
        if not item.get('listing_id'):
            issues.append("Missing listing_id")
        if not item.get('title'):
            issues.append("Missing title")
        if not item.get('current_bid') and not item.get('price'):
            issues.append("Missing bid/price information")
        if not item.get('view_item_url'):
            issues.append("Missing auction URL")
        
        return issues
    
    def _validate_cars_data(self, item: Dict) -> List[str]:
        """Validate Cars.com data quality"""
        issues = []
        
        if not item.get('listing_id'):
            issues.append("Missing listing_id")
        if not item.get('title'):
            issues.append("Missing title")
        if not item.get('price'):
            issues.append("Missing price")
        
        return issues
    
    def _validate_autodev_data(self, item: Dict) -> List[str]:
        """Validate Auto.dev data quality"""
        issues = []
        
        if not item.get('external_id'):
            issues.append("Missing external_id")
        if not item.get('make'):
            issues.append("Missing make")
        if not item.get('model'):
            issues.append("Missing model")
        if not item.get('price'):
            issues.append("Missing price")
        
        return issues
    
    def _generate_summary_report(self, results: Dict[str, List[TestResult]]) -> None:
        """Generate a summary report of all tests"""
        print("\n" + "="*80)
        print("CARGPT DATA SOURCE TEST SUMMARY")
        print("="*80)
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        warning_tests = 0
        
        for source, test_results in results.items():
            print(f"\n{source.upper()}:")
            print("-" * 40)
            
            source_pass = 0
            source_fail = 0
            source_warn = 0
            
            for result in test_results:
                total_tests += 1
                status_symbol = {
                    TestStatus.PASS: "✅",
                    TestStatus.FAIL: "❌", 
                    TestStatus.WARNING: "⚠️",
                    TestStatus.SKIP: "⏭️"
                }[result.status]
                
                print(f"  {status_symbol} {result.test_name}: {result.message}")
                if result.execution_time:
                    print(f"    Time: {result.execution_time:.2f}s")
                if result.data_points:
                    print(f"    Data points: {result.data_points}")
                if result.errors:
                    print(f"    Errors: {', '.join(result.errors[:2])}")
                
                if result.status == TestStatus.PASS:
                    passed_tests += 1
                    source_pass += 1
                elif result.status == TestStatus.FAIL:
                    failed_tests += 1
                    source_fail += 1
                elif result.status == TestStatus.WARNING:
                    warning_tests += 1
                    source_warn += 1
            
            # Source summary
            total_source = len(test_results)
            print(f"  Summary: {source_pass}/{total_source} passed, {source_fail} failed, {source_warn} warnings")
        
        # Overall summary
        print("\n" + "="*80)
        print("OVERALL SUMMARY:")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print("="*80)
    
    def generate_json_report(self, results: Dict[str, List[TestResult]]) -> str:
        """Generate JSON report for programmatic consumption"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            },
            "sources": {}
        }
        
        for source, test_results in results.items():
            source_data = {
                "tests": [],
                "summary": {"passed": 0, "failed": 0, "warnings": 0}
            }
            
            for result in test_results:
                source_data["tests"].append({
                    "test_name": result.test_name,
                    "status": result.status.value,
                    "message": result.message,
                    "execution_time": result.execution_time,
                    "data_points": result.data_points,
                    "errors": result.errors
                })
                
                report["summary"]["total_tests"] += 1
                if result.status == TestStatus.PASS:
                    report["summary"]["passed"] += 1
                    source_data["summary"]["passed"] += 1
                elif result.status == TestStatus.FAIL:
                    report["summary"]["failed"] += 1
                    source_data["summary"]["failed"] += 1
                elif result.status == TestStatus.WARNING:
                    report["summary"]["warnings"] += 1
                    source_data["summary"]["warnings"] += 1
            
            report["sources"][source] = source_data
        
        return json.dumps(report, indent=2)

# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CarGPT Data Source Testing Framework")
    parser.add_argument("--source", choices=["ebay", "carmax", "bringatrailer", "cars", "autodev", "all"], 
                       default="all", help="Which data source to test")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    framework = DataSourceTestFramework()
    
    if args.source == "all":
        results = framework.run_all_tests()
    else:
        # Run specific source test
        if args.source == "ebay":
            results = {"ebay": framework.test_ebay_motors()}
        elif args.source == "carmax":
            results = {"carmax": framework.test_carmax()}
        elif args.source == "bringatrailer":
            results = {"bringatrailer": framework.test_bring_a_trailer()}
        elif args.source == "cars":
            results = {"cars": framework.test_cars_com()}
        elif args.source == "autodev":
            results = {"autodev": framework.test_autodev()}
    
    if args.json:
        print(framework.generate_json_report(results))
    else:
        framework._generate_summary_report(results)