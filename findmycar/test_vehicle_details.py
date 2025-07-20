#!/usr/bin/env python3
"""Test vehicle details from API"""

import requests
import json

# Get Honda vehicles
response = requests.get("http://localhost:8602/api/search/v2", params={"query": "honda", "per_page": 5})
data = response.json()

print(f"Found {data['total']} Honda vehicles\n")
print("First 5 vehicles:")
print("-" * 80)

for i, vehicle in enumerate(data['vehicles'], 1):
    print(f"\n{i}. {vehicle['year']} {vehicle['make']} {vehicle['model']}")
    print(f"   Price: ${vehicle['price']:,.0f}" if vehicle['price'] else "   Price: N/A")
    print(f"   Mileage: {vehicle['mileage']:,} miles" if vehicle['mileage'] else "   Mileage: N/A")
    print(f"   Body Style: {vehicle['body_style'] or 'N/A'}")
    print(f"   Color: {vehicle['exterior_color'] or 'N/A'}")
    print(f"   Location: {vehicle['location'] or 'N/A'}")
    
    # Check attributes
    attrs = vehicle.get('attributes', {})
    if attrs:
        print(f"   Attributes: MPG City: {attrs.get('mpg_city', 'N/A')}, "
              f"Seats: {attrs.get('seating_capacity', 'N/A')}")
    
    # Check features
    features = vehicle.get('features', [])
    if features:
        print(f"   Features: {', '.join(features[:3])}...")

print("\n" + "-" * 80)
print("\nTesting specific filters:")

# Test family SUV preset
response = requests.get("http://localhost:8602/api/search/v2", params={
    "preset": "family_suv",
    "per_page": 3
})
data = response.json()

print(f"\nFamily SUVs found: {data['total']}")
for vehicle in data['vehicles']:
    print(f"  - {vehicle['year']} {vehicle['make']} {vehicle['model']} "
          f"(${vehicle['price']:,.0f}, {vehicle.get('body_style', 'N/A')})")