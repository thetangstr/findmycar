#!/usr/bin/env python3
"""
Cache manager for production application
"""

import os
import json
import hashlib
import logging
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
import time
from functools import wraps

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not installed, using in-memory cache")

class CacheManager:
    """Centralized cache management with Redis or in-memory fallback"""
    
    def __init__(self):
        self.redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        self.default_ttl = 300  # 5 minutes
        self.enabled = True
        
        # Initialize Redis connection
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis not available, using in-memory cache: {e}")
        
        # Fallback to in-memory cache
        if not self.redis_client:
            self.cache = {}
            self.ttl = {}
            logger.info("Using in-memory cache")
        
        # Cache statistics
        self._hits = 0
        self._misses = 0
    
    def create_key(self, prefix: str, params: dict) -> str:
        """Create a cache key from prefix and parameters"""
        # Sort parameters for consistent keys
        sorted_params = sorted(params.items())
        param_str = json.dumps(sorted_params, sort_keys=True, default=str)
        
        # Create hash of parameters
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:16]
        
        return f"{prefix}:{param_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    self._hits += 1
                    return json.loads(value)
                else:
                    self._misses += 1
                    return None
            else:
                # In-memory cache
                if key in self.cache:
                    # Check if expired
                    if key in self.ttl and time.time() > self.ttl[key]:
                        del self.cache[key]
                        del self.ttl[key]
                        self._misses += 1
                        return None
                    self._hits += 1
                    return self.cache[key]
                self._misses += 1
                return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        if not self.enabled:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            
            if self.redis_client:
                serialized = json.dumps(value, default=str)
                self.redis_client.setex(key, ttl, serialized)
            else:
                # In-memory cache
                self.cache[key] = value
                self.ttl[key] = time.time() + ttl
            
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False
        
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                # In-memory cache
                self.cache.pop(key, None)
                self.ttl.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.enabled:
            return 0
        
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # In-memory cache - simple pattern matching
                deleted = 0
                pattern_prefix = pattern.replace('*', '')
                keys_to_delete = [k for k in self.cache.keys() if k.startswith(pattern_prefix)]
                for key in keys_to_delete:
                    self.cache.pop(key, None)
                    self.ttl.pop(key, None)
                    deleted += 1
                return deleted
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    def get_or_set(self, key: str, func: Callable, ttl: Optional[int] = None) -> Any:
        """Get from cache or compute and set"""
        # Try to get from cache
        cached = self.get(key)
        if cached is not None:
            return cached
        
        # Compute value
        value = func()
        
        # Cache it
        self.set(key, value, ttl)
        
        return value
    
    def invalidate_search_cache(self):
        """Invalidate all search-related cache entries"""
        deleted = self.delete_pattern("search:*")
        logger.info(f"Invalidated {deleted} search cache entries")
        return deleted
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate"""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total
    
    def get_total_keys(self) -> int:
        """Get total number of keys in cache"""
        if not self.enabled:
            return 0
        
        try:
            if self.redis_client:
                return self.redis_client.dbsize()
            else:
                return len(self.cache)
        except Exception:
            return 0
    
    def cache_stats(self) -> dict:
        """Get cache statistics"""
        return {
            'enabled': self.enabled,
            'type': 'redis' if self.redis_client else 'in-memory',
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': self.get_hit_rate(),
            'total_keys': self.get_total_keys()
        }
    
    def clear(self) -> None:
        """Clear all cache"""
        if self.redis_client:
            self.redis_client.flushdb()
        else:
            self.cache.clear()
            self.ttl.clear()


def cached(ttl: int = 300, key_prefix: str = None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache manager
            cache = CacheManager()
            
            # Generate cache key
            key_parts = [key_prefix or func.__name__]
            if args:
                key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Cache it
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


class RateLimiter:
    """Rate limiter using Redis or in-memory counter"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        if not redis_client and REDIS_AVAILABLE:
            try:
                redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
                self.redis_client = redis.from_url(redis_url)
            except Exception as e:
                logger.warning(f"Redis not available for rate limiting: {e}")
                self.redis_client = None
        
        # In-memory fallback
        if not self.redis_client:
            self.counters = {}
            self.windows = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed under rate limit"""
        try:
            if self.redis_client:
                current = self.redis_client.incr(key)
                if current == 1:
                    self.redis_client.expire(key, window)
                
                return current <= limit
            else:
                # In-memory rate limiting
                now = time.time()
                
                # Clean up old windows
                if key in self.windows and now > self.windows[key]:
                    del self.counters[key]
                    del self.windows[key]
                
                # Initialize or increment counter
                if key not in self.counters:
                    self.counters[key] = 1
                    self.windows[key] = now + window
                else:
                    self.counters[key] += 1
                
                return self.counters[key] <= limit
                
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True  # Allow on error
    
    def get_remaining(self, key: str, limit: int) -> int:
        """Get remaining requests in current window"""
        try:
            if self.redis_client:
                current = self.redis_client.get(key)
                if current:
                    return max(0, limit - int(current))
                return limit
            else:
                # In-memory
                if key in self.counters:
                    return max(0, limit - self.counters[key])
                return limit
        except Exception:
            return limit

# Global cache manager instance
cache_manager = CacheManager()