#!/usr/bin/env python3
"""
Debug the raw eBay API response
"""
import os
import base64
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_ebay_raw_response():
    """Check the raw eBay API response structure"""
    print("🔍 Debugging Raw eBay API Response")
    print("=" * 60)
    
    client_id = os.getenv('EBAY_CLIENT_ID')
    client_secret = os.getenv('EBAY_CLIENT_SECRET')
    
    # Get OAuth token
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    auth_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {credentials}'
    }
    
    auth_data = {
        'grant_type': 'client_credentials',
        'scope': 'https://api.ebay.com/oauth/api_scope'
    }
    
    # Get token
    auth_response = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers=auth_headers,
        data=auth_data,
        timeout=30
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.status_code}")
        return
    
    token = auth_response.json()['access_token']
    print("✅ Got eBay OAuth token")
    
    # Make search request
    search_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
    }
    
    params = {
        'q': 'Honda',
        'category_ids': '6001',
        'limit': 3,
        'offset': 0,
        'sort': 'price',
        'filter': 'price:[0..35000],buyingOptions:{FIXED_PRICE},itemLocationCountry:US'
    }
    
    search_response = requests.get(
        "https://api.ebay.com/buy/browse/v1/item_summary/search",
        headers=search_headers,
        params=params,
        timeout=30
    )
    
    print(f"Search Status Code: {search_response.status_code}")
    
    if search_response.status_code == 200:
        data = search_response.json()
        
        print("\n📋 Response Structure:")
        print(f"Top-level keys: {list(data.keys())}")
        
        if 'itemSummaries' in data:
            print(f"✅ Found 'itemSummaries' with {len(data['itemSummaries'])} items")
            if data['itemSummaries']:
                print(f"Sample item keys: {list(data['itemSummaries'][0].keys())}")
                print(f"Sample item title: {data['itemSummaries'][0].get('title', 'N/A')}")
        else:
            print("❌ No 'itemSummaries' key found")
            print("Available keys:")
            for key, value in data.items():
                if isinstance(value, list):
                    print(f"  {key}: list with {len(value)} items")
                elif isinstance(value, dict):
                    print(f"  {key}: dict with keys {list(value.keys())}")
                else:
                    print(f"  {key}: {type(value).__name__} = {value}")
        
        print(f"\nTotal results: {data.get('total', 'not specified')}")
        
        # Save full response for inspection
        with open('ebay_debug_response.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("\n💾 Full response saved to ebay_debug_response.json")
        
    else:
        print(f"❌ Search failed: {search_response.status_code}")
        print(f"Response: {search_response.text}")

if __name__ == "__main__":
    debug_ebay_raw_response()