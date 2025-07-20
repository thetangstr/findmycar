#!/usr/bin/env python3
"""
Enhanced production search service with 16 vehicle sources
Uses the unified source manager for comprehensive vehicle search
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
import os

from comprehensive_search_engine_sqlite_fixed import ComprehensiveSearchEngine
from unified_source_manager import UnifiedSourceManager
from database_v2_sqlite import VehicleV2, get_session
from cache_manager import CacheManager

logger = logging.getLogger(__name__)

class EnhancedProductionSearchService:
    """
    Production search service with support for 16+ vehicle sources
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.local_search = ComprehensiveSearchEngine(db_session)
        self.cache_manager = CacheManager()
        
        # Initialize unified source manager with all sources
        self.source_manager = UnifiedSourceManager(cache_manager=self.cache_manager)
        
        # Configuration
        self.enable_live_search = True
        self.live_search_threshold = 50  # Min local results before skipping live search
        self.max_live_results = 100
        self.data_freshness_hours = 24
        
        # Configure which sources to use based on environment
        self._configure_sources()
        
        logger.info(f"Initialized with {len(self.source_manager.get_enabled_sources())} active sources")
    
    def _configure_sources(self):
        """
        Configure which sources are enabled based on environment and settings
        """
        # Enable/disable sources based on environment
        if os.environ.get('ENABLE_ALL_SOURCES', 'false').lower() == 'true':
            # Enable all available sources
            for source in self.source_manager.source_config:
                self.source_manager.enable_source(source)
        else:
            # Default configuration - enable only stable sources
            stable_sources = [
                'ebay',        # API - stable
                'hemmings',    # RSS - works
                'cars_bids',   # API - works
                'craigslist',  # RSS - works
                'carsoup',     # Simple scrape - works
                'revy_autos',  # API - works
                'carmax',      # Scrape - sometimes works
                'autotrader'   # Scrape - sometimes works
            ]
            
            # Disable all first
            for source in self.source_manager.source_config:
                self.source_manager.disable_source(source)
            
            # Enable stable sources
            for source in stable_sources:
                self.source_manager.enable_source(source)
            
            # Disable problematic sources unless explicitly enabled
            if os.environ.get('ENABLE_RISKY_SOURCES', 'false').lower() != 'true':
                self.source_manager.disable_source('cargurus')
                self.source_manager.disable_source('truecar')
    
    def search(self, query: str = "", filters: Optional[Dict] = None, 
               page: int = 1, per_page: int = 20) -> Dict:
        """
        Comprehensive search across local database and all enabled live sources
        """
        try:
            filters = filters or {}
            start_time = datetime.now()
            
            # Extract filters
            make = filters.get('make')
            model = filters.get('model')
            year_min = filters.get('year_min')
            year_max = filters.get('year_max')
            price_min = filters.get('price_min')
            price_max = filters.get('price_max')
            mileage_max = filters.get('mileage_max')
            
            # Phase 1: Search local database
            local_results = self._search_local(query, filters, page, per_page)
            
            # Phase 2: Search live sources if enabled
            live_results = {'vehicles': [], 'sources_searched': [], 'sources_failed': []}
            if self.enable_live_search:
                # Determine if we need live search
                need_live_search = (
                    local_results['total'] < self.live_search_threshold or
                    self._is_data_stale(local_results['vehicles'])
                )
                
                if need_live_search:
                    live_results = self._search_live_sources(
                        query, make, model, year_min, year_max,
                        price_min, price_max, mileage_max, page, per_page
                    )
            
            # Phase 3: Merge and deduplicate results
            all_vehicles = self._merge_results(
                local_results['vehicles'],
                live_results['vehicles']
            )
            
            # Apply relevance scoring
            scored_vehicles = self._score_and_sort_vehicles(all_vehicles, query, filters)
            
            # Apply pagination on merged results
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_vehicles = scored_vehicles[start_idx:end_idx]
            
            # Calculate search time
            search_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'vehicles': paginated_vehicles,
                'total': len(scored_vehicles),
                'page': page,
                'per_page': per_page,
                'local_count': local_results['total'],
                'live_count': len(live_results['vehicles']),
                'sources_searched': live_results.get('sources_searched', []),
                'sources_failed': live_results.get('sources_failed', []),
                'source_details': live_results.get('source_details', {}),
                'search_time': search_time,
                'data_sources': {
                    'local': local_results['total'] > 0,
                    'live': len(live_results['vehicles']) > 0
                }
            }
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}", exc_info=True)
            return {
                'vehicles': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'error': str(e)
            }
    
    def _search_local(self, query: str, filters: Dict, page: int, per_page: int) -> Dict:
        """
        Search local database
        """
        try:
            result = self.local_search.search(query, filters, page, per_page * 2)
            
            # Convert ORM objects to dicts if needed
            if result.get('vehicles') and len(result['vehicles']) > 0 and hasattr(result['vehicles'][0], '__dict__'):
                vehicles_as_dicts = []
                for vehicle in result['vehicles']:
                    v_dict = {
                        'id': vehicle.id,
                        'title': vehicle.title,
                        'price': vehicle.price,
                        'year': vehicle.year,
                        'make': vehicle.make,
                        'model': vehicle.model,
                        'mileage': vehicle.mileage,
                        'location': vehicle.location,
                        'link': vehicle.view_item_url,
                        'image': vehicle.image_urls[0] if vehicle.image_urls else None,
                        'description': vehicle.description,
                        'source': vehicle.source,
                        'condition': getattr(vehicle, 'condition', 'Used'),
                        'created_date': vehicle.created_at.isoformat() if vehicle.created_at else None,
                        'vin': getattr(vehicle, 'vin', None),
                        'exterior_color': getattr(vehicle, 'exterior_color', None),
                        'interior_color': getattr(vehicle, 'interior_color', None),
                        'transmission': getattr(vehicle, 'transmission', None),
                        'drivetrain': getattr(vehicle, 'drivetrain', None),
                        'body_style': getattr(vehicle, 'body_style', None),
                    }
                    vehicles_as_dicts.append(v_dict)
                result['vehicles'] = vehicles_as_dicts
            
            return result
        except Exception as e:
            logger.error(f"Local search error: {str(e)}")
            return {'vehicles': [], 'total': 0}
    
    def _search_live_sources(self, query: str, make: Optional[str], model: Optional[str],
                           year_min: Optional[int], year_max: Optional[int],
                           price_min: Optional[float], price_max: Optional[float],
                           mileage_max: Optional[int], page: int, per_page: int) -> Dict:
        """
        Search all enabled live sources using the unified manager
        """
        try:
            # Use unified source manager to search all sources
            result = self.source_manager.search_all_sources(
                query=query,
                make=make,
                model=model,
                year_min=year_min,
                year_max=year_max,
                price_min=price_min,
                price_max=price_max,
                mileage_max=mileage_max,
                page=1,  # Always get first page from live sources
                per_page=self.max_live_results
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Live search error: {str(e)}")
            return {
                'vehicles': [],
                'sources_searched': [],
                'sources_failed': list(self.source_manager.get_enabled_sources()),
                'source_details': {}
            }
    
    def _merge_results(self, local_vehicles: List[Dict], live_vehicles: List[Dict]) -> List[Dict]:
        """
        Merge and deduplicate results from local and live sources
        """
        # Use the source manager's deduplication logic
        return self.source_manager._merge_and_dedupe_results([
            {'vehicles': local_vehicles},
            {'vehicles': live_vehicles}
        ])
    
    def _score_and_sort_vehicles(self, vehicles: List[Dict], query: str, filters: Dict) -> List[Dict]:
        """
        Apply relevance scoring and sort vehicles
        """
        query_lower = query.lower() if query else ""
        
        for vehicle in vehicles:
            score = 0
            
            # Title match
            title = (vehicle.get('title') or '').lower()
            if query_lower and query_lower in title:
                score += 10
            
            # Exact make/model match
            if filters.get('make') and vehicle.get('make'):
                if filters['make'].lower() == vehicle['make'].lower():
                    score += 5
            
            if filters.get('model') and vehicle.get('model'):
                if filters['model'].lower() in vehicle['model'].lower():
                    score += 5
            
            # Data completeness
            if vehicle.get('price'):
                score += 2
            if vehicle.get('mileage'):
                score += 2
            if vehicle.get('image'):
                score += 1
            if vehicle.get('location'):
                score += 1
            
            # Source quality bonus
            source = vehicle.get('source', '')
            if source in ['ebay', 'cars_bids', 'carvana']:
                score += 3  # API sources get bonus
            elif source in ['hemmings', 'craigslist']:
                score += 2  # RSS sources
            
            # Freshness bonus
            created_date = vehicle.get('created_date', '')
            if created_date:
                try:
                    created_dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    days_old = (datetime.now(created_dt.tzinfo) - created_dt).days
                    if days_old <= 1:
                        score += 5
                    elif days_old <= 7:
                        score += 3
                    elif days_old <= 30:
                        score += 1
                except:
                    pass
            
            vehicle['relevance_score'] = score
        
        # Sort by relevance score (descending) and then by date
        vehicles.sort(key=lambda x: (
            -x.get('relevance_score', 0),
            x.get('created_date', '')
        ), reverse=True)
        
        return vehicles
    
    def _is_data_stale(self, vehicles: List[Dict]) -> bool:
        """
        Check if local data is stale
        """
        if not vehicles:
            return True
        
        # Check the age of the most recent vehicle
        latest_date = None
        for vehicle in vehicles[:10]:  # Check first 10
            # Handle both dict and ORM objects
            if hasattr(vehicle, 'created_at'):
                created_date = vehicle.created_at
            else:
                created_date = vehicle.get('created_date')
            if created_date:
                try:
                    if isinstance(created_date, str):
                        dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    else:
                        dt = created_date  # Already a datetime object
                    if not latest_date or dt > latest_date:
                        latest_date = dt
                except:
                    continue
        
        if not latest_date:
            return True
        
        # Data is stale if older than configured hours
        from datetime import timezone
        now = datetime.now(timezone.utc) if latest_date.tzinfo else datetime.now()
        age_hours = (now - latest_date).total_seconds() / 3600
        return age_hours > self.data_freshness_hours
    
    def get_vehicle_details(self, vehicle_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific vehicle
        """
        # First check local database
        local_vehicle = self.local_search.get_vehicle_by_id(vehicle_id)
        if local_vehicle:
            return local_vehicle
        
        # Then check each source
        for source_name, client in self.source_manager.sources.items():
            if hasattr(client, 'get_vehicle_details'):
                try:
                    vehicle = client.get_vehicle_details(vehicle_id)
                    if vehicle:
                        return vehicle
                except Exception as e:
                    logger.error(f"Error getting vehicle details from {source_name}: {e}")
        
        return None
    
    def get_source_stats(self) -> Dict:
        """
        Get statistics about available sources
        """
        stats = self.source_manager.get_source_stats()
        
        # Add health check results
        health_results = self.source_manager.check_all_sources_health()
        stats['health_status'] = health_results
        
        return stats