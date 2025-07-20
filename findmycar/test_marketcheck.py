#!/usr/bin/env python3
"""
Test Marketcheck API integration for Cars.com
"""
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from cars_com_client import CarsComClient
from unified_source_manager import UnifiedSourceManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_marketcheck_api():
    """Test Marketcheck API directly"""
    print("\n" + "="*50)
    print("Testing Marketcheck API for Cars.com")
    print("="*50)
    
    # Check if API key is set
    api_key = os.getenv('MARKETCHECK_API_KEY')
    if not api_key:
        print("❌ MARKETCHECK_API_KEY not found in environment")
        return False
    
    print(f"✅ API key found: {api_key[:8]}...")
    
    try:
        client = CarsComClient()
        
        # Test 1: Health check
        print("\n1. Testing health check...")
        health = client.check_health()
        print(f"   Status: {health['status']}")
        print(f"   Response time: {health.get('response_time', 0):.2f}s")
        print(f"   Message: {health['message']}")
        
        if health['status'] != 'healthy':
            print("\n⚠️  API health check failed, but continuing tests...")
        
        # Test 2: Basic search
        print("\n2. Testing basic search (Popular vehicles)...")
        results = client.search_vehicles(
            query="SUV",
            year_min=2020,
            price_max=40000,
            per_page=10
        )
        
        print(f"   Found {results['total']} vehicles")
        print(f"   Showing {len(results['vehicles'])} results")
        
        # Display sample results
        if results['vehicles']:
            print("\n   Sample vehicles:")
            for i, vehicle in enumerate(results['vehicles'][:5], 1):
                print(f"\n   Vehicle {i}:")
                print(f"     Title: {vehicle['title']}")
                print(f"     Price: ${vehicle['price']:,}")
                print(f"     Mileage: {vehicle.get('mileage', 'N/A'):,} miles" if vehicle.get('mileage') else "     Mileage: N/A")
                print(f"     Location: {vehicle.get('location', 'N/A')}")
                print(f"     Dealer: {vehicle.get('dealer_info', {}).get('name', 'N/A')}")
                print(f"     Link: {vehicle.get('link', 'N/A')}")
        
        # Test 3: Specific make/model search
        print("\n3. Testing specific search (Honda CR-V)...")
        honda_results = client.search_vehicles(
            make="Honda",
            model="CR-V",
            year_min=2019,
            per_page=5
        )
        
        print(f"   Found {honda_results['total']} Honda CR-Vs")
        if honda_results['vehicles']:
            avg_price = sum(v['price'] for v in honda_results['vehicles'] if v.get('price')) / len(honda_results['vehicles'])
            print(f"   Average price: ${avg_price:,.0f}")
        
        # Test 4: Price range search
        print("\n4. Testing budget search (Under $25k)...")
        budget_results = client.search_vehicles(
            price_max=25000,
            year_min=2018,
            mileage_max=60000,
            per_page=5
        )
        
        print(f"   Found {budget_results['total']} vehicles under $25k")
        
        # Test 5: Luxury search
        print("\n5. Testing luxury search (BMW/Mercedes)...")
        luxury_results = client.search_vehicles(
            query="BMW Mercedes",
            year_min=2020,
            per_page=5
        )
        
        print(f"   Found {luxury_results['total']} luxury vehicles")
        
        return True
        
    except Exception as e:
        logger.error(f"Marketcheck test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_unified_search():
    """Test Cars.com through unified source manager"""
    print("\n" + "="*50)
    print("Testing Unified Search with Cars.com")
    print("="*50)
    
    try:
        manager = UnifiedSourceManager()
        
        # Check enabled sources
        enabled = manager.get_enabled_sources()
        print(f"\nEnabled sources: {', '.join(enabled)}")
        
        if 'cars_com' not in enabled:
            print("❌ Cars.com is not enabled")
            return False
        
        print("✅ Cars.com is enabled")
        
        # Test search with multiple sources including Cars.com
        print("\n1. Searching with Cars.com and other sources...")
        sources_to_search = ['cars_com', 'ebay', 'hemmings', 'cars_bids']
        available_sources = [s for s in sources_to_search if s in enabled]
        
        print(f"   Searching sources: {', '.join(available_sources)}")
        
        results = manager.search_all_sources(
            query="sedan",
            year_min=2019,
            price_max=35000,
            per_page=20,
            sources=available_sources
        )
        
        print(f"\n   Search completed in {results['search_time']:.2f} seconds")
        print(f"   Sources succeeded: {', '.join(results['sources_searched'])}")
        print(f"   Sources failed: {', '.join(results['sources_failed'])}")
        print(f"   Total vehicles found: {results['total']}")
        
        # Show distribution by source
        source_counts = {}
        for vehicle in results['vehicles']:
            source = vehicle.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print("\n   Vehicles by source:")
        for source, count in sorted(source_counts.items()):
            print(f"     {source}: {count}")
        
        # Test Cars.com only search
        print("\n2. Testing Cars.com exclusive search...")
        cars_only = manager.search_all_sources(
            query="truck",
            year_min=2020,
            price_max=45000,
            per_page=10,
            sources=['cars_com']
        )
        
        print(f"   Found {cars_only['total']} trucks from Cars.com")
        
        return True
        
    except Exception as e:
        logger.error(f"Unified search test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all Marketcheck/Cars.com tests"""
    print("Marketcheck API Integration Test")
    print("================================")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check for API key
    if not os.getenv('MARKETCHECK_API_KEY'):
        print("\n❌ MARKETCHECK_API_KEY not set in environment")
        print("   Please add it to your .env file")
        return
    
    tests = [
        ("Marketcheck API", test_marketcheck_api),
        ("Unified Search", test_unified_search)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            logger.error(f"{name} test crashed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    
    for name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Cars.com integration is working.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()