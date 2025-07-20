#!/usr/bin/env python3
"""
Test currently available sources that don't require API keys
"""
import logging
from datetime import datetime
from unified_source_manager import UnifiedSourceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    print("Testing Available Sources")
    print("="*50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    manager = UnifiedSourceManager()
    
    # Get source statistics
    stats = manager.get_source_stats()
    print(f"\nTotal sources configured: {stats['total_sources']}")
    print(f"Currently enabled: {stats['enabled_sources']}")
    
    # List enabled sources
    enabled = manager.get_enabled_sources()
    print(f"\nEnabled sources without API keys required:")
    no_key_sources = []
    for source in enabled:
        config = manager.source_config[source]
        # These sources work without API keys
        if source in ['ebay', 'hemmings', 'cars_bids', 'craigslist', 'revy_autos', 'carsoup']:
            no_key_sources.append(source)
            print(f"  ✅ {source}: {config['description']}")
    
    print(f"\nEnabled sources requiring scraping (may have issues):")
    scraping_sources = []
    for source in enabled:
        config = manager.source_config[source]
        if config['type'] == 'scrape':
            scraping_sources.append(source)
            print(f"  ⚠️  {source}: {config['description']}")
    
    # Run a test search with available sources
    print(f"\n\nRunning test search with {len(no_key_sources)} no-key sources...")
    print("Searching for: SUVs under $35,000")
    
    results = manager.search_all_sources(
        query="SUV",
        year_min=2018,
        price_max=35000,
        per_page=20,
        sources=no_key_sources  # Only use sources that don't need keys
    )
    
    print(f"\nSearch Results:")
    print(f"  Time: {results['search_time']:.2f} seconds")
    print(f"  Total vehicles found: {results['total']}")
    print(f"  Sources succeeded: {', '.join(results['sources_searched'])}")
    print(f"  Sources failed: {', '.join(results['sources_failed'])}")
    
    # Show sample results
    if results['vehicles']:
        print(f"\n  Sample vehicles (showing first 5):")
        for i, vehicle in enumerate(results['vehicles'][:5], 1):
            print(f"\n  {i}. {vehicle['title']}")
            print(f"     Price: ${vehicle['price']:,}")
            print(f"     Source: {vehicle['source']}")
            print(f"     Location: {vehicle.get('location', 'N/A')}")
    
    # Show vehicle distribution by source
    if results['vehicles']:
        source_counts = {}
        for vehicle in results['vehicles']:
            source = vehicle.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print(f"\n  Vehicles by source:")
        for source, count in sorted(source_counts.items()):
            print(f"    {source}: {count}")
    
    print("\n" + "="*50)
    print("Summary:")
    print(f"  - {len(no_key_sources)} sources work without API keys")
    print(f"  - {len(scraping_sources)} sources use web scraping (may be blocked)")
    print(f"  - Cars.com will work once MARKETCHECK_API_KEY is added")
    print(f"  - Autobytel and CarsDirect need partner access")

if __name__ == "__main__":
    main()