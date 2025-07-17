"""
Enhanced caching system with intelligent pre-warming and performance optimization
"""

import os
import json
import redis
import logging
import hashlib
import time
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from threading import Thread
from sqlalchemy.orm import Session
from database import SessionLocal
import asyncio

logger = logging.getLogger(__name__)

class EnhancedCacheManager:
    """Advanced cache manager with intelligent pre-warming and performance optimization"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._redis_client = None
        self._memory_cache = {}
        self._use_redis = True
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'warm_hits': 0,
            'total_requests': 0
        }
        
        # Cache tiers with different TTLs
        self.cache_tiers = {
            'hot': 300,      # 5 minutes - frequently accessed
            'warm': 1800,    # 30 minutes - recently accessed
            'cold': 7200     # 2 hours - rarely accessed
        }
        
        # Popular search patterns for pre-warming
        self.popular_patterns = [
            "honda civic",
            "toyota camry", 
            "ford f150",
            "bmw 3 series",
            "mercedes c class",
            "audi a4",
            "nissan altima",
            "mazda cx5"
        ]
        
        # Connect to Redis
        self._connect_redis()
        
        # Start background pre-warming
        self._start_background_tasks()
    
    def _connect_redis(self):
        """Connect to Redis with fallback to in-memory cache"""
        try:
            self._redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self._redis_client.ping()
            logger.info("✅ Enhanced Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory cache: {e}")
            self._use_redis = False
    
    def _start_background_tasks(self):
        """Start background tasks for cache optimization"""
        # Pre-warm cache with popular searches
        thread = Thread(target=self._pre_warm_cache, daemon=True)
        thread.start()
        
        # Cache cleanup and optimization
        cleanup_thread = Thread(target=self._cache_cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def _pre_warm_cache(self):
        """Pre-warm cache with popular search patterns"""
        logger.info("🔥 Starting cache pre-warming...")
        
        for pattern in self.popular_patterns:
            try:
                # Create basic filters for popular searches
                filters = {'make': pattern.split()[0].title()}
                if len(pattern.split()) > 1:
                    filters['model'] = pattern.split()[1].title()
                
                # Generate cache key
                cache_key = self._generate_cache_key(pattern, filters)
                
                # Check if already cached
                if not self._get_from_cache(cache_key):
                    logger.info(f"🔥 Pre-warming cache for: {pattern}")
                    
                    # Simulate search to warm cache
                    # Note: This would need actual search implementation
                    # For now, we'll just mark these as warm entries
                    self._set_cache_tier(cache_key, 'warm')
                    
            except Exception as e:
                logger.error(f"Error pre-warming cache for {pattern}: {e}")
            
            # Don't overwhelm the system
            time.sleep(1)
    
    def _cache_cleanup_worker(self):
        """Background worker for cache cleanup and optimization"""
        while True:
            try:
                # Clean up every 5 minutes
                time.sleep(300)
                
                # Promote frequently accessed cache entries
                self._promote_hot_entries()
                
                # Clean up expired entries
                self._cleanup_expired_entries()
                
                # Log cache statistics
                self._log_cache_stats()
                
            except Exception as e:
                logger.error(f"Error in cache cleanup worker: {e}")
    
    def _generate_cache_key(self, query: str, filters: Dict = None, source: str = "multi") -> str:
        """Generate intelligent cache key with normalization"""
        # Normalize query
        normalized_query = query.lower().strip()
        
        # Sort filters for consistent keys
        filter_str = ""
        if filters:
            sorted_filters = sorted(filters.items())
            filter_str = json.dumps(sorted_filters, sort_keys=True)
        
        # Create unique key
        key_data = f"{source}:{normalized_query}:{filter_str}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        
        return f"search:{key_hash}"
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get from cache with tier tracking"""
        result = None
        
        if self._use_redis and self._redis_client:
            try:
                cached_data = self._redis_client.get(key)
                if cached_data:
                    result = json.loads(cached_data)
                    self._cache_stats['hits'] += 1
                    
                    # Track cache tier
                    tier = self._redis_client.get(f"{key}:tier")
                    if tier == 'warm':
                        self._cache_stats['warm_hits'] += 1
                    
                    # Promote to hot if frequently accessed
                    self._track_access(key)
                    
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        # Fallback to memory cache
        if not result and key in self._memory_cache:
            result = self._memory_cache[key]
            self._cache_stats['hits'] += 1
        
        if not result:
            self._cache_stats['misses'] += 1
        
        self._cache_stats['total_requests'] += 1
        return result
    
    def _set_to_cache(self, key: str, value: Dict, ttl: int = 1800):
        """Set to cache with intelligent TTL"""
        try:
            serialized_value = json.dumps(value)
            
            if self._use_redis and self._redis_client:
                self._redis_client.setex(key, ttl, serialized_value)
                
                # Set tier information
                tier = self._determine_cache_tier(key, value)
                self._redis_client.setex(f"{key}:tier", ttl, tier)
                
                logger.debug(f"💾 Cached {key} in {tier} tier (TTL: {ttl}s)")
            else:
                # Memory cache with expiration
                self._memory_cache[key] = value
                
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def _determine_cache_tier(self, key: str, value: Dict) -> str:
        """Determine appropriate cache tier based on content"""
        # Check if this is a popular search
        if any(pattern in key for pattern in self.popular_patterns):
            return 'hot'
        
        # Check result count and quality
        result_count = len(value.get('results', []))
        if result_count > 10:
            return 'warm'
        elif result_count > 0:
            return 'warm'
        else:
            return 'cold'
    
    def _set_cache_tier(self, key: str, tier: str):
        """Set cache tier for a key"""
        if self._use_redis and self._redis_client:
            ttl = self.cache_tiers[tier]
            self._redis_client.setex(f"{key}:tier", ttl, tier)
    
    def _track_access(self, key: str):
        """Track cache access for promotion decisions"""
        if self._use_redis and self._redis_client:
            access_key = f"{key}:access_count"
            self._redis_client.incr(access_key)
            self._redis_client.expire(access_key, 3600)  # Expire after 1 hour
    
    def _promote_hot_entries(self):
        """Promote frequently accessed entries to hot tier"""
        if not self._use_redis or not self._redis_client:
            return
        
        try:
            # Find frequently accessed entries
            for key in self._redis_client.scan_iter(match="search:*"):
                if key.endswith(':access_count') or key.endswith(':tier'):
                    continue
                
                access_count = self._redis_client.get(f"{key}:access_count")
                if access_count and int(access_count) > 5:  # Accessed more than 5 times
                    # Promote to hot tier
                    self._set_cache_tier(key, 'hot')
                    
                    # Extend TTL
                    self._redis_client.expire(key, self.cache_tiers['hot'])
                    
        except Exception as e:
            logger.error(f"Error promoting hot entries: {e}")
    
    def _cleanup_expired_entries(self):
        """Clean up expired cache entries"""
        if not self._use_redis:
            # Clean memory cache
            current_time = time.time()
            expired_keys = []
            
            for key, value in self._memory_cache.items():
                if isinstance(value, dict) and 'cached_at' in value:
                    if current_time - value['cached_at'] > 1800:  # 30 minutes
                        expired_keys.append(key)
            
            for key in expired_keys:
                del self._memory_cache[key]
    
    def _log_cache_stats(self):
        """Log cache performance statistics"""
        total = self._cache_stats['total_requests']
        if total > 0:
            hit_rate = (self._cache_stats['hits'] / total) * 100
            warm_hit_rate = (self._cache_stats['warm_hits'] / total) * 100
            
            logger.info(f"📊 Cache stats: {hit_rate:.1f}% hit rate, {warm_hit_rate:.1f}% warm hits, {total} total requests")
    
    def cache_search_results(self, query: str, filters: Dict, results: List, source: str = "multi", expire: int = 1800):
        """Cache search results with intelligent tiering"""
        cache_key = self._generate_cache_key(query, filters, source)
        
        cache_data = {
            'results': results,
            'query': query,
            'filters': filters,
            'source': source,
            'cached_at': time.time(),
            'count': len(results)
        }
        
        self._set_to_cache(cache_key, cache_data, expire)
        return cache_key
    
    def get_cached_search_results(self, query: str, filters: Dict, source: str = "multi") -> Optional[List]:
        """Get cached search results"""
        cache_key = self._generate_cache_key(query, filters, source)
        cached_data = self._get_from_cache(cache_key)
        
        if cached_data:
            return cached_data.get('results', [])
        
        return None
    
    def invalidate_cache(self, pattern: str = None):
        """Invalidate cache entries"""
        if self._use_redis and self._redis_client:
            if pattern:
                for key in self._redis_client.scan_iter(match=f"search:*{pattern}*"):
                    self._redis_client.delete(key)
            else:
                self._redis_client.flushdb()
        else:
            if pattern:
                keys_to_delete = [k for k in self._memory_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self._memory_cache[key]
            else:
                self._memory_cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        return self._cache_stats.copy()

# Global enhanced cache manager instance
enhanced_cache = EnhancedCacheManager()