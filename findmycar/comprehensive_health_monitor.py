#!/usr/bin/env python3
"""
Comprehensive health monitor for production Flask application
Provides detailed monitoring of all system components including:
- Database connectivity and performance
- External API availability and response times
- Cache status and performance
- Application metrics and error rates
"""

import os
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import deque, defaultdict
from threading import Lock
from sqlalchemy.orm import Session
from sqlalchemy import text
import json

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and stores application metrics"""
    
    def __init__(self, window_size: int = 300):
        """
        Initialize metrics collector
        
        Args:
            window_size: Time window in seconds for metrics (default: 5 minutes)
        """
        self.window_size = window_size
        self.lock = Lock()
        
        # Response time tracking
        self.response_times = deque()
        
        # Error tracking
        self.errors = deque()
        self.error_counts = defaultdict(int)
        
        # API call tracking
        self.api_calls = defaultdict(deque)
        
        # Database query tracking
        self.db_queries = deque()
        
        # Cache hit/miss tracking
        self.cache_hits = 0
        self.cache_misses = 0
    
    def record_response_time(self, endpoint: str, duration: float):
        """Record response time for an endpoint"""
        with self.lock:
            timestamp = datetime.utcnow()
            self.response_times.append({
                'timestamp': timestamp,
                'endpoint': endpoint,
                'duration': duration
            })
            self._cleanup_old_entries(self.response_times)
    
    def record_error(self, error_type: str, details: str):
        """Record an error occurrence"""
        with self.lock:
            timestamp = datetime.utcnow()
            self.errors.append({
                'timestamp': timestamp,
                'type': error_type,
                'details': details
            })
            self.error_counts[error_type] += 1
            self._cleanup_old_entries(self.errors)
    
    def record_api_call(self, api_name: str, duration: float, success: bool):
        """Record an external API call"""
        with self.lock:
            timestamp = datetime.utcnow()
            self.api_calls[api_name].append({
                'timestamp': timestamp,
                'duration': duration,
                'success': success
            })
            self._cleanup_old_entries(self.api_calls[api_name])
    
    def record_db_query(self, query_type: str, duration: float):
        """Record a database query"""
        with self.lock:
            timestamp = datetime.utcnow()
            self.db_queries.append({
                'timestamp': timestamp,
                'type': query_type,
                'duration': duration
            })
            self._cleanup_old_entries(self.db_queries)
    
    def record_cache_hit(self):
        """Record a cache hit"""
        with self.lock:
            self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss"""
        with self.lock:
            self.cache_misses += 1
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics"""
        with self.lock:
            # Calculate response time statistics
            response_stats = self._calculate_response_stats()
            
            # Calculate error rate
            error_rate = len(self.errors) / max(len(self.response_times), 1)
            
            # Calculate API statistics
            api_stats = self._calculate_api_stats()
            
            # Calculate database statistics
            db_stats = self._calculate_db_stats()
            
            # Calculate cache hit rate
            total_cache_ops = self.cache_hits + self.cache_misses
            cache_hit_rate = self.cache_hits / total_cache_ops if total_cache_ops > 0 else 0
            
            return {
                'response_times': response_stats,
                'error_rate': error_rate,
                'error_counts': dict(self.error_counts),
                'api_performance': api_stats,
                'database_performance': db_stats,
                'cache_hit_rate': cache_hit_rate,
                'metrics_window': f"{self.window_size} seconds"
            }
    
    def _cleanup_old_entries(self, collection: deque):
        """Remove entries older than the time window"""
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.window_size)
        while collection and collection[0]['timestamp'] < cutoff_time:
            collection.popleft()
    
    def _calculate_response_stats(self) -> Dict[str, Any]:
        """Calculate response time statistics"""
        if not self.response_times:
            return {'avg': 0, 'p50': 0, 'p95': 0, 'p99': 0, 'count': 0}
        
        times = sorted([r['duration'] for r in self.response_times])
        count = len(times)
        
        return {
            'avg': sum(times) / count,
            'p50': times[int(count * 0.5)],
            'p95': times[int(count * 0.95)] if count > 20 else times[-1],
            'p99': times[int(count * 0.99)] if count > 100 else times[-1],
            'count': count
        }
    
    def _calculate_api_stats(self) -> Dict[str, Any]:
        """Calculate API performance statistics"""
        stats = {}
        for api_name, calls in self.api_calls.items():
            if not calls:
                continue
            
            durations = [c['duration'] for c in calls]
            success_count = sum(1 for c in calls if c['success'])
            
            stats[api_name] = {
                'avg_duration': sum(durations) / len(durations),
                'success_rate': success_count / len(calls),
                'total_calls': len(calls)
            }
        
        return stats
    
    def _calculate_db_stats(self) -> Dict[str, Any]:
        """Calculate database performance statistics"""
        if not self.db_queries:
            return {'avg_duration': 0, 'query_count': 0}
        
        durations = [q['duration'] for q in self.db_queries]
        
        return {
            'avg_duration': sum(durations) / len(durations),
            'query_count': len(durations),
            'query_types': defaultdict(int, 
                {q['type']: sum(1 for query in self.db_queries if query['type'] == q['type'])
                 for q in self.db_queries})
        }


class ComprehensiveHealthMonitor:
    """Enhanced health monitor with detailed component monitoring"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.metrics = MetricsCollector()
        
        # API endpoints to monitor
        self.api_endpoints = {
            'ebay': {
                'name': 'eBay Motors API',
                'health_url': 'https://api.ebay.com/buy/browse/v1/item_summary/search',
                'requires_auth': True,
                'timeout': 5
            },
            'carmax': {
                'name': 'CarMax API',
                'health_url': 'https://api.carmax.com/v1/vehicles',
                'requires_auth': False,
                'timeout': 5
            },
            'autotrader': {
                'name': 'AutoTrader API',
                'health_url': 'https://www.autotrader.com/cars-for-sale/searchresults.xhtml',
                'requires_auth': False,
                'timeout': 5
            }
        }
    
    def get_detailed_status(self, db: Session) -> Dict[str, Any]:
        """Get comprehensive health status of all components"""
        components = []
        
        # Database health check
        db_status = self._check_database(db)
        components.append(db_status)
        
        # Cache health check
        cache_status = self._check_cache()
        components.append(cache_status)
        
        # External API health checks
        for api_key, api_config in self.api_endpoints.items():
            api_status = self._check_external_api(api_key, api_config)
            components.append(api_status)
        
        # Application metrics
        app_metrics = self._get_application_metrics()
        
        # Calculate overall status
        statuses = [c['status'] for c in components]
        if all(s == 'healthy' for s in statuses):
            overall_status = 'healthy'
        elif any(s == 'unhealthy' for s in statuses):
            overall_status = 'unhealthy'
        else:
            overall_status = 'degraded'
        
        # Calculate uptime
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': uptime_seconds,
            'uptime_human': self._format_uptime(uptime_seconds),
            'components': components,
            'metrics': app_metrics,
            'version': os.environ.get('APP_VERSION', '1.0.0'),
            'environment': os.environ.get('ENVIRONMENT', 'production'),
            'host': os.environ.get('HOSTNAME', 'unknown')
        }
    
    def _check_database(self, db: Session) -> Dict[str, Any]:
        """Check database health and performance"""
        start_time = time.time()
        
        try:
            # Basic connectivity check
            result = db.execute(text("SELECT 1")).scalar()
            
            # Check table existence and row counts
            vehicle_count = db.execute(text("SELECT COUNT(*) FROM vehicles_v2")).scalar()
            
            # Check database response time
            duration = time.time() - start_time
            self.metrics.record_db_query('health_check', duration)
            
            # Determine status based on response time
            if duration < 0.1:
                status = 'healthy'
            elif duration < 0.5:
                status = 'degraded'
            else:
                status = 'unhealthy'
            
            return {
                'name': 'database',
                'status': status,
                'message': f'Database connection OK, {vehicle_count} vehicles',
                'response_time_ms': round(duration * 1000, 2),
                'details': {
                    'vehicle_count': vehicle_count,
                    'connection_pool_size': getattr(db.bind.pool, 'size', 'N/A'),
                    'active_connections': getattr(db.bind.pool, 'checked_out', 'N/A')
                },
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_error('database', str(e))
            
            return {
                'name': 'database',
                'status': 'unhealthy',
                'message': f'Database error: {str(e)}',
                'response_time_ms': round(duration * 1000, 2),
                'checked_at': datetime.utcnow().isoformat()
            }
    
    def _check_cache(self) -> Dict[str, Any]:
        """Check cache health and performance"""
        start_time = time.time()
        
        try:
            from cache_manager import CacheManager
            cache = CacheManager()
            
            # Test cache operations
            test_key = 'health_check_test'
            test_value = {'timestamp': datetime.utcnow().isoformat()}
            
            # Test set operation
            cache.set(test_key, test_value, ttl=60)
            
            # Test get operation
            retrieved = cache.get(test_key)
            
            # Check cache statistics
            cache_stats = cache.cache_stats()
            
            duration = time.time() - start_time
            
            # Determine status
            if cache_stats['enabled'] and retrieved == test_value:
                status = 'healthy'
                message = f"Cache operational, hit rate: {cache_stats['hit_rate']:.2%}"
            elif cache_stats['enabled']:
                status = 'degraded'
                message = "Cache enabled but experiencing issues"
            else:
                status = 'degraded'
                message = "Cache disabled, using fallback"
            
            return {
                'name': 'cache',
                'status': status,
                'message': message,
                'response_time_ms': round(duration * 1000, 2),
                'details': cache_stats,
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_error('cache', str(e))
            
            return {
                'name': 'cache',
                'status': 'unhealthy',
                'message': f'Cache error: {str(e)}',
                'response_time_ms': round(duration * 1000, 2),
                'checked_at': datetime.utcnow().isoformat()
            }
    
    def _check_external_api(self, api_key: str, api_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check external API health"""
        start_time = time.time()
        
        try:
            # Check if credentials are configured
            if api_key == 'ebay':
                if not (os.environ.get('EBAY_CLIENT_ID') and os.environ.get('EBAY_CLIENT_SECRET')):
                    return {
                        'name': api_config['name'],
                        'status': 'degraded',
                        'message': 'API credentials not configured',
                        'checked_at': datetime.utcnow().isoformat()
                    }
            
            # For now, we'll just check if the endpoint is reachable
            # In production, you'd want to make actual API calls with proper auth
            response = requests.head(
                api_config['health_url'],
                timeout=api_config['timeout'],
                allow_redirects=True
            )
            
            duration = time.time() - start_time
            self.metrics.record_api_call(api_key, duration, response.status_code < 500)
            
            # Determine status based on response
            if response.status_code < 400:
                status = 'healthy'
                message = f'API endpoint reachable, status: {response.status_code}'
            elif response.status_code < 500:
                status = 'degraded'
                message = f'API endpoint returned client error: {response.status_code}'
            else:
                status = 'unhealthy'
                message = f'API endpoint returned server error: {response.status_code}'
            
            return {
                'name': api_config['name'],
                'status': status,
                'message': message,
                'response_time_ms': round(duration * 1000, 2),
                'details': {
                    'status_code': response.status_code,
                    'endpoint': api_config['health_url']
                },
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            self.metrics.record_api_call(api_key, duration, False)
            self.metrics.record_error(f'api_{api_key}', 'Timeout')
            
            return {
                'name': api_config['name'],
                'status': 'unhealthy',
                'message': f'API timeout after {api_config["timeout"]}s',
                'response_time_ms': round(duration * 1000, 2),
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_api_call(api_key, duration, False)
            self.metrics.record_error(f'api_{api_key}', str(e))
            
            return {
                'name': api_config['name'],
                'status': 'unhealthy',
                'message': f'API error: {str(e)}',
                'response_time_ms': round(duration * 1000, 2),
                'checked_at': datetime.utcnow().isoformat()
            }
    
    def _get_application_metrics(self) -> Dict[str, Any]:
        """Get application performance metrics"""
        return self.metrics.get_metrics_summary()
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human readable format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        
        return " ".join(parts) if parts else "< 1m"
    
    def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        metrics = self.metrics.get_metrics_summary()
        output = []
        
        # Response time metrics
        output.append('# HELP http_request_duration_seconds HTTP request latency')
        output.append('# TYPE http_request_duration_seconds summary')
        output.append(f'http_request_duration_seconds_avg {metrics["response_times"]["avg"]:.3f}')
        output.append(f'http_request_duration_seconds_p50 {metrics["response_times"]["p50"]:.3f}')
        output.append(f'http_request_duration_seconds_p95 {metrics["response_times"]["p95"]:.3f}')
        output.append(f'http_request_duration_seconds_p99 {metrics["response_times"]["p99"]:.3f}')
        output.append(f'http_request_duration_seconds_count {metrics["response_times"]["count"]}')
        
        # Error rate metrics
        output.append('# HELP http_request_error_rate Request error rate')
        output.append('# TYPE http_request_error_rate gauge')
        output.append(f'http_request_error_rate {metrics["error_rate"]:.3f}')
        
        # Cache metrics
        output.append('# HELP cache_hit_rate Cache hit rate')
        output.append('# TYPE cache_hit_rate gauge')
        output.append(f'cache_hit_rate {metrics["cache_hit_rate"]:.3f}')
        
        # API performance metrics
        for api_name, stats in metrics['api_performance'].items():
            output.append(f'# HELP api_{api_name}_duration_seconds API response time')
            output.append(f'# TYPE api_{api_name}_duration_seconds gauge')
            output.append(f'api_{api_name}_duration_seconds {stats["avg_duration"]:.3f}')
            
            output.append(f'# HELP api_{api_name}_success_rate API success rate')
            output.append(f'# TYPE api_{api_name}_success_rate gauge')
            output.append(f'api_{api_name}_success_rate {stats["success_rate"]:.3f}')
        
        # Database metrics
        output.append('# HELP database_query_duration_seconds Database query duration')
        output.append('# TYPE database_query_duration_seconds gauge')
        output.append(f'database_query_duration_seconds {metrics["database_performance"]["avg_duration"]:.3f}')
        
        output.append('# HELP database_query_total Total database queries')
        output.append('# TYPE database_query_total counter')
        output.append(f'database_query_total {metrics["database_performance"]["query_count"]}')
        
        return '\n'.join(output)


# Global instance for use in the application
health_monitor = ComprehensiveHealthMonitor()