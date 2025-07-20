#!/usr/bin/env python3
"""
Analyze Cars & Bids website to understand authentication and data access
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def analyze_auctions_page():
    """Analyze the auctions page to find data loading patterns"""
    print("🔍 Analyzing Cars & Bids Auctions Page")
    print("=" * 50)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get("https://carsandbids.com/auctions", headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for embedded JSON data
            scripts = soup.find_all('script')
            api_patterns = []
            
            for script in scripts:
                if script.string:
                    content = script.string
                    
                    # Look for API calls
                    api_matches = re.findall(r'["\']https?://[^"\']*api[^"\']*["\']', content)
                    for match in api_matches:
                        clean_match = match.strip('"\'')
                        if clean_match not in api_patterns:
                            api_patterns.append(clean_match)
                    
                    # Look for authentication patterns
                    auth_patterns = re.findall(r'(authorization|bearer|api[_-]?key|token|x-api-key)["\']?\s*[:=]\s*["\'][^"\']+["\']', content, re.IGNORECASE)
                    if auth_patterns:
                        print(f"✅ Found auth patterns: {auth_patterns}")
                    
                    # Look for GraphQL queries
                    if 'query' in content and 'auction' in content.lower():
                        print("✅ Found GraphQL auction queries")
                        
                        # Extract GraphQL patterns
                        graphql_matches = re.findall(r'query[^{]*{[^}]+}', content, re.IGNORECASE)
                        for match in graphql_matches[:3]:  # Show first 3
                            print(f"  GraphQL: {match[:100]}...")
            
            print(f"Found {len(api_patterns)} API endpoints:")
            for pattern in api_patterns:
                print(f"  - {pattern}")
                
            # Look for initial data in window object
            window_data_pattern = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', response.text, re.DOTALL)
            if window_data_pattern:
                print("✅ Found window.__INITIAL_STATE__ data")
                try:
                    initial_data = json.loads(window_data_pattern.group(1))
                    print(f"  Keys: {list(initial_data.keys()) if isinstance(initial_data, dict) else 'Not a dict'}")
                except:
                    print("  ❌ Could not parse initial state JSON")
            
            # Look for Next.js data
            nextjs_pattern = re.search(r'__NEXT_DATA__"\s*type="application/json">([^<]+)</script>', response.text)
            if nextjs_pattern:
                print("✅ Found Next.js data")
                try:
                    nextjs_data = json.loads(nextjs_pattern.group(1))
                    if 'props' in nextjs_data:
                        print(f"  Props keys: {list(nextjs_data['props'].keys())}")
                except:
                    print("  ❌ Could not parse Next.js JSON")
                    
        else:
            print(f"❌ Could not access auctions page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error analyzing auctions page: {e}")

def test_graphql_endpoint():
    """Test the GraphQL endpoint for auction data"""
    print("\n🔍 Testing GraphQL Endpoint")
    print("=" * 50)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Referer': 'https://carsandbids.com/auctions'
        }
        
        # Test different GraphQL queries
        queries = [
            {
                'query': '''
                query GetAuctions {
                    auctions {
                        id
                        title
                        currentBid
                        endDate
                        vehicle {
                            make
                            model
                            year
                        }
                    }
                }
                '''
            },
            {
                'query': '''
                query {
                    liveAuctions {
                        id
                        slug
                        currentBid
                        car {
                            year
                            make
                            model
                        }
                    }
                }
                '''
            },
            {
                'query': '''
                {
                    auctions(status: "live") {
                        id
                        currentBid
                        car {
                            year
                            make
                            model
                            mileage
                        }
                    }
                }
                '''
            }
        ]
        
        for i, query_data in enumerate(queries):
            print(f"\n--- Testing GraphQL Query {i+1} ---")
            
            response = requests.post(
                "https://carsandbids.com/graphql", 
                headers=headers,
                json=query_data,
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ GraphQL Response: {json.dumps(data, indent=2)[:300]}...")
                    if 'data' in data and data['data']:
                        print("✅ Found auction data in GraphQL response!")
                        return data
                except:
                    print("❌ Invalid JSON response")
                    print(f"Response text: {response.text[:200]}...")
            else:
                print(f"❌ GraphQL failed: {response.text[:200]}")
                
    except Exception as e:
        print(f"❌ GraphQL test error: {e}")
    
    return None

def find_public_data_sources():
    """Look for public data sources that don't require authentication"""
    print("\n🔍 Looking for Public Data Sources")
    print("=" * 50)
    
    # Check sitemap for data URLs
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get("https://carsandbids.com/sitemap.xml", headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Look for patterns in sitemap that might contain data
            auction_urls = re.findall(r'<loc>(https://carsandbids\.com/auctions/[^<]+)</loc>', response.text)
            print(f"Found {len(auction_urls)} auction URLs in sitemap")
            
            if auction_urls:
                # Test accessing individual auction pages
                test_url = auction_urls[0]
                print(f"Testing individual auction: {test_url}")
                
                auction_response = requests.get(test_url, headers=headers, timeout=10)
                if auction_response.status_code == 200:
                    print("✅ Individual auction pages accessible")
                    
                    # Look for embedded JSON data in auction page
                    if '__NEXT_DATA__' in auction_response.text:
                        print("✅ Found structured data in auction page")
                        
                        nextjs_match = re.search(r'__NEXT_DATA__[^>]*>([^<]+)</script>', auction_response.text)
                        if nextjs_match:
                            try:
                                auction_data = json.loads(nextjs_match.group(1))
                                print("✅ Successfully parsed auction page data")
                                
                                # Save sample for analysis
                                with open('/Users/Kailor_1/Desktop/Projects/fmc/findmycar/cars_bids_auction_sample.json', 'w') as f:
                                    json.dump(auction_data, f, indent=2)
                                print("Saved sample to cars_bids_auction_sample.json")
                                
                                return True
                            except:
                                print("❌ Could not parse auction page JSON")
        
    except Exception as e:
        print(f"❌ Sitemap analysis error: {e}")
    
    return False

if __name__ == "__main__":
    print("🔧 Cars & Bids Website Analysis")
    print("=" * 50)
    
    analyze_auctions_page()
    graphql_data = test_graphql_endpoint()
    public_data_found = find_public_data_sources()
    
    print("\n" + "=" * 50)
    print("🏁 Analysis Summary:")
    print(f"GraphQL working: {'✅' if graphql_data else '❌'}")
    print(f"Public data found: {'✅' if public_data_found else '❌'}")
    print("=" * 50)