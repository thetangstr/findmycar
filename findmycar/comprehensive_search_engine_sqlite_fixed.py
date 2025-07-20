"""
Comprehensive multi-layer search engine for vehicles (SQLite compatible) - FIXED VERSION
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from sqlalchemy import or_, and_, func, text, cast, String
from sqlalchemy.orm import Session

from database_v2_sqlite import VehicleV2, SavedSearch, SearchHistory
from nlp_search_wrapper import NLPSearchParser
from vehicle_attribute_inference import VehicleAttributeInferencer as VehicleAttributeInference

logger = logging.getLogger(__name__)


class ComprehensiveSearchEngine:
    """
    Multi-layer search engine with SQLite compatibility - FIXED
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.nlp_parser = NLPSearchParser()
        self.inference_engine = VehicleAttributeInference()
        
        # Search presets
        self.smart_presets = {
            'family_suv': {
                'body_style': 'suv',
                'attributes': {'seating_capacity_min': 7},
                'features': ['backup_camera', 'third_row'],
                'description': 'Family-friendly SUVs with 3rd row seating'
            },
            'fuel_efficient': {
                'attributes': {'mpg_combined_min': 30},
                'fuel_type': ['hybrid', 'electric', 'plug-in hybrid'],
                'description': 'Fuel-efficient vehicles (30+ MPG)'
            },
            'luxury': {
                'make': ['mercedes-benz', 'bmw', 'audi', 'lexus', 'porsche', 'jaguar'],
                'features': ['leather_seats', 'navigation', 'premium_audio'],
                'description': 'Luxury vehicles with premium features'
            },
            'first_car': {
                'price_max': 15000,
                'year_min': datetime.now().year - 10,
                'mileage_max': 100000,
                'description': 'Affordable, reliable vehicles for first-time buyers'
            },
            'off_road': {
                'body_style': ['truck', 'suv'],
                'drivetrain': ['4wd', 'awd'],
                'description': 'Off-road capable vehicles'
            },
            'electric': {
                'fuel_type': 'electric',
                'description': 'All-electric vehicles'
            }
        }
    
    def search(self, 
               query: Optional[str] = None,
               filters: Optional[Dict[str, Any]] = None,
               preset: Optional[str] = None,
               sort_by: str = 'relevance',
               page: int = 1,
               per_page: int = 20,
               user_id: Optional[str] = None,
               save_search: bool = False,
               search_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive vehicle search with multiple filter layers (SQLite compatible)
        """
        # Track search time
        start_time = datetime.utcnow()
        
        # Initialize filters
        all_filters = filters or {}
        
        # Layer 1: Apply smart preset if specified
        if preset and preset in self.smart_presets:
            preset_filters = self._apply_preset(preset)
            all_filters = {**preset_filters, **all_filters}  # User filters override preset
        
        # Layer 2: Parse natural language query
        if query:
            nlp_filters = self.nlp_parser.parse_natural_language_query(query)
            # Merge with existing filters (NLP has lower priority)
            for key, value in nlp_filters.items():
                if key not in all_filters:
                    all_filters[key] = value
        
        # Build the query
        base_query = self.db.query(VehicleV2).filter(VehicleV2.is_active == True)
        
        # Layer 3: Apply structured SQL filters
        base_query = self._apply_sql_filters(base_query, all_filters)
        
        # Layer 4: Apply JSON attribute filters (SQLite compatible)
        base_query = self._apply_json_filters_sqlite(base_query, all_filters)
        
        # Layer 5: Apply feature filters (SQLite compatible)
        base_query = self._apply_feature_filters_sqlite(base_query, all_filters)
        
        # Layer 6: Apply text search if query provided (SQLite compatible)
        # FIXED: Skip text search if we have meaningful structured filters
        if query and not all_filters.get('skip_text_search'):
            # Check if query was fully parsed into structured filters
            has_structured_filters = any([
                all_filters.get('make'),
                all_filters.get('model'),
                all_filters.get('body_style'),
                all_filters.get('price_min'),
                all_filters.get('price_max'),
                all_filters.get('year_min'),
                all_filters.get('year_max'),
                all_filters.get('mileage_max'),
                all_filters.get('fuel_type')
            ])
            
            # Only apply text search if we don't have structured filters
            # or if the query contains additional terms
            if not has_structured_filters:
                base_query = self._apply_text_search_sqlite(base_query, query)
        
        # Get total count before pagination
        total = base_query.count()
        
        # Apply sorting
        base_query = self._apply_sorting(base_query, sort_by, query)
        
        # Apply pagination
        offset = (page - 1) * per_page
        vehicles = base_query.limit(per_page).offset(offset).all()
        
        # Track search history if user_id provided
        if user_id:
            self._track_search_history(user_id, query, all_filters, total)
        
        # Save search if requested
        if save_search and user_id:
            self._save_search(user_id, query, all_filters, search_name)
        
        # Calculate search time
        search_time = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            'vehicles': vehicles,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'applied_filters': all_filters,
            'search_time': search_time
        }
    
    def _apply_preset(self, preset_name: str) -> Dict[str, Any]:
        """Apply a smart preset and return filters"""
        preset = self.smart_presets.get(preset_name, {})
        filters = {}
        
        # Copy all preset filters except description
        for key, value in preset.items():
            if key != 'description':
                filters[key] = value
        
        return filters
    
    def _apply_sql_filters(self, query, filters: Dict[str, Any]):
        """Apply filters on core SQL columns"""
        
        # Make filter
        if filters.get('make'):
            if isinstance(filters['make'], list):
                query = query.filter(VehicleV2.make.in_([m.lower() for m in filters['make']]))
            else:
                query = query.filter(func.lower(VehicleV2.make) == filters['make'].lower())
        
        # Model filter
        if filters.get('model'):
            if isinstance(filters['model'], list):
                query = query.filter(VehicleV2.model.in_([m.lower() for m in filters['model']]))
            else:
                query = query.filter(func.lower(VehicleV2.model).contains(filters['model'].lower()))
        
        # Year range
        if filters.get('year_min'):
            query = query.filter(VehicleV2.year >= filters['year_min'])
        if filters.get('year_max'):
            query = query.filter(VehicleV2.year <= filters['year_max'])
        
        # Price range
        if filters.get('price_min'):
            query = query.filter(VehicleV2.price >= filters['price_min'])
        if filters.get('price_max'):
            query = query.filter(VehicleV2.price <= filters['price_max'])
        
        # Mileage range
        if filters.get('mileage_min'):
            query = query.filter(VehicleV2.mileage >= filters['mileage_min'])
        if filters.get('mileage_max'):
            query = query.filter(VehicleV2.mileage <= filters['mileage_max'])
        
        # Body style
        if filters.get('body_style'):
            if isinstance(filters['body_style'], list):
                query = query.filter(VehicleV2.body_style.in_(filters['body_style']))
            else:
                query = query.filter(VehicleV2.body_style == filters['body_style'])
        
        # Fuel type
        if filters.get('fuel_type'):
            if isinstance(filters['fuel_type'], list):
                query = query.filter(VehicleV2.fuel_type.in_(filters['fuel_type']))
            else:
                query = query.filter(VehicleV2.fuel_type == filters['fuel_type'])
        
        # Transmission
        if filters.get('transmission'):
            if isinstance(filters['transmission'], list):
                query = query.filter(VehicleV2.transmission.in_(filters['transmission']))
            else:
                query = query.filter(VehicleV2.transmission == filters['transmission'])
        
        # Drivetrain
        if filters.get('drivetrain'):
            if isinstance(filters['drivetrain'], list):
                query = query.filter(VehicleV2.drivetrain.in_(filters['drivetrain']))
            else:
                query = query.filter(VehicleV2.drivetrain == filters['drivetrain'])
        
        # Exterior color
        if filters.get('exterior_color'):
            query = query.filter(func.lower(VehicleV2.exterior_color) == filters['exterior_color'].lower())
        
        # Exclude colors
        if filters.get('exclude_colors'):
            for color in filters['exclude_colors']:
                query = query.filter(
                    or_(
                        VehicleV2.exterior_color == None,
                        func.lower(VehicleV2.exterior_color) != color.lower()
                    )
                )
        
        # Location/Zip
        if filters.get('zip_code'):
            query = query.filter(VehicleV2.zip_code == filters['zip_code'])
        elif filters.get('location'):
            query = query.filter(VehicleV2.location.contains(filters['location']))
        
        # Source filter
        if filters.get('sources'):
            if isinstance(filters['sources'], list):
                query = query.filter(VehicleV2.source.in_(filters['sources']))
            else:
                query = query.filter(VehicleV2.source == filters['sources'])
        
        return query
    
    def _apply_json_filters_sqlite(self, query, filters: Dict[str, Any]):
        """Apply filters on JSON attributes (SQLite compatible)"""
        
        attributes = filters.get('attributes', {})
        
        # MPG filters
        if attributes.get('mpg_city_min'):
            query = query.filter(
                cast(func.json_extract(VehicleV2.attributes, '$.mpg_city'), String).cast(Integer) >= attributes['mpg_city_min']
            )
        
        if attributes.get('mpg_highway_min'):
            query = query.filter(
                cast(func.json_extract(VehicleV2.attributes, '$.mpg_highway'), String).cast(Integer) >= attributes['mpg_highway_min']
            )
        
        if attributes.get('mpg_combined_min'):
            query = query.filter(
                cast(func.json_extract(VehicleV2.attributes, '$.mpg_combined'), String).cast(Integer) >= attributes['mpg_combined_min']
            )
        
        # Seating capacity
        if attributes.get('seating_capacity_min'):
            query = query.filter(
                cast(func.json_extract(VehicleV2.attributes, '$.seating_capacity'), String).cast(Integer) >= attributes['seating_capacity_min']
            )
        
        if attributes.get('seating_capacity_max'):
            query = query.filter(
                cast(func.json_extract(VehicleV2.attributes, '$.seating_capacity'), String).cast(Integer) <= attributes['seating_capacity_max']
            )
        
        # Number of doors
        if attributes.get('doors'):
            query = query.filter(
                func.json_extract(VehicleV2.attributes, '$.doors') == str(attributes['doors'])
            )
        
        return query
    
    def _apply_feature_filters_sqlite(self, query, filters: Dict[str, Any]):
        """Apply feature filters using JSON functions (SQLite compatible)"""
        
        if filters.get('features'):
            for feature in filters['features']:
                # Check if feature exists in the JSON array
                query = query.filter(
                    func.json_extract(VehicleV2.features, '$') != None
                ).filter(
                    func.json_extract(VehicleV2.features, '$').contains(f'"{feature}"')
                )
        
        return query
    
    def _apply_text_search_sqlite(self, query, search_text: str):
        """Apply text search across multiple fields (SQLite compatible)"""
        search_pattern = f"%{search_text}%"
        
        return query.filter(
            or_(
                VehicleV2.title.ilike(search_pattern),
                VehicleV2.description.ilike(search_pattern),
                VehicleV2.make.ilike(search_pattern),
                VehicleV2.model.ilike(search_pattern),
                VehicleV2.search_text.ilike(search_pattern)
            )
        )
    
    def _apply_sorting(self, query, sort_by: str, search_query: Optional[str] = None):
        """Apply sorting to the query"""
        
        if sort_by == 'price_asc':
            return query.order_by(VehicleV2.price.asc().nullslast())
        elif sort_by == 'price_desc':
            return query.order_by(VehicleV2.price.desc().nullsfirst())
        elif sort_by == 'year_desc':
            return query.order_by(VehicleV2.year.desc().nullsfirst())
        elif sort_by == 'year_asc':
            return query.order_by(VehicleV2.year.asc().nullslast())
        elif sort_by == 'mileage_asc':
            return query.order_by(VehicleV2.mileage.asc().nullslast())
        elif sort_by == 'mileage_desc':
            return query.order_by(VehicleV2.mileage.desc().nullsfirst())
        elif sort_by == 'newest':
            return query.order_by(VehicleV2.created_at.desc())
        elif sort_by == 'relevance' and search_query:
            # For relevance sorting, prioritize exact matches
            # This is simplified for SQLite
            return query.order_by(VehicleV2.created_at.desc())
        else:
            # Default sorting
            return query.order_by(VehicleV2.created_at.desc())
    
    def _track_search_history(self, user_id: str, query: Optional[str], filters: Dict[str, Any], result_count: int):
        """Track search history for personalization"""
        try:
            history = SearchHistory(
                user_id=user_id,
                query=query,
                filters=json.dumps(filters),
                result_count=result_count,
                created_at=datetime.utcnow()
            )
            self.db.add(history)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error tracking search history: {e}")
            self.db.rollback()
    
    def _save_search(self, user_id: str, query: Optional[str], filters: Dict[str, Any], name: Optional[str] = None):
        """Save a search for later use"""
        try:
            saved = SavedSearch(
                user_id=user_id,
                name=name or f"Search: {query or 'Custom filters'}",
                query=query,
                filters=json.dumps(filters),
                created_at=datetime.utcnow()
            )
            self.db.add(saved)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error saving search: {e}")
            self.db.rollback()
    
    def get_saved_searches(self, user_id: str) -> List[SavedSearch]:
        """Get user's saved searches"""
        return self.db.query(SavedSearch).filter(
            SavedSearch.user_id == user_id
        ).order_by(SavedSearch.created_at.desc()).all()
    
    def get_search_suggestions(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get search suggestions based on history and popular searches"""
        suggestions = {
            'popular_makes': [],
            'popular_models': [],
            'recent_searches': [],
            'recommended_filters': {}
        }
        
        # Get popular makes
        popular_makes = self.db.query(
            VehicleV2.make,
            func.count(VehicleV2.id).label('count')
        ).filter(
            VehicleV2.make != None
        ).group_by(
            VehicleV2.make
        ).order_by(
            func.count(VehicleV2.id).desc()
        ).limit(10).all()
        
        suggestions['popular_makes'] = [
            {'make': make, 'count': count}
            for make, count in popular_makes
        ]
        
        # Get user's recent searches if user_id provided
        if user_id:
            recent = self.db.query(SearchHistory).filter(
                SearchHistory.user_id == user_id
            ).order_by(
                SearchHistory.created_at.desc()
            ).limit(5).all()
            
            suggestions['recent_searches'] = [
                {
                    'query': search.query,
                    'filters': json.loads(search.filters) if search.filters else {},
                    'result_count': search.result_count,
                    'timestamp': search.created_at.isoformat()
                }
                for search in recent
            ]
        
        return suggestions