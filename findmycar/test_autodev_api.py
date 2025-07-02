#!/usr/bin/env python3

"""
Test Auto.dev Vehicle Listings API
"""

import requests
import json
from typing import Dict, List, Optional

class AutoDevAPITester:
    """Test client for Auto.dev Vehicle Listings API"""
    
    def __init__(self):
        self.base_url = "https://auto.dev/api/listings"
        self.api_key = None  # Will need to get free API key
    
    def test_without_auth(self):
        """Test API without authentication to see response format"""
        
        print("🔍 Testing Auto.dev API without authentication...")
        
        # Test basic request
        params = {
            'make': 'Honda',
            'model': 'Civic',
            'year_min': 2020,
            'page': 1
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📝 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 401:
                print("✅ Expected 401 - Authentication required")
                print("💡 Need to sign up for free API key at auto.dev")
                
            elif response.status_code == 200:
                print("✅ Success! Got data without auth")
                data = response.json()
                print(f"📦 Response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                
            else:
                print(f"❓ Unexpected status: {response.status_code}")
                print(f"📄 Response: {response.text[:500]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
    
    def get_api_key_info(self):
        """Show how to get API key"""
        print("\n🔑 To get Auto.dev API key:")
        print("1. Visit: https://www.auto.dev/listings")
        print("2. Click 'Get your free API key in seconds'")
        print("3. Sign up for free tier (10,000 calls/month)")
        print("4. Copy API key to .env file")
    
    def test_with_api_key(self, api_key: str):
        """Test API with authentication"""
        
        print(f"\n🔍 Testing Auto.dev API with authentication...")
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Test Honda Civic search
        params = {
            'make': 'Honda',
            'model': 'Civic',
            'year_min': 2020,
            'page': 1,
            'condition': 'used'
        }
        
        try:
            response = requests.get(self.base_url, params=params, headers=headers, timeout=15)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Success! Got vehicle listings")
                
                # Analyze response structure
                if isinstance(data, dict):
                    print(f"📦 Response keys: {list(data.keys())}")
                    
                    if 'listings' in data:
                        listings = data['listings']
                        print(f"🚗 Found {len(listings)} listings")
                        
                        if listings:
                            # Show first listing structure
                            first_listing = listings[0]
                            print(f"📋 First listing keys: {list(first_listing.keys())}")
                            
                            # Show sample data
                            sample_data = {
                                'title': first_listing.get('title', 'N/A'),
                                'price': first_listing.get('price', 'N/A'),
                                'year': first_listing.get('year', 'N/A'),
                                'make': first_listing.get('make', 'N/A'),
                                'model': first_listing.get('model', 'N/A'),
                                'mileage': first_listing.get('mileage', 'N/A'),
                                'location': first_listing.get('location', 'N/A'),
                                'url': first_listing.get('url', 'N/A')
                            }
                            
                            print("📄 Sample listing:")
                            for key, value in sample_data.items():
                                print(f"  {key}: {value}")
                    
                    elif 'data' in data:
                        listings = data['data']
                        print(f"🚗 Found {len(listings)} listings in 'data' field")
                        
                    else:
                        print("📦 Response structure:")
                        print(json.dumps(data, indent=2)[:1000])
                        
                elif isinstance(data, list):
                    print(f"🚗 Got {len(data)} listings as array")
                    if data:
                        print(f"📋 First listing keys: {list(data[0].keys())}")
                        
            elif response.status_code == 401:
                print("❌ Authentication failed - check API key")
                
            elif response.status_code == 403:
                print("❌ Forbidden - API key may be invalid or expired")
                
            else:
                print(f"❌ Error {response.status_code}: {response.text[:500]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")

def main():
    """Run Auto.dev API tests"""
    
    print("🧪 Auto.dev Vehicle Listings API Test")
    print("=" * 50)
    
    tester = AutoDevAPITester()
    
    # Test without auth first
    tester.test_without_auth()
    
    # Show how to get API key
    tester.get_api_key_info()
    
    # Test with API key if available
    print("\n" + "=" * 50)
    api_key = input("Enter your Auto.dev API key (or press Enter to skip): ").strip()
    
    if api_key:
        tester.test_with_api_key(api_key)
    else:
        print("⏭️  Skipping authenticated test")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()