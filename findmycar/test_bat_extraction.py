#!/usr/bin/env python3
"""
Test BaT data extraction directly
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from bat_client import BringATrailerClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_bat_extraction():
    print("🧪 Testing BaT Data Extraction")
    print("=" * 60)
    
    client = BringATrailerClient()
    
    try:
        # Test with a general search
        print("\n🔍 Testing general auction search...")
        vehicles = client.search_listings("Porsche", limit=3)
        
        print(f"✅ Found {len(vehicles)} auction listings")
        
        for i, vehicle in enumerate(vehicles):
            print(f"\n🏁 Auction {i+1}:")
            print(f"   Title: {vehicle.get('title')}")
            print(f"   Make: {vehicle.get('make')}")
            print(f"   Model: {vehicle.get('model')}")
            print(f"   Year: {vehicle.get('year')}")
            print(f"   Current Bid: ${vehicle.get('price'):,}" if vehicle.get('price') else "   Current Bid: None")
            print(f"   BaT URL: {vehicle.get('view_item_url')}")
            print(f"   Auction ID: {vehicle.get('listing_id')}")
            print(f"   Image: {vehicle.get('image_urls')[0] if vehicle.get('image_urls') else 'None'}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    test_bat_extraction()