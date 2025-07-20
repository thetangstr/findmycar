#!/usr/bin/env python3
"""
Advanced Hemmings debugging - check for working RSS feeds and alternative methods
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin, urlparse
import cloudscraper

def test_with_cloudscraper():
    """Test using cloudscraper to bypass Cloudflare/Incapsula"""
    print("🔍 Testing with CloudScraper...")
    
    try:
        scraper = cloudscraper.create_scraper()
        
        # Test main RSS feed
        response = scraper.get("https://www.hemmings.com/classifieds/cars-for-sale/rss")
        print(f"CloudScraper RSS status: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")
        print(f"Content length: {len(response.text)}")
        
        if 'xml' in response.headers.get('content-type', '').lower():
            print("✅ Got XML content!")
            with open('/Users/Kailor_1/Desktop/Projects/fmc/findmycar/hemmings_cloudscraper_rss.xml', 'w') as f:
                f.write(response.text)
            print("Saved to hemmings_cloudscraper_rss.xml")
        else:
            print("❌ Still getting HTML")
            print("First 300 chars:", response.text[:300])
            
    except Exception as e:
        print(f"CloudScraper error: {e}")

def find_rss_feeds_in_sitemap():
    """Look for RSS feeds in sitemap"""
    print("\n🔍 Checking sitemap for RSS feeds...")
    
    sitemap_urls = [
        "https://www.hemmings.com/sitemap.xml",
        "https://www.hemmings.com/robots.txt"
    ]
    
    try:
        scraper = cloudscraper.create_scraper()
        
        for url in sitemap_urls:
            try:
                response = scraper.get(url, timeout=10)
                print(f"{url}: {response.status_code}")
                
                if response.status_code == 200:
                    if 'robots.txt' in url:
                        print("Robots.txt content:")
                        print(response.text[:500])
                    else:
                        print("Sitemap found!")
                        # Look for RSS references
                        if 'rss' in response.text.lower():
                            print("✅ RSS references found in sitemap!")
                            
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                
    except Exception as e:
        print(f"Sitemap error: {e}")

def test_mobile_api():
    """Test if mobile app endpoints work"""
    print("\n🔍 Testing mobile/app API endpoints...")
    
    mobile_endpoints = [
        "https://m.hemmings.com/api/classifieds",
        "https://mobile.hemmings.com/api/vehicles", 
        "https://app.hemmings.com/api/search",
        "https://www.hemmings.com/mobile/api/cars"
    ]
    
    mobile_headers = {
        'User-Agent': 'HemmingsApp/1.0 (iPhone; iOS 14.0)',
        'Accept': 'application/json'
    }
    
    try:
        scraper = cloudscraper.create_scraper()
        
        for endpoint in mobile_endpoints:
            try:
                response = scraper.get(endpoint, headers=mobile_headers, timeout=5)
                print(f"{endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  Content preview: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"{endpoint}: Error - {e}")
                
    except Exception as e:
        print(f"Mobile API error: {e}")

def check_for_api_documentation():
    """Look for API documentation or developer pages"""
    print("\n🔍 Checking for API documentation...")
    
    doc_urls = [
        "https://www.hemmings.com/developers",
        "https://www.hemmings.com/api",
        "https://www.hemmings.com/api-docs", 
        "https://developers.hemmings.com",
        "https://api.hemmings.com/docs"
    ]
    
    try:
        scraper = cloudscraper.create_scraper()
        
        for url in doc_urls:
            try:
                response = scraper.get(url, timeout=5)
                print(f"{url}: {response.status_code}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    if soup.find(string=lambda text: text and 'api' in text.lower()):
                        print("  ✅ Potential API documentation found!")
                        
            except Exception as e:
                print(f"{url}: Error - {e}")
                
    except Exception as e:
        print(f"API docs error: {e}")

def test_alternative_rss_patterns():
    """Test various RSS URL patterns"""
    print("\n🔍 Testing alternative RSS patterns...")
    
    base_patterns = [
        "https://feeds.hemmings.com/cars",
        "https://rss.hemmings.com/classifieds",
        "https://www.hemmings.com/feeds/cars",
        "https://www.hemmings.com/xml/cars",
        "https://www.hemmings.com/rss2/cars",
        "https://www.hemmings.com/atom/cars",
        "https://content.hemmings.com/rss/cars"
    ]
    
    try:
        scraper = cloudscraper.create_scraper()
        
        for pattern in base_patterns:
            try:
                response = scraper.get(pattern, timeout=5)
                print(f"{pattern}: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'xml' in content_type.lower() or 'rss' in content_type.lower():
                        print(f"  ✅ Valid RSS/XML content type: {content_type}")
                        
            except Exception as e:
                print(f"{pattern}: Error - {e}")
                
    except Exception as e:
        print(f"RSS patterns error: {e}")

def analyze_current_website():
    """Analyze current website structure for data sources"""
    print("\n🔍 Analyzing current website structure...")
    
    try:
        scraper = cloudscraper.create_scraper()
        
        # Get the classifieds page
        response = scraper.get("https://www.hemmings.com/classifieds/cars-for-sale")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for JSON data embedded in page
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and ('vehicles' in script.string or 'listings' in script.string):
                    print("✅ Found potential vehicle data in script tag!")
                    print(f"Script preview: {script.string[:200]}...")
                    
            # Look for AJAX endpoints
            if 'ajax' in response.text or 'api' in response.text:
                print("✅ Found AJAX/API references in page")
                
            # Look for data attributes
            elements_with_data = soup.find_all(attrs=lambda x: x and any(key.startswith('data-') for key in x.keys()))
            print(f"Found {len(elements_with_data)} elements with data attributes")
            
        else:
            print(f"❌ Could not access classifieds page: {response.status_code}")
            
    except Exception as e:
        print(f"Website analysis error: {e}")

if __name__ == "__main__":
    print("🔧 Advanced Hemmings Analysis")
    print("=" * 50)
    
    # Install cloudscraper if not available
    try:
        import cloudscraper
    except ImportError:
        print("Installing cloudscraper...")
        import subprocess
        subprocess.check_call(["pip", "install", "cloudscraper"])
        import cloudscraper
    
    test_with_cloudscraper()
    find_rss_feeds_in_sitemap()
    test_mobile_api()
    check_for_api_documentation()
    test_alternative_rss_patterns()
    analyze_current_website()
    
    print("\n" + "=" * 50)
    print("🏁 Advanced analysis complete!")