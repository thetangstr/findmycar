"""
Comprehensive multi-layer search engine for vehicles
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from sqlalchemy import or_, and_, func, text
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB

from database_v2 import VehicleV2, SavedSearch, SearchHistory
from nlp_search import NLPSearchParser
from vehicle_attribute_inference import VehicleAttributeInference

logger = logging.getLogger(__name__)


class ComprehensiveSearchEngine:
    """
    Multi-layer search engine with:
    1. Natural language processing
    2. Structured SQL filters
    3. JSONB attribute queries
    4. Full-text search
    5. Intelligent ranking
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
                'mileage_max': 80000,
                'features': ['backup_camera'],
                'description': 'Reliable first cars under $15k'
            },
            'off_road': {
                'drivetrain': ['4wd', 'awd'],
                'body_style': ['truck', 'suv'],
                'description': 'Off-road capable vehicles'
            },
            'sports_car': {
                'body_style': ['coupe', 'convertible'],
                'transmission': ['manual', 'dual-clutch'],
                'attributes': {'horsepower_min': 300},
                'description': 'High-performance sports cars'
            },
            'electric': {
                'fuel_type': 'electric',
                'description': 'All-electric vehicles'
            },
            'work_truck': {
                'body_style': 'truck',
                'features': ['tow_package'],
                'description': 'Work-ready pickup trucks'
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
        Comprehensive vehicle search with multiple filter layers
        
        Returns:
            {
                'vehicles': List[VehicleV2],
                'total': int,
                'page': int,
                'pages': int,
                'applied_filters': dict,
                'search_id': Optional[str]
            }
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
        
        # Layer 4: Apply JSONB attribute filters
        base_query = self._apply_jsonb_filters(base_query, all_filters)
        
        # Layer 5: Apply feature filters
        base_query = self._apply_feature_filters(base_query, all_filters)
        
        # Layer 6: Apply full-text search if query provided
        if query and not all_filters.get('skip_text_search'):
            base_query = self._apply_text_search(base_query, query)
        
        # Get total count before pagination
        total = base_query.count()
        
        # Apply sorting
        base_query = self._apply_sorting(base_query, sort_by, query)
        
        # Apply pagination
        offset = (page - 1) * per_page
        vehicles = base_query.offset(offset).limit(per_page).all()
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page
        
        # Save search history
        search_history = self._save_search_history(
            query=query,
            filters=all_filters,
            result_count=total,
            user_id=user_id
        )
        
        # Save search if requested
        saved_search_id = None
        if save_search and search_name:
            saved_search = self._save_search(
                name=search_name,
                query=query,
                filters=all_filters,
                user_id=user_id
            )
            saved_search_id = saved_search.id
        
        # Track search time
        search_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Search completed in {search_time:.2f}s, found {total} vehicles")
        
        return {
            'vehicles': vehicles,
            'total': total,
            'page': page,
            'pages': total_pages,
            'applied_filters': all_filters,
            'search_id': saved_search_id,
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
        
        # Colors
        if filters.get('exterior_color'):
            if isinstance(filters['exterior_color'], list):
                query = query.filter(VehicleV2.exterior_color.in_(filters['exterior_color']))
            else:
                query = query.filter(VehicleV2.exterior_color == filters['exterior_color'])
        
        # Color exclusion
        if filters.get('exclude_colors'):
            for color in filters['exclude_colors']:
                query = query.filter(
                    or_(
                        VehicleV2.exterior_color == None,
                        VehicleV2.exterior_color == '',
                        ~func.lower(VehicleV2.exterior_color).contains(color.lower())
                    )
                )
        
        # Interior color
        if filters.get('interior_color'):
            if isinstance(filters['interior_color'], list):
                query = query.filter(VehicleV2.interior_color.in_(filters['interior_color']))
            else:
                query = query.filter(VehicleV2.interior_color == filters['interior_color'])
        
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
        
        # Fuel type
        if filters.get('fuel_type'):
            if isinstance(filters['fuel_type'], list):
                query = query.filter(VehicleV2.fuel_type.in_(filters['fuel_type']))
            else:
                query = query.filter(VehicleV2.fuel_type == filters['fuel_type'])
        
        # Location
        if filters.get('zip_code'):
            query = query.filter(VehicleV2.zip_code == filters['zip_code'])
        elif filters.get('location'):
            query = query.filter(VehicleV2.location.contains(filters['location']))
        
        # Source
        if filters.get('source'):
            if isinstance(filters['source'], list):
                query = query.filter(VehicleV2.source.in_(filters['source']))
            else:
                query = query.filter(VehicleV2.source == filters['source'])
        
        return query
    
    def _apply_jsonb_filters(self, query, filters: Dict[str, Any]):
        """Apply filters on JSONB attributes"""
        
        # Extract attribute filters
        attribute_filters = filters.get('attributes', {})
        
        # MPG filters
        if filters.get('mpg_city_min') or attribute_filters.get('mpg_city_min'):
            min_mpg = filters.get('mpg_city_min') or attribute_filters.get('mpg_city_min')
            query = query.filter(
                VehicleV2.attributes['mpg_city'].astext.cast(Integer) >= min_mpg
            )
        
        if filters.get('mpg_highway_min') or attribute_filters.get('mpg_highway_min'):
            min_mpg = filters.get('mpg_highway_min') or attribute_filters.get('mpg_highway_min')
            query = query.filter(
                VehicleV2.attributes['mpg_highway'].astext.cast(Integer) >= min_mpg
            )
        
        if filters.get('mpg_combined_min') or attribute_filters.get('mpg_combined_min'):
            min_mpg = filters.get('mpg_combined_min') or attribute_filters.get('mpg_combined_min')
            query = query.filter(
                VehicleV2.attributes['mpg_combined'].astext.cast(Integer) >= min_mpg
            )
        
        # Electric range
        if filters.get('electric_range_min') or attribute_filters.get('electric_range_min'):
            min_range = filters.get('electric_range_min') or attribute_filters.get('electric_range_min')
            query = query.filter(
                VehicleV2.attributes['electric_range'].astext.cast(Integer) >= min_range
            )
        
        # Seating capacity
        if filters.get('seating_capacity_min') or attribute_filters.get('seating_capacity_min'):
            min_seats = filters.get('seating_capacity_min') or attribute_filters.get('seating_capacity_min')
            query = query.filter(
                VehicleV2.attributes['seating_capacity'].astext.cast(Integer) >= min_seats
            )
        
        # Cylinders
        if filters.get('cylinders'):
            query = query.filter(
                VehicleV2.attributes['cylinders'].astext.cast(Integer) == filters['cylinders']
            )
        
        # Horsepower
        if filters.get('horsepower_min') or attribute_filters.get('horsepower_min'):
            min_hp = filters.get('horsepower_min') or attribute_filters.get('horsepower_min')
            query = query.filter(
                VehicleV2.attributes['horsepower'].astext.cast(Integer) >= min_hp
            )
        
        # Doors
        if filters.get('doors'):
            query = query.filter(
                VehicleV2.attributes['doors'].astext.cast(Integer) == filters['doors']
            )
        
        # History filters
        if filters.get('clean_title_only'):
            query = query.filter(
                VehicleV2.history['clean_title'].astext == 'true'
            )
        
        if filters.get('no_accidents'):
            query = query.filter(
                or_(
                    VehicleV2.history['accident_reported'].astext == 'false',
                    VehicleV2.history['accident_reported'] == None
                )
            )
        
        if filters.get('one_owner_only'):
            query = query.filter(
                VehicleV2.history['previous_owners'].astext.cast(Integer) <= 1
            )
        
        # Certified pre-owned
        if filters.get('certified_only'):
            query = query.filter(
                VehicleV2.attributes['certified'].astext == 'true'
            )
        
        return query
    
    def _apply_feature_filters(self, query, filters: Dict[str, Any]):
        """Apply filters on JSONB features array"""
        
        required_features = filters.get('required_features', [])
        if not required_features:
            return query
        
        # PostgreSQL JSONB contains operator for arrays
        for feature in required_features:
            query = query.filter(
                VehicleV2.features.contains([feature])
            )
        
        return query
    
    def _apply_text_search(self, query, search_text: str):
        """Apply PostgreSQL full-text search"""
        
        # Convert search text to tsquery
        search_query = func.plainto_tsquery('english', search_text)
        
        # Search in multiple fields via search_vector
        query = query.filter(
            VehicleV2.search_vector.match(search_query)
        )
        
        return query
    
    def _apply_sorting(self, query, sort_by: str, search_text: Optional[str] = None):
        """Apply sorting to results"""
        
        if sort_by == 'relevance' and search_text:
            # Sort by text search relevance
            search_query = func.plainto_tsquery('english', search_text)
            query = query.order_by(
                func.ts_rank(VehicleV2.search_vector, search_query).desc()
            )
        elif sort_by == 'price_low':
            query = query.order_by(VehicleV2.price.asc())
        elif sort_by == 'price_high':
            query = query.order_by(VehicleV2.price.desc())
        elif sort_by == 'mileage_low':
            query = query.order_by(VehicleV2.mileage.asc())
        elif sort_by == 'year_new':
            query = query.order_by(VehicleV2.year.desc())
        elif sort_by == 'year_old':
            query = query.order_by(VehicleV2.year.asc())
        elif sort_by == 'recent':
            query = query.order_by(VehicleV2.created_at.desc())
        else:
            # Default: newest listings first
            query = query.order_by(VehicleV2.created_at.desc())
        
        return query
    
    def _save_search_history(self, query: Optional[str], filters: Dict[str, Any], 
                           result_count: int, user_id: Optional[str]) -> SearchHistory:
        """Save search to history for analytics"""
        
        search_history = SearchHistory(
            query=query,
            filters=filters,
            result_count=result_count,
            user_id=user_id
        )
        
        self.db.add(search_history)
        self.db.commit()
        
        return search_history
    
    def _save_search(self, name: str, query: Optional[str], filters: Dict[str, Any],
                    user_id: Optional[str]) -> SavedSearch:
        """Save a search for future use"""
        
        saved_search = SavedSearch(
            name=name,
            user_id=user_id,
            search_params={
                'query': query,
                'filters': filters
            }
        )
        
        self.db.add(saved_search)
        self.db.commit()
        
        return saved_search
    
    def get_saved_searches(self, user_id: str) -> List[SavedSearch]:
        """Get user's saved searches"""
        return self.db.query(SavedSearch).filter(
            SavedSearch.user_id == user_id
        ).order_by(SavedSearch.created_at.desc()).all()
    
    def run_saved_search(self, saved_search_id: int, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Run a saved search"""
        
        saved_search = self.db.query(SavedSearch).filter(
            SavedSearch.id == saved_search_id
        ).first()
        
        if not saved_search:
            raise ValueError("Saved search not found")
        
        # Update last run time
        saved_search.last_run_at = datetime.utcnow()
        self.db.commit()
        
        # Run the search
        params = saved_search.search_params
        return self.search(
            query=params.get('query'),
            filters=params.get('filters'),
            user_id=user_id
        )
    
    def get_search_suggestions(self, partial_query: str) -> List[Dict[str, Any]]:
        """Get search suggestions based on partial query"""
        
        suggestions = []
        
        # Suggest makes
        if len(partial_query) >= 2:
            makes = self.db.query(VehicleV2.make).distinct().filter(
                func.lower(VehicleV2.make).startswith(partial_query.lower())
            ).limit(5).all()
            
            for make in makes:
                suggestions.append({
                    'type': 'make',
                    'value': make[0],
                    'display': f"Make: {make[0].title()}"
                })
        
        # Suggest models if make is included
        parts = partial_query.split()
        if len(parts) >= 2:
            make_part = parts[0]
            model_part = ' '.join(parts[1:])
            
            models = self.db.query(VehicleV2.model).distinct().filter(
                func.lower(VehicleV2.make) == make_part.lower(),
                func.lower(VehicleV2.model).contains(model_part.lower())
            ).limit(5).all()
            
            for model in models:
                suggestions.append({
                    'type': 'model',
                    'value': f"{make_part} {model[0]}",
                    'display': f"{make_part.title()} {model[0].title()}"
                })
        
        # Suggest smart presets
        for preset_name, preset_data in self.smart_presets.items():
            if preset_name.replace('_', ' ').startswith(partial_query.lower()):
                suggestions.append({
                    'type': 'preset',
                    'value': f"preset:{preset_name}",
                    'display': preset_data['description']
                })
        
        return suggestions
    
    def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular searches from history"""
        
        # Get most common search queries
        popular = self.db.query(
            SearchHistory.query,
            func.count(SearchHistory.id).label('count')
        ).filter(
            SearchHistory.query != None
        ).group_by(
            SearchHistory.query
        ).order_by(
            func.count(SearchHistory.id).desc()
        ).limit(limit).all()
        
        return [
            {'query': query, 'count': count}
            for query, count in popular
        ]