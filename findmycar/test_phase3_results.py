#!/usr/bin/env python3
"""
Test Phase 3 implementation results - verify all 5 sources are working
"""
import os
import logging
from datetime import datetime

# Set up environment for testing
# Note: Set these as environment variables before running the test
# export EBAY_CLIENT_ID='your-ebay-client-id'
# export EBAY_CLIENT_SECRET='your-ebay-client-secret'

from unified_source_manager import UnifiedSourceManager

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_phase3_sources():
    """Test all Phase 3 sources"""
    print("🚀 Phase 3 Implementation Test")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    manager = UnifiedSourceManager()
    
    # Expected working sources after Phase 3
    phase3_sources = ['ebay', 'carmax', 'autotrader', 'cargurus', 'truecar']
    
    print(f"\n📋 Testing {len(phase3_sources)} Phase 3 sources:")
    for source in phase3_sources:
        config = manager.source_config.get(source, {})
        print(f"   • {source}: {config.get('description', 'N/A')}")
    
    # Test each source individually
    working_sources = []
    failed_sources = []
    
    for source in phase3_sources:
        print(f"\n🔍 Testing {source}...")
        
        try:
            results = manager.search_all_sources(
                query="Honda Civic",
                year_min=2018,
                price_max=30000,
                per_page=10,
                sources=[source]
            )
            
            total = results.get('total', 0)
            search_time = results.get('search_time', 0)
            succeeded = source in results.get('sources_searched', [])
            
            if succeeded and total > 0:
                print(f"   ✅ SUCCESS - {total} vehicles in {search_time:.2f}s")
                
                # Show sample vehicle
                vehicles = results.get('vehicles', [])
                if vehicles:
                    sample = vehicles[0]
                    price = sample.get('price', 0)
                    title = sample.get('title', 'N/A')
                    print(f"   📋 Sample: {title} - ${price:,}")
                
                working_sources.append(source)
            else:
                print(f"   ❌ FAILED - No results")
                failed_sources.append(source)
                
        except Exception as e:
            print(f"   💥 ERROR - {str(e)}")
            failed_sources.append(source)
    
    # Test combined search
    if working_sources:
        print(f"\n🔄 Testing combined search with {len(working_sources)} sources...")
        print(f"   Sources: {', '.join(working_sources)}")
        
        combined_results = manager.search_all_sources(
            query="SUV",
            year_min=2019,
            price_max=40000,
            per_page=50,
            sources=working_sources
        )
        
        total_vehicles = combined_results.get('total', 0)
        search_time = combined_results.get('search_time', 0)
        sources_used = combined_results.get('sources_searched', [])
        
        print(f"\n   🎯 Combined Results:")
        print(f"      Total vehicles: {total_vehicles}")
        print(f"      Search time: {search_time:.2f}s")
        print(f"      Sources succeeded: {', '.join(sources_used)}")
        
        # Show distribution
        if combined_results.get('vehicles'):
            source_counts = {}
            for vehicle in combined_results['vehicles']:
                source = vehicle.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            print(f"\n   📊 Vehicle distribution:")
            for source, count in sorted(source_counts.items()):
                print(f"      {source}: {count} vehicles")
    
    # Final summary
    print(f"\n" + "="*60)
    print("🏆 PHASE 3 RESULTS")
    print("="*60)
    
    print(f"\n✅ Working sources: {len(working_sources)}/{len(phase3_sources)}")
    if working_sources:
        for source in working_sources:
            print(f"   • {source}")
    
    if failed_sources:
        print(f"\n❌ Failed sources: {len(failed_sources)}")
        for source in failed_sources:
            print(f"   • {source}")
    
    # Success metrics
    success_rate = len(working_sources) / len(phase3_sources) * 100
    print(f"\n📈 Success rate: {success_rate:.1f}%")
    
    if len(working_sources) >= 4:
        print("🎉 EXCELLENT - Phase 3 implementation highly successful!")
    elif len(working_sources) >= 3:
        print("✅ GOOD - Phase 3 implementation successful!")
    elif len(working_sources) >= 2:
        print("⚠️  PARTIAL - Some sources working, needs improvement")
    else:
        print("❌ POOR - Major issues need addressing")
    
    return working_sources, failed_sources

if __name__ == "__main__":
    working, failed = test_phase3_sources()
    
    print(f"\n💡 NEXT STEPS:")
    
    if len(working) >= 3:
        print("   • System ready for production with multiple sources")
        print("   • Consider implementing Phase 4 (AutoTrader.ca, PrivateAuto)")
        print("   • Monitor and maintain working sources")
    else:
        print("   • Debug failing sources")
        print("   • Consider alternative implementations")
        print("   • Focus on most reliable sources first")