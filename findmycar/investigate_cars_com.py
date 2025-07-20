#!/usr/bin/env python3
"""
Investigate Cars.com / Marketcheck API issues
"""
import os
import requests
import logging
from datetime import datetime
import socket
import dns.resolver

# Set the API key
os.environ['MARKETCHECK_API_KEY'] = 'azp8YlkVTRrRty9kOktQMyF0YNDCv2SR'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_dns_resolution():
    """Test DNS resolution for Marketcheck endpoints"""
    print("\n🔍 DNS Resolution Test")
    print("-" * 40)
    
    endpoints = [
        'marketcheck-prod.apigee.net',
        'api.marketcheck.com',
        'mc-api.marketcheck.com',
        'marketcheck.com'
    ]
    
    for endpoint in endpoints:
        try:
            # Try DNS resolution
            result = socket.gethostbyname(endpoint)
            print(f"✅ {endpoint} -> {result}")
        except socket.gaierror as e:
            print(f"❌ {endpoint} -> DNS Error: {e}")
        except Exception as e:
            print(f"💥 {endpoint} -> Error: {e}")

def test_marketcheck_endpoints():
    """Test different Marketcheck API endpoints"""
    print("\n🔍 Marketcheck API Endpoints Test")
    print("-" * 40)
    
    api_key = os.getenv('MARKETCHECK_API_KEY')
    
    # Different endpoint possibilities
    endpoints = [
        "https://mc-api.marketcheck.com/v2/search/car",
        "https://api.marketcheck.com/v2/search/car", 
        "https://marketcheck-prod.apigee.net/v2/search/car/active",
        "https://marketcheck.com/api/v2/search/car"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint}")
        try:
            params = {
                'api_key': api_key,
                'make': 'Honda',
                'rows': 3
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS - Found {data.get('num_found', 0)} vehicles")
                return endpoint  # Return working endpoint
            else:
                print(f"   ❌ Error: {response.text[:100]}...")
                
        except requests.exceptions.ConnectTimeout:
            print(f"   ⏰ Timeout")
        except requests.exceptions.ConnectionError as e:
            print(f"   🔌 Connection Error: {str(e)[:100]}...")
        except Exception as e:
            print(f"   💥 Error: {str(e)[:100]}...")
    
    return None

def test_api_key_validity():
    """Test if the API key is valid with different approaches"""
    print("\n🔍 API Key Validity Test")
    print("-" * 40)
    
    api_key = os.getenv('MARKETCHECK_API_KEY')
    print(f"API Key: {api_key[:10]}...")
    
    # Try the main marketcheck.com website
    try:
        # Check if we can access the main site
        response = requests.get("https://www.marketcheck.com", timeout=10)
        print(f"Main site status: {response.status_code}")
        
        # Try to find API documentation or endpoints
        if 'api' in response.text.lower():
            print("✅ Main site mentions API")
        else:
            print("⚠️ No API references found on main site")
            
    except Exception as e:
        print(f"❌ Cannot access main site: {e}")

def check_alternative_cars_sources():
    """Check if Cars.com has alternative access methods"""
    print("\n🔍 Alternative Cars.com Access Methods")
    print("-" * 40)
    
    # Try direct Cars.com API (if any)
    try:
        # Check robots.txt
        response = requests.get("https://www.cars.com/robots.txt", timeout=10)
        if response.status_code == 200:
            print("✅ Cars.com robots.txt accessible")
            if 'api' in response.text.lower():
                print("   Found API references in robots.txt")
        
        # Try to access their search endpoint directly
        cars_search_url = "https://www.cars.com/shopping/api/search"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.cars.com/'
        }
        
        params = {
            'make': 'honda',
            'maximum_distance': 50,
            'zip': '10001'
        }
        
        response = requests.get(cars_search_url, headers=headers, params=params, timeout=10)
        print(f"Cars.com direct API status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Cars.com direct API accessible!")
            return True
            
    except Exception as e:
        print(f"❌ Cars.com direct access failed: {e}")
    
    return False

def investigate_marketcheck_status():
    """Check Marketcheck service status"""
    print("\n🔍 Marketcheck Service Status Investigation")
    print("-" * 40)
    
    # Check if Marketcheck has a status page
    status_urls = [
        "https://status.marketcheck.com",
        "https://marketcheck.statuspage.io",
        "https://www.marketcheck.com/status"
    ]
    
    for url in status_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Found status page: {url}")
                return
        except:
            continue
    
    print("❌ No accessible status pages found")
    
    # Try to find documentation
    doc_urls = [
        "https://www.marketcheck.com/api",
        "https://docs.marketcheck.com",
        "https://api.marketcheck.com/docs"
    ]
    
    for url in doc_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Found documentation: {url}")
                return
        except:
            continue
    
    print("❌ No accessible documentation found")

def test_cars_com_client_fix():
    """Test potential fixes for the Cars.com client"""
    print("\n🔧 Testing Cars.com Client Fixes")
    print("-" * 40)
    
    # Try updating the Cars.com client with different endpoints
    from cars_com_client import CarsComClient
    
    # Test different API base URLs
    test_urls = [
        "https://mc-api.marketcheck.com/v2",
        "https://api.marketcheck.com/v2",
        "https://marketcheck.com/api/v2"
    ]
    
    for base_url in test_urls:
        print(f"\nTesting base URL: {base_url}")
        
        try:
            # Temporarily modify the client
            client = CarsComClient()
            original_url = client.API_BASE_URL
            client.API_BASE_URL = base_url
            
            # Test health check
            health = client.check_health()
            print(f"   Health: {health['status']}")
            
            if health['status'] == 'healthy':
                print(f"   ✅ Working base URL found: {base_url}")
                return base_url
            
            # Restore original
            client.API_BASE_URL = original_url
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}...")
    
    return None

def main():
    print("🔍 Cars.com / Marketcheck API Investigation")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all investigation tests
    test_dns_resolution()
    working_endpoint = test_marketcheck_endpoints()
    test_api_key_validity()
    cars_direct = check_alternative_cars_sources()
    investigate_marketcheck_status()
    working_client_url = test_cars_com_client_fix()
    
    # Summary
    print("\n" + "=" * 60)
    print("🔍 INVESTIGATION SUMMARY")
    print("=" * 60)
    
    if working_endpoint:
        print(f"✅ Working Marketcheck endpoint found: {working_endpoint}")
    else:
        print("❌ No working Marketcheck endpoints found")
    
    if cars_direct:
        print("✅ Cars.com direct API accessible")
    else:
        print("❌ Cars.com direct API not accessible")
    
    if working_client_url:
        print(f"✅ Working client base URL: {working_client_url}")
    else:
        print("❌ No working client configurations found")
    
    print("\n💡 RECOMMENDATIONS:")
    
    if working_endpoint or working_client_url:
        print("1. Update Cars.com client with working endpoint")
        print("2. Test thoroughly with new configuration")
    elif cars_direct:
        print("1. Implement direct Cars.com scraping approach")
        print("2. Use their website API instead of Marketcheck")
    else:
        print("1. Marketcheck API appears to be discontinued or moved")
        print("2. Consider alternative Cars.com integration methods")
        print("3. Look for other automotive data providers")
        print("4. Implement direct Cars.com website scraping")

if __name__ == "__main__":
    main()