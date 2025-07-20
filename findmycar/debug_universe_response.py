#!/usr/bin/env python3
"""
Debug the Universe Marketcheck API response to find the correct format
"""
import requests

def debug_universe_response():
    """Debug what Universe API is actually returning"""
    print("🔍 Debugging Universe Marketcheck Response")
    print("=" * 60)
    
    api_key = 'azp8YlkVTRrRty9kOktQMyF0YNDCv2SR'
    url = "https://universe.marketcheck.com/api/v1/search"
    
    params = {
        'api_key': api_key,
        'make': 'Honda',
        'rows': 3
    }
    
    headers = {
        'User-Agent': 'FindMyCar/1.0',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Content Type: {response.headers.get('content-type', 'unknown')}")
        print(f"Response Length: {len(response.text)}")
        
        # Check if it's HTML or JSON
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/json' in content_type:
            print("\n✅ Response is JSON")
            try:
                data = response.json()
                print(f"JSON Keys: {list(data.keys())}")
                return data
            except:
                print("❌ Failed to parse JSON")
        elif 'text/html' in content_type:
            print("\n⚠️ Response is HTML (not JSON)")
            print("First 500 characters:")
            print("-" * 40)
            print(response.text[:500])
            print("-" * 40)
            
            # Look for clues in the HTML
            html = response.text.lower()
            if 'api' in html:
                print("📍 Found 'api' references in HTML")
            if 'endpoint' in html:
                print("📍 Found 'endpoint' references in HTML")
            if 'documentation' in html:
                print("📍 Found 'documentation' references in HTML")
            if 'login' in html or 'sign' in html:
                print("📍 May require authentication/login")
                
        # Try different endpoints
        print("\n🔍 Trying Alternative Endpoints:")
        
        alt_endpoints = [
            "/api/v2/search",
            "/api/search", 
            "/api/listings",
            "/api/inventory",
            "/api/v1/listings",
            "/api/v1/cars"
        ]
        
        for endpoint in alt_endpoints:
            alt_url = f"https://universe.marketcheck.com{endpoint}"
            try:
                alt_response = requests.get(alt_url, params=params, headers=headers, timeout=10)
                alt_content_type = alt_response.headers.get('content-type', '').lower()
                
                if alt_response.status_code == 200:
                    if 'application/json' in alt_content_type:
                        print(f"  ✅ {endpoint}: JSON response!")
                        return alt_response.json()
                    else:
                        print(f"  ⚠️ {endpoint}: HTML response (status 200)")
                else:
                    print(f"  ❌ {endpoint}: Status {alt_response.status_code}")
            except:
                print(f"  💥 {endpoint}: Connection error")
                
    except Exception as e:
        print(f"💥 Error: {e}")
    
    return None

def test_universe_with_proper_headers():
    """Try with headers that might work for Universe"""
    print("\n🔍 Testing with Different Headers")
    print("=" * 60)
    
    api_key = 'azp8YlkVTRrRty9kOktQMyF0YNDCv2SR'
    url = "https://universe.marketcheck.com/api/v1/search"
    
    params = {
        'api_key': api_key,
        'make': 'Honda',
        'rows': 5
    }
    
    # Try different header combinations
    header_sets = [
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://universe.marketcheck.com',
            'Referer': 'https://universe.marketcheck.com/'
        },
        {
            'User-Agent': 'FindMyCar API Client 1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        {
            'User-Agent': 'curl/7.68.0',
            'Accept': '*/*'
        }
    ]
    
    for i, headers in enumerate(header_sets, 1):
        print(f"\nHeader set {i}:")
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            content_type = response.headers.get('content-type', '').lower()
            
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {content_type}")
            
            if 'application/json' in content_type:
                print(f"  ✅ JSON response!")
                data = response.json()
                print(f"  Keys: {list(data.keys())}")
                return data
            else:
                print(f"  ⚠️ Non-JSON response")
                
        except Exception as e:
            print(f"  💥 Error: {e}")
    
    return None

def main():
    print("🔍 Universe Marketcheck API Debug")
    print("=" * 80)
    
    # Debug the response
    data = debug_universe_response()
    
    if not data:
        # Try with different headers
        data = test_universe_with_proper_headers()
    
    print("\n" + "=" * 80)
    print("🔍 DEBUG RESULTS")
    print("=" * 80)
    
    if data:
        print("✅ Successfully got JSON data from Universe API!")
        print("✅ Can fix Cars.com integration")
    else:
        print("❌ Universe API is not returning JSON data")
        print("💡 Possible issues:")
        print("   1. API endpoints may have changed")
        print("   2. Free tier may require different authentication")
        print("   3. May need to authenticate through web interface first")
        print("   4. API key may need activation in Universe dashboard")
        
        print("\n💡 RECOMMENDATION:")
        print("   Use the direct Cars.com scraping implementation as it's working")

if __name__ == "__main__":
    main()