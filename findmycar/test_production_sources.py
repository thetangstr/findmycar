#!/usr/bin/env python3
"""
Test all 3 production sources individually and together
"""
import os
import logging
import time
from dotenv import load_dotenv
from unified_source_manager import UnifiedSourceManager

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_individual_sources():
    """Test each production source individually"""
    print("🔍 Testing Individual Production Sources")
    print("=" * 60)
    
    manager = UnifiedSourceManager()
    production_sources = ['ebay', 'carmax', 'autotrader']
    
    results = {}
    
    for source in production_sources:
        print(f"\n📡 Testing {source.upper()}")
        print("-" * 30)
        
        # Test if source is available
        if source not in manager.sources:
            print(f"❌ {source} not initialized")
            results[source] = {'status': 'not_initialized', 'vehicles': 0}
            continue
        
        # Test search
        try:
            start_time = time.time()
            result = manager.search_all_sources(
                query="Honda",
                year_min=2018,
                price_max=35000,
                per_page=5,
                sources=[source]  # Test only this source
            )
            search_time = time.time() - start_time
            
            vehicle_count = result.get('total', 0)
            sources_succeeded = result.get('sources_searched', [])
            sources_failed = result.get('sources_failed', [])
            
            if source in sources_succeeded:
                print(f"✅ {source}: {vehicle_count} vehicles in {search_time:.2f}s")
                results[source] = {
                    'status': 'success',
                    'vehicles': vehicle_count,
                    'time': search_time
                }
                
                # Show sample vehicle
                if result.get('vehicles'):
                    sample = result['vehicles'][0]
                    print(f"   Sample: {sample.get('title', 'N/A')} - ${sample.get('price', 0):,}")
            else:
                print(f"❌ {source}: Failed - {sources_failed}")
                results[source] = {'status': 'failed', 'vehicles': 0}
                
        except Exception as e:
            print(f"💥 {source}: Error - {str(e)}")
            results[source] = {'status': 'error', 'vehicles': 0}
    
    return results

def test_combined_search():
    """Test all production sources together"""
    print("\n🔍 Testing Combined Production Search")
    print("=" * 60)
    
    manager = UnifiedSourceManager()
    
    # Configure for production
    production_sources = ['ebay', 'carmax', 'autotrader']
    
    # Disable all non-production sources
    for source_name in manager.source_config.keys():
        if source_name in production_sources:
            manager.enable_source(source_name)
        else:
            manager.disable_source(source_name)
    
    # Test combined search
    try:
        start_time = time.time()
        result = manager.search_all_sources(
            query="Honda",
            year_min=2018,
            price_max=35000,
            per_page=15  # 5 from each source
        )
        search_time = time.time() - start_time
        
        print(f"Total vehicles: {result.get('total', 0)}")
        print(f"Search time: {search_time:.2f}s")
        print(f"Sources succeeded: {result.get('sources_searched', [])}")
        print(f"Sources failed: {result.get('sources_failed', [])}")
        
        # Show vehicle distribution
        if result.get('vehicles'):
            source_counts = {}
            for vehicle in result['vehicles']:
                source = vehicle.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            print(f"\nVehicle distribution:")
            for source, count in sorted(source_counts.items()):
                print(f"  {source}: {count}")
        
        return result
        
    except Exception as e:
        print(f"💥 Combined search failed: {str(e)}")
        return None

def main():
    print("🎯 Production Sources Test")
    print("=" * 80)
    
    # Test individual sources
    individual_results = test_individual_sources()
    
    # Test combined search
    combined_result = test_combined_search()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 PRODUCTION SOURCES SUMMARY")
    print("=" * 80)
    
    working_sources = []
    total_individual_vehicles = 0
    
    for source, result in individual_results.items():
        status = result['status']
        vehicles = result['vehicles']
        
        if status == 'success' and vehicles > 0:
            working_sources.append(source)
            total_individual_vehicles += vehicles
            print(f"✅ {source.upper()}: {vehicles} vehicles")
        else:
            print(f"❌ {source.upper()}: {status}")
    
    print(f"\n📈 Working sources: {len(working_sources)}/3")
    print(f"📈 Total vehicles (individual): {total_individual_vehicles}")
    
    if combined_result:
        combined_total = combined_result.get('total', 0)
        combined_sources = len(combined_result.get('sources_searched', []))
        print(f"📈 Total vehicles (combined): {combined_total}")
        print(f"📈 Sources in combined search: {combined_sources}")
    
    # Production readiness assessment
    if len(working_sources) >= 2 and total_individual_vehicles > 20:
        print(f"\n🎉 PRODUCTION READY!")
        print(f"   ✅ Multiple working sources ({len(working_sources)})")
        print(f"   ✅ Good vehicle coverage ({total_individual_vehicles}+ vehicles)")
    else:
        print(f"\n⚠️  Production needs attention")
        print(f"   Working sources: {len(working_sources)}")
        print(f"   Vehicle coverage: {total_individual_vehicles}")

if __name__ == "__main__":
    main()