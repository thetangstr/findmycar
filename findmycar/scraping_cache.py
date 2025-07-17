#!/usr/bin/env python3
"""
Caching layer for web scraping operations to improve performance
"""

import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class ScrapingCache:
    """Simple in-memory cache for scraping results"""
    
    def __init__(self, ttl: int = 300):  # 5 minutes default TTL
        self.cache = {}
        self.ttl = ttl
    
    def _get_cache_key(self, source: str, query: str, filters: Optional[Dict] = None) -> str:
        """Generate a unique cache key for the request"""
        cache_data = {
            'source': source,
            'query': query.lower().strip(),
            'filters': filters or {}
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def get(self, source: str, query: str, filters: Optional[Dict] = None) -> Optional[Any]:
        """Get cached result if available and not expired"""
        key = self._get_cache_key(source, query, filters)
        
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                logger.info(f"🎯 Cache HIT for {source}: {query}")
                return entry['data']
            else:
                # Expired, remove from cache
                del self.cache[key]
                logger.info(f"⏰ Cache EXPIRED for {source}: {query}")
        
        logger.info(f"❌ Cache MISS for {source}: {query}")
        return None
    
    def set(self, source: str, query: str, data: Any, filters: Optional[Dict] = None):
        """Store result in cache"""
        key = self._get_cache_key(source, query, filters)
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        logger.info(f"💾 Cached result for {source}: {query}")
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("🗑️  Cache cleared")

# Global cache instance
scraping_cache = ScrapingCache(ttl=300)  # 5 minute cache

def cache_scraping_result(source_name: str):
    """Decorator to cache scraping results"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, query: str, filters: Optional[Dict] = None, *args, **kwargs):
            # Check cache first
            cached_result = scraping_cache.get(source_name, query, filters)
            if cached_result is not None:
                return cached_result
            
            # Call the original function
            result = func(self, query, filters, *args, **kwargs)
            
            # Cache the result if successful
            if result and len(result) > 0:
                scraping_cache.set(source_name, query, result, filters)
            
            return result
        
        return wrapper
    return decorator

def with_retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator to retry failed operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed")
            
            raise last_exception
        
        return wrapper
    return decorator