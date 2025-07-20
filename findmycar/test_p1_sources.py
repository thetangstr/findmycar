#!/usr/bin/env python3
"""
Test script for P1 (Priority 1) sources
Tests Hemmings, Cars & Bids, and Facebook Marketplace clients
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hemmings_client import HemmingsClient
from cars_bids_client import CarsBidsClient  
from facebook_marketplace_client import FacebookMarketplaceClient
import json
from datetime import datetime

def test_hemmings():
    """Test Hemmings client"""
    print("🔍 Testing Hemmings Client")
    print("=" * 50)
    
    try:
        client = HemmingsClient()
        
        # Test search
        results = client.search_vehicles(query="mustang", per_page=5)
        print(f"Search results: {results['total']} vehicles found")
        print(f"Source: {results.get('source')}")
        print(f"Warning: {results.get('warning', 'None')}")
        
        if results['vehicles']:
            print("\nFirst vehicle:")
            vehicle = results['vehicles'][0]
            print(f"  Title: {vehicle.get('title')}")
            print(f"  Price: ${vehicle.get('price'):,}" if vehicle.get('price') else "  Price: Not specified")
            print(f"  Year: {vehicle.get('year')}")
            print(f"  Make/Model: {vehicle.get('make')} {vehicle.get('model')}")
        
        # Test health check
        health = client.check_health()
        print(f"\nHealth Status: {health['status']}")
        print(f"Health Message: {health['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hemmings test failed: {e}")
        return False

def test_cars_bids():
    """Test Cars & Bids client"""
    print("\n🔍 Testing Cars & Bids Client")
    print("=" * 50)
    
    try:
        client = CarsBidsClient()
        
        # Test search
        results = client.search_vehicles(query="bmw", per_page=5)
        print(f"Search results: {results['total']} vehicles found")
        print(f"Source: {results.get('source')}")
        print(f"Warning: {results.get('warning', 'None')}")
        
        if results['vehicles']:
            print("\nFirst vehicle:")
            vehicle = results['vehicles'][0]
            print(f"  Title: {vehicle.get('title')}")
            print(f"  Current Bid: ${vehicle.get('price'):,}" if vehicle.get('price') else "  Price: Not specified")
            print(f"  Year: {vehicle.get('year')}")
            print(f"  Make/Model: {vehicle.get('make')} {vehicle.get('model')}")
            
            # Show auction info if available
            auction_info = vehicle.get('auction_info', {})
            if auction_info:
                print(f"  Bid Count: {auction_info.get('bid_count', 0)}")
                print(f"  Time Left: {auction_info.get('time_left', 'Unknown')}")
        
        # Test health check
        health = client.check_health()
        print(f"\nHealth Status: {health['status']}")
        print(f"Health Message: {health['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cars & Bids test failed: {e}")
        return False

def test_facebook_marketplace():
    """Test Facebook Marketplace client"""
    print("\n🔍 Testing Facebook Marketplace Client")
    print("=" * 50)
    
    try:
        client = FacebookMarketplaceClient()
        
        # Test search
        results = client.search_vehicles(query="honda", per_page=5)
        print(f"Search results: {results['total']} vehicles found")
        print(f"Source: {results.get('source')}")
        print(f"Note: {results.get('note', 'None')}")
        
        if results['vehicles']:
            print("\nFirst vehicle:")
            vehicle = results['vehicles'][0]
            print(f"  Title: {vehicle.get('title')}")
            print(f"  Price: ${vehicle.get('price'):,}" if vehicle.get('price') else "  Price: Not specified")
            print(f"  Year: {vehicle.get('year')}")
            print(f"  Make/Model: {vehicle.get('make')} {vehicle.get('model')}")
            print(f"  Location: {vehicle.get('location')}")
        
        # Test submission functionality
        print("\n📤 Testing submission functionality...")
        test_submission = {
            'title': '2017 Test Vehicle',
            'price': 25000,
            'url': 'https://www.facebook.com/marketplace/item/test123',
            'location': 'Test City, CA',
            'description': 'This is a test submission'
        }
        
        submission_result = client.submit_listing('test_user', test_submission)
        print(f"Submission result: {submission_result['success']}")
        print(f"Submission message: {submission_result['message']}")
        
        # Test stats
        stats = client.get_submission_stats()
        print(f"\nSubmission stats:")
        print(f"  Total submissions: {stats['total_submissions']}")
        print(f"  Sample listings: {stats['sample_listings']}")
        print(f"  Total available: {stats['total_available']}")
        
        # Test health check
        health = client.check_health()
        print(f"\nHealth Status: {health['status']}")
        print(f"Health Message: {health['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Facebook Marketplace test failed: {e}")
        return False

def test_combined_search():
    """Test searching across all P1 sources"""
    print("\n🔍 Testing Combined P1 Source Search")
    print("=" * 50)
    
    try:
        # Initialize all clients
        hemmings = HemmingsClient()
        cars_bids = CarsBidsClient()
        facebook = FacebookMarketplaceClient()
        
        # Search all sources
        search_term = "toyota"
        print(f"Searching all P1 sources for: '{search_term}'")
        
        hemmings_results = hemmings.search_vehicles(query=search_term, per_page=3)
        cars_bids_results = cars_bids.search_vehicles(query=search_term, per_page=3)
        facebook_results = facebook.search_vehicles(query=search_term, per_page=3)
        
        # Combine results
        all_vehicles = []
        all_vehicles.extend(hemmings_results['vehicles'])
        all_vehicles.extend(cars_bids_results['vehicles'])
        all_vehicles.extend(facebook_results['vehicles'])
        
        print(f"\nCombined Results:")
        print(f"  Hemmings: {len(hemmings_results['vehicles'])} vehicles")
        print(f"  Cars & Bids: {len(cars_bids_results['vehicles'])} vehicles")
        print(f"  Facebook Marketplace: {len(facebook_results['vehicles'])} vehicles")
        print(f"  Total: {len(all_vehicles)} vehicles")
        
        # Show sample from each source
        if all_vehicles:
            print(f"\nSample vehicles from P1 sources:")
            for i, vehicle in enumerate(all_vehicles[:6]):  # Show first 6
                print(f"  {i+1}. {vehicle.get('title')} - ${vehicle.get('price'):,} ({vehicle.get('source')})")
        
        return len(all_vehicles) > 0
        
    except Exception as e:
        print(f"❌ Combined search test failed: {e}")
        return False

def main():
    """Run all P1 source tests"""
    print("🧪 P1 Sources Test Suite")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 60)
    
    # Track test results
    test_results = {}
    
    # Test individual sources
    test_results['hemmings'] = test_hemmings()
    test_results['cars_bids'] = test_cars_bids()
    test_results['facebook_marketplace'] = test_facebook_marketplace()
    test_results['combined_search'] = test_combined_search()
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 P1 Sources Test Summary")
    print("=" * 60)
    
    for source, success in test_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{source.replace('_', ' ').title()}: {status}")
    
    total_passed = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All P1 sources are working correctly!")
        print("\nP1 Sources Status:")
        print("✅ Hemmings - Fallback data (RSS feeds blocked)")
        print("✅ Cars & Bids - Fallback data (API requires auth)")
        print("✅ Facebook Marketplace - User submission system (ToS compliant)")
        
    else:
        print("⚠️  Some P1 sources have issues that need attention")
    
    print("\n" + "=" * 60)
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)