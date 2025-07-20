"""
Test script for new vehicle sources
Tests Hemmings, Cars & Bids, Craigslist, CarSoup, and Revy Autos
"""
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_hemmings():
    """Test Hemmings RSS client"""
    print("\n" + "="*50)
    print("Testing Hemmings Classic Cars...")
    print("="*50)
    
    try:
        from hemmings_client import HemmingsClient
        client = HemmingsClient()
        
        # Test health check
        health = client.check_health()
        print(f"Health Status: {health['status']}")
        print(f"Message: {health['message']}")
        
        # Test search
        result = client.search_vehicles(query="mustang", year_min=1960, year_max=1970)
        print(f"\nSearch Results:")
        print(f"Total vehicles found: {result['total']}")
        
        # Display first few results
        for i, vehicle in enumerate(result['vehicles'][:3]):
            print(f"\nVehicle {i+1}:")
            print(f"  Title: {vehicle['title']}")
            print(f"  Price: ${vehicle.get('price', 'N/A')}")
            print(f"  Year: {vehicle.get('year', 'N/A')}")
            print(f"  Location: {vehicle.get('location', 'N/A')}")
            print(f"  Link: {vehicle.get('link', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def test_cars_bids():
    """Test Cars & Bids API client"""
    print("\n" + "="*50)
    print("Testing Cars & Bids Auctions...")
    print("="*50)
    
    try:
        from cars_bids_client import CarsBidsClient
        client = CarsBidsClient()
        
        # Test health check
        health = client.check_health()
        print(f"Health Status: {health['status']}")
        print(f"Message: {health['message']}")
        
        # Test search
        result = client.search_vehicles(query="porsche", price_min=20000)
        print(f"\nSearch Results:")
        print(f"Total auctions found: {result['total']}")
        
        # Display first few results
        for i, vehicle in enumerate(result['vehicles'][:3]):
            print(f"\nAuction {i+1}:")
            print(f"  Title: {vehicle['title']}")
            print(f"  Current Bid: ${vehicle.get('price', 'N/A')}")
            print(f"  Year: {vehicle.get('year', 'N/A')}")
            print(f"  Mileage: {vehicle.get('mileage', 'N/A')}")
            if 'auction_info' in vehicle:
                print(f"  Time Left: {vehicle['auction_info'].get('time_left', 'N/A')}")
                print(f"  Bid Count: {vehicle['auction_info'].get('bid_count', 'N/A')}")
            print(f"  Link: {vehicle.get('link', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def test_craigslist():
    """Test Craigslist RSS client"""
    print("\n" + "="*50)
    print("Testing Craigslist...")
    print("="*50)
    
    try:
        from craigslist_client import CraigslistClient
        # Test with just a few regions to be faster
        client = CraigslistClient(regions=['losangeles', 'newyork', 'chicago'])
        
        # Test health check
        health = client.check_health()
        print(f"Health Status: {health['status']}")
        print(f"Message: {health['message']}")
        
        # Test search
        result = client.search_vehicles(query="honda civic", price_max=15000)
        print(f"\nSearch Results:")
        print(f"Total vehicles found: {result['total']}")
        print(f"Regions searched: {client.regions}")
        
        # Display first few results
        for i, vehicle in enumerate(result['vehicles'][:3]):
            print(f"\nVehicle {i+1}:")
            print(f"  Title: {vehicle['title']}")
            print(f"  Price: ${vehicle.get('price', 'N/A')}")
            print(f"  Year: {vehicle.get('year', 'N/A')}")
            print(f"  Region: {vehicle.get('region', 'N/A')}")
            print(f"  Location: {vehicle.get('location', 'N/A')}")
            print(f"  Link: {vehicle.get('link', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def test_carsoup():
    """Test CarSoup scraper"""
    print("\n" + "="*50)
    print("Testing CarSoup...")
    print("="*50)
    
    try:
        from carsoup_client import CarSoupClient
        client = CarSoupClient()
        
        # Test health check
        health = client.check_health()
        print(f"Health Status: {health['status']}")
        print(f"Message: {health['message']}")
        
        # Test search
        result = client.search_vehicles(make="ford", model="f-150")
        print(f"\nSearch Results:")
        print(f"Total vehicles found: {result['total']}")
        
        # Display first few results
        for i, vehicle in enumerate(result['vehicles'][:3]):
            print(f"\nVehicle {i+1}:")
            print(f"  Title: {vehicle['title']}")
            print(f"  Price: ${vehicle.get('price', 'N/A')}")
            print(f"  Year: {vehicle.get('year', 'N/A')}")
            print(f"  Mileage: {vehicle.get('mileage', 'N/A')}")
            print(f"  Location: {vehicle.get('location', 'N/A')}")
            print(f"  Link: {vehicle.get('link', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def test_revy_autos():
    """Test Revy Autos API client"""
    print("\n" + "="*50)
    print("Testing Revy Autos...")
    print("="*50)
    
    try:
        from revy_autos_client import RevyAutosClient
        client = RevyAutosClient()
        
        # Test health check
        health = client.check_health()
        print(f"Health Status: {health['status']}")
        print(f"Message: {health['message']}")
        
        # Test search
        result = client.search_vehicles(query="suv", year_min=2018)
        print(f"\nSearch Results:")
        print(f"Total vehicles found: {result['total']}")
        
        # Display first few results
        for i, vehicle in enumerate(result['vehicles'][:3]):
            print(f"\nVehicle {i+1}:")
            print(f"  Title: {vehicle['title']}")
            print(f"  Price: ${vehicle.get('price', 'N/A')}")
            print(f"  Year: {vehicle.get('year', 'N/A')}")
            print(f"  Mileage: {vehicle.get('mileage', 'N/A')}")
            print(f"  Condition: {vehicle.get('condition', 'N/A')}")
            print(f"  Location: {vehicle.get('location', 'N/A')}")
            print(f"  Link: {vehicle.get('link', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def test_unified_manager():
    """Test the unified source manager"""
    print("\n" + "="*50)
    print("Testing Unified Source Manager...")
    print("="*50)
    
    try:
        from unified_source_manager import UnifiedSourceManager
        manager = UnifiedSourceManager()
        
        # Get source stats
        stats = manager.get_source_stats()
        print(f"\nSource Statistics:")
        print(f"Total sources configured: {stats['total_sources']}")
        print(f"Enabled sources: {stats['enabled_sources']}")
        print(f"Source types: {json.dumps(stats['source_types'], indent=2)}")
        
        # List enabled sources
        enabled = manager.get_enabled_sources()
        print(f"\nEnabled sources: {enabled}")
        
        # Test unified search with just the new sources
        print("\nPerforming unified search...")
        start_time = datetime.now()
        
        result = manager.search_all_sources(
            query="sedan",
            price_max=30000,
            sources=['hemmings', 'cars_bids', 'craigslist', 'carsoup', 'revy_autos']
        )
        
        search_time = (datetime.now() - start_time).total_seconds()
        
        print(f"\nUnified Search Results:")
        print(f"Total vehicles found: {result['total']}")
        print(f"Sources searched: {result['sources_searched']}")
        print(f"Sources failed: {result['sources_failed']}")
        print(f"Search time: {search_time:.2f} seconds")
        
        # Display first few results
        for i, vehicle in enumerate(result['vehicles'][:5]):
            print(f"\nVehicle {i+1} (from {vehicle.get('source', 'unknown')}):")
            print(f"  Title: {vehicle['title']}")
            print(f"  Price: ${vehicle.get('price', 'N/A')}")
            print(f"  Year: {vehicle.get('year', 'N/A')}")
            print(f"  Location: {vehicle.get('location', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("FindMyCar New Sources Test Suite")
    print("================================")
    print(f"Testing at: {datetime.now()}")
    
    results = {}
    
    # Test individual sources
    results['hemmings'] = test_hemmings()
    results['cars_bids'] = test_cars_bids()
    results['craigslist'] = test_craigslist()
    results['carsoup'] = test_carsoup()
    results['revy_autos'] = test_revy_autos()
    
    # Test unified manager
    results['unified_manager'] = test_unified_manager()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for source, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{source}: {status}")
    
    total_passed = sum(1 for passed in results.values() if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! New sources are ready for integration.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()