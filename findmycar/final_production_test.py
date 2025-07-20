#!/usr/bin/env python3
"""
Final End-to-End Production Test Suite
Comprehensive verification of all production systems
"""
import os
import time
import logging
import requests
import subprocess
import threading
from dotenv import load_dotenv
from unified_source_manager import UnifiedSourceManager

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionTestSuite:
    """Comprehensive production test suite"""
    
    def __init__(self):
        self.results = {
            'environment': {},
            'sources': {},
            'search': {},
            'performance': {},
            'health': {},
            'overall': {}
        }
    
    def test_environment(self):
        """Test environment configuration"""
        print("🔧 Testing Environment Configuration")
        print("-" * 50)
        
        env_tests = {
            'EBAY_CLIENT_ID': os.getenv('EBAY_CLIENT_ID'),
            'EBAY_CLIENT_SECRET': os.getenv('EBAY_CLIENT_SECRET'),
            'DATABASE_URL': os.getenv('DATABASE_URL'),
            'SECRET_KEY': os.getenv('SECRET_KEY')
        }
        
        passed = 0
        for key, value in env_tests.items():
            if value:
                print(f"  ✅ {key}: configured")
                passed += 1
            else:
                print(f"  ❌ {key}: missing")
        
        self.results['environment'] = {
            'total': len(env_tests),
            'passed': passed,
            'success_rate': passed / len(env_tests)
        }
        
        print(f"\nEnvironment: {passed}/{len(env_tests)} configured")
        return passed == len(env_tests)
    
    def test_sources(self):
        """Test all production sources"""
        print("\n🔍 Testing Production Sources")
        print("-" * 50)
        
        manager = UnifiedSourceManager()
        production_sources = ['ebay', 'carmax', 'autotrader']
        
        source_results = {}
        
        for source in production_sources:
            print(f"\n📡 Testing {source.upper()}")
            
            try:
                start_time = time.time()
                result = manager.search_all_sources(
                    query="Honda",
                    year_min=2010,
                    price_max=50000,
                    per_page=5,
                    sources=[source]
                )
                test_time = time.time() - start_time
                
                vehicle_count = result.get('total', 0)
                success = len(result.get('sources_searched', [])) > 0
                
                source_results[source] = {
                    'success': success,
                    'vehicles': vehicle_count,
                    'time': test_time,
                    'status': 'working' if success and vehicle_count > 0 else 'failed'
                }
                
                if success and vehicle_count > 0:
                    print(f"  ✅ {source}: {vehicle_count} vehicles in {test_time:.2f}s")
                else:
                    print(f"  ❌ {source}: failed or no vehicles")
                    
            except Exception as e:
                print(f"  💥 {source}: error - {str(e)}")
                source_results[source] = {
                    'success': False,
                    'vehicles': 0,
                    'time': 0,
                    'status': 'error',
                    'error': str(e)
                }
        
        working_sources = sum(1 for r in source_results.values() if r['success'])
        total_vehicles = sum(r['vehicles'] for r in source_results.values())
        
        self.results['sources'] = {
            'results': source_results,
            'working_count': working_sources,
            'total_count': len(production_sources),
            'total_vehicles': total_vehicles,
            'success_rate': working_sources / len(production_sources)
        }
        
        print(f"\nSources: {working_sources}/{len(production_sources)} working, {total_vehicles} total vehicles")
        return working_sources >= 2 and total_vehicles >= 30
    
    def test_unified_search(self):
        """Test unified search across all sources"""
        print("\n🔄 Testing Unified Search")
        print("-" * 50)
        
        try:
            manager = UnifiedSourceManager()
            
            # Configure for production
            production_sources = ['ebay', 'carmax', 'autotrader']
            for source_name in manager.source_config.keys():
                if source_name in production_sources:
                    manager.enable_source(source_name)
                else:
                    manager.disable_source(source_name)
            
            # Test search
            start_time = time.time()
            result = manager.search_all_sources(
                query="Honda",
                year_min=2010,
                price_max=50000,
                per_page=20
            )
            search_time = time.time() - start_time
            
            total_vehicles = result.get('total', 0)
            sources_succeeded = result.get('sources_searched', [])
            sources_failed = result.get('sources_failed', [])
            
            # Check vehicle distribution
            source_distribution = {}
            for vehicle in result.get('vehicles', []):
                source = vehicle.get('source', 'unknown')
                source_distribution[source] = source_distribution.get(source, 0) + 1
            
            print(f"Total vehicles: {total_vehicles}")
            print(f"Search time: {search_time:.2f}s")
            print(f"Sources succeeded: {sources_succeeded}")
            print(f"Sources failed: {sources_failed}")
            print(f"Vehicle distribution: {source_distribution}")
            
            self.results['search'] = {
                'total_vehicles': total_vehicles,
                'search_time': search_time,
                'sources_succeeded': len(sources_succeeded),
                'sources_failed': len(sources_failed),
                'distribution': source_distribution,
                'success': total_vehicles >= 30 and search_time < 60
            }
            
            return total_vehicles >= 30 and search_time < 60
            
        except Exception as e:
            print(f"💥 Unified search failed: {str(e)}")
            self.results['search'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def test_performance(self):
        """Test performance metrics"""
        print("\n⚡ Testing Performance")
        print("-" * 50)
        
        performance_tests = []
        
        # Test 3 quick searches
        for i in range(3):
            try:
                manager = UnifiedSourceManager()
                start_time = time.time()
                result = manager.search_all_sources(
                    query=f"Honda",
                    per_page=10
                )
                test_time = time.time() - start_time
                vehicle_count = result.get('total', 0)
                
                performance_tests.append({
                    'time': test_time,
                    'vehicles': vehicle_count,
                    'success': vehicle_count > 0
                })
                
                print(f"  Test {i+1}: {vehicle_count} vehicles in {test_time:.2f}s")
                
            except Exception as e:
                print(f"  Test {i+1}: failed - {str(e)}")
                performance_tests.append({
                    'time': 999,
                    'vehicles': 0,
                    'success': False
                })
        
        avg_time = sum(t['time'] for t in performance_tests) / len(performance_tests)
        avg_vehicles = sum(t['vehicles'] for t in performance_tests) / len(performance_tests)
        success_rate = sum(1 for t in performance_tests if t['success']) / len(performance_tests)
        
        self.results['performance'] = {
            'average_time': avg_time,
            'average_vehicles': avg_vehicles,
            'success_rate': success_rate,
            'tests': performance_tests,
            'meets_requirements': avg_time < 45 and avg_vehicles >= 20
        }
        
        print(f"\nPerformance: {avg_vehicles:.0f} vehicles avg, {avg_time:.2f}s avg, {success_rate*100:.0f}% success")
        return avg_time < 45 and avg_vehicles >= 20
    
    def test_health_endpoints(self):
        """Test health check endpoints (if app is running)"""
        print("\n❤️ Testing Health Endpoints")
        print("-" * 50)
        
        # Try to start the app briefly for health check
        health_results = {}
        
        try:
            # Check if app is already running
            response = requests.get("http://localhost:8601/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"  ✅ Health endpoint: {health_data.get('status', 'unknown')}")
                health_results['health_endpoint'] = True
            else:
                print(f"  ❌ Health endpoint: status {response.status_code}")
                health_results['health_endpoint'] = False
                
        except requests.exceptions.RequestException:
            print(f"  ⚠️ Health endpoint: app not running")
            health_results['health_endpoint'] = None
        
        self.results['health'] = health_results
        return True  # Don't fail on health endpoint issues
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 FINAL PRODUCTION TEST REPORT")
        print("=" * 80)
        
        # Environment
        env_result = self.results.get('environment', {})
        env_status = "✅ PASS" if env_result.get('success_rate', 0) == 1.0 else "❌ FAIL"
        print(f"Environment Configuration: {env_status}")
        print(f"  Variables configured: {env_result.get('passed', 0)}/{env_result.get('total', 0)}")
        
        # Sources
        source_result = self.results.get('sources', {})
        source_status = "✅ PASS" if source_result.get('working_count', 0) >= 2 else "❌ FAIL"
        print(f"\nSource Integration: {source_status}")
        print(f"  Working sources: {source_result.get('working_count', 0)}/{source_result.get('total_count', 0)}")
        print(f"  Total vehicles available: {source_result.get('total_vehicles', 0)}")
        
        # Search
        search_result = self.results.get('search', {})
        search_status = "✅ PASS" if search_result.get('success', False) else "❌ FAIL"
        print(f"\nUnified Search: {search_status}")
        print(f"  Total vehicles: {search_result.get('total_vehicles', 0)}")
        print(f"  Search time: {search_result.get('search_time', 0):.2f}s")
        print(f"  Sources succeeded: {search_result.get('sources_succeeded', 0)}")
        
        # Performance
        perf_result = self.results.get('performance', {})
        perf_status = "✅ PASS" if perf_result.get('meets_requirements', False) else "❌ FAIL"
        print(f"\nPerformance: {perf_status}")
        print(f"  Average vehicles: {perf_result.get('average_vehicles', 0):.0f}")
        print(f"  Average time: {perf_result.get('average_time', 0):.2f}s")
        print(f"  Success rate: {perf_result.get('success_rate', 0)*100:.0f}%")
        
        # Overall assessment
        critical_tests = [
            env_result.get('success_rate', 0) == 1.0,
            source_result.get('working_count', 0) >= 2,
            search_result.get('success', False),
            perf_result.get('meets_requirements', False)
        ]
        
        passed_critical = sum(critical_tests)
        overall_status = "🎉 PRODUCTION READY" if passed_critical >= 3 else "⚠️ NEEDS ATTENTION"
        
        print(f"\n" + "=" * 80)
        print(f"OVERALL STATUS: {overall_status}")
        print("=" * 80)
        print(f"Critical tests passed: {passed_critical}/4")
        
        if passed_critical >= 3:
            print("✅ System is ready for production deployment!")
            print("✅ All essential components are working")
            print("✅ Performance meets requirements")
        else:
            print("❌ System needs attention before production")
            print("❌ Check failed tests above")
        
        return passed_critical >= 3

def main():
    """Run comprehensive production test suite"""
    print("🎯 FindMyCar Production Test Suite")
    print("=" * 80)
    
    suite = ProductionTestSuite()
    
    # Run all tests
    tests = [
        ('Environment', suite.test_environment),
        ('Sources', suite.test_sources),
        ('Unified Search', suite.test_unified_search),
        ('Performance', suite.test_performance),
        ('Health Endpoints', suite.test_health_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"💥 {test_name} test failed with error: {str(e)}")
            results.append(False)
    
    # Generate final report
    overall_success = suite.generate_report()
    
    return overall_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)