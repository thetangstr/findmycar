#!/usr/bin/env python3
"""
Debug script for Cars & Bids API 403 errors
Tests various API endpoints and authentication methods
"""

import requests
import json
from datetime import datetime
import time

def test_cars_bids_endpoints():
    """Test various Cars & Bids API endpoints"""
    print("🔍 Testing Cars & Bids API Endpoints")
    print("=" * 50)
    
    # Different endpoint patterns to test
    endpoints = [
        # Current API endpoints
        "https://carsandbids.com/api/v2/auctions",
        "https://carsandbids.com/api/v1/auctions",
        "https://carsandbids.com/api/auctions",
        
        # Alternative API paths
        "https://api.carsandbids.com/v2/auctions",
        "https://api.carsandbids.com/v1/auctions",
        "https://api.carsandbids.com/auctions",
        
        # GraphQL endpoint
        "https://carsandbids.com/graphql",
        
        # Public data endpoints
        "https://carsandbids.com/public/auctions",
        "https://carsandbids.com/feed/auctions",
        "https://carsandbids.com/data/auctions.json",
        
        # RSS/XML feeds
        "https://carsandbids.com/rss",
        "https://carsandbids.com/feed",
        "https://carsandbids.com/rss/auctions",
    ]
    
    # Different header combinations to test
    header_sets = [
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://carsandbids.com/'
        },
        {
            'User-Agent': 'CarsAndBids/1.0 (Mobile App)',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
            'Accept': 'application/json',
            'Referer': 'https://carsandbids.com/auctions'
        },
        {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
        }
    ]
    
    results = []
    
    for i, headers in enumerate(header_sets):
        print(f"\n--- Testing with Header Set {i+1} ---")
        print(f"User-Agent: {headers.get('User-Agent', 'None')}")
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers=headers, timeout=10)
                
                result = {
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'content_length': len(response.text),
                    'headers_used': i + 1,
                    'response_preview': response.text[:200] if response.text else 'Empty'
                }
                
                results.append(result)
                
                print(f"{endpoint}: {response.status_code} ({response.headers.get('content-type', 'unknown')})")
                
                if response.status_code == 200:
                    print(f"  ✅ SUCCESS! Content length: {len(response.text)}")
                    if response.headers.get('content-type', '').startswith('application/json'):
                        try:
                            data = response.json()
                            print(f"  📄 JSON keys: {list(data.keys()) if isinstance(data, dict) else 'Array/Other'}")
                        except:
                            print("  ❌ Invalid JSON response")
                elif response.status_code == 403:
                    print(f"  🚫 FORBIDDEN - {response.text[:100]}")
                elif response.status_code == 429:
                    print(f"  ⏱️ RATE LIMITED")
                elif response.status_code == 404:
                    print(f"  ❌ NOT FOUND")
                else:
                    print(f"  ❓ Other: {response.text[:100]}")
                    
                # Brief delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"{endpoint}: ERROR - {str(e)}")
                results.append({
                    'endpoint': endpoint,
                    'status_code': 'ERROR',
                    'error': str(e),
                    'headers_used': i + 1
                })
    
    # Save detailed results
    with open('/Users/Kailor_1/Desktop/Projects/fmc/findmycar/cars_bids_debug_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

def test_website_analysis():
    """Analyze the Cars & Bids website for API patterns"""
    print("\n🔍 Analyzing Cars & Bids Website")
    print("=" * 50)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Test main website
        response = requests.get("https://carsandbids.com", headers=headers, timeout=10)
        print(f"Main website: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Look for API endpoints in JavaScript
            if 'api/' in content.lower():
                print("✅ Found API references in main page")
                
            # Look for specific patterns
            patterns = [
                '/api/v2/auctions',
                '/api/v1/auctions', 
                '/graphql',
                'api_key',
                'authorization',
                'bearer',
                'x-api-key'
            ]
            
            found_patterns = []
            for pattern in patterns:
                if pattern.lower() in content.lower():
                    found_patterns.append(pattern)
            
            if found_patterns:
                print(f"✅ Found patterns: {', '.join(found_patterns)}")
            else:
                print("❌ No API patterns found in main page")
                
        # Test auctions page specifically
        response = requests.get("https://carsandbids.com/auctions", headers=headers, timeout=10)
        print(f"Auctions page: {response.status_code}")
        
        if response.status_code == 200:
            # Look for AJAX calls or embedded data
            content = response.text
            if 'auctions' in content and ('json' in content.lower() or 'api' in content.lower()):
                print("✅ Found auction data patterns")
                
    except Exception as e:
        print(f"❌ Website analysis error: {e}")

def test_alternative_access_methods():
    """Test alternative methods to access Cars & Bids data"""
    print("\n🔍 Testing Alternative Access Methods")
    print("=" * 50)
    
    # Test if they have a sitemap with data
    sitemap_urls = [
        "https://carsandbids.com/sitemap.xml",
        "https://carsandbids.com/robots.txt",
        "https://carsandbids.com/feed",
        "https://carsandbids.com/rss",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url in sitemap_urls:
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print(f"{url}: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                print(f"  Content-Type: {content_type}")
                print(f"  Content preview: {response.text[:200]}...")
                
        except Exception as e:
            print(f"{url}: ERROR - {e}")

def find_working_endpoints():
    """Try to find any working endpoints that return auction data"""
    print("\n🔍 Searching for Working Endpoints")
    print("=" * 50)
    
    # Test specific auction endpoints that might work
    specific_endpoints = [
        "https://carsandbids.com/past-auctions",
        "https://carsandbids.com/search",
        "https://carsandbids.com/browse",
        "https://carsandbids.com/api/search", 
        "https://carsandbids.com/api/browse",
        "https://carsandbids.com/api/past-auctions"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/html, */*',
        'Referer': 'https://carsandbids.com/'
    }
    
    for endpoint in specific_endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"{endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type:
                    print(f"  ✅ JSON response! Length: {len(response.text)}")
                    try:
                        data = response.json()
                        print(f"  📄 Data structure: {type(data)} with {len(data) if isinstance(data, (list, dict)) else '?'} items")
                    except:
                        pass
                else:
                    print(f"  📄 Content-Type: {content_type}")
                    
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

if __name__ == "__main__":
    print("🔧 Cars & Bids Debug Analysis")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 50)
    
    # Run all tests
    test_cars_bids_endpoints()
    test_website_analysis()
    test_alternative_access_methods()
    find_working_endpoints()
    
    print("\n" + "=" * 50)
    print("🏁 Cars & Bids debug complete!")
    print("Check cars_bids_debug_results.json for detailed results")
    print("=" * 50)