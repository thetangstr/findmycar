"""
Redis caching layer for AutoNavigator
"""

import os
import json
import redis
import logging
import datetime
from typing import Any, Optional, Union
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)

class CacheManager:
    """Redis cache manager with fallback to in-memory caching"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._redis_client = None
        self._memory_cache = {}  # Fallback in-memory cache
        self._use_redis = True
        
        # Try to connect to Redis
        try:
            self._redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self._redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory cache: {e}")
            self._use_redis = False
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self._use_redis and self._redis_client:
                value = self._redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self._memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache with expiration"""
        try:
            if self._use_redis and self._redis_client:
                serialized_value = json.dumps(value, default=str)
                return self._redis_client.setex(key, expire, serialized_value)
            else:
                self._memory_cache[key] = value
                # Simple expiration for in-memory cache (not implemented)
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self._use_redis and self._redis_client:
                return bool(self._redis_client.delete(key))
            else:
                return self._memory_cache.pop(key, None) is not None
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern (Redis only)"""
        try:
            if self._use_redis and self._redis_client:
                keys = self._redis_client.keys(pattern)
                if keys:
                    return self._redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache flush pattern error: {e}")
            return 0
    
    def increment(self, key: str, amount: int = 1, expire: int = 3600) -> int:
        """Increment a counter in cache"""
        try:
            if self._use_redis and self._redis_client:
                value = self._redis_client.incr(key, amount)
                self._redis_client.expire(key, expire)
                return value
            else:
                current = self._memory_cache.get(key, 0)
                self._memory_cache[key] = current + amount
                return self._memory_cache[key]
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return 0

# Global cache instance
cache = CacheManager()

def cached(expire: int = 3600, prefix: str = "cache"):
    """
    Decorator to cache function results
    
    Args:
        expire: Cache expiration time in seconds
        prefix: Cache key prefix
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._generate_key(f"{prefix}:{func.__name__}", *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, expire)
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            
            return result
        return wrapper
    return decorator

def cache_search_results(query: str, filters: dict, results: list, expire: int = 1800):
    """Cache search results for 30 minutes"""
    cache_key = cache._generate_key("search", query, **filters)
    cache.set(cache_key, results, expire)

def get_cached_search_results(query: str, filters: dict) -> Optional[list]:
    """Get cached search results"""
    cache_key = cache._generate_key("search", query, **filters)
    return cache.get(cache_key)

def cache_vehicle_details(vehicle_id: str, details: dict, expire: int = 3600):
    """Cache vehicle details for 1 hour"""
    cache_key = f"vehicle_details:{vehicle_id}"
    cache.set(cache_key, details, expire)

def get_cached_vehicle_details(vehicle_id: str) -> Optional[dict]:
    """Get cached vehicle details"""
    cache_key = f"vehicle_details:{vehicle_id}"
    return cache.get(cache_key)

def cache_valuation(make: str, model: str, year: int, mileage: int, valuation: dict, expire: int = 7200):
    """Cache vehicle valuation for 2 hours"""
    cache_key = cache._generate_key("valuation", make, model, year, mileage)
    cache.set(cache_key, valuation, expire)

def get_cached_valuation(make: str, model: str, year: int, mileage: int) -> Optional[dict]:
    """Get cached vehicle valuation"""
    cache_key = cache._generate_key("valuation", make, model, year, mileage)
    return cache.get(cache_key)

def increment_search_counter(query: str):
    """Track search popularity"""
    cache.increment(f"search_count:{query}", expire=86400)  # 24 hours

def get_popular_searches(limit: int = 10) -> list:
    """Get most popular searches"""
    try:
        if cache._use_redis and cache._redis_client:
            # Get all search count keys
            keys = cache._redis_client.keys("search_count:*")
            if not keys:
                return []
            
            # Get counts for all keys
            pipe = cache._redis_client.pipeline()
            for key in keys:
                pipe.get(key)
            counts = pipe.execute()
            
            # Create list of (query, count) tuples
            search_counts = []
            for key, count in zip(keys, counts):
                if count:
                    query = key.replace("search_count:", "")
                    search_counts.append((query, int(count)))
            
            # Sort by count and return top queries
            search_counts.sort(key=lambda x: x[1], reverse=True)
            return [query for query, count in search_counts[:limit]]
    except Exception as e:
        logger.error(f"Error getting popular searches: {e}")
    
    return []

def cache_api_response(endpoint: str, params: dict, response: dict, expire: int = 300):
    """Cache API responses for 5 minutes"""
    cache_key = cache._generate_key(f"api:{endpoint}", **params)
    cache.set(cache_key, response, expire)

def get_cached_api_response(endpoint: str, params: dict) -> Optional[dict]:
    """Get cached API response"""
    cache_key = cache._generate_key(f"api:{endpoint}", **params)
    return cache.get(cache_key)

def clear_cache_by_pattern(pattern: str) -> int:
    """Clear all cache entries matching pattern"""
    return cache.flush_pattern(pattern)

def rate_limit_check(identifier: str, limit: int = 100, window: int = 3600) -> bool:
    """
    Check if identifier is within rate limit
    
    Args:
        identifier: IP address or user identifier
        limit: Maximum requests allowed
        window: Time window in seconds
    
    Returns:
        True if within limit, False if exceeded
    """
    key = f"rate_limit:{identifier}"
    try:
        current = cache.increment(key, expire=window)
        return current <= limit
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return True  # Allow on error

# Database warm cache functions
def store_warm_cache(db_session, query: str, filters: dict, results: list, source: str = "ebay", expire_hours: int = 168):
    """Store search results in database warm cache (default 7 days)"""
    try:
        from database import SearchCache, QueryAnalytics
        import json
        
        # Normalize query for analytics
        query_normalized = query.lower().strip()
        filters_json = json.dumps(filters or {}, sort_keys=True)
        
        # Calculate expiration time
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=expire_hours)
        
        # Create cache entry
        cache_entry = SearchCache(
            query_text=query,
            filters_json=filters_json,
            results=results,
            source=source,
            expires_at=expires_at
        )
        
        # Try to add to database (handle duplicates)
        try:
            db_session.add(cache_entry)
            db_session.commit()
            logger.info(f"Stored {len(results)} results in warm cache for query: {query}")
        except Exception:
            db_session.rollback()
            # Update existing entry
            existing = db_session.query(SearchCache).filter(
                SearchCache.cache_key == cache_entry.cache_key
            ).first()
            if existing:
                existing.results = results
                existing.expires_at = expires_at
                existing.last_accessed = datetime.datetime.utcnow()
                existing.access_count += 1
                db_session.commit()
                logger.info(f"Updated existing warm cache entry for query: {query}")
        
        # Update query analytics
        update_query_analytics(db_session, query_normalized, len(results), cache_miss=True)
        
    except Exception as e:
        logger.error(f"Error storing warm cache: {e}")
        if db_session:
            db_session.rollback()

def get_warm_cache(db_session, query: str, filters: dict) -> list:
    """Get search results from database warm cache"""
    try:
        from database import SearchCache
        import json
        
        filters_json = json.dumps(filters or {}, sort_keys=True)
        key_data = f"{query}:{filters_json}"
        query_hash = hashlib.md5(key_data.encode()).hexdigest()
        cache_key = f"search_{query_hash}"
        
        # Query cache
        cache_entry = db_session.query(SearchCache).filter(
            SearchCache.cache_key == cache_key,
            SearchCache.expires_at > datetime.datetime.utcnow()
        ).first()
        
        if cache_entry:
            # Update access statistics
            cache_entry.access_count += 1
            cache_entry.last_accessed = datetime.datetime.utcnow()
            db_session.commit()
            
            # Update query analytics
            query_normalized = query.lower().strip()
            update_query_analytics(db_session, query_normalized, len(cache_entry.results), cache_hit=True)
            
            logger.info(f"Retrieved {len(cache_entry.results)} results from warm cache for query: {query}")
            return cache_entry.results
        
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving warm cache: {e}")
        return None

def update_query_analytics(db_session, query_normalized: str, result_count: int, cache_hit: bool = False, cache_miss: bool = False):
    """Update query analytics for caching decisions"""
    try:
        from database import QueryAnalytics
        
        # Get or create analytics entry
        analytics = db_session.query(QueryAnalytics).filter(
            QueryAnalytics.query_normalized == query_normalized
        ).first()
        
        if analytics:
            analytics.search_count += 1
            analytics.last_searched = datetime.datetime.utcnow()
            
            # Update average results
            if analytics.avg_results:
                analytics.avg_results = int((analytics.avg_results + result_count) / 2)
            else:
                analytics.avg_results = result_count
            
            # Update cache statistics
            if cache_hit:
                analytics.cache_hits += 1
            if cache_miss:
                analytics.cache_misses += 1
        else:
            analytics = QueryAnalytics(
                query_normalized=query_normalized,
                search_count=1,
                avg_results=result_count,
                cache_hits=1 if cache_hit else 0,
                cache_misses=1 if cache_miss else 0
            )
            db_session.add(analytics)
        
        db_session.commit()
        
    except Exception as e:
        logger.error(f"Error updating query analytics: {e}")
        db_session.rollback()

def get_popular_queries(db_session, limit: int = 10):
    """Get most popular queries from database analytics"""
    try:
        from database import QueryAnalytics
        
        popular = db_session.query(QueryAnalytics).order_by(
            QueryAnalytics.search_count.desc()
        ).limit(limit).all()
        
        return [(q.query_normalized, q.search_count, q.cache_hit_rate) for q in popular]
        
    except Exception as e:
        logger.error(f"Error getting popular queries: {e}")
        return []

def cleanup_expired_cache(db_session):
    """Clean up expired cache entries"""
    try:
        from database import SearchCache
        
        expired_count = db_session.query(SearchCache).filter(
            SearchCache.expires_at < datetime.datetime.utcnow()
        ).delete()
        
        db_session.commit()
        logger.info(f"Cleaned up {expired_count} expired cache entries")
        return expired_count
        
    except Exception as e:
        logger.error(f"Error cleaning up cache: {e}")
        db_session.rollback()
        return 0

# Health check for cache
def cache_health_check() -> dict:
    """Check cache health status"""
    try:
        if cache._use_redis and cache._redis_client:
            cache._redis_client.ping()
            return {"status": "healthy", "type": "redis"}
        else:
            return {"status": "healthy", "type": "memory"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}