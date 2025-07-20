#!/usr/bin/env python3
"""
Production Source Configuration
Disables non-working sources and optimizes for production
"""
import logging
import os
from dotenv import load_dotenv
from unified_source_manager import UnifiedSourceManager

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def configure_production_sources():
    """Configure sources for production deployment"""
    print("🔧 Configuring Production Sources")
    print("=" * 50)
    
    # Check eBay environment variables
    ebay_client_id = os.getenv('EBAY_CLIENT_ID')
    ebay_client_secret = os.getenv('EBAY_CLIENT_SECRET')
    print(f"EBAY_CLIENT_ID: {'SET' if ebay_client_id else 'MISSING'}")
    print(f"EBAY_CLIENT_SECRET: {'SET' if ebay_client_secret else 'MISSING'}")
    
    manager = UnifiedSourceManager()
    
    # P0 Production sources (working)
    production_sources = ['ebay', 'carmax', 'autotrader']
    
    # Disable all non-production sources
    all_sources = list(manager.source_config.keys())
    
    for source in all_sources:
        if source in production_sources:
            manager.enable_source(source)
            print(f"✅ Enabled: {source}")
        else:
            manager.disable_source(source)
            print(f"❌ Disabled: {source}")
    
    # Test production configuration
    print(f"\n🔍 Testing Production Configuration")
    enabled = manager.get_enabled_sources()
    print(f"Enabled sources: {enabled}")
    
    # Debug source initialization
    print(f"Sources in manager: {list(manager.sources.keys())}")
    print(f"eBay initialized: {'ebay' in manager.sources}")
    print(f"eBay config enabled: {manager.source_config.get('ebay', {}).get('enabled', False)}")
    
    # Quick test search with reasonable parameters
    print(f"\n🔄 Testing production search...")
    results = manager.search_all_sources(
        query="Honda",
        year_min=2010,  # More reasonable year filter
        price_max=50000,  # Higher price limit
        per_page=15  # 5 from each source
    )
    
    print(f"Results:")
    print(f"  Total vehicles: {results['total']}")
    print(f"  Search time: {results['search_time']:.2f}s")
    print(f"  Sources succeeded: {results['sources_searched']}")
    print(f"  Sources failed: {results['sources_failed']}")
    
    # Show vehicle distribution
    if results['vehicles']:
        source_counts = {}
        for vehicle in results['vehicles']:
            source = vehicle.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print(f"\n  Vehicle distribution:")
        for source, count in sorted(source_counts.items()):
            print(f"    {source}: {count}")
    
    return len(enabled), results['total'] > 0

if __name__ == "__main__":
    enabled_count, has_results = configure_production_sources()
    
    print(f"\n" + "=" * 50)
    print("🎯 PRODUCTION CONFIGURATION SUMMARY")
    print("=" * 50)
    print(f"✅ Production sources enabled: {enabled_count}")
    print(f"✅ Search working: {'Yes' if has_results else 'No'}")
    
    if enabled_count >= 3 and has_results:
        print("🎉 PRODUCTION READY!")
    else:
        print("⚠️  Production configuration needs attention")