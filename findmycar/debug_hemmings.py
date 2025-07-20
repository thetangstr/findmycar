#!/usr/bin/env python3
"""
Debug script for Hemmings RSS feeds
Tests RSS feed access and analyzes content structure
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Test all known Hemmings RSS feeds
RSS_FEEDS = {
    'current_cars': "https://www.hemmings.com/classifieds/cars-for-sale/rss",
    'current_all': "https://www.hemmings.com/classifieds/rss",
    'current_parts': "https://www.hemmings.com/classifieds/parts/rss",
    'current_muscle': "https://www.hemmings.com/classifieds/dealer-showcases/rss",
    # Alternative feeds to test
    'alt_cars_1': "https://www.hemmings.com/rss/cars",
    'alt_cars_2': "https://www.hemmings.com/feed/cars",
    'alt_classifieds': "https://www.hemmings.com/rss/classifieds",
    'alt_listings': "https://www.hemmings.com/rss/listings",
}

def test_rss_feed(name, url):
    """Test a single RSS feed"""
    print(f"\n{'='*50}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*50)
    
    try:
        # Test with requests first
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"HTTP Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"Content-Length: {len(response.text)}")
        
        if response.status_code == 200:
            # Try to parse as RSS
            feed = feedparser.parse(response.text)
            print(f"Feed valid: {feed.bozo == 0}")
            print(f"Feed title: {feed.feed.get('title', 'No title')}")
            print(f"Entries found: {len(feed.entries)}")
            
            if feed.entries:
                print("\nFirst 3 entries:")
                for i, entry in enumerate(feed.entries[:3]):
                    print(f"  {i+1}. {entry.get('title', 'No title')}")
                    print(f"     Link: {entry.get('link', 'No link')}")
                    print(f"     Published: {entry.get('published', 'No date')}")
                
                # Save sample data for analysis
                sample_data = {
                    'feed_info': {
                        'title': feed.feed.get('title'),
                        'description': feed.feed.get('description'),
                        'link': feed.feed.get('link')
                    },
                    'entries': [
                        {
                            'title': entry.get('title'),
                            'link': entry.get('link'),
                            'description': entry.get('description'),
                            'published': entry.get('published'),
                            'summary': entry.get('summary')
                        }
                        for entry in feed.entries[:5]
                    ]
                }
                
                with open(f'/Users/Kailor_1/Desktop/Projects/fmc/findmycar/hemmings_sample_{name}.json', 'w') as f:
                    json.dump(sample_data, f, indent=2)
                
                print(f"✅ Sample data saved to hemmings_sample_{name}.json")
            else:
                print("❌ No entries found in feed")
                
        else:
            print(f"❌ Failed to fetch: {response.status_code}")
            print(f"Response text (first 500 chars): {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_hemmings_website():
    """Test if we can access Hemmings website directly"""
    print(f"\n{'='*50}")
    print("Testing Hemmings Website Access")
    print('='*50)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get("https://www.hemmings.com", headers=headers, timeout=10)
        print(f"Main site status: {response.status_code}")
        
        # Test classifieds page
        response = requests.get("https://www.hemmings.com/classifieds/cars-for-sale", 
                              headers=headers, timeout=10)
        print(f"Classifieds page status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for RSS links
            rss_links = soup.find_all('link', {'type': 'application/rss+xml'})
            print(f"\nFound {len(rss_links)} RSS links:")
            for link in rss_links:
                print(f"  - {link.get('href')} ({link.get('title', 'No title')})")
            
            # Look for alternate RSS patterns
            rss_patterns = soup.find_all('a', href=lambda x: x and 'rss' in x.lower())
            print(f"\nFound {len(rss_patterns)} potential RSS links:")
            for link in rss_patterns[:10]:  # Limit to first 10
                print(f"  - {link.get('href')}")
                
        print("✅ Website accessible")
        
    except Exception as e:
        print(f"❌ Website error: {str(e)}")

def test_alternative_hemmings_apis():
    """Test if there are any API endpoints"""
    print(f"\n{'='*50}")
    print("Testing Alternative Hemmings APIs")
    print('='*50)
    
    api_endpoints = [
        "https://api.hemmings.com/v1/vehicles",
        "https://www.hemmings.com/api/vehicles", 
        "https://www.hemmings.com/api/classifieds",
        "https://www.hemmings.com/api/search",
        "https://classifieds.hemmings.com/api/vehicles"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    for endpoint in api_endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=5)
            print(f"{endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"  Content: {response.text[:200]}...")
        except Exception as e:
            print(f"{endpoint}: Error - {str(e)}")

if __name__ == "__main__":
    print("🔍 Debugging Hemmings RSS Feeds")
    print(f"Timestamp: {datetime.now()}")
    
    # Test website access first
    test_hemmings_website()
    
    # Test all RSS feeds
    for name, url in RSS_FEEDS.items():
        test_rss_feed(name, url)
    
    # Test API endpoints
    test_alternative_hemmings_apis()
    
    print(f"\n{'='*50}")
    print("🏁 Debug complete! Check the JSON files for detailed feed analysis.")
    print('='*50)