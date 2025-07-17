#!/usr/bin/env python3
"""
Test CarMax data extraction directly
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from carmax_client import CarMaxClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_carmax_extraction():
    print("🧪 Testing CarMax Data Extraction")
    print("=" * 60)
    
    client = CarMaxClient()
    
    try:
        # Test with Honda Civic
        print("\n🔍 Testing Honda Civic search...")
        vehicles = client.search_listings("Honda Civic", limit=5)
        
        print(f"✅ Found {len(vehicles)} vehicles")
        
        for i, vehicle in enumerate(vehicles):
            print(f"\n🚗 Vehicle {i+1}:")
            print(f"   Title: {vehicle.get('title')}")
            print(f"   Make: {vehicle.get('make')}")
            print(f"   Model: {vehicle.get('model')}")
            print(f"   Year: {vehicle.get('year')}")
            print(f"   Price: ${vehicle.get('price'):,}" if vehicle.get('price') else "   Price: None")
            print(f"   Mileage: {vehicle.get('mileage'):,} miles" if vehicle.get('mileage') else "   Mileage: None")
            print(f"   URL: {vehicle.get('view_item_url')}")
            print(f"   Listing ID: {vehicle.get('listing_id')}")
            print(f"   Image: {vehicle.get('image_urls')[0] if vehicle.get('image_urls') else 'None'}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    test_carmax_extraction()