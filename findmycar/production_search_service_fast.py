#!/usr/bin/env python3
"""
Optimized production search service with parallel execution and timeouts
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import asyncio
import os
from functools import partial

from comprehensive_search_engine_sqlite_fixed import ComprehensiveSearchEngine
from ebay_live_client import EbayLiveClient
from database_v2_sqlite import VehicleV2, get_session
from cache_manager import CacheManager
import json

logger = logging.getLogger(__name__)

class FastProductionSearchService:
    """
    Optimized production search service with parallel execution and timeouts
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.local_search = ComprehensiveSearchEngine(db_session)
        self.ebay_client = EbayLiveClient()
        self.cache_manager = CacheManager()
        
        # Configuration - make it fast by default
        self.enable_live_search = True
        self.enable_slow_sources = os.environ.get('ENABLE_SLOW_SOURCES', 'false').lower() == 'true'
        self.live_search_threshold = 50  # Min local results before skipping live search
        self.max_live_results = 50  # Reduced for speed
        self.data_freshness_hours = 24
        
        # Timeouts for each source (in seconds)
        self.source_timeouts = {
            'ebay': 5.0,      # API is fast
            'carmax': 15.0,   # Selenium is slow
            'autotrader': 15.0 # Selenium is slow
        }
        
        # Only enable fast sources by default
        self.enabled_sources = ['ebay']
        if self.enable_slow_sources:
            self.enabled_sources.extend(['carmax', 'autotrader'])
            
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
        Perform hybrid search with optimized performance
        """
        start_time = datetime.utcnow()
        
        # Create cache key for the entire search
        cache_key = self.cache_manager.create_key('search_results', {
            'query': query,
            'filters': filters,
            'preset': preset,
            'sort_by': sort_by,
            'page': page,
            'per_page': per_page,
            'include_live': include_live
        })
        
        # Check cache first
        cached_result = self.cache_manager.get(cache_key)
        if cached_result and not self._needs_fresh_data(query, filters):
            logger.info(f"Returning cached search results")
            cached_result['cached'] = True
            cached_result['search_time'] = 0.1  # Indicate fast cache hit
            return cached_result
        
        # Search local database first
        local_results = self.local_search.search(
            query=query,
            filters=filters or {},
            preset=preset,
            sort_by=sort_by,
            page=1,  # Get all for merging
            per_page=500,  # Reduced from 1000 for speed
            user_id=user_id
        )
        
        all_vehicles = list(local_results['vehicles'])
        sources_used = ['local']
        live_count = 0
        
        # Determine if we need live search
        should_search_live = (
            include_live and 
            self.enable_live_search and
            len(self.enabled_sources) > 0 and
            (local_results['total'] < self.live_search_threshold or 
             self._needs_fresh_data(query, filters))
        )
        
        if should_search_live:
            try:
                # Perform PARALLEL live search with timeouts
                live_results = self._search_live_sources_parallel(
                    query, filters, page, self.max_live_results
                )
                
                # Merge and deduplicate results
                all_vehicles = self._merge_results(all_vehicles, live_results['vehicles'])
                sources_used.extend(live_results['sources'])
                live_count = live_results['count']
                
                # Store new vehicles asynchronously (don't wait)
                if live_results['vehicles']:
                    self._store_new_vehicles_async(live_results['vehicles'])
                
            except Exception as e:
                logger.error(f"Live search failed: {e}")
                # Continue with local results only
        
        # Apply sorting to merged results
        sorted_vehicles = self._sort_vehicles(all_vehicles, sort_by, query)
        
        # Apply pagination
        total = len(sorted_vehicles)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_vehicles = sorted_vehicles[start_idx:end_idx]
        
        # Calculate search time
        search_time = (datetime.utcnow() - start_time).total_seconds()
        
        result = {
            'success': True,
            'vehicles': paginated_vehicles,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'sources_used': sources_used,
            'local_count': local_results['total'],
            'live_count': live_count,
            'search_time': search_time,
            'cached': False
        }
        
        # Cache the result
        self.cache_manager.set(cache_key, result, ttl=300)  # 5 minutes
        
        return result
        
    def _search_live_sources_parallel(self, query: str, filters: Dict, page: int, limit: int) -> Dict:
        """Search all available live sources in PARALLEL with timeouts"""
        vehicles = []
        sources = []
        
        # Limit per source
        per_source_limit = min(limit // len(self.enabled_sources), 20)
        
        # Prepare search tasks
        search_tasks = []
        
        if 'ebay' in self.enabled_sources:
            search_tasks.append(('ebay', self._search_ebay, query, filters, page, per_source_limit))
            
        if 'carmax' in self.enabled_sources:
            search_tasks.append(('carmax', self._search_carmax, query, filters, per_source_limit))
            
        if 'autotrader' in self.enabled_sources:
            search_tasks.append(('autotrader', self._search_autotrader, query, filters, per_source_limit))
        
        # Execute searches in parallel with timeouts
        with ThreadPoolExecutor(max_workers=len(search_tasks)) as executor:
            future_to_source = {}
            
            for source_name, search_func, *args in search_tasks:
                future = executor.submit(search_func, *args)
                future_to_source[future] = source_name
            
            # Collect results with timeouts
            for future in as_completed(future_to_source, timeout=max(self.source_timeouts.values())):
                source_name = future_to_source[future]
                try:
                    # Get result with source-specific timeout
                    source_vehicles = future.result(timeout=self.source_timeouts.get(source_name, 10))
                    if source_vehicles:
                        vehicles.extend(source_vehicles)
                        sources.append(source_name)
                        logger.info(f"Got {len(source_vehicles)} vehicles from {source_name}")
                except TimeoutError:
                    logger.warning(f"{source_name} search timed out after {self.source_timeouts.get(source_name)}s")
                except Exception as e:
                    logger.error(f"{source_name} search error: {e}")
        
        return {
            'vehicles': vehicles,
            'sources': sources,
            'count': len(vehicles)
        }
        
    def _search_ebay(self, query: str, filters: Dict, page: int, limit: int) -> List[Dict]:
        """Search eBay with caching"""
        cache_key = self.cache_manager.create_key('ebay_search', {
            'query': query, 'filters': filters, 'page': page, 'limit': limit
        })
        
        cached = self.cache_manager.get(cache_key)
        if cached:
            return cached
            
        try:
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
                per_page=limit,
                use_cache=True  # Use eBay client's cache too
            )
            
            vehicles = results.get('vehicles', [])
            self.cache_manager.set(cache_key, vehicles, ttl=600)  # 10 minutes
            return vehicles
            
        except Exception as e:
            logger.error(f"eBay search error: {e}")
            return []
            
    def _search_carmax(self, query: str, filters: Dict, limit: int) -> List[Dict]:
        """Search CarMax with aggressive caching"""
        cache_key = self.cache_manager.create_key('carmax_search', {
            'query': query, 'filters': filters, 'limit': limit
        })
        
        # Check cache first
        cached = self.cache_manager.get(cache_key)
        if cached:
            logger.info("Using cached CarMax results")
            return cached
            
        try:
            from carmax_client import CarMaxClient
            
            # Use context manager to ensure cleanup
            with CarMaxClient() as client:
                vehicles = client.search_listings(
                    query=query,
                    filters=filters,
                    limit=limit
                )
                
                # Add source info
                for vehicle in vehicles:
                    vehicle['source'] = 'carmax'
                    vehicle['is_live'] = True
                
                # Cache for longer since scraping is expensive
                self.cache_manager.set(cache_key, vehicles, ttl=3600)  # 1 hour
                return vehicles
                
        except Exception as e:
            logger.error(f"CarMax search error: {e}")
            return []
            
    def _search_autotrader(self, query: str, filters: Dict, limit: int) -> List[Dict]:
        """Search AutoTrader with aggressive caching"""
        cache_key = self.cache_manager.create_key('autotrader_search', {
            'query': query, 'filters': filters, 'limit': limit
        })
        
        # Check cache first
        cached = self.cache_manager.get(cache_key)
        if cached:
            logger.info("Using cached AutoTrader results")
            return cached
            
        try:
            from autotrader_client import AutotraderClient
            
            # Use context manager to ensure cleanup
            with AutotraderClient() as client:
                vehicles = client.search_listings(
                    query=query,
                    filters=filters,
                    limit=limit
                )
                
                # Add source info
                for vehicle in vehicles:
                    vehicle['source'] = 'autotrader'
                    vehicle['is_live'] = True
                
                # Cache for longer since scraping is expensive
                self.cache_manager.set(cache_key, vehicles, ttl=3600)  # 1 hour
                return vehicles
                
        except Exception as e:
            logger.error(f"AutoTrader search error: {e}")
            return []
    
    def _merge_results(self, local_vehicles: List, live_vehicles: List) -> List:
        """Merge and deduplicate results efficiently"""
        # Create a set of existing vehicle identifiers
        seen = set()
        merged = []
        
        # Add local vehicles first
        for vehicle in local_vehicles:
            if isinstance(vehicle, dict):
                key = (vehicle.get('make'), vehicle.get('model'), 
                       vehicle.get('year'), vehicle.get('price'))
            else:
                key = (vehicle.make, vehicle.model, vehicle.year, vehicle.price)
            
            if key not in seen and key[0] is not None:
                seen.add(key)
                merged.append(vehicle)
        
        # Add live vehicles that aren't duplicates
        for vehicle in live_vehicles:
            key = (vehicle.get('make'), vehicle.get('model'), 
                   vehicle.get('year'), vehicle.get('price'))
            
            if key not in seen and key[0] is not None:
                seen.add(key)
                merged.append(vehicle)
        
        return merged
        
    def _sort_vehicles(self, vehicles: List, sort_by: str, query: Optional[str] = None) -> List:
        """Sort vehicles by specified criteria"""
        def get_sort_key(vehicle):
            if isinstance(vehicle, dict):
                if sort_by == 'price_asc':
                    return vehicle.get('price') or float('inf')
                elif sort_by == 'price_desc':
                    return -(vehicle.get('price') or 0)
                elif sort_by == 'mileage_asc':
                    return vehicle.get('mileage') or float('inf')
                elif sort_by == 'year_desc':
                    return -(vehicle.get('year') or 0)
                elif sort_by == 'relevance' and query:
                    return self._calculate_relevance_score(vehicle, query)
                else:
                    return 0
            else:
                # SQLAlchemy object
                if sort_by == 'price_asc':
                    return vehicle.price or float('inf')
                elif sort_by == 'price_desc':
                    return -(vehicle.price or 0)
                elif sort_by == 'mileage_asc':
                    return vehicle.mileage or float('inf')
                elif sort_by == 'year_desc':
                    return -(vehicle.year or 0)
                elif sort_by == 'relevance' and query:
                    return self._calculate_relevance_score(vehicle.__dict__, query)
                else:
                    return 0
        
        return sorted(vehicles, key=get_sort_key, reverse=(sort_by == 'relevance'))
        
    def _calculate_relevance_score(self, vehicle: Dict, query: str) -> float:
        """Calculate relevance score for sorting"""
        score = 0
        query_lower = query.lower()
        
        # Check make
        make = vehicle.get('make', '')
        if make and query_lower in make.lower():
            score += 50
        
        # Check model
        model = vehicle.get('model', '')
        if model and query_lower in model.lower():
            score += 30
            
        # Check title
        title = vehicle.get('title', '')
        if title and query_lower in title.lower():
            score += 20
            
        # Prefer newer vehicles
        year = vehicle.get('year', 0)
        if year:
            score += (year - 2000) / 10
            
        # Prefer lower mileage
        mileage = vehicle.get('mileage', 0)
        if mileage:
            score -= mileage / 100000
            
        return score
        
    def _needs_fresh_data(self, query: Optional[str], filters: Optional[Dict]) -> bool:
        """Determine if we need fresh data for this search"""
        # Always get fresh data for specific searches
        if filters and any(filters.get(k) for k in ['make', 'model', 'year_min', 'year_max']):
            return True
            
        # For general queries, check cache age
        cache_key = f"search_freshness:{query or 'all'}"
        last_update = self.cache_manager.get(cache_key)
        
        if not last_update:
            self.cache_manager.set(cache_key, datetime.utcnow().isoformat(), ttl=3600)
            return True
            
        # Check if data is stale
        last_update_time = datetime.fromisoformat(last_update)
        age_hours = (datetime.utcnow() - last_update_time).total_seconds() / 3600
        
        return age_hours > self.data_freshness_hours
        
    def _store_new_vehicles_async(self, vehicles: List[Dict]):
        """Store new vehicles asynchronously without blocking"""
        # Run in a separate thread to avoid blocking
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(self._store_new_vehicles, vehicles)
        executor.shutdown(wait=False)
        
    def _store_new_vehicles(self, vehicles: List[Dict]):
        """Store new vehicles in database"""
        try:
            session = get_session()
            stored_count = 0
            
            for vehicle_data in vehicles:
                try:
                    # Check if vehicle already exists
                    existing = session.query(VehicleV2).filter_by(
                        listing_id=vehicle_data.get('listing_id'),
                        source=vehicle_data.get('source')
                    ).first()
                    
                    if not existing:
                        vehicle = VehicleV2(
                            listing_id=vehicle_data.get('listing_id'),
                            source=vehicle_data.get('source'),
                            make=vehicle_data.get('make'),
                            model=vehicle_data.get('model'),
                            year=vehicle_data.get('year'),
                            price=vehicle_data.get('price'),
                            mileage=vehicle_data.get('mileage'),
                            location=vehicle_data.get('location'),
                            title=vehicle_data.get('title'),
                            view_item_url=vehicle_data.get('view_item_url'),
                            image_urls=vehicle_data.get('image_urls', []),
                            raw_data=vehicle_data
                        )
                        session.add(vehicle)
                        stored_count += 1
                        
                except Exception as e:
                    logger.error(f"Error storing vehicle: {e}")
                    continue
            
            if stored_count > 0:
                session.commit()
                logger.info(f"Stored {stored_count} new vehicles")
                
        except Exception as e:
            logger.error(f"Error in store_new_vehicles: {e}")
        finally:
            session.close()