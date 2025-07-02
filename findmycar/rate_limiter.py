import time
import threading
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Token bucket rate limiter for API requests.
    """
    def __init__(self, rate: int = 5, per: int = 1, burst: int = 10):
        """
        Initialize rate limiter.
        
        Args:
            rate: Number of requests allowed per time period
            per: Time period in seconds
            burst: Maximum burst size (max tokens in bucket)
        """
        self.rate = rate
        self.per = per
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
        self.lock = threading.Lock()
        
    def _refill(self):
        """Refill tokens based on time elapsed"""
        now = time.time()
        elapsed = now - self.last_update
        tokens_to_add = elapsed * (self.rate / self.per)
        self.tokens = min(self.burst, self.tokens + tokens_to_add)
        self.last_update = now
        
    def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens for a request.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens acquired, False if rate limited
        """
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
            
    def wait_if_needed(self, tokens: int = 1) -> float:
        """
        Wait if necessary to acquire tokens.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            Time waited in seconds
        """
        wait_time = 0
        while not self.acquire(tokens):
            # Calculate time to wait for next token
            with self.lock:
                tokens_needed = tokens - self.tokens
                time_for_tokens = tokens_needed * (self.per / self.rate)
                wait_time = max(0.1, time_for_tokens)
            
            logger.debug(f"Rate limited, waiting {wait_time:.2f}s")
            time.sleep(wait_time)
            
        return wait_time


class EbayRateLimiter:
    """
    eBay-specific rate limiter with different limits per operation
    """
    def __init__(self):
        # eBay Browse API limits (approximate)
        # Search: 5,000 calls/day ≈ 3.5 calls/minute
        # Get Item: 5,000 calls/day ≈ 3.5 calls/minute
        
        self.limiters = {
            'search': RateLimiter(rate=3, per=60, burst=10),  # 3 per minute, burst of 10
            'get_item': RateLimiter(rate=3, per=60, burst=10),  # 3 per minute, burst of 10
            'oauth': RateLimiter(rate=1, per=60, burst=3),  # 1 per minute for OAuth
        }
        
        # Track daily usage
        self.daily_counts = {
            'search': 0,
            'get_item': 0,
            'oauth': 0
        }
        self.daily_limits = {
            'search': 5000,
            'get_item': 5000,
            'oauth': 100
        }
        self.day_start = datetime.now().date()
        
    def _check_daily_reset(self):
        """Reset daily counters if new day"""
        current_date = datetime.now().date()
        if current_date > self.day_start:
            self.daily_counts = {k: 0 for k in self.daily_counts}
            self.day_start = current_date
            logger.info("Daily rate limit counters reset")
            
    def check_limit(self, operation: str) -> bool:
        """
        Check if operation would exceed rate limit.
        
        Args:
            operation: Type of operation ('search', 'get_item', 'oauth')
            
        Returns:
            True if within limits, False if would exceed
        """
        self._check_daily_reset()
        
        if operation not in self.limiters:
            return True
            
        # Check daily limit
        if self.daily_counts[operation] >= self.daily_limits[operation]:
            logger.warning(f"Daily limit reached for {operation}: {self.daily_counts[operation]}/{self.daily_limits[operation]}")
            return False
            
        # Check rate limit
        return self.limiters[operation].acquire()
        
    def wait_and_acquire(self, operation: str) -> float:
        """
        Wait if necessary and acquire permission for operation.
        
        Args:
            operation: Type of operation
            
        Returns:
            Time waited in seconds
            
        Raises:
            Exception: If daily limit exceeded
        """
        self._check_daily_reset()
        
        if operation not in self.limiters:
            return 0
            
        # Check daily limit
        if self.daily_counts[operation] >= self.daily_limits[operation]:
            raise Exception(f"Daily limit exceeded for {operation}: {self.daily_limits[operation]} calls")
            
        # Wait for rate limit if needed
        wait_time = self.limiters[operation].wait_if_needed()
        
        # Increment daily counter
        self.daily_counts[operation] += 1
        
        if self.daily_counts[operation] % 100 == 0:
            logger.info(f"{operation} usage: {self.daily_counts[operation]}/{self.daily_limits[operation]}")
            
        return wait_time
        
    def get_remaining_calls(self, operation: str) -> int:
        """Get remaining calls for the day"""
        self._check_daily_reset()
        return self.daily_limits.get(operation, 0) - self.daily_counts.get(operation, 0)


# Global rate limiter instance
ebay_rate_limiter = EbayRateLimiter()