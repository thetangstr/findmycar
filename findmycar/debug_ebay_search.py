#!/usr/bin/env python3
"""
Debug eBay search specifically
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_ebay_search():
    """Debug eBay search in detail"""
    print("🔍 Debugging eBay Search")
    print("=" * 50)
    
    try:
        from ebay_live_client import EbayLiveClient
        
        client = EbayLiveClient()
        print("✅ eBay client initialized")
        
        # Test with simple parameters
        print("\n📡 Testing eBay search...")
        
        result = client.search_vehicles(
            query="Honda",
            year_min=2018,
            price_max=35000,
            per_page=5
        )
        
        print(f"Search result: {result}")
        print(f"Total vehicles: {result.get('total', 0)}")
        print(f"Vehicles returned: {len(result.get('vehicles', []))}")
        
        if result.get('vehicles'):
            print("\nSample vehicles:")
            for i, vehicle in enumerate(result['vehicles'][:3]):
                print(f"  {i+1}. {vehicle.get('title', 'N/A')} - ${vehicle.get('price', 0):,}")
        
        return result.get('total', 0) > 0
        
    except Exception as e:
        print(f"💥 eBay search failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def debug_ebay_oauth():
    """Debug eBay OAuth token specifically"""
    print("\n🔍 Debugging eBay OAuth")
    print("=" * 50)
    
    try:
        from ebay_live_client import EbayLiveClient
        
        client = EbayLiveClient()
        
        # Check if token exists
        print(f"OAuth token: {'SET' if hasattr(client, 'oauth_token') and client.oauth_token else 'NOT_SET'}")
        
        # Try to get a fresh token
        if hasattr(client, 'get_oauth_token'):
            token = client.get_oauth_token()
            print(f"Fresh token obtained: {'YES' if token else 'NO'}")
            if token:
                print(f"Token length: {len(token)}")
        
        return True
        
    except Exception as e:
        print(f"💥 OAuth debug failed: {str(e)}")
        return False

def main():
    print("🔍 eBay Integration Deep Debug")
    print("=" * 80)
    
    # Debug OAuth
    oauth_working = debug_ebay_oauth()
    
    # Debug search
    search_working = debug_ebay_search()
    
    print("\n" + "=" * 80)
    print("🔍 EBAY DEBUG SUMMARY")
    print("=" * 80)
    print(f"OAuth working: {'✅ YES' if oauth_working else '❌ NO'}")
    print(f"Search working: {'✅ YES' if search_working else '❌ NO'}")
    
    if oauth_working and not search_working:
        print("\n💡 ISSUE: OAuth works but search fails")
        print("   Possible causes:")
        print("   1. Search parameters not compatible with eBay API")
        print("   2. No vehicles match the search criteria")
        print("   3. API response format changed")
        print("   4. Network/timeout issues")
    elif not oauth_working:
        print("\n💡 ISSUE: OAuth not working")
        print("   Check eBay API credentials and network connectivity")

if __name__ == "__main__":
    main()