#!/usr/bin/env python3
"""
Comprehensive test of all vehicle sources to determine what's actually working
"""
import os
import logging
from datetime import datetime
from unified_source_manager import UnifiedSourceManager

# Set API keys for testing
os.environ['MARKETCHECK_API_KEY'] = 'azp8YlkVTRrRty9kOktQMyF0YNDCv2SR'

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_individual_source(manager, source_name):
    """Test a single source individually"""
    try:
        print(f"\n🔍 Testing {source_name}...")
        
        # Get source config
        config = manager.source_config.get(source_name, {})
        source_type = config.get('type', 'unknown')
        description = config.get('description', 'No description')
        
        print(f"   Type: {source_type}")
        print(f"   Description: {description}")
        
        # Test with a simple search
        results = manager.search_all_sources(
            query="Honda",
            year_min=2018,
            price_max=40000,
            per_page=10,
            sources=[source_name]
        )
        
        search_time = results.get('search_time', 0)
        total = results.get('total', 0)
        vehicles_count = len(results.get('vehicles', []))
        succeeded = source_name in results.get('sources_searched', [])
        failed = source_name in results.get('sources_failed', [])
        
        if succeeded and total > 0:
            print(f"   ✅ WORKING - Found {total} vehicles in {search_time:.2f}s")
            
            # Show sample vehicle
            vehicles = results.get('vehicles', [])
            if vehicles:
                sample = vehicles[0]
                print(f"   📋 Sample: {sample.get('title', 'N/A')} - ${sample.get('price', 0):,}")
            
            return {
                'status': 'working',
                'total_vehicles': total,
                'search_time': search_time,
                'type': source_type,
                'description': description
            }
        elif failed:
            print(f"   ❌ FAILED - Source returned error")
            return {
                'status': 'failed',
                'total_vehicles': 0,
                'search_time': search_time,
                'type': source_type,
                'description': description,
                'error': 'Source failed'
            }
        else:
            print(f"   ⚠️  NO RESULTS - Source responded but no vehicles found")
            return {
                'status': 'no_results',
                'total_vehicles': 0,
                'search_time': search_time,
                'type': source_type,
                'description': description
            }
            
    except Exception as e:
        print(f"   💥 ERROR - {str(e)}")
        return {
            'status': 'error',
            'total_vehicles': 0,
            'search_time': 0,
            'type': source_type,
            'description': description,
            'error': str(e)
        }

def main():
    print("🚗 Comprehensive Vehicle Source Test")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    manager = UnifiedSourceManager()
    
    # Get all sources (enabled and disabled)
    all_sources = list(manager.source_config.keys())
    enabled_sources = manager.get_enabled_sources()
    
    print(f"\n📊 Overview:")
    print(f"   Total sources configured: {len(all_sources)}")
    print(f"   Currently enabled: {len(enabled_sources)}")
    
    # Test each enabled source
    working_sources = []
    failed_sources = []
    no_result_sources = []
    error_sources = []
    
    results = {}
    
    for source in enabled_sources:
        result = test_individual_source(manager, source)
        results[source] = result
        
        if result['status'] == 'working':
            working_sources.append(source)
        elif result['status'] == 'failed':
            failed_sources.append(source)
        elif result['status'] == 'no_results':
            no_result_sources.append(source)
        else:
            error_sources.append(source)
    
    # Summary
    print("\n" + "="*60)
    print("📈 SUMMARY")
    print("="*60)
    
    print(f"\n✅ WORKING SOURCES ({len(working_sources)}):")
    if working_sources:
        for source in working_sources:
            result = results[source]
            print(f"   • {source}: {result['total_vehicles']} vehicles ({result['type']})")
            print(f"     {result['description']}")
    else:
        print("   None")
    
    print(f"\n❌ FAILED SOURCES ({len(failed_sources)}):")
    if failed_sources:
        for source in failed_sources:
            result = results[source]
            print(f"   • {source}: {result.get('error', 'Unknown error')} ({result['type']})")
    else:
        print("   None")
    
    print(f"\n⚠️  NO RESULTS SOURCES ({len(no_result_sources)}):")
    if no_result_sources:
        for source in no_result_sources:
            result = results[source]
            print(f"   • {source}: Responded but no vehicles found ({result['type']})")
    else:
        print("   None")
    
    print(f"\n💥 ERROR SOURCES ({len(error_sources)}):")
    if error_sources:
        for source in error_sources:
            result = results[source]
            print(f"   • {source}: {result.get('error', 'Unknown error')} ({result['type']})")
    else:
        print("   None")
    
    # Test combined search with working sources
    if working_sources:
        print(f"\n🔄 TESTING COMBINED SEARCH WITH {len(working_sources)} WORKING SOURCES")
        print("-" * 60)
        
        combined_results = manager.search_all_sources(
            query="sedan",
            year_min=2019,
            price_max=35000,
            per_page=30,
            sources=working_sources
        )
        
        print(f"Combined search results:")
        print(f"   Total vehicles: {combined_results['total']}")
        print(f"   Search time: {combined_results['search_time']:.2f}s")
        print(f"   Sources used: {', '.join(combined_results['sources_searched'])}")
        
        # Show distribution
        if combined_results['vehicles']:
            source_counts = {}
            for vehicle in combined_results['vehicles']:
                source = vehicle.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            print(f"\n   Vehicle distribution:")
            for source, count in sorted(source_counts.items()):
                print(f"     {source}: {count} vehicles")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 60)
    
    if working_sources:
        print(f"✅ {len(working_sources)} sources are operational")
        print("   Your system is ready for production with these sources")
    else:
        print("❌ No sources are currently working")
        print("   Check API credentials and network connectivity")
    
    if len(working_sources) < 3:
        print("\n🔧 TO IMPROVE COVERAGE:")
        print("   1. Check and fix failing sources")
        print("   2. Obtain API keys for disabled sources")
        print("   3. Update scrapers that may be blocked")
    
    total_working = len(working_sources)
    total_enabled = len(enabled_sources)
    
    print(f"\n📊 FINAL SCORE: {total_working}/{total_enabled} sources working")

if __name__ == "__main__":
    main()