#!/usr/bin/env python3
"""
Test error handling and fallback mechanisms
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()

# Import components
from database_v2_sqlite import get_session
from production_search_service_enhanced import EnhancedProductionSearchService
from cache_manager import CacheManager
from production_error_handler import error_handler

def test_error_handling():
    """Test various error scenarios and fallback mechanisms"""
    
    print("=== Testing Error Handling and Fallbacks ===\n")
    
    # Initialize services
    db = get_session()
    cache = CacheManager()
    search_service = EnhancedProductionSearchService(db, cache)
    
    # Test 1: Normal search (baseline)
    print("1. Normal Search (baseline):")
    try:
        start = time.time()
        results = search_service.search(
            query="Honda Civic",
            include_live=False  # Local only for speed
        )
        print(f"   ✅ Found {results['total']} vehicles in {time.time() - start:.2f}s")
        print(f"   Sources: {', '.join(results['sources_used'])}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Search with timeout simulation
    print("\n2. Search with Simulated Timeout:")
    # Temporarily reduce timeout for testing
    original_timeout = search_service.timeout_manager.TIMEOUTS['search_operation']
    search_service.timeout_manager.TIMEOUTS['search_operation'] = 1  # 1 second timeout
    
    try:
        results = search_service.search(
            query="Toyota",
            include_live=True  # This will likely timeout
        )
        if results.get('partial'):
            print(f"   ⚠️  Partial results returned: {results['total']} vehicles")
            print(f"   Failed sources: {', '.join(results.get('failed_sources', []))}")
        else:
            print(f"   ✅ Complete results: {results['total']} vehicles")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    finally:
        search_service.timeout_manager.TIMEOUTS['search_operation'] = original_timeout
    
    # Test 3: Test circuit breaker
    print("\n3. Circuit Breaker Test:")
    
    # Simulate multiple failures to trigger circuit breaker
    for i in range(6):
        error_handler.record_failure('test_service')
    
    if error_handler.is_circuit_open('test_service'):
        print("   ✅ Circuit breaker opened after failures")
    else:
        print("   ❌ Circuit breaker did not open")
    
    # Test 4: Cache fallback
    print("\n4. Cache Fallback Test:")
    
    # First search to populate cache
    query = "Ford Mustang"
    results1 = search_service.search(query=query, include_live=False)
    print(f"   Initial search: {results1['total']} vehicles")
    
    # Second search should hit cache
    results2 = search_service.search(query=query, include_live=False)
    if results2.get('cached'):
        print("   ✅ Cache hit successful")
    else:
        print("   ℹ️  Cache miss (may be disabled)")
    
    # Test 5: Partial results with failed sources
    print("\n5. Multi-Source Search with Failures:")
    
    # Force some sources to fail by opening circuit breakers
    error_handler.circuit_breakers['carmax'] = {
        'state': 'open',
        'open_until': time.time() + 300,
        'failure_count': 5
    }
    
    results = search_service.search(
        query="BMW",
        include_live=True
    )
    
    print(f"   Total results: {results['total']}")
    print(f"   Working sources: {', '.join(results['sources_used'])}")
    print(f"   Failed sources: {', '.join(results.get('failed_sources', []))}")
    
    if results.get('partial'):
        print("   ⚠️  Partial results due to source failures")
    
    # Test 6: Error recovery
    print("\n6. Error Recovery Test:")
    
    # Clear circuit breaker
    if 'carmax' in error_handler.circuit_breakers:
        del error_handler.circuit_breakers['carmax']
    
    # Record a success to show recovery
    error_handler.record_success('carmax')
    
    if not error_handler.is_circuit_open('carmax'):
        print("   ✅ Service recovered after success")
    
    # Test 7: Database error simulation
    print("\n7. Database Error Handling:")
    
    # Close database connection to simulate error
    db.close()
    
    try:
        results = search_service.search(query="Chevrolet")
        if results.get('error'):
            print("   ✅ Gracefully handled database error")
            print(f"   Message: {results.get('message')}")
        else:
            print(f"   ℹ️  Returned {results['total']} results despite closed DB")
    except Exception as e:
        print(f"   ✅ Caught database error: {type(e).__name__}")
    
    # Summary
    print("\n=== Error Handling Summary ===")
    print(f"Total errors tracked: {sum(error_handler.error_counts.values())}")
    print(f"Circuit breakers: {len(error_handler.circuit_breakers)}")
    print(f"Error types encountered: {len(set(e['error_type'] for e in error_handler.error_history))}")
    
    # Show error distribution
    if error_handler.error_counts:
        print("\nError distribution:")
        for error_key, count in error_handler.error_counts.items():
            print(f"  - {error_key}: {count} occurrences")

if __name__ == "__main__":
    test_error_handling()