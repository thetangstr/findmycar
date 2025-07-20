#!/usr/bin/env python3
"""
Test script specifically for Carvana integration
"""
import logging
from datetime import datetime
from carvana_client import CarvanaClient
from unified_source_manager import UnifiedSourceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_carvana_direct():
    """Test Carvana client directly"""
    print("\n" + "="*50)
    print("Testing Carvana Client Directly")
    print("="*50)
    
    try:
        client = CarvanaClient()
        
        # Test health check
        print("\n1. Testing health check...")
        health = client.check_health()
        print(f"Health Status: {health['status']}")
        print(f"Response Time: {health['response_time']:.2f}s")
        print(f"Message: {health['message']}")
        
        if health['status'] != 'healthy':
            print("⚠️  Carvana API is not healthy, results may be limited")
        
        # Test basic search
        print("\n2. Testing basic search (Honda)...")
        results = client.search_vehicles(
            make="Honda",
            year_min=2020,
            price_max=30000,
            per_page=5
        )
        
        print(f"Found {results['total']} vehicles")
        print(f"Showing {len(results['vehicles'])} on this page")
        
        # Display sample results
        for i, vehicle in enumerate(results['vehicles'][:3], 1):
            print(f"\nVehicle {i}:")
            print(f"  Title: {vehicle['title']}")
            print(f"  Price: ${vehicle['price']:,}")
            print(f"  Mileage: {vehicle['mileage']:,} miles")
            print(f"  Location: {vehicle['location']}")
            print(f"  Link: {vehicle['link']}")
            
            # Show Carvana-specific features
            carvana_features = vehicle.get('carvana_features', {})
            if carvana_features.get('free_delivery'):
                print(f"  ✓ Free Delivery")
            if carvana_features.get('return_policy'):
                print(f"  ✓ {carvana_features['return_policy']} Return Policy")
            if carvana_features.get('certified'):
                print(f"  ✓ Carvana Certified")
        
        # Test specific model search
        print("\n3. Testing specific model search (Toyota RAV4)...")
        results2 = client.search_vehicles(
            make="Toyota",
            model="RAV4",
            year_min=2021,
            per_page=3
        )
        print(f"Found {results2['total']} Toyota RAV4s")
        
        # Test price range search
        print("\n4. Testing price range search (Under $20k)...")
        results3 = client.search_vehicles(
            price_max=20000,
            mileage_max=50000,
            per_page=5
        )
        print(f"Found {results3['total']} vehicles under $20k with less than 50k miles")
        
        return True
        
    except Exception as e:
        logger.error(f"Carvana direct test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_carvana_via_manager():
    """Test Carvana through unified source manager"""
    print("\n" + "="*50)
    print("Testing Carvana via Unified Manager")
    print("="*50)
    
    try:
        manager = UnifiedSourceManager()
        
        # Check if Carvana is enabled
        enabled_sources = manager.get_enabled_sources()
        if 'carvana' not in enabled_sources:
            print("❌ Carvana is not enabled in the source manager")
            return False
        
        print(f"✓ Carvana is enabled (among {len(enabled_sources)} total sources)")
        
        # Search only through Carvana
        print("\n1. Searching via Carvana only...")
        results = manager.search_all_sources(
            query="SUV",
            year_min=2020,
            price_max=35000,
            per_page=10,
            sources=['carvana']
        )
        
        print(f"Search completed in {results['search_time']:.2f} seconds")
        print(f"Total vehicles found: {results['total']}")
        print(f"Sources succeeded: {', '.join(results['sources_searched'])}")
        print(f"Sources failed: {', '.join(results['sources_failed'])}")
        
        # Display some results
        for i, vehicle in enumerate(results['vehicles'][:3], 1):
            print(f"\nVehicle {i}:")
            print(f"  Title: {vehicle['title']}")
            print(f"  Price: ${vehicle['price']:,}")
            print(f"  Source: {vehicle['source']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Carvana manager test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all Carvana tests"""
    print("Carvana Integration Test Suite")
    print("==============================")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Carvana Direct", test_carvana_direct),
        ("Carvana via Manager", test_carvana_via_manager)
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

if __name__ == "__main__":
    main()