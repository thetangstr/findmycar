#!/usr/bin/env python3
"""
Production error handling and fallback strategies
"""

import logging
import time
import functools
from typing import Any, Callable, Optional, Dict, List
from datetime import datetime, timedelta
import json
import traceback
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorType(Enum):
    """Types of errors for categorization"""
    DATABASE_ERROR = "database_error"
    API_ERROR = "api_error"
    SCRAPING_ERROR = "scraping_error"
    CACHE_ERROR = "cache_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    UNKNOWN_ERROR = "unknown_error"

class FallbackStrategy(Enum):
    """Available fallback strategies"""
    RETRY = "retry"
    USE_CACHE = "use_cache"
    USE_DEFAULT = "use_default"
    PARTIAL_RESPONSE = "partial_response"
    DEGRADE_GRACEFULLY = "degrade_gracefully"
    FAIL_FAST = "fail_fast"

class ErrorHandler:
    """Central error handling with fallback strategies"""
    
    def __init__(self):
        self.error_counts = {}
        self.error_history = []
        self.circuit_breakers = {}
        
    def handle_error(self, 
                    error: Exception, 
                    context: Dict[str, Any],
                    fallback_strategy: FallbackStrategy = FallbackStrategy.RETRY) -> Any:
        """
        Handle an error with appropriate fallback strategy
        
        Args:
            error: The exception that occurred
            context: Context information about where the error occurred
            fallback_strategy: Strategy to use for recovery
        
        Returns:
            Fallback response based on strategy
        """
        error_type = self._categorize_error(error)
        error_id = self._generate_error_id()
        
        # Log error with context
        logger.error(f"Error {error_id}: {error_type.value} in {context.get('operation', 'unknown')}",
                    extra={
                        'error_id': error_id,
                        'error_type': error_type.value,
                        'context': context,
                        'traceback': traceback.format_exc()
                    })
        
        # Track error
        self._track_error(error_type, context)
        
        # Apply fallback strategy
        return self._apply_fallback(error, error_type, context, fallback_strategy)
    
    def _categorize_error(self, error: Exception) -> ErrorType:
        """Categorize error for appropriate handling"""
        error_name = error.__class__.__name__
        error_msg = str(error).lower()
        
        if any(db_err in error_name for db_err in ['DatabaseError', 'OperationalError', 'IntegrityError']):
            return ErrorType.DATABASE_ERROR
        elif any(api_err in error_msg for api_err in ['api', 'unauthorized', '401', '403', '429']):
            if '429' in error_msg or 'rate limit' in error_msg:
                return ErrorType.RATE_LIMIT_ERROR
            return ErrorType.API_ERROR
        elif any(scrape_err in error_msg for scrape_err in ['selenium', 'webdriver', 'element not found']):
            return ErrorType.SCRAPING_ERROR
        elif any(cache_err in error_msg for cache_err in ['redis', 'cache']):
            return ErrorType.CACHE_ERROR
        elif 'timeout' in error_msg:
            return ErrorType.TIMEOUT_ERROR
        elif any(val_err in error_name for val_err in ['ValidationError', 'ValueError', 'TypeError']):
            return ErrorType.VALIDATION_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID for tracking"""
        return f"ERR-{int(time.time() * 1000)}"
    
    def _track_error(self, error_type: ErrorType, context: Dict[str, Any]):
        """Track error for monitoring and circuit breaking"""
        key = f"{error_type.value}:{context.get('operation', 'unknown')}"
        
        # Increment error count
        if key not in self.error_counts:
            self.error_counts[key] = 0
        self.error_counts[key] += 1
        
        # Add to history
        self.error_history.append({
            'timestamp': datetime.utcnow(),
            'error_type': error_type.value,
            'context': context
        })
        
        # Clean old history (keep last hour)
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.error_history = [e for e in self.error_history if e['timestamp'] > cutoff]
    
    def _apply_fallback(self, 
                       error: Exception,
                       error_type: ErrorType,
                       context: Dict[str, Any],
                       strategy: FallbackStrategy) -> Any:
        """Apply appropriate fallback strategy"""
        
        if strategy == FallbackStrategy.RETRY:
            return self._retry_strategy(error, context)
        elif strategy == FallbackStrategy.USE_CACHE:
            return self._cache_fallback(context)
        elif strategy == FallbackStrategy.USE_DEFAULT:
            return self._default_fallback(context)
        elif strategy == FallbackStrategy.PARTIAL_RESPONSE:
            return self._partial_response_fallback(context)
        elif strategy == FallbackStrategy.DEGRADE_GRACEFULLY:
            return self._graceful_degradation(context)
        else:  # FAIL_FAST
            raise error
    
    def _retry_strategy(self, error: Exception, context: Dict[str, Any]) -> Any:
        """Retry with exponential backoff"""
        max_retries = context.get('max_retries', 3)
        retry_count = context.get('retry_count', 0)
        
        if retry_count >= max_retries:
            logger.warning(f"Max retries ({max_retries}) exceeded for {context.get('operation')}")
            return self._default_fallback(context)
        
        # Calculate backoff
        backoff = min(2 ** retry_count * 0.1, 5)  # Max 5 seconds
        logger.info(f"Retrying {context.get('operation')} after {backoff}s (attempt {retry_count + 1}/{max_retries})")
        
        return {
            'retry': True,
            'backoff': backoff,
            'retry_count': retry_count + 1
        }
    
    def _cache_fallback(self, context: Dict[str, Any]) -> Any:
        """Return cached data if available"""
        cache_key = context.get('cache_key')
        if cache_key and 'cache_manager' in context:
            cached_data = context['cache_manager'].get(cache_key)
            if cached_data:
                logger.info(f"Using cached data for {context.get('operation')}")
                return cached_data
        
        return self._default_fallback(context)
    
    def _default_fallback(self, context: Dict[str, Any]) -> Any:
        """Return sensible defaults based on operation"""
        operation = context.get('operation', '')
        
        if 'search' in operation:
            return {
                'vehicles': [],
                'total': 0,
                'error': True,
                'message': 'Search temporarily unavailable'
            }
        elif 'detail' in operation:
            return {
                'error': True,
                'message': 'Vehicle details temporarily unavailable'
            }
        else:
            return None
    
    def _partial_response_fallback(self, context: Dict[str, Any]) -> Any:
        """Return partial results if some sources succeeded"""
        partial_results = context.get('partial_results', {})
        if partial_results:
            logger.info(f"Returning partial results for {context.get('operation')}")
            return {
                **partial_results,
                'partial': True,
                'failed_sources': context.get('failed_sources', [])
            }
        
        return self._default_fallback(context)
    
    def _graceful_degradation(self, context: Dict[str, Any]) -> Any:
        """Degrade functionality gracefully"""
        operation = context.get('operation', '')
        
        if 'live_search' in operation:
            # Fall back to local search only
            return {
                'use_local_only': True,
                'degraded': True,
                'message': 'Using local data only due to external service issues'
            }
        
        return self._default_fallback(context)
    
    def is_circuit_open(self, service: str) -> bool:
        """Check if circuit breaker is open for a service"""
        if service not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[service]
        if breaker['state'] == 'open':
            # Check if cooldown period has passed
            if datetime.utcnow() > breaker['open_until']:
                # Move to half-open state
                self.circuit_breakers[service]['state'] = 'half-open'
                logger.info(f"Circuit breaker for {service} moved to half-open")
                return False
            return True
        
        return False
    
    def record_success(self, service: str):
        """Record successful operation for circuit breaker"""
        if service in self.circuit_breakers:
            breaker = self.circuit_breakers[service]
            if breaker['state'] == 'half-open':
                # Close circuit on success
                self.circuit_breakers[service] = {
                    'state': 'closed',
                    'failure_count': 0,
                    'last_failure': None
                }
                logger.info(f"Circuit breaker for {service} closed")
    
    def record_failure(self, service: str):
        """Record failed operation for circuit breaker"""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = {
                'state': 'closed',
                'failure_count': 0,
                'last_failure': None
            }
        
        breaker = self.circuit_breakers[service]
        breaker['failure_count'] += 1
        breaker['last_failure'] = datetime.utcnow()
        
        # Check if we should open the circuit
        failure_threshold = 5
        if breaker['failure_count'] >= failure_threshold:
            breaker['state'] = 'open'
            breaker['open_until'] = datetime.utcnow() + timedelta(minutes=5)
            logger.warning(f"Circuit breaker opened for {service}")

# Global error handler instance
error_handler = ErrorHandler()

def with_fallback(fallback_strategy: FallbackStrategy = FallbackStrategy.RETRY,
                 operation: str = "unknown"):
    """Decorator for adding error handling with fallback to functions"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            context = {
                'operation': operation or func.__name__,
                'args': args,
                'kwargs': kwargs
            }
            
            retry_count = 0
            max_retries = 3
            
            while retry_count <= max_retries:
                try:
                    result = func(*args, **kwargs)
                    # Record success if service-specific
                    if 'service' in kwargs:
                        error_handler.record_success(kwargs['service'])
                    return result
                
                except Exception as e:
                    context['retry_count'] = retry_count
                    context['max_retries'] = max_retries
                    
                    # Record failure if service-specific
                    if 'service' in kwargs:
                        error_handler.record_failure(kwargs['service'])
                    
                    fallback_result = error_handler.handle_error(e, context, fallback_strategy)
                    
                    if isinstance(fallback_result, dict) and fallback_result.get('retry'):
                        retry_count += 1
                        time.sleep(fallback_result.get('backoff', 1))
                        continue
                    
                    return fallback_result
            
            # If all retries exhausted
            return error_handler._default_fallback(context)
        
        return wrapper
    return decorator

class RobustSearchService:
    """Enhanced search service with comprehensive error handling"""
    
    def __init__(self, base_search_service, cache_manager=None):
        self.base_service = base_search_service
        self.cache_manager = cache_manager
        self.error_handler = error_handler
    
    @with_fallback(FallbackStrategy.PARTIAL_RESPONSE, "multi_source_search")
    def search_with_fallback(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Search with comprehensive error handling"""
        results = {
            'vehicles': [],
            'sources_used': [],
            'failed_sources': [],
            'partial': False
        }
        
        # Try local search first (most reliable)
        try:
            local_results = self._search_local(query, filters)
            results['vehicles'].extend(local_results['vehicles'])
            results['sources_used'].append('local')
        except Exception as e:
            logger.error(f"Local search failed: {e}")
            results['failed_sources'].append('local')
        
        # Try each external source with circuit breaker
        external_sources = [
            ('ebay', self._search_ebay),
            ('carmax', self._search_carmax),
            ('autotrader', self._search_autotrader)
        ]
        
        for source_name, search_func in external_sources:
            if self.error_handler.is_circuit_open(source_name):
                logger.warning(f"Circuit breaker open for {source_name}, skipping")
                results['failed_sources'].append(source_name)
                continue
            
            try:
                source_results = search_func(query, filters)
                results['vehicles'].extend(source_results.get('vehicles', []))
                results['sources_used'].append(source_name)
                self.error_handler.record_success(source_name)
            except Exception as e:
                logger.error(f"{source_name} search failed: {e}")
                results['failed_sources'].append(source_name)
                self.error_handler.record_failure(source_name)
                results['partial'] = True
        
        # Deduplicate results
        results['vehicles'] = self._deduplicate_vehicles(results['vehicles'])
        results['total'] = len(results['vehicles'])
        
        return results
    
    def _search_local(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Search local database with timeout"""
        # Implementation would call base service with timeout
        return self.base_service.search_local(query, filters)
    
    def _search_ebay(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Search eBay with error handling"""
        # Implementation would call eBay client with timeout
        return self.base_service.search_ebay(query, filters)
    
    def _search_carmax(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Search CarMax with error handling"""
        # Implementation would call CarMax scraper with timeout
        return self.base_service.search_carmax(query, filters)
    
    def _search_autotrader(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Search AutoTrader with error handling"""
        # Implementation would call AutoTrader scraper with timeout
        return self.base_service.search_autotrader(query, filters)
    
    def _deduplicate_vehicles(self, vehicles: List[Dict]) -> List[Dict]:
        """Remove duplicate vehicles based on listing ID"""
        seen = set()
        unique = []
        
        for vehicle in vehicles:
            listing_id = vehicle.get('listing_id')
            if listing_id and listing_id not in seen:
                seen.add(listing_id)
                unique.append(vehicle)
            elif not listing_id:
                # Keep vehicles without listing IDs
                unique.append(vehicle)
        
        return unique