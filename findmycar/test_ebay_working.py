#!/usr/bin/env python3
"""
Test eBay API which should be working
"""
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from ebay_live_client import EbayLiveClient
from unified_source_manager import UnifiedSourceManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_ebay_direct():
    """Test eBay API directly"""
    print("\n" + "="*50)
    print("Testing eBay Motors API")
    print("="*50)
    
    # Check if API keys are set
    client_id = os.getenv('EBAY_CLIENT_ID')
    client_secret = os.getenv('EBAY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ eBay API credentials not found")
        return False
    
    print(f"✅ eBay credentials found")
    
    try:
        client = EbayLiveClient()
        
        # Test basic search
        print("\n1. Testing basic search (Honda Civic)...")
        results = client.search_vehicles(
            query="Honda Civic",
            year_min=2018,
            price_max=25000,
            per_page=10
        )
        
        print(f"   Found {results['total']} vehicles")
        print(f"   Showing {len(results['vehicles'])} results")
        
        # Display sample results
        if results['vehicles']:
            print("\n   Sample vehicles:")
            for i, vehicle in enumerate(results['vehicles'][:3], 1):
                print(f"\n   Vehicle {i}:")
                print(f"     Title: {vehicle['title']}")
                print(f"     Price: ${vehicle['price']:,}")
                print(f"     Mileage: {vehicle.get('mileage', 'N/A'):,} miles" if vehicle.get('mileage') else "     Mileage: N/A")
                print(f"     Location: {vehicle.get('location', 'N/A')}")
                print(f"     Link: {vehicle.get('link', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error(f"eBay test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_working_sources():
    """Test all potentially working sources"""
    print("\n" + "="*50)
    print("Testing All Available Sources")
    print("="*50)
    
    manager = UnifiedSourceManager()
    
    # Test each source individually
    sources_to_test = ['ebay', 'hemmings', 'cars_bids', 'craigslist', 'carsoup', 'revy_autos']
    
    working_sources = []
    
    for source in sources_to_test:
        if source in manager.get_enabled_sources():
            print(f"\nTesting {source}...")
            try:
                results = manager.search_all_sources(
                    query="car",
                    price_max=50000,
                    per_page=5,
                    sources=[source]
                )
                
                if results['sources_searched'] and results['total'] > 0:
                    print(f"  ✅ {source}: Found {results['total']} vehicles")
                    working_sources.append(source)
                else:
                    print(f"  ❌ {source}: No results or failed")
            except Exception as e:
                print(f"  ❌ {source}: Error - {str(e)}")
    
    print(f"\n\nWorking sources: {', '.join(working_sources) if working_sources else 'None'}")
    
    # If we have working sources, do a combined search
    if working_sources:
        print(f"\nRunning combined search with working sources...")
        results = manager.search_all_sources(
            query="SUV",
            year_min=2018,
            price_max=40000,
            per_page=20,
            sources=working_sources
        )
        
        print(f"\nCombined search results:")
        print(f"  Total vehicles: {results['total']}")
        print(f"  Search time: {results['search_time']:.2f}s")
        
        if results['vehicles']:
            # Show distribution
            source_counts = {}
            for vehicle in results['vehicles']:
                source = vehicle.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            print(f"\n  Vehicles by source:")
            for source, count in sorted(source_counts.items()):
                print(f"    {source}: {count}")

def main():
    """Run all tests"""
    print("Vehicle Source Availability Test")
    print("================================")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # First test eBay directly
    test_ebay_direct()
    
    # Then test all sources
    test_working_sources()
    
    print("\n" + "="*50)
    print("Next Steps:")
    print("1. Add MARKETCHECK_API_KEY to .env file to enable Cars.com")
    print("2. eBay should be working if you have valid API credentials")
    print("3. Other sources may have temporary issues or require updates")

if __name__ == "__main__":
    main()