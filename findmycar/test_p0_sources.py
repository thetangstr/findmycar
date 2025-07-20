#!/usr/bin/env python3
"""
Test P0 (Priority 0) sources with updated credentials
P0: eBay, Cars.com (Marketcheck), CarMax, AutoTrader
"""
import os
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

def test_ebay():
    """Test eBay with production credentials"""
    print("\n🔍 Testing eBay (P0)")
    print("-" * 40)
    
    from ebay_live_client import EbayLiveClient
    
    client_id = os.getenv('EBAY_CLIENT_ID')
    client_secret = os.getenv('EBAY_CLIENT_SECRET')
    
    print(f"Client ID: {client_id[:15]}...")
    print(f"Client Secret: {client_secret[:15]}...")
    
    try:
        client = EbayLiveClient()
        
        results = client.search_vehicles(
            query="Honda Civic",
            year_min=2018,
            price_max=30000,
            per_page=10
        )
        
        total = results.get('total', 0)
        vehicles = results.get('vehicles', [])
        
        if total > 0:
            print(f"✅ SUCCESS - Found {total} vehicles")
            if vehicles:
                sample = vehicles[0]
                print(f"   Sample: {sample.get('title', 'N/A')} - ${sample.get('price', 0):,}")
            return True
        else:
            print(f"❌ FAILED - No vehicles found")
            return False
            
    except Exception as e:
        print(f"💥 ERROR - {str(e)}")
        return False

def test_cars_com():
    """Test Cars.com via Marketcheck"""
    print("\n🔍 Testing Cars.com via Marketcheck (P0)")
    print("-" * 40)
    
    from cars_com_client import CarsComClient
    
    api_key = os.getenv('MARKETCHECK_API_KEY')
    print(f"API Key: {api_key[:15]}...")
    
    try:
        client = CarsComClient()
        
        # Test health first
        health = client.check_health()
        print(f"Health Status: {health['status']}")
        
        if health['status'] == 'healthy':
            results = client.search_vehicles(
                make="Toyota",
                model="Camry",
                year_min=2020,
                price_max=35000,
                per_page=10
            )
            
            total = results.get('total', 0)
            vehicles = results.get('vehicles', [])
            
            if total > 0:
                print(f"✅ SUCCESS - Found {total} vehicles")
                if vehicles:
                    sample = vehicles[0]
                    print(f"   Sample: {sample.get('title', 'N/A')} - ${sample.get('price', 0):,}")
                return True
            else:
                print(f"❌ FAILED - No vehicles found")
                return False
        else:
            print(f"❌ FAILED - API unhealthy: {health['message']}")
            return False
            
    except Exception as e:
        print(f"💥 ERROR - {str(e)}")
        return False

def test_carmax():
    """Test CarMax scraping"""
    print("\n🔍 Testing CarMax (P0)")
    print("-" * 40)
    
    from carmax_wrapper import CarMaxWrapper
    
    try:
        client = CarMaxWrapper()
        
        results = client.search_vehicles(
            make="Honda",
            year_min=2018,
            price_max=30000,
            per_page=10
        )
        
        total = results.get('total', 0)
        vehicles = results.get('vehicles', [])
        
        if total > 0 and vehicles:
            print(f"✅ SUCCESS - Found {len(vehicles)} vehicles")
            sample = vehicles[0]
            print(f"   Sample: {sample.get('title', 'N/A')} - ${sample.get('price', 0):,}")
            return True
        else:
            print(f"❌ FAILED - No vehicles found")
            return False
            
    except Exception as e:
        print(f"💥 ERROR - {str(e)}")
        return False

def test_autotrader():
    """Test AutoTrader scraping"""
    print("\n🔍 Testing AutoTrader (P0)")
    print("-" * 40)
    
    from autotrader_wrapper import AutoTraderWrapper
    
    try:
        client = AutoTraderWrapper()
        
        results = client.search_vehicles(
            make="Honda",
            year_min=2018,
            price_max=30000,
            per_page=10
        )
        
        total = results.get('total', 0)
        vehicles = results.get('vehicles', [])
        
        if total > 0 and vehicles:
            print(f"✅ SUCCESS - Found {len(vehicles)} vehicles")
            sample = vehicles[0]
            print(f"   Sample: {sample.get('title', 'N/A')} - ${sample.get('price', 0):,}")
            return True
        else:
            print(f"❌ FAILED - No vehicles found")
            return False
            
    except Exception as e:
        print(f"💥 ERROR - {str(e)}")
        return False

def test_unified_p0():
    """Test P0 sources through unified manager"""
    print("\n🔄 Testing P0 Sources via Unified Manager")
    print("-" * 40)
    
    from unified_source_manager import UnifiedSourceManager
    
    try:
        manager = UnifiedSourceManager()
        p0_sources = ['ebay', 'cars_com', 'carmax', 'autotrader']
        
        # Filter to only enabled sources
        enabled = manager.get_enabled_sources()
        available_p0 = [s for s in p0_sources if s in enabled]
        
        print(f"Available P0 sources: {available_p0}")
        
        if available_p0:
            results = manager.search_all_sources(
                query="Honda",
                year_min=2018,
                price_max=35000,
                per_page=20,
                sources=available_p0
            )
            
            total = results.get('total', 0)
            search_time = results.get('search_time', 0)
            succeeded = results.get('sources_searched', [])
            failed = results.get('sources_failed', [])
            
            print(f"\nCombined Results:")
            print(f"   Total vehicles: {total}")
            print(f"   Search time: {search_time:.2f}s")
            print(f"   Sources succeeded: {succeeded}")
            print(f"   Sources failed: {failed}")
            
            # Show distribution
            if results.get('vehicles'):
                source_counts = {}
                for vehicle in results['vehicles']:
                    source = vehicle.get('source', 'unknown')
                    source_counts[source] = source_counts.get(source, 0) + 1
                
                print(f"\n   Vehicle distribution:")
                for source, count in sorted(source_counts.items()):
                    print(f"     {source}: {count}")
            
            return len(succeeded), len(failed)
        else:
            print("No P0 sources available")
            return 0, len(p0_sources)
            
    except Exception as e:
        print(f"💥 ERROR - {str(e)}")
        return 0, len(p0_sources)

def main():
    print("🎯 P0 Sources Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nP0 Sources: eBay, Cars.com, CarMax, AutoTrader")
    
    # Test each P0 source individually
    p0_tests = [
        ("eBay", test_ebay),
        ("Cars.com", test_cars_com),
        ("CarMax", test_carmax),
        ("AutoTrader", test_autotrader)
    ]
    
    working = []
    failed = []
    
    for name, test_func in p0_tests:
        try:
            success = test_func()
            if success:
                working.append(name)
            else:
                failed.append(name)
        except Exception as e:
            print(f"💥 {name} test crashed: {str(e)}")
            failed.append(name)
    
    # Test unified manager
    succeeded_count, failed_count = test_unified_p0()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏆 P0 SOURCES SUMMARY")
    print("=" * 60)
    
    print(f"\n✅ Working P0 sources ({len(working)}/4):")
    for source in working:
        print(f"   • {source}")
    
    if failed:
        print(f"\n❌ Failed P0 sources ({len(failed)}/4):")
        for source in failed:
            print(f"   • {source}")
    
    success_rate = len(working) / 4 * 100
    print(f"\n📊 P0 Success Rate: {success_rate:.1f}%")
    
    if len(working) >= 3:
        print("🎉 EXCELLENT - Most P0 sources operational!")
    elif len(working) >= 2:
        print("✅ GOOD - Core P0 sources working!")
    else:
        print("⚠️ CRITICAL - Need to fix P0 sources!")

if __name__ == "__main__":
    main()