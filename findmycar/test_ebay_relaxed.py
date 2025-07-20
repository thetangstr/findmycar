#!/usr/bin/env python3
"""
Test eBay with more relaxed search parameters
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ebay_with_relaxed_params():
    """Test eBay with more relaxed search parameters"""
    print("🔍 Testing eBay with Relaxed Parameters")
    print("=" * 50)
    
    try:
        from ebay_live_client import EbayLiveClient
        
        client = EbayLiveClient()
        print("✅ eBay client initialized")
        
        # Test 1: Very relaxed parameters
        print("\n📡 Test 1: Very relaxed search...")
        result1 = client.search_vehicles(
            query="Honda",
            year_min=2000,  # Much lower year limit
            price_max=50000,  # Higher price limit
            per_page=5
        )
        
        print(f"Result 1: {result1.get('total', 0)} total, {len(result1.get('vehicles', []))} returned")
        if result1.get('vehicles'):
            for i, vehicle in enumerate(result1['vehicles'][:3]):
                print(f"  {i+1}. {vehicle.get('title', 'N/A')} ({vehicle.get('year', 'N/A')}) - ${vehicle.get('price', 0):,}")
        
        # Test 2: No year filter
        print("\n📡 Test 2: No year filter...")
        result2 = client.search_vehicles(
            query="Honda",
            price_max=50000,
            per_page=5
        )
        
        print(f"Result 2: {result2.get('total', 0)} total, {len(result2.get('vehicles', []))} returned")
        if result2.get('vehicles'):
            for i, vehicle in enumerate(result2['vehicles'][:3]):
                print(f"  {i+1}. {vehicle.get('title', 'N/A')} ({vehicle.get('year', 'N/A')}) - ${vehicle.get('price', 0):,}")
        
        # Test 3: No filters at all
        print("\n📡 Test 3: No filters...")
        result3 = client.search_vehicles(
            query="Honda",
            per_page=5
        )
        
        print(f"Result 3: {result3.get('total', 0)} total, {len(result3.get('vehicles', []))} returned")
        if result3.get('vehicles'):
            for i, vehicle in enumerate(result3['vehicles'][:3]):
                print(f"  {i+1}. {vehicle.get('title', 'N/A')} ({vehicle.get('year', 'N/A')}) - ${vehicle.get('price', 0):,}")
        
        return len(result3.get('vehicles', [])) > 0
        
    except Exception as e:
        print(f"💥 eBay test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 eBay Relaxed Parameters Test")
    print("=" * 80)
    
    success = test_ebay_with_relaxed_params()
    
    print("\n" + "=" * 80)
    print("📊 EBAY TEST SUMMARY")
    print("=" * 80)
    
    if success:
        print("✅ eBay is working with relaxed parameters!")
        print("💡 Issue was overly restrictive search filters")
        print("🔧 Fix: Use broader year range or remove year filter for testing")
    else:
        print("❌ eBay still not working")

if __name__ == "__main__":
    main()