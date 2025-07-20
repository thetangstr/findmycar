#!/usr/bin/env python3
"""
Test all priority sources: P0 + P1
P0: eBay, Cars.com, CarMax, AutoTrader  
P1: Hemmings, Cars & Bids, Facebook Marketplace
"""
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from unified_source_manager import UnifiedSourceManager

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_combined_priority_sources():
    """Test P0 + P1 sources combined"""
    print("🎯 Combined Priority Sources Test")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    manager = UnifiedSourceManager()
    
    # Define priority sources
    p0_sources = ['ebay', 'cars_com', 'carmax', 'autotrader']
    p1_sources = ['hemmings', 'cars_bids', 'facebook_marketplace']
    
    all_priority_sources = p0_sources + p1_sources
    
    # Check which are enabled
    enabled = manager.get_enabled_sources()
    available_sources = [s for s in all_priority_sources if s in enabled]
    
    print(f"\n📋 Priority Sources Overview:")
    print(f"   P0 (Critical): {p0_sources}")
    print(f"   P1 (Important): {p1_sources}")
    print(f"   Available: {available_sources}")
    
    # Test individual sources quickly
    print(f"\n🔍 Quick Individual Tests:")
    working_sources = []
    failed_sources = []
    
    for source in available_sources:
        print(f"   Testing {source}...", end=" ")
        
        try:
            results = manager.search_all_sources(
                query="car",
                year_min=2018,
                price_max=50000,
                per_page=5,
                sources=[source]
            )
            
            total = results.get('total', 0)
            succeeded = source in results.get('sources_searched', [])
            
            if succeeded and total > 0:
                print(f"✅ {total} vehicles")
                working_sources.append(source)
            else:
                print("❌ No results")
                failed_sources.append(source)
                
        except Exception as e:
            print(f"💥 Error")
            failed_sources.append(source)
    
    # Test combined search with all working sources
    if working_sources:
        print(f"\n🔄 Combined Search Test:")
        print(f"   Using {len(working_sources)} working sources: {working_sources}")
        
        combined_results = manager.search_all_sources(
            query="Honda sedan",
            year_min=2018,
            price_max=40000,
            per_page=50,
            sources=working_sources
        )
        
        total = combined_results.get('total', 0)
        search_time = combined_results.get('search_time', 0)
        sources_used = combined_results.get('sources_searched', [])
        sources_failed = combined_results.get('sources_failed', [])
        
        print(f"\n   🎯 Combined Results:")
        print(f"      Total vehicles: {total}")
        print(f"      Search time: {search_time:.2f}s")
        print(f"      Sources succeeded: {sources_used}")
        print(f"      Sources failed: {sources_failed}")
        
        # Show detailed distribution
        if combined_results.get('vehicles'):
            source_counts = {}
            for vehicle in combined_results['vehicles']:
                source = vehicle.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            print(f"\n   📊 Vehicle Distribution:")
            p0_total = 0
            p1_total = 0
            
            for source, count in sorted(source_counts.items()):
                category = "P0" if source in p0_sources else "P1" if source in p1_sources else "Other"
                print(f"      {source}: {count} vehicles ({category})")
                
                if source in p0_sources:
                    p0_total += count
                elif source in p1_sources:
                    p1_total += count
            
            print(f"\n   📈 Category Totals:")
            print(f"      P0 (Critical): {p0_total} vehicles")
            print(f"      P1 (Important): {p1_total} vehicles")
            print(f"      Total Coverage: {p0_total + p1_total} vehicles")
    
    # Final assessment
    print(f"\n" + "=" * 60)
    print("🏆 PRIORITY SOURCES ASSESSMENT")
    print("=" * 60)
    
    p0_working = [s for s in p0_sources if s in working_sources]
    p1_working = [s for s in p1_sources if s in working_sources]
    
    print(f"\n✅ P0 Working ({len(p0_working)}/4):")
    for source in p0_working:
        print(f"   • {source}")
    
    print(f"\n✅ P1 Working ({len(p1_working)}/3):")
    for source in p1_working:
        print(f"   • {source}")
    
    if failed_sources:
        print(f"\n❌ Failed Sources ({len(failed_sources)}):")
        for source in failed_sources:
            category = "P0" if source in p0_sources else "P1" if source in p1_sources else "Other"
            print(f"   • {source} ({category})")
    
    # Calculate success rates
    p0_rate = len(p0_working) / len(p0_sources) * 100
    p1_rate = len(p1_working) / len(p1_sources) * 100
    overall_rate = len(working_sources) / len(all_priority_sources) * 100
    
    print(f"\n📊 Success Rates:")
    print(f"   P0 (Critical): {p0_rate:.1f}% ({len(p0_working)}/4)")
    print(f"   P1 (Important): {p1_rate:.1f}% ({len(p1_working)}/3)")
    print(f"   Overall: {overall_rate:.1f}% ({len(working_sources)}/7)")
    
    # System assessment
    print(f"\n💡 System Assessment:")
    if len(p0_working) >= 3 and len(p1_working) >= 2:
        print("🎉 EXCELLENT - Both P0 and P1 sources highly operational!")
        print("   System ready for production with comprehensive coverage")
    elif len(p0_working) >= 3:
        print("✅ GOOD - P0 sources solid, P1 sources need attention")
        print("   Core functionality working well")
    elif len(working_sources) >= 4:
        print("✅ ACCEPTABLE - Good overall coverage")
        print("   System operational with mixed P0/P1 success")
    else:
        print("⚠️ NEEDS WORK - Insufficient source coverage")
        print("   Focus on fixing critical P0 sources first")

if __name__ == "__main__":
    test_combined_priority_sources()