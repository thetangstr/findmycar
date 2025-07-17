"""
Simple cache manager for AutoNavigator
"""
import time
from typing import Any, Optional

class CacheManager:
    """Simple in-memory cache manager"""
    
    def __init__(self):
        self.cache = {}
        self.ttl = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            # Check if expired
            if key in self.ttl and time.time() > self.ttl[key]:
                del self.cache[key]
                del self.ttl[key]
                return None
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Set value in cache with TTL"""
        self.cache[key] = value
        self.ttl[key] = time.time() + ttl_seconds
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        self.ttl.clear()

# Global cache manager instance
cache_manager = CacheManager()