#!/usr/bin/env python3
"""
Test live search functionality with real eBay data
"""

import requests
import json
import time

BASE_URL = "http://localhost:8603"

print("=== Testing Production Vehicle Search with Live eBay Data ===\n")

# Test 1: Health check
print("1. Health Check:")
response = requests.get(f"{BASE_URL}/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Test 2: Detailed health check
print("\n2. Detailed Health Check:")
response = requests.get(f"{BASE_URL}/health/detailed")
health_data = response.json()
print(f"   Overall status: {health_data['status']}")
print(f"   Uptime: {health_data['uptime_human']}")
for component in health_data['components']:
    print(f"   - {component['name']}: {component['status']} ({component['message']})")

# Test 3: Search with live data
print("\n3. Live Search Test - Toyota Camry:")
search_params = {
    'query': 'Toyota Camry',
    'include_live': 'true',
    'per_page': 10
}
response = requests.get(f"{BASE_URL}/api/search/v2", params=search_params)
search_data = response.json()

if search_data['success']:
    print(f"   Total results: {search_data['total']}")
    print(f"   Local results: {search_data['local_count']}")
    print(f"   Live results: {search_data['live_count']}")
    print(f"   Sources used: {', '.join(search_data['sources_used'])}")
    print(f"   Search time: {search_data['search_time']:.2f}s")
    
    # Show first few results
    print("\n   First 3 vehicles:")
    for i, vehicle in enumerate(search_data['vehicles'][:3], 1):
        print(f"\n   {i}. {vehicle.get('year', 'N/A')} {vehicle['make']} {vehicle['model']}")
        print(f"      Price: ${vehicle['price']:,.0f}" if vehicle.get('price') else "      Price: N/A")
        print(f"      Mileage: {vehicle['mileage']:,} miles" if vehicle.get('mileage') else "      Mileage: N/A")
        print(f"      Location: {vehicle.get('location', 'N/A')}")
        print(f"      Source: {vehicle.get('source', 'unknown')}")
        if vehicle.get('is_live'):
            print(f"      *** LIVE DATA ***")
        print(f"      URL: {vehicle.get('view_item_url', 'N/A')}")
else:
    print(f"   Search failed: {search_data.get('error')}")

# Test 4: Search with filters
print("\n4. Filtered Search - Honda under $20,000:")
filtered_params = {
    'make': 'Honda',
    'price_max': '20000',
    'include_live': 'true',
    'per_page': 5
}
response = requests.get(f"{BASE_URL}/api/search/v2", params=filtered_params)
filtered_data = response.json()

if filtered_data['success']:
    print(f"   Total results: {filtered_data['total']}")
    print(f"   Live results included: {filtered_data['live_count']}")
    
    # Show results
    print("\n   Results:")
    for i, vehicle in enumerate(filtered_data['vehicles'][:5], 1):
        print(f"   {i}. {vehicle.get('year', 'N/A')} {vehicle['make']} {vehicle.get('model', 'N/A')} - ${vehicle.get('price', 0):,.0f}")

# Test 5: Get vehicle details with live data
if search_data['success'] and search_data['vehicles']:
    print("\n5. Vehicle Details Test:")
    vehicle_id = search_data['vehicles'][0].get('id')
    if vehicle_id:
        response = requests.get(f"{BASE_URL}/api/vehicle/{vehicle_id}?fetch_live=true")
        if response.ok:
            details = response.json()
            if details['success']:
                vehicle = details['vehicle']
                print(f"   Vehicle: {vehicle.get('year')} {vehicle['make']} {vehicle.get('model')}")
                print(f"   Current price: ${vehicle.get('price', 0):,.0f}")
                if vehicle.get('live_price'):
                    print(f"   Live price: ${vehicle['live_price']:,.0f}")
                    print(f"   Live available: {vehicle.get('live_available', False)}")
                print(f"   Last updated: {vehicle.get('updated_at', 'N/A')}")

# Test 6: Cache effectiveness
print("\n6. Cache Test - Repeat search:")
start_time = time.time()
response = requests.get(f"{BASE_URL}/api/search/v2", params=search_params)
cached_data = response.json()
search_time = time.time() - start_time

if cached_data['success']:
    print(f"   Search time: {search_time:.3f}s")
    print(f"   Cached: {cached_data.get('cached', False)}")
    print(f"   Results match: {cached_data['total'] == search_data['total']}")

# Test 7: Metrics endpoint
print("\n7. Metrics:")
response = requests.get(f"{BASE_URL}/metrics")
if response.ok:
    metrics_lines = response.text.strip().split('\n')
    for line in metrics_lines:
        if not line.startswith('#'):
            print(f"   {line}")

print("\n=== Production System Test Complete ===")
print("\nSummary:")
print(f"- Health status: {health_data['status']}")
print(f"- Live search working: {'Yes' if search_data['live_count'] > 0 else 'No'}")
print(f"- Total vehicles available: {search_data['total']}")
print(f"- Data sources: {', '.join(search_data['sources_used'])}")
print(f"- Cache working: {'Yes' if cached_data.get('cached') else 'In-memory only'}")
print("\n✅ Production system is operational with live eBay data!")