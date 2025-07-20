#!/usr/bin/env python3
"""
Enhanced production search service with comprehensive error handling and fallbacks
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from production_search_service import ProductionSearchService
from production_error_handler import error_handler, with_fallback, FallbackStrategy
from timeout_handler import TimeoutManager, run_with_timeout, BatchTimeout
from cache_manager import CacheManager

logger = logging.getLogger(__name__)

class EnhancedProductionSearchService(ProductionSearchService):
    """
    Production search service with robust error handling, timeouts, and fallbacks
    """
    
    def __init__(self, db_session: Session, cache_manager: Optional[CacheManager] = None):
        super().__init__(db_session)
        self.cache = cache_manager or CacheManager()
        self.timeout_manager = TimeoutManager()
        
    def search(self,
               query: Optional[str] = None,
               filters: Optional[Dict[str, Any]] = None,
               preset: Optional[str] = None,
               sort_by: str = 'relevance',
               page: int = 1,
               per_page: int = 20,
               include_live: bool = True,
               user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhanced search with comprehensive error handling
        """
        start_time = time.time()
        search_context = {
            'operation': 'vehicle_search',
            'query': query,
            'filters': filters,
            'cache_manager': self.cache
        }
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(query, filters, sort_by, page, per_page)
            search_context['cache_key'] = cache_key
            
            # Check cache first
            cached_results = self._get_cached_results(cache_key)
            if cached_results:
                logger.info(f"Returning cached results for key: {cache_key}")
                return cached_results
            
            # Perform search with timeout
            results = self._perform_search_with_timeout(
                query, filters, preset, sort_by, page, per_page, include_live, user_id
            )
            
            # Cache successful results
            if results and not results.get('error'):
                self._cache_results(cache_key, results)
            
            # Add timing information
            results['search_time'] = time.time() - start_time
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            # Return fallback response
            fallback_response = error_handler.handle_error(
                e, search_context, FallbackStrategy.PARTIAL_RESPONSE
            )
            
            # Try to return at least local results
            if fallback_response is None:
                fallback_response = self._get_local_only_results(
                    query, filters, preset, sort_by, page, per_page, user_id
                )
            
            return fallback_response
    
    def _perform_search_with_timeout(self, 
                                   query: Optional[str],
                                   filters: Optional[Dict[str, Any]],
                                   preset: Optional[str],
                                   sort_by: str,
                                   page: int,
                                   per_page: int,
                                   include_live: bool,
                                   user_id: Optional[str]) -> Dict[str, Any]:
        """Perform search with timeout management"""
        
        # Use batch timeout for entire search operation
        with BatchTimeout(total_timeout=60, per_item_timeout=20) as batch_timeout:
            
            # First, get local results (fast and reliable)
            local_results = self._search_local_with_timeout(
                query, filters, preset, sort_by, user_id,
                timeout=batch_timeout.get_item_timeout()
            )
            
            all_vehicles = list(local_results.get('vehicles', []))
            sources_used = ['local']
            failed_sources = []
            live_count = 0
            
            # Check if we should search live sources
            if include_live and self.enable_live_search:
                batch_timeout.check_timeout()
                
                # Search live sources in parallel
                live_results = self._search_live_sources_parallel(
                    query, filters, page,
                    remaining_time=batch_timeout.get_remaining_time()
                )
                
                all_vehicles.extend(live_results['vehicles'])
                sources_used.extend(live_results['sources'])
                failed_sources.extend(live_results['failed_sources'])
                live_count = live_results['count']
            
            # Sort and paginate combined results
            sorted_vehicles = self._sort_vehicles(all_vehicles, sort_by, query)
            
            # Apply pagination
            total = len(sorted_vehicles)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_vehicles = sorted_vehicles[start_idx:end_idx]
            
            return {
                'vehicles': paginated_vehicles,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page,
                'sources_used': sources_used,
                'failed_sources': failed_sources,
                'local_count': local_results.get('total', 0),
                'live_count': live_count,
                'partial': len(failed_sources) > 0,
                'cached': False
            }
    
    @with_fallback(FallbackStrategy.USE_DEFAULT, "local_search")
    def _search_local_with_timeout(self,
                                  query: Optional[str],
                                  filters: Optional[Dict[str, Any]],
                                  preset: Optional[str],
                                  sort_by: str,
                                  user_id: Optional[str],
                                  timeout: int = 5) -> Dict[str, Any]:
        """Search local database with timeout"""
        
        def search_func():
            return self.local_search.search(
                query=query,
                filters=filters or {},
                preset=preset,
                sort_by=sort_by,
                page=1,
                per_page=1000,
                user_id=user_id
            )
        
        return run_with_timeout(
            search_func,
            timeout_seconds=timeout,
            default_value={'vehicles': [], 'total': 0}
        )
    
    def _search_live_sources_parallel(self,
                                    query: str,
                                    filters: Dict[str, Any],
                                    page: int,
                                    remaining_time: float) -> Dict[str, Any]:
        """Search all live sources in parallel with timeout and error handling"""
        
        results = {
            'vehicles': [],
            'sources': [],
            'failed_sources': [],
            'count': 0
        }
        
        # Define search tasks
        search_tasks = [
            ('ebay', self._search_ebay_safe),
            ('carmax', self._search_carmax_safe),
            ('autotrader', self._search_autotrader_safe)
        ]
        
        # Calculate timeout per source
        per_source_timeout = int(remaining_time / len(search_tasks))
        
        # Execute searches in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_source = {
                executor.submit(
                    search_func, 
                    query, 
                    filters, 
                    page,
                    per_source_timeout
                ): source_name
                for source_name, search_func in search_tasks
            }
            
            for future in as_completed(future_to_source, timeout=remaining_time):
                source_name = future_to_source[future]
                
                try:
                    source_results = future.result()
                    if source_results and source_results.get('vehicles'):
                        results['vehicles'].extend(source_results['vehicles'])
                        results['sources'].append(source_name)
                        results['count'] += len(source_results['vehicles'])
                        error_handler.record_success(source_name)
                    else:
                        results['failed_sources'].append(source_name)
                        
                except Exception as e:
                    logger.error(f"Error searching {source_name}: {e}")
                    results['failed_sources'].append(source_name)
                    error_handler.record_failure(source_name)
        
        return results
    
    def _search_ebay_safe(self, query: str, filters: Dict, page: int, timeout: int) -> Dict:
        """Search eBay with error handling and timeout"""
        if error_handler.is_circuit_open('ebay'):
            logger.warning("eBay circuit breaker is open")
            return {'vehicles': []}
        
        try:
            return run_with_timeout(
                lambda: self._search_ebay_internal(query, filters, page),
                timeout_seconds=timeout,
                default_value={'vehicles': []}
            )
        except Exception as e:
            logger.error(f"eBay search error: {e}")
            return {'vehicles': []}
    
    def _search_carmax_safe(self, query: str, filters: Dict, page: int, timeout: int) -> Dict:
        """Search CarMax with error handling and timeout"""
        if error_handler.is_circuit_open('carmax'):
            logger.warning("CarMax circuit breaker is open")
            return {'vehicles': []}
        
        try:
            return run_with_timeout(
                lambda: self._search_carmax_internal(query, filters, page),
                timeout_seconds=timeout,
                default_value={'vehicles': []}
            )
        except Exception as e:
            logger.error(f"CarMax search error: {e}")
            return {'vehicles': []}
    
    def _search_autotrader_safe(self, query: str, filters: Dict, page: int, timeout: int) -> Dict:
        """Search AutoTrader with error handling and timeout"""
        if error_handler.is_circuit_open('autotrader'):
            logger.warning("AutoTrader circuit breaker is open")
            return {'vehicles': []}
        
        try:
            return run_with_timeout(
                lambda: self._search_autotrader_internal(query, filters, page),
                timeout_seconds=timeout,
                default_value={'vehicles': []}
            )
        except Exception as e:
            logger.error(f"AutoTrader search error: {e}")
            return {'vehicles': []}
    
    def _search_ebay_internal(self, query: str, filters: Dict, page: int) -> Dict:
        """Internal eBay search implementation"""
        results = self.ebay_client.search_vehicles(
            query=query or "",
            make=filters.get('make'),
            model=filters.get('model'),
            year_min=filters.get('year_min'),
            year_max=filters.get('year_max'),
            price_min=filters.get('price_min'),
            price_max=filters.get('price_max'),
            mileage_max=filters.get('mileage_max'),
            page=page,
            per_page=20
        )
        
        # Add source info to vehicles
        for vehicle in results.get('vehicles', []):
            vehicle['source'] = 'ebay'
            vehicle['is_live'] = True
        
        return results
    
    def _search_carmax_internal(self, query: str, filters: Dict, page: int) -> Dict:
        """Internal CarMax search implementation"""
        from carmax_client import CarMaxClient
        
        client = CarMaxClient()
        try:
            vehicles = client.search_listings(
                query=query,
                filters=filters,
                limit=20
            )
            
            # Add source info
            for vehicle in vehicles:
                vehicle['source'] = 'carmax'
                vehicle['is_live'] = True
            
            return {'vehicles': vehicles}
        finally:
            client.close()
    
    def _search_autotrader_internal(self, query: str, filters: Dict, page: int) -> Dict:
        """Internal AutoTrader search implementation"""
        from autotrader_client import AutotraderClient
        
        client = AutotraderClient()
        try:
            vehicles = client.search_listings(
                query=query,
                filters=filters,
                limit=20
            )
            
            # Add source info
            for vehicle in vehicles:
                vehicle['source'] = 'autotrader'
                vehicle['is_live'] = True
            
            return {'vehicles': vehicles}
        finally:
            client.close()
    
    def _get_local_only_results(self,
                               query: Optional[str],
                               filters: Optional[Dict[str, Any]],
                               preset: Optional[str],
                               sort_by: str,
                               page: int,
                               per_page: int,
                               user_id: Optional[str]) -> Dict[str, Any]:
        """Get results from local database only (fallback)"""
        try:
            local_results = self.local_search.search(
                query=query,
                filters=filters or {},
                preset=preset,
                sort_by=sort_by,
                page=page,
                per_page=per_page,
                user_id=user_id
            )
            
            return {
                **local_results,
                'sources_used': ['local'],
                'failed_sources': ['ebay', 'carmax', 'autotrader'],
                'partial': True,
                'fallback': True,
                'message': 'Showing local results only due to external service issues'
            }
        except Exception as e:
            logger.error(f"Local search fallback failed: {e}")
            return {
                'vehicles': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'pages': 0,
                'sources_used': [],
                'failed_sources': ['all'],
                'error': True,
                'message': 'Search temporarily unavailable'
            }
    
    def _generate_cache_key(self, 
                           query: Optional[str],
                           filters: Optional[Dict],
                           sort_by: str,
                           page: int,
                           per_page: int) -> str:
        """Generate cache key for search results"""
        import hashlib
        import json
        
        key_data = {
            'query': query or '',
            'filters': filters or {},
            'sort_by': sort_by,
            'page': page,
            'per_page': per_page
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return f"search:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def _get_cached_results(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached search results"""
        try:
            cached = self.cache.get(cache_key)
            if cached:
                cached['cached'] = True
                cached['cache_hit'] = True
                return cached
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        
        return None
    
    def _cache_results(self, cache_key: str, results: Dict[str, Any]):
        """Cache search results"""
        try:
            # Don't cache error responses or partial results
            if not results.get('error') and not results.get('partial'):
                # Cache for 5 minutes
                self.cache.set(cache_key, results, ttl=300)
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
    
    def get_vehicle_details_safe(self, vehicle_id: int, fetch_live: bool = True) -> Optional[Dict]:
        """Get vehicle details with error handling"""
        context = {
            'operation': 'vehicle_details',
            'vehicle_id': vehicle_id,
            'cache_manager': self.cache
        }
        
        try:
            # Try with timeout
            return run_with_timeout(
                lambda: self.get_vehicle_details(vehicle_id, fetch_live),
                timeout_seconds=10,
                default_value=None
            )
        except Exception as e:
            logger.error(f"Failed to get vehicle details: {e}")
            return error_handler.handle_error(
                e, context, FallbackStrategy.USE_DEFAULT
            )