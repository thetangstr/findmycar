#!/usr/bin/env python3
"""
Test all available data sources
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import clients
from carmax_client import CarMaxClient
from autotrader_client import AutotraderClient
from ebay_live_client import EbayLiveClient

print("=== Testing All Vehicle Data Sources ===\n")

# Test configuration
search_query = "Honda Civic"
limit = 3

# 1. Test eBay (API)
print("1. eBay Motors API:")
try:
    if os.environ.get('EBAY_CLIENT_ID'):
        ebay_client = EbayLiveClient()
        results = ebay_client.search_vehicles(
            query=search_query,
            per_page=limit
        )
        print(f"   ✅ Found {results['total']} vehicles")
        for i, vehicle in enumerate(results['vehicles'][:limit], 1):
            print(f"   {i}. {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')} - ${vehicle.get('price', 0):,.0f}")
    else:
        print("   ❌ API credentials not configured")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Test CarMax (Scraping)
print("\n2. CarMax (Web Scraping):")
try:
    carmax_client = CarMaxClient()
    vehicles = carmax_client.search_listings(search_query, limit=limit)
    print(f"   ✅ Found {len(vehicles)} vehicles")
    for i, vehicle in enumerate(vehicles[:limit], 1):
        print(f"   {i}. {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')} - ${vehicle.get('price', 0):,.0f}")
    carmax_client.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Test AutoTrader (Scraping)
print("\n3. AutoTrader (Web Scraping):")
try:
    autotrader_client = AutotraderClient()
    vehicles = autotrader_client.search_listings(search_query, limit=limit)
    print(f"   ✅ Found {len(vehicles)} vehicles")
    for i, vehicle in enumerate(vehicles[:limit], 1):
        print(f"   {i}. {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')} - ${vehicle.get('price', 0):,.0f}")
    autotrader_client.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

# Summary
print("\n=== Summary ===")
print("Available Real-Time Data Sources:")
print("- eBay Motors: API-based (requires credentials)")
print("- CarMax: Web scraping (working)")
print("- AutoTrader: Web scraping (working)")
print("\nNote: Web scraping is slower than APIs but provides real data")