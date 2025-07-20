#!/usr/bin/env python3
"""
Test new Marketcheck API endpoints based on investigation
"""
import requests
import json
import os

# Set the API key
api_key = 'azp8YlkVTRrRty9kOktQMyF0YNDCv2SR'

def test_api_endpoints():
    """Test various possible API endpoints"""
    print("🔍 Testing Marketcheck API Endpoints")
    print("=" * 50)
    
    # Based on the investigation, try different API patterns
    base_urls = [
        "https://api.marketcheck.com",
        "https://mc-api.marketcheck.com", 
        "https://marketcheck-api.herokuapp.com",
        "https://api.marketcheck.io",
        "https://v2.api.marketcheck.com"
    ]
    
    endpoints = [
        "/v1/search",
        "/v2/search", 
        "/v1/search/car",
        "/v2/search/car",
        "/search",
        "/inventory/search"
    ]
    
    for base_url in base_urls:
        for endpoint in endpoints:
            full_url = f"{base_url}{endpoint}"
            print(f"\nTesting: {full_url}")
            
            try:
                params = {
                    'api_key': api_key,
                    'make': 'Honda',
                    'year_min': 2020,
                    'rows': 5
                }
                
                headers = {
                    'User-Agent': 'FindMyCar/1.0',
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {api_key}'  # Try bearer auth too
                }
                
                # Try both GET and POST
                for method in ['GET', 'POST']:
                    try:
                        if method == 'GET':
                            response = requests.get(full_url, params=params, headers=headers, timeout=10)
                        else:
                            response = requests.post(full_url, json=params, headers=headers, timeout=10)
                        
                        print(f"   {method} Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                if 'listings' in data or 'results' in data or 'data' in data:
                                    print(f"   ✅ SUCCESS! Working endpoint found")
                                    print(f"   Data keys: {list(data.keys())}")
                                    return full_url, method, params, headers
                            except:
                                pass
                        elif response.status_code in [400, 401, 403]:
                            print(f"   Auth/param issue: {response.text[:100]}")
                        elif response.status_code == 404:
                            print(f"   Not found")
                        else:
                            print(f"   Other: {response.text[:50]}")
                            
                    except requests.exceptions.ConnectTimeout:
                        print(f"   {method} Timeout")
                    except requests.exceptions.ConnectionError:
                        print(f"   {method} Connection error")
                    except Exception as e:
                        print(f"   {method} Error: {str(e)[:30]}")
            
            except Exception as e:
                print(f"   Setup error: {e}")
    
    return None, None, None, None

def test_alternative_auth():
    """Test different authentication methods"""
    print("\n🔑 Testing Alternative Authentication")
    print("=" * 50)
    
    # Try the most promising endpoint with different auth
    url = "https://api.marketcheck.com/v2/search"
    
    auth_methods = [
        {'params': {'api_key': api_key}},
        {'headers': {'X-API-Key': api_key}},
        {'headers': {'Authorization': f'Bearer {api_key}'}},
        {'headers': {'Authorization': f'ApiKey {api_key}'}},
        {'params': {'token': api_key}},
        {'params': {'access_token': api_key}}
    ]
    
    base_params = {
        'make': 'Honda',
        'year_min': 2020,
        'rows': 3
    }
    
    for i, auth in enumerate(auth_methods):
        print(f"\nAuth method {i+1}: {auth}")
        
        try:
            params = base_params.copy()
            headers = {'User-Agent': 'FindMyCar/1.0'}
            
            if 'params' in auth:
                params.update(auth['params'])
            if 'headers' in auth:
                headers.update(auth['headers'])
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS with auth method {i+1}")
                return auth
            else:
                print(f"   Response: {response.text[:100]}")
                
        except Exception as e:
            print(f"   Error: {e}")
    
    return None

def create_fixed_cars_com_client():
    """Create a fixed Cars.com client if we find working endpoints"""
    print("\n🔧 Creating Fixed Cars.com Client")
    print("=" * 50)
    
    # Test if any endpoints work first
    working_url, method, params, headers = test_api_endpoints()
    
    if working_url:
        print(f"✅ Found working endpoint: {working_url}")
        
        # Create updated client code
        client_code = f'''
# Updated Cars.com client with working Marketcheck endpoint
class CarsComClientFixed:
    def __init__(self):
        self.api_key = "{api_key}"
        self.base_url = "{working_url.rsplit('/', 1)[0]}"
        self.method = "{method}"
        
    def search_vehicles(self, **kwargs):
        # Implementation with working endpoint
        pass
'''
        
        print("Client update code generated")
        return True
    else:
        print("❌ No working endpoints found")
        return False

def main():
    print("🔍 New Marketcheck API Investigation")
    print("=" * 60)
    
    # Test endpoints
    working_url, method, params, headers = test_api_endpoints()
    
    if not working_url:
        # Try alternative auth
        auth = test_alternative_auth()
    
    # Try to create fixed client
    fixed = create_fixed_cars_com_client()
    
    print("\n" + "=" * 60)
    print("🔍 INVESTIGATION RESULTS")
    print("=" * 60)
    
    if working_url:
        print(f"✅ Working endpoint found: {working_url}")
        print(f"✅ Method: {method}")
        print("✅ Can fix Cars.com integration")
    else:
        print("❌ No working Marketcheck endpoints found")
        print("💡 Recommendations:")
        print("   1. API key may be invalid or expired")
        print("   2. Marketcheck may have changed their API completely")
        print("   3. Need to sign up for new account at universe.marketcheck.com")
        print("   4. Consider implementing direct Cars.com scraping instead")

if __name__ == "__main__":
    main()