#!/usr/bin/env python3
"""
Test script for Phase 2 API integration sources
Tests Cars.com (Marketcheck), Autobytel, and CarsDirect clients
"""
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the new clients
from cars_com_client import CarsComClient
from autobytel_client import AutobytelClient
from carsdirect_client import CarsDirectClient

def test_cars_com():
    """Test Cars.com client via Marketcheck API"""
    print("\n" + "="*50)
    print("Testing Cars.com (Marketcheck) Client")
    print("="*50)
    
    try:
        client = CarsComClient()
        
        # Test health check
        print("\n1. Testing health check...")
        health = client.check_health()
        print(f"Health Status: {health['status']}")
        print(f"Message: {health['message']}")
        
        # Test basic search
        print("\n2. Testing basic search (Honda Civic)...")
        results = client.search_vehicles(
            query="honda civic",
            year_min=2018,
            price_max=30000,
            per_page=5
        )
        
        print(f"Found {results['total']} vehicles")
        print(f"Showing {len(results['vehicles'])} on this page")
        
        # Display sample results
        for i, vehicle in enumerate(results['vehicles'][:3], 1):
            print(f"\nVehicle {i}:")
            print(f"  Title: {vehicle['title']}")
            print(f"  Price: ${vehicle['price']:,}")
            print(f"  Mileage: {vehicle['mileage']:,} miles")
            print(f"  Location: {vehicle['location']}")
            print(f"  Link: {vehicle['link']}")
            
            # Show dealer info if available
            dealer = vehicle.get('dealer_info', {})
            if dealer.get('name'):
                print(f"  Dealer: {dealer['name']}")
        
        # Test specific make/model search
        print("\n3. Testing specific make/model search (Toyota Camry)...")
        results2 = client.search_vehicles(
            make="Toyota",
            model="Camry",
            year_min=2020,
            per_page=3
        )
        print(f"Found {results2['total']} Toyota Camrys")
        
        return True
        
    except Exception as e:
        logger.error(f"Cars.com test failed: {str(e)}")
        return False

def test_autobytel():
    """Test Autobytel/AutoWeb client"""
    print("\n" + "="*50)
    print("Testing Autobytel/AutoWeb Client")
    print("="*50)
    
    try:
        client = AutobytelClient()
        
        # Test health check
        print("\n1. Testing health check...")
        health = client.check_health()
        print(f"Health Status: {health['status']}")
        print(f"Message: {health['message']}")
        
        if health['status'] == 'unhealthy' and 'credentials' in health['message'].lower():
            print("⚠️  AutoWeb credentials not configured - skipping detailed tests")
            print("   Set AUTOWEB_PARTNER_ID and AUTOWEB_API_KEY to enable")
            return True
        
        # Test basic search
        print("\n2. Testing basic search...")
        results = client.search_vehicles(
            query="SUV",
            price_max=40000,
            per_page=5
        )
        
        print(f"Found {results['total']} vehicles")
        print(f"Showing {len(results['vehicles'])} on this page")
        
        # Display sample results
        for i, vehicle in enumerate(results['vehicles'][:3], 1):
            print(f"\nVehicle {i}:")
            print(f"  Title: {vehicle['title']}")
            print(f"  Price: ${vehicle['price']:,}")
            print(f"  Condition: {vehicle['condition']}")
            print(f"  Stock #: {vehicle.get('stock_number', 'N/A')}")
            
            # Show AutoWeb specific data
            ab_data = vehicle.get('autobytel_data', {})
            if ab_data.get('certified'):
                print(f"  ✓ Certified Pre-Owned")
            if ab_data.get('warranty'):
                print(f"  Warranty: {ab_data['warranty']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Autobytel test failed: {str(e)}")
        return False

def test_carsdirect():
    """Test CarsDirect client"""
    print("\n" + "="*50)
    print("Testing CarsDirect Client")
    print("="*50)
    
    try:
        client = CarsDirectClient()
        
        # Test health check
        print("\n1. Testing health check...")
        health = client.check_health()
        print(f"Health Status: {health['status']}")
        print(f"Message: {health['message']}")
        
        if health['status'] == 'unhealthy' and 'ID not configured' in health['message']:
            print("⚠️  CarsDirect affiliate ID not configured - skipping detailed tests")
            print("   Set CARSDIRECT_AFFILIATE_ID to enable")
            return True
        
        # Test basic search
        print("\n2. Testing basic search (Trucks)...")
        results = client.search_vehicles(
            query="truck",
            year_min=2019,
            per_page=5
        )
        
        print(f"Found {results['total']} vehicles")
        print(f"Showing {len(results['vehicles'])} on this page")
        
        # Display sample results
        for i, vehicle in enumerate(results['vehicles'][:3], 1):
            print(f"\nVehicle {i}:")
            print(f"  Title: {vehicle['title']}")
            print(f"  Price: ${vehicle['price']:,}")
            print(f"  Mileage: {vehicle['mileage']:,} miles")
            
            # Show CarsDirect specific data
            cd_data = vehicle.get('carsdirect_data', {})
            if cd_data.get('savings'):
                print(f"  💰 Savings: ${cd_data['savings']:,}")
            if cd_data.get('price_rating'):
                print(f"  Price Rating: {cd_data['price_rating']}")
            if cd_data.get('financing_available'):
                print(f"  ✓ Financing Available")
        
        # Test price analysis if available
        print("\n3. Testing price analysis...")
        analysis = client.get_price_analysis("Honda", "CR-V", 2022)
        if analysis:
            print(f"Honda CR-V 2022 Market Analysis:")
            print(f"  Average Price: ${analysis['average_price']:,}")
            print(f"  Inventory Count: {analysis['inventory_count']}")
        
        return True
        
    except Exception as e:
        logger.error(f"CarsDirect test failed: {str(e)}")
        return False

def test_unified_manager():
    """Test the unified source manager with new sources"""
    print("\n" + "="*50)
    print("Testing Unified Source Manager Integration")
    print("="*50)
    
    try:
        from unified_source_manager import UnifiedSourceManager
        
        manager = UnifiedSourceManager()
        
        # Get source stats
        stats = manager.get_source_stats()
        print(f"\nTotal sources: {stats['total_sources']}")
        print(f"Enabled sources: {stats['enabled_sources']}")
        
        # Check which Phase 2 sources are available
        phase2_sources = ['cars_com', 'autobytel', 'carsdirect']
        available = [s for s in phase2_sources if s in manager.get_enabled_sources()]
        
        print(f"\nPhase 2 sources available: {', '.join(available) if available else 'None'}")
        
        if available:
            # Test search with Phase 2 sources only
            print(f"\nSearching with Phase 2 sources: {available}")
            results = manager.search_all_sources(
                query="sedan",
                year_min=2020,
                price_max=35000,
                per_page=10,
                sources=available
            )
            
            print(f"\nSearch completed in {results['search_time']:.2f} seconds")
            print(f"Sources succeeded: {', '.join(results['sources_searched'])}")
            print(f"Sources failed: {', '.join(results['sources_failed'])}")
            print(f"Total vehicles found: {results['total']}")
            
            # Show distribution by source
            source_counts = {}
            for vehicle in results['vehicles']:
                source = vehicle.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            print("\nVehicles by source:")
            for source, count in source_counts.items():
                print(f"  {source}: {count}")
        
        return True
        
    except Exception as e:
        logger.error(f"Unified manager test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Phase 2 API Integration Test Suite")
    print("==================================")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check for required environment variables
    print("\nChecking environment configuration...")
    env_vars = {
        'MARKETCHECK_API_KEY': 'Cars.com (Marketcheck)',
        'AUTOWEB_PARTNER_ID': 'Autobytel Partner ID',
        'AUTOWEB_API_KEY': 'Autobytel API Key',
        'CARSDIRECT_AFFILIATE_ID': 'CarsDirect Affiliate ID'
    }
    
    configured = []
    missing = []
    
    for var, desc in env_vars.items():
        if os.getenv(var):
            configured.append(desc)
        else:
            missing.append(f"{desc} ({var})")
    
    if configured:
        print(f"✓ Configured: {', '.join(configured)}")
    if missing:
        print(f"✗ Missing: {', '.join(missing)}")
    
    # Run individual tests
    tests = [
        ("Cars.com", test_cars_com),
        ("Autobytel", test_autobytel),
        ("CarsDirect", test_carsdirect),
        ("Unified Manager", test_unified_manager)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            logger.error(f"{name} test crashed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    
    for name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if missing:
        print("\n⚠️  Note: Some features are disabled due to missing API credentials")
        print("   Configure the environment variables listed above to enable all features")

if __name__ == "__main__":
    main()