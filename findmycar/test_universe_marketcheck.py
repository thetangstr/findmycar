#!/usr/bin/env python3
"""
Test Universe Marketcheck API with the free tier key
"""
import requests
import json
import os

# Your free tier API key
api_key = 'azp8YlkVTRrRty9kOktQMyF0YNDCv2SR'

def test_universe_api_endpoints():
    """Test possible Universe Marketcheck API endpoints"""
    print("🔍 Testing Universe Marketcheck API Endpoints")
    print("=" * 60)
    
    # Possible new API endpoints for Universe platform
    base_urls = [
        "https://api.universe.marketcheck.com",
        "https://universe-api.marketcheck.com", 
        "https://marketcheck-universe.herokuapp.com",
        "https://universe.marketcheck.com/api",
        "https://api.marketcheck.com/universe",
        "https://mc-api.marketcheck.com/universe"
    ]
    
    endpoints = [
        "/v1/search",
        "/v2/search",
        "/v1/listings/search",
        "/v2/listings/search", 
        "/search",
        "/inventory/search",
        "/cars/search"
    ]
    
    for base_url in base_urls:
        print(f"\nTesting base URL: {base_url}")
        
        # First, test if the base URL is accessible
        try:
            response = requests.get(base_url, timeout=10)
            print(f"  Base URL status: {response.status_code}")
            
            if response.status_code == 200:
                print("  ✅ Base URL accessible")
            elif response.status_code == 404:
                print("  ❌ Base URL not found")
                continue
            else:
                print(f"  ⚠️ Base URL returned {response.status_code}")
        except:
            print("  💥 Base URL connection failed")
            continue
        
        # Test endpoints
        for endpoint in endpoints:
            full_url = f"{base_url}{endpoint}"
            
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
                    'Authorization': f'Bearer {api_key}',
                    'X-API-Key': api_key
                }
                
                response = requests.get(full_url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"    ✅ SUCCESS: {endpoint}")
                        print(f"       Response keys: {list(data.keys())}")
                        
                        # Check for vehicle data
                        if 'listings' in data:
                            print(f"       Found {len(data['listings'])} listings")
                        elif 'results' in data:
                            print(f"       Found {len(data['results'])} results")
                        elif 'data' in data:
                            print(f"       Found data: {type(data['data'])}")
                        
                        return full_url, params, headers  # Return working endpoint
                        
                    except json.JSONDecodeError:
                        print(f"    ⚠️ {endpoint}: Non-JSON response")
                elif response.status_code == 401:
                    print(f"    🔑 {endpoint}: Unauthorized (API key issue)")
                elif response.status_code == 403:
                    print(f"    🚫 {endpoint}: Forbidden")
                elif response.status_code == 404:
                    print(f"    ❌ {endpoint}: Not found")
                else:
                    print(f"    ⚠️ {endpoint}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"    💥 {endpoint}: Error - {str(e)[:30]}")
    
    return None, None, None

def test_universe_with_different_auth():
    """Test with different authentication methods for Universe"""
    print("\n🔑 Testing Different Authentication Methods")
    print("=" * 60)
    
    # Try the most likely Universe endpoint
    test_urls = [
        "https://api.universe.marketcheck.com/v1/search",
        "https://universe.marketcheck.com/api/v1/search",
        "https://api.marketcheck.com/v1/search"  # Maybe they updated this one
    ]
    
    auth_methods = [
        {'params': {'api_key': api_key}},
        {'params': {'key': api_key}},
        {'params': {'token': api_key}},
        {'headers': {'Authorization': f'Bearer {api_key}'}},
        {'headers': {'X-API-Key': api_key}},
        {'headers': {'X-Auth-Token': api_key}},
        {'params': {'apikey': api_key}},
        {'params': {'access_token': api_key}}
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        
        for i, auth in enumerate(auth_methods):
            try:
                params = {'make': 'Honda', 'rows': 3}
                headers = {'User-Agent': 'FindMyCar/1.0'}
                
                if 'params' in auth:
                    params.update(auth['params'])
                if 'headers' in auth:
                    headers.update(auth['headers'])
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"  ✅ SUCCESS with auth method {i+1}: {auth}")
                    try:
                        data = response.json()
                        print(f"     Data keys: {list(data.keys())}")
                        return url, auth
                    except:
                        print("     Non-JSON response")
                elif response.status_code in [401, 403]:
                    print(f"  🔑 Auth method {i+1}: {response.status_code}")
                else:
                    print(f"  ❌ Auth method {i+1}: {response.status_code}")
                    
            except Exception as e:
                print(f"  💥 Auth method {i+1}: Error")
    
    return None, None

def check_universe_documentation():
    """Try to find documentation for the Universe API"""
    print("\n📖 Checking for Universe Documentation")
    print("=" * 60)
    
    doc_urls = [
        "https://universe.marketcheck.com/docs",
        "https://universe.marketcheck.com/api-docs",
        "https://docs.universe.marketcheck.com",
        "https://api.universe.marketcheck.com/docs",
        "https://universe.marketcheck.com/help"
    ]
    
    for url in doc_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Found documentation: {url}")
                
                # Look for API endpoint information in the response
                content = response.text.lower()
                if 'api.universe.marketcheck.com' in content:
                    print("  📍 Found api.universe.marketcheck.com reference")
                if '/v1/' in content:
                    print("  📍 Found /v1/ endpoint references")
                if '/search' in content:
                    print("  📍 Found /search endpoint references")
                    
                return url
            else:
                print(f"❌ {url}: Status {response.status_code}")
        except:
            print(f"💥 {url}: Connection error")
    
    return None

def main():
    print("🔍 Universe Marketcheck API Investigation")
    print("=" * 80)
    print(f"API Key: {api_key[:15]}... (Free Tier)")
    
    # Test different endpoints
    working_url, params, headers = test_universe_api_endpoints()
    
    if not working_url:
        # Try different auth methods
        working_url, auth = test_universe_with_different_auth()
    
    # Look for documentation
    doc_url = check_universe_documentation()
    
    print("\n" + "=" * 80)
    print("🔍 UNIVERSE INVESTIGATION RESULTS")
    print("=" * 80)
    
    if working_url:
        print(f"✅ Working Universe endpoint found: {working_url}")
        print("✅ Can fix Cars.com integration with Universe API")
    else:
        print("❌ No working Universe endpoints found")
        print("💡 Possible issues:")
        print("   1. Free tier API key may have limited endpoints")
        print("   2. Universe platform may require different base URLs")
        print("   3. API key may need activation or verification")
        print("   4. Free tier may have restricted access")
    
    if doc_url:
        print(f"📖 Documentation found: {doc_url}")
    else:
        print("📖 No accessible documentation found")
    
    print("\n💡 NEXT STEPS:")
    if working_url:
        print("1. Update Cars.com client with working Universe endpoint")
        print("2. Test with various search parameters")
        print("3. Implement proper error handling for free tier limits")
    else:
        print("1. Check universe.marketcheck.com dashboard for API details")
        print("2. Verify API key is activated and has correct permissions")
        print("3. Contact Marketcheck support for Universe API documentation")
        print("4. Consider using the direct Cars.com scraping as backup")

if __name__ == "__main__":
    main()