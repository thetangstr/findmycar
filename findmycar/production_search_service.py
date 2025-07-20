#!/usr/bin/env python3
"""
Production search service that combines local database with live API data
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

from comprehensive_search_engine_sqlite import ComprehensiveSearchEngine
from ebay_live_client import EbayLiveClient
from database_v2_sqlite import VehicleV2, get_session
import json

logger = logging.getLogger(__name__)

class ProductionSearchService:
    """
    Production search service with hybrid local/live search capabilities
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.local_search = ComprehensiveSearchEngine(db_session)
        self.ebay_client = EbayLiveClient()
        
        # Configuration
        self.enable_live_search = True
        self.live_search_threshold = 50  # Min local results before skipping live search
        self.max_live_results = 100  # Max results to fetch from APIs
        self.data_freshness_hours = 24  # Consider data stale after this many hours
        
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
        Perform hybrid search combining local database and live API results
        """
        start_time = datetime.utcnow()
        
        # First, search local database
        local_results = self.local_search.search(
            query=query,
            filters=filters or {},
            preset=preset,
            sort_by=sort_by,
            page=1,  # Get all for merging
            per_page=1000,  # Get more for better merging
            user_id=user_id
        )
        
        all_vehicles = list(local_results['vehicles'])
        sources_used = ['local']
        live_count = 0
        
        # Determine if we need live search
        should_search_live = (
            include_live and 
            self.enable_live_search and
            (local_results['total'] < self.live_search_threshold or self._needs_fresh_data(query, filters))
        )
        
        if should_search_live:
            try:
                # Perform live search
                live_results = self._search_live_sources(query, filters, page, self.max_live_results)
                
                # Merge and deduplicate results
                all_vehicles = self._merge_results(all_vehicles, live_results['vehicles'])
                sources_used.extend(live_results['sources'])
                live_count = live_results['count']
                
                # Store new vehicles in database for future searches
                self._store_new_vehicles(live_results['vehicles'])
                
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
        
        # Enhance results with real-time data if available
        if self.enable_live_search:
            paginated_vehicles = self._enhance_with_live_data(paginated_vehicles)
        
        end_time = datetime.utcnow()
        search_time = (end_time - start_time).total_seconds()
        
        return {
            'vehicles': paginated_vehicles,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'sources_used': sources_used,
            'local_count': local_results['total'],
            'live_count': live_count,
            'search_time': search_time,
            'applied_filters': local_results.get('applied_filters', {}),
            'cached': False
        }
    
    def _needs_fresh_data(self, query: str, filters: Dict) -> bool:
        """Determine if we need fresh data based on search parameters"""
        # Always get fresh data for specific searches
        if filters and any(filters.get(key) for key in ['vin', 'listing_id']):
            return True
        
        # Check when we last fetched data for this search
        # (In production, this would check a search cache timestamp)
        return True
    
    def _search_live_sources(self, query: str, filters: Dict, page: int, limit: int) -> Dict:
        """Search all available live sources"""
        vehicles = []
        sources = []
        
        # Import additional clients
        from carmax_client import CarMaxClient
        from autotrader_client import AutotraderClient
        
        # Limit per source to avoid too many results
        per_source_limit = min(limit // 3, 20)  # Divide among sources
        
        # 1. eBay API (fastest)
        try:
            ebay_results = self.ebay_client.search_vehicles(
                query=query or "",
                make=filters.get('make'),
                model=filters.get('model'),
                year_min=filters.get('year_min'),
                year_max=filters.get('year_max'),
                price_min=filters.get('price_min'),
                price_max=filters.get('price_max'),
                mileage_max=filters.get('mileage_max'),
                page=page,
                per_page=per_source_limit
            )
            
            vehicles.extend(ebay_results['vehicles'])
            sources.append('ebay')
            
        except Exception as e:
            logger.error(f"eBay search error: {e}")
        
        # 2. CarMax scraping (if not too many results yet)
        if len(vehicles) < limit:
            try:
                carmax_client = CarMaxClient()
                carmax_vehicles = carmax_client.search_listings(
                    query=query,
                    filters=filters,
                    limit=per_source_limit
                )
                
                # Add source info
                for vehicle in carmax_vehicles:
                    vehicle['source'] = 'carmax'
                    vehicle['is_live'] = True
                    vehicles.append(vehicle)
                
                sources.append('carmax')
                carmax_client.close()
                
            except Exception as e:
                logger.error(f"CarMax search error: {e}")
        
        # 3. AutoTrader scraping (if still need more results)
        if len(vehicles) < limit:
            try:
                autotrader_client = AutotraderClient()
                autotrader_vehicles = autotrader_client.search_listings(
                    query=query,
                    filters=filters,
                    limit=per_source_limit
                )
                
                # Add source info
                for vehicle in autotrader_vehicles:
                    vehicle['source'] = 'autotrader'
                    vehicle['is_live'] = True
                    vehicles.append(vehicle)
                
                sources.append('autotrader')
                autotrader_client.close()
                
            except Exception as e:
                logger.error(f"AutoTrader search error: {e}")
        
        return {
            'vehicles': vehicles[:limit],  # Respect limit
            'sources': sources,
            'count': len(vehicles)
        }
    
    def _merge_results(self, local_vehicles: List, live_vehicles: List) -> List:
        """Merge and deduplicate local and live results"""
        # Create a map of existing vehicles by listing_id
        seen_listings = {v.listing_id for v in local_vehicles if hasattr(v, 'listing_id')}
        
        # Convert local SQLAlchemy objects to dicts
        merged = []
        for vehicle in local_vehicles:
            if hasattr(vehicle, '__dict__'):
                v_dict = {
                    'id': vehicle.id,
                    'listing_id': vehicle.listing_id,
                    'source': vehicle.source,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'year': vehicle.year,
                    'price': vehicle.price,
                    'mileage': vehicle.mileage,
                    'body_style': vehicle.body_style,
                    'exterior_color': vehicle.exterior_color,
                    'interior_color': vehicle.interior_color,
                    'transmission': vehicle.transmission,
                    'drivetrain': vehicle.drivetrain,
                    'fuel_type': vehicle.fuel_type,
                    'location': vehicle.location,
                    'title': vehicle.title,
                    'description': vehicle.description,
                    'view_item_url': vehicle.view_item_url,
                    'image_urls': vehicle.image_urls or [],
                    'attributes': vehicle.attributes or {},
                    'features': vehicle.features or [],
                    'created_at': vehicle.created_at,
                    'is_live': False
                }
                merged.append(v_dict)
            else:
                merged.append(vehicle)
        
        # Add new live vehicles
        for vehicle in live_vehicles:
            if vehicle.get('listing_id') not in seen_listings:
                vehicle['is_live'] = True
                vehicle['is_new'] = True
                merged.append(vehicle)
                seen_listings.add(vehicle.get('listing_id'))
        
        return merged
    
    def _sort_vehicles(self, vehicles: List[Dict], sort_by: str, query: str) -> List[Dict]:
        """Sort vehicles by specified criteria"""
        if sort_by == 'price_asc':
            return sorted(vehicles, key=lambda x: x.get('price') or float('inf'))
        elif sort_by == 'price_desc':
            return sorted(vehicles, key=lambda x: x.get('price') or 0, reverse=True)
        elif sort_by == 'mileage_asc':
            return sorted(vehicles, key=lambda x: x.get('mileage') or float('inf'))
        elif sort_by == 'year_desc':
            return sorted(vehicles, key=lambda x: x.get('year') or 0, reverse=True)
        elif sort_by == 'date_listed':
            return sorted(vehicles, key=lambda x: x.get('created_at') or '', reverse=True)
        else:  # relevance or default
            # Simple relevance: prioritize exact matches, then live results
            def relevance_score(vehicle):
                score = 0
                if query:
                    query_lower = query.lower()
                    # Exact make match
                    if vehicle.get('make', '').lower() == query_lower:
                        score += 100
                    # Make contains query
                    elif query_lower in vehicle.get('make', '').lower():
                        score += 50
                    # Model contains query
                    model = vehicle.get('model', '')
                    if model and query_lower in model.lower():
                        score += 30
                    # Title contains query
                    if query_lower in vehicle.get('title', '').lower():
                        score += 10
                
                # Prefer live results
                if vehicle.get('is_live'):
                    score += 20
                
                # Prefer complete listings
                if vehicle.get('price'):
                    score += 5
                if vehicle.get('mileage'):
                    score += 5
                if vehicle.get('image_urls'):
                    score += 5
                
                return score
            
            return sorted(vehicles, key=relevance_score, reverse=True)
    
    def _enhance_with_live_data(self, vehicles: List[Dict]) -> List[Dict]:
        """Enhance vehicles with live pricing or availability data"""
        # In production, this could:
        # 1. Check if stored listings are still available
        # 2. Update pricing for older listings
        # 3. Get additional details for popular listings
        
        # For now, just mark data freshness
        for vehicle in vehicles:
            if 'created_at' in vehicle and vehicle['created_at']:
                created = vehicle['created_at']
                if isinstance(created, str):
                    created = datetime.fromisoformat(created.replace('Z', '+00:00'))
                
                age_hours = (datetime.utcnow() - created).total_seconds() / 3600
                vehicle['data_age_hours'] = age_hours
                vehicle['is_fresh'] = age_hours < self.data_freshness_hours
        
        return vehicles
    
    def _store_new_vehicles(self, vehicles: List[Dict]):
        """Store new vehicles from live search in database"""
        stored_count = 0
        
        for vehicle_data in vehicles:
            try:
                # Check if already exists
                existing = self.db.query(VehicleV2).filter_by(
                    listing_id=vehicle_data.get('listing_id')
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in vehicle_data.items():
                        if hasattr(existing, key) and key not in ['id', 'created_at']:
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    existing.last_seen_at = datetime.utcnow()
                else:
                    # Create new record
                    vehicle = VehicleV2(
                        listing_id=vehicle_data.get('listing_id'),
                        source=vehicle_data.get('source', 'ebay'),
                        make=vehicle_data.get('make'),
                        model=vehicle_data.get('model'),
                        year=vehicle_data.get('year'),
                        price=vehicle_data.get('price'),
                        mileage=vehicle_data.get('mileage'),
                        body_style=vehicle_data.get('body_style'),
                        exterior_color=vehicle_data.get('exterior_color'),
                        interior_color=vehicle_data.get('interior_color'),
                        transmission=vehicle_data.get('transmission'),
                        drivetrain=vehicle_data.get('drivetrain'),
                        fuel_type=vehicle_data.get('fuel_type'),
                        location=vehicle_data.get('location'),
                        title=vehicle_data.get('title'),
                        description=vehicle_data.get('description'),
                        view_item_url=vehicle_data.get('view_item_url'),
                        image_urls=vehicle_data.get('image_urls', []),
                        attributes=vehicle_data.get('attributes', {}),
                        features=vehicle_data.get('features', []),
                        raw_data=vehicle_data,
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        last_seen_at=datetime.utcnow()
                    )
                    
                    # Generate search text for full-text search
                    search_parts = [
                        str(vehicle.year),
                        vehicle.make,
                        vehicle.model,
                        vehicle.body_style,
                        vehicle.title,
                        vehicle.description
                    ]
                    vehicle.search_text = ' '.join(filter(None, search_parts))
                    
                    self.db.add(vehicle)
                    stored_count += 1
                
                # Commit in batches
                if stored_count % 10 == 0:
                    self.db.commit()
                    
            except Exception as e:
                logger.error(f"Error storing vehicle {vehicle_data.get('listing_id')}: {e}")
                self.db.rollback()
        
        # Final commit
        try:
            self.db.commit()
            logger.info(f"Stored {stored_count} new vehicles from live search")
        except Exception as e:
            logger.error(f"Error committing vehicles: {e}")
            self.db.rollback()
    
    def get_vehicle_details(self, vehicle_id: int, fetch_live: bool = True) -> Optional[Dict]:
        """Get detailed vehicle information with optional live data fetch"""
        # Get from database
        vehicle = self.db.query(VehicleV2).filter_by(id=vehicle_id).first()
        
        if not vehicle:
            return None
        
        vehicle_dict = {
            'id': vehicle.id,
            'listing_id': vehicle.listing_id,
            'source': vehicle.source,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'price': vehicle.price,
            'mileage': vehicle.mileage,
            'body_style': vehicle.body_style,
            'exterior_color': vehicle.exterior_color,
            'interior_color': vehicle.interior_color,
            'transmission': vehicle.transmission,
            'drivetrain': vehicle.drivetrain,
            'fuel_type': vehicle.fuel_type,
            'location': vehicle.location,
            'title': vehicle.title,
            'description': vehicle.description,
            'view_item_url': vehicle.view_item_url,
            'image_urls': vehicle.image_urls or [],
            'attributes': vehicle.attributes or {},
            'features': vehicle.features or [],
            'history': vehicle.history or {},
            'created_at': vehicle.created_at,
            'updated_at': vehicle.updated_at
        }
        
        # Fetch live details if requested and source supports it
        if fetch_live and vehicle.source == 'ebay' and vehicle.listing_id:
            try:
                live_details = self.ebay_client.get_vehicle_details(vehicle.listing_id)
                if live_details:
                    # Merge live details
                    vehicle_dict.update({
                        'live_price': live_details.get('price'),
                        'live_available': True,
                        'live_updated': datetime.utcnow().isoformat()
                    })
                    
                    # Update database with fresh data
                    vehicle.price = live_details.get('price', vehicle.price)
                    vehicle.last_seen_at = datetime.utcnow()
                    self.db.commit()
            except Exception as e:
                logger.error(f"Error fetching live details: {e}")
                vehicle_dict['live_available'] = False
        
        return vehicle_dict