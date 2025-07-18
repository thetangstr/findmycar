#!/usr/bin/env python3
"""Simple test to verify search behavior."""

import requests

def test_search_endpoints():
    """Test both sync and async search endpoints."""
    
    print("🧪 Testing search endpoints\n")
    
    # Test data
    search_data = {
        'query': 'honda civic eg6',
        'year_min': 2000,
        'year_max': 2024,
        'price_min': 5000,
        'price_max': 100000,
        'sources': ['ebay', 'carmax']
    }
    
    base_url = "http://localhost:8601"
    
    # Test 1: Sync search endpoint
    print("🔄 Testing sync search endpoint (/ingest)...")
    try:
        response = requests.post(f"{base_url}/ingest", data=search_data, allow_redirects=False)
        print(f"  Status: {response.status_code}")
        if response.status_code == 303:
            redirect_url = response.headers.get('Location', '')
            print(f"  Redirect: {redirect_url}")
            print("  ✅ Sync endpoint working")
        else:
            print(f"  ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 2: Async search endpoint
    print("\n🚀 Testing async search endpoint (/search/async)...")
    try:
        response = requests.post(f"{base_url}/search/async", data=search_data)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ Async endpoint working")
            # Check if it returns HTML (progress page)
            if 'html' in response.headers.get('content-type', '').lower():
                print("  📄 Returns HTML progress page")
            else:
                print("  📄 Returns:", response.text[:200])
        else:
            print(f"  ❌ Unexpected status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 3: Direct homepage with filters
    print("\n🔍 Testing homepage with filters...")
    try:
        params = {
            'make': 'Honda',
            'model': 'Civic', 
            'year_min': 1992,
            'year_max': 1995
        }
        response = requests.get(f"{base_url}/", params=params)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            # Check if it shows filtered results
            if 'vehicles found' in response.text:
                import re
                match = re.search(r'(\d+) vehicles found', response.text)
                if match:
                    count = match.group(1)
                    print(f"  📊 Shows {count} vehicles")
                    if count == '2':
                        print("  ✅ Filtering working correctly")
                    else:
                        print("  ❌ Filtering not working - should show 2 vehicles")
                else:
                    print("  ❌ Could not find vehicle count")
            else:
                print("  ❌ Could not find vehicle count in response")
        else:
            print(f"  ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    test_search_endpoints()