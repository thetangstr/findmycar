#!/usr/bin/env python3
"""
Test Marketcheck API directly with the provided key
"""
import os
import logging
import requests
from datetime import datetime

# Set the API key directly
os.environ['MARKETCHECK_API_KEY'] = 'azp8YlkVTRrRty9kOktQMyF0YNDCv2SR'

from cars_com_client import CarsComClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_marketcheck_raw_api():
    """Test Marketcheck API directly"""
    print("\n" + "="*50)
    print("Testing Marketcheck API Directly")
    print("="*50)
    
    api_key = os.getenv('MARKETCHECK_API_KEY')
    print(f"API Key: {api_key[:8]}...")
    
    # Test raw API call
    try:
        url = "https://mc-api.marketcheck.com/v2/search/car"
        params = {
            'api_key': api_key,
            'year_min': 2020,
            'make': 'Honda',
            'rows': 10
        }
        
        print("\n1. Testing raw API call...")
        response = requests.get(url, params=params, timeout=10)
        print(f"   Status code: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Total listings: {data.get('num_found', 0)}")
            print(f"   Listings returned: {len(data.get('listings', []))}")
            
            # Show sample listing
            listings = data.get('listings', [])
            if listings:
                sample = listings[0]
                print(f"\n   Sample listing:")
                print(f"     VIN: {sample.get('vin', 'N/A')}")
                print(f"     Year: {sample.get('year', 'N/A')}")
                print(f"     Make: {sample.get('make', 'N/A')}")
                print(f"     Model: {sample.get('model', 'N/A')}")
                print(f"     Price: ${sample.get('price', 0):,}")
                print(f"     Mileage: {sample.get('miles', 'N/A'):,}")
        else:
            print(f"   Error response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"   Error: {str(e)}")
        return False

def test_cars_com_client():
    """Test Cars.com client with the API key"""
    print("\n" + "="*50)
    print("Testing Cars.com Client")
    print("="*50)
    
    try:
        client = CarsComClient()
        
        # Test health check
        print("\n1. Testing health check...")
        health = client.check_health()
        print(f"   Status: {health['status']}")
        print(f"   Message: {health['message']}")
        
        if health['status'] != 'healthy':
            print("   ⚠️  Health check failed, but continuing...")
        
        # Test search
        print("\n2. Testing vehicle search...")
        results = client.search_vehicles(
            make="Toyota",
            model="Camry",
            year_min=2020,
            price_max=35000,
            per_page=5
        )
        
        print(f"   Found {results['total']} vehicles")
        print(f"   Showing {len(results['vehicles'])} results")
        
        # Display results
        for i, vehicle in enumerate(results['vehicles'][:3], 1):
            print(f"\n   Vehicle {i}:")
            print(f"     Title: {vehicle['title']}")
            print(f"     Price: ${vehicle['price']:,}")
            print(f"     Mileage: {vehicle.get('mileage', 'N/A'):,} miles" if vehicle.get('mileage') else "     Mileage: N/A")
            print(f"     Location: {vehicle.get('location', 'N/A')}")
        
        return results['total'] > 0
        
    except Exception as e:
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Marketcheck API Direct Test")
    print("===========================")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test raw API first
    raw_success = test_marketcheck_raw_api()
    
    # Test client implementation
    client_success = test_cars_com_client()
    
    print("\n" + "="*50)
    print("Test Results")
    print("="*50)
    print(f"Raw API: {'✓ PASSED' if raw_success else '✗ FAILED'}")
    print(f"Client: {'✓ PASSED' if client_success else '✗ FAILED'}")
    
    if raw_success and client_success:
        print("\n🎉 Cars.com (Marketcheck) is working!")
    elif raw_success:
        print("\n⚠️  API works but client needs fixes")
    else:
        print("\n❌ API key or endpoint issues")

if __name__ == "__main__":
    main()