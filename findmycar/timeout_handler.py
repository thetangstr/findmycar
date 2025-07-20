#!/usr/bin/env python3
"""
Timeout handling utilities for production services
"""

import signal
import functools
import threading
import time
from typing import Callable, Any, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import logging

logger = logging.getLogger(__name__)

class TimeoutException(Exception):
    """Custom timeout exception"""
    pass

def timeout(seconds: int, default_value: Any = None, error_message: str = "Operation timed out"):
    """
    Decorator to add timeout to functions
    
    Args:
        seconds: Timeout in seconds
        default_value: Value to return on timeout
        error_message: Error message for timeout exception
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use ThreadPoolExecutor for timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    result = future.result(timeout=seconds)
                    return result
                except FuturesTimeoutError:
                    logger.warning(f"{func.__name__} timed out after {seconds}s")
                    if default_value is not None:
                        return default_value
                    raise TimeoutException(f"{error_message} after {seconds}s")
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {e}")
                    raise
        
        return wrapper
    return decorator

class TimeoutManager:
    """Manages timeouts for different operations"""
    
    # Default timeouts in seconds
    TIMEOUTS = {
        'database_query': 5,
        'api_call': 30,
        'web_scraping': 45,
        'cache_operation': 2,
        'search_operation': 60,
        'health_check': 10
    }
    
    @classmethod
    def get_timeout(cls, operation_type: str) -> int:
        """Get timeout for operation type"""
        return cls.TIMEOUTS.get(operation_type, 30)
    
    @classmethod
    def with_timeout(cls, operation_type: str, default_value: Any = None):
        """Decorator with operation-specific timeout"""
        timeout_seconds = cls.get_timeout(operation_type)
        return timeout(timeout_seconds, default_value)

def run_with_timeout(func: Callable, 
                    args: tuple = (), 
                    kwargs: dict = None,
                    timeout_seconds: int = 30,
                    default_value: Any = None) -> Any:
    """
    Run a function with timeout
    
    Args:
        func: Function to run
        args: Positional arguments
        kwargs: Keyword arguments
        timeout_seconds: Timeout in seconds
        default_value: Value to return on timeout
    
    Returns:
        Function result or default_value on timeout
    """
    kwargs = kwargs or {}
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            result = future.result(timeout=timeout_seconds)
            return result
        except FuturesTimeoutError:
            logger.warning(f"{func.__name__} timed out after {timeout_seconds}s")
            if default_value is not None:
                return default_value
            raise TimeoutException(f"Operation timed out after {timeout_seconds}s")

class BatchTimeout:
    """Handle timeouts for batch operations"""
    
    def __init__(self, total_timeout: int, per_item_timeout: Optional[int] = None):
        self.total_timeout = total_timeout
        self.per_item_timeout = per_item_timeout
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def check_timeout(self):
        """Check if total timeout exceeded"""
        if self.start_time and time.time() - self.start_time > self.total_timeout:
            raise TimeoutException(f"Batch operation exceeded total timeout of {self.total_timeout}s")
    
    def get_remaining_time(self) -> float:
        """Get remaining time in seconds"""
        if not self.start_time:
            return self.total_timeout
        
        elapsed = time.time() - self.start_time
        return max(0, self.total_timeout - elapsed)
    
    def get_item_timeout(self) -> int:
        """Get timeout for next item"""
        if self.per_item_timeout:
            return min(self.per_item_timeout, int(self.get_remaining_time()))
        return int(self.get_remaining_time())