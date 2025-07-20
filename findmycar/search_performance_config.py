#!/usr/bin/env python3
"""
Search performance configuration for FindMyCar
"""

import os

# Search performance settings
SEARCH_CONFIG = {
    # Enable/disable slow sources (CarMax, AutoTrader use Selenium)
    'ENABLE_SLOW_SOURCES': os.environ.get('ENABLE_SLOW_SOURCES', 'false').lower() == 'true',
    
    # Timeouts for each source (in seconds)
    'SOURCE_TIMEOUTS': {
        'ebay': 5.0,       # API is fast
        'carmax': 15.0,    # Selenium scraping
        'autotrader': 15.0 # Selenium scraping
    },
    
    # Cache TTLs (in seconds)
    'CACHE_TTL': {
        'search_results': 300,      # 5 minutes for search results
        'ebay_search': 600,         # 10 minutes for eBay API
        'carmax_search': 3600,      # 1 hour for CarMax scraping
        'autotrader_search': 3600,  # 1 hour for AutoTrader scraping
    },
    
    # Search limits
    'MAX_RESULTS_PER_SOURCE': 20,
    'MAX_TOTAL_RESULTS': 100,
    
    # Performance features
    'PARALLEL_SEARCH': True,
    'AGGRESSIVE_CACHING': True,
    'ASYNC_DB_WRITES': True,
}

def get_enabled_sources():
    """Get list of enabled sources based on configuration"""
    sources = ['ebay']  # Always enable eBay (fast API)
    
    if SEARCH_CONFIG['ENABLE_SLOW_SOURCES']:
        sources.extend(['carmax', 'autotrader'])
    
    return sources

def get_search_message():
    """Get a user-friendly message about search sources"""
    if SEARCH_CONFIG['ENABLE_SLOW_SOURCES']:
        return "Searching eBay, CarMax, and AutoTrader (this may take up to 30 seconds)"
    else:
        return "Searching eBay Motors (fast mode - add ?enable_slow=true for more sources)"