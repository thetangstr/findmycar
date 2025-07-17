"""
Enhanced Search Module for CarGPT
Provides advanced search capabilities with filtering, sorting, and recommendations
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, case, desc, asc
from database import Vehicle, UserSession
from nlp_search import parse_natural_language_query, enhance_query_with_use_case
from cache import cache
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class EnhancedSearchEngine:
    """Enhanced search engine with advanced filtering and AI-powered recommendations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache_timeout = 1800  # 30 minutes
        
    def search_vehicles(self, 
                       query: str, 
                       filters: Dict[str, Any] = None, 
                       sort_by: str = 'relevance',
                       page: int = 1,
                       per_page: int = 20) -> Dict[str, Any]:
        """
        Perform enhanced vehicle search with advanced filtering and sorting
        
        Args:
            query: Natural language search query
            filters: Dictionary of filter parameters
            sort_by: Sorting method ('relevance', 'price_low', 'price_high', etc.)
            page: Page number for pagination
            per_page: Results per page
            
        Returns:
            Dictionary containing search results and metadata
        """
        try:
            # Parse natural language query
            parsed_query = parse_natural_language_query(query)
            
            # Build base query
            base_query = self._build_base_query(parsed_query, filters)
            
            # Apply sorting
            sorted_query = self._apply_sorting(base_query, sort_by)
            
            # Get total count
            total_count = base_query.count()
            
            # Apply pagination
            offset = (page - 1) * per_page
            vehicles = sorted_query.offset(offset).limit(per_page).all()
            
            # Generate search insights
            insights = self._generate_search_insights(vehicles, parsed_query, filters)
            
            # Get related searches
            related_searches = self._get_related_searches(query, parsed_query)
            
            return {
                'vehicles': vehicles,
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': (total_count + per_page - 1) // per_page,
                'insights': insights,
                'related_searches': related_searches,
                'applied_filters': filters or {},
                'sort_by': sort_by,
                'query': query,
                'parsed_query': parsed_query
            }
            
        except Exception as e:
            logger.error(f"Enhanced search error: {e}")
            return {
                'vehicles': [],
                'total_count': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0,
                'insights': {},
                'related_searches': [],
                'applied_filters': filters or {},
                'sort_by': sort_by,
                'query': query,
                'error': str(e)
            }
    
    def _build_base_query(self, parsed_query: Dict, filters: Dict[str, Any] = None):
        """Build base SQL query with filters"""
        query = self.db.query(Vehicle)
        
        # Apply parsed query filters
        if parsed_query.get('make'):
            query = query.filter(Vehicle.make.ilike(f"%{parsed_query['make']}%"))
        
        if parsed_query.get('model'):
            query = query.filter(Vehicle.model.ilike(f"%{parsed_query['model']}%"))
        
        if parsed_query.get('year_min'):
            query = query.filter(Vehicle.year >= parsed_query['year_min'])
        
        if parsed_query.get('year_max'):
            query = query.filter(Vehicle.year <= parsed_query['year_max'])
        
        if parsed_query.get('price_min'):
            query = query.filter(Vehicle.price >= parsed_query['price_min'])
        
        if parsed_query.get('price_max'):
            query = query.filter(Vehicle.price <= parsed_query['price_max'])
        
        if parsed_query.get('mileage_max'):
            query = query.filter(Vehicle.mileage <= parsed_query['mileage_max'])
        
        if parsed_query.get('body_style'):
            query = query.filter(Vehicle.body_style.ilike(f"%{parsed_query['body_style']}%"))
        
        if parsed_query.get('fuel_type'):
            query = query.filter(Vehicle.fuel_type.ilike(f"%{parsed_query['fuel_type']}%"))
        
        # Apply additional filters
        if filters:
            if filters.get('make'):
                query = query.filter(Vehicle.make.ilike(f"%{filters['make']}%"))
            
            if filters.get('model'):
                query = query.filter(Vehicle.model.ilike(f"%{filters['model']}%"))
            
            if filters.get('body_style'):
                query = query.filter(Vehicle.body_style.ilike(f"%{filters['body_style']}%"))
            
            if filters.get('fuel_type'):
                query = query.filter(Vehicle.fuel_type.ilike(f"%{filters['fuel_type']}%"))
            
            if filters.get('transmission'):
                query = query.filter(Vehicle.transmission.ilike(f"%{filters['transmission']}%"))
            
            if filters.get('color'):
                query = query.filter(Vehicle.color.ilike(f"%{filters['color']}%"))
            
            if filters.get('condition'):
                query = query.filter(Vehicle.condition.ilike(f"%{filters['condition']}%"))
            
            if filters.get('price_min'):
                query = query.filter(Vehicle.price >= float(filters['price_min']))
            
            if filters.get('price_max'):
                query = query.filter(Vehicle.price <= float(filters['price_max']))
            
            if filters.get('year_min'):
                query = query.filter(Vehicle.year >= int(filters['year_min']))
            
            if filters.get('year_max'):
                query = query.filter(Vehicle.year <= int(filters['year_max']))
            
            if filters.get('mileage_max'):
                query = query.filter(Vehicle.mileage <= int(filters['mileage_max']))
            
            if filters.get('location'):
                query = query.filter(Vehicle.location.ilike(f"%{filters['location']}%"))
            
            if filters.get('source'):
                query = query.filter(Vehicle.source == filters['source'])
        
        return query
    
    def _apply_sorting(self, query, sort_by: str):
        """Apply sorting to query"""
        if sort_by == 'price_low':
            return query.order_by(Vehicle.price.asc().nulls_last())
        elif sort_by == 'price_high':
            return query.order_by(Vehicle.price.desc().nulls_last())
        elif sort_by == 'year_new':
            return query.order_by(Vehicle.year.desc().nulls_last())
        elif sort_by == 'year_old':
            return query.order_by(Vehicle.year.asc().nulls_last())
        elif sort_by == 'mileage_low':
            return query.order_by(Vehicle.mileage.asc().nulls_last())
        elif sort_by == 'mileage_high':
            return query.order_by(Vehicle.mileage.desc().nulls_last())
        elif sort_by == 'deal_rating':
            # Sort by deal rating: Great Deal > Good Deal > Fair Price > others
            deal_order = case(
                (Vehicle.deal_rating == 'Great Deal', 1),
                (Vehicle.deal_rating == 'Good Deal', 2),
                (Vehicle.deal_rating == 'Fair Price', 3),
                else_=4
            )
            return query.order_by(deal_order, Vehicle.price.asc())
        else:  # relevance (default)
            # Score based on multiple factors
            relevance_score = self._calculate_relevance_score()
            return query.order_by(relevance_score.desc(), Vehicle.created_at.desc())
    
    def _calculate_relevance_score(self):
        """Calculate relevance score for sorting"""
        # Combine multiple factors for relevance
        price_score = case(
            (Vehicle.price.between(10000, 30000), 10),
            (Vehicle.price.between(5000, 50000), 5),
            else_=1
        )
        
        deal_score = case(
            (Vehicle.deal_rating == 'Great Deal', 15),
            (Vehicle.deal_rating == 'Good Deal', 10),
            (Vehicle.deal_rating == 'Fair Price', 5),
            else_=0
        )
        
        mileage_score = case(
            (Vehicle.mileage < 50000, 10),
            (Vehicle.mileage < 100000, 5),
            else_=1
        )
        
        year_score = case(
            (Vehicle.year >= 2020, 10),
            (Vehicle.year >= 2015, 5),
            else_=1
        )
        
        return price_score + deal_score + mileage_score + year_score
    
    def _generate_search_insights(self, vehicles: List[Vehicle], 
                                 parsed_query: Dict, 
                                 filters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights about search results"""
        if not vehicles:
            return {}
        
        insights = {}
        
        # Price insights
        prices = [v.price for v in vehicles if v.price]
        if prices:
            insights['price'] = {
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices),
                'median': sorted(prices)[len(prices) // 2]
            }
        
        # Year insights
        years = [v.year for v in vehicles if v.year]
        if years:
            insights['year'] = {
                'min': min(years),
                'max': max(years),
                'avg': sum(years) / len(years)
            }
        
        # Mileage insights
        mileages = [v.mileage for v in vehicles if v.mileage]
        if mileages:
            insights['mileage'] = {
                'min': min(mileages),
                'max': max(mileages),
                'avg': sum(mileages) / len(mileages)
            }
        
        # Deal rating distribution
        deal_ratings = [v.deal_rating for v in vehicles if v.deal_rating]
        if deal_ratings:
            from collections import Counter
            deal_counts = Counter(deal_ratings)
            insights['deal_ratings'] = dict(deal_counts)
        
        # Popular makes
        makes = [v.make for v in vehicles if v.make]
        if makes:
            from collections import Counter
            make_counts = Counter(makes)
            insights['popular_makes'] = dict(make_counts.most_common(5))
        
        # Source distribution
        sources = [v.source for v in vehicles if v.source]
        if sources:
            from collections import Counter
            source_counts = Counter(sources)
            insights['sources'] = dict(source_counts)
        
        return insights
    
    def _get_related_searches(self, original_query: str, parsed_query: Dict) -> List[str]:
        """Generate related search suggestions"""
        related = []
        
        # Add make-based suggestions
        if parsed_query.get('make'):
            make = parsed_query['make']
            related.extend([
                f"{make} under $20000",
                f"{make} under $30000",
                f"{make} sedan",
                f"{make} SUV",
                f"reliable {make}",
                f"luxury {make}"
            ])
        
        # Add price-based suggestions
        if parsed_query.get('price_max'):
            price = parsed_query['price_max']
            related.extend([
                f"cars under ${price}",
                f"SUV under ${price}",
                f"sedan under ${price}",
                f"reliable car under ${price}"
            ])
        
        # Add year-based suggestions
        if parsed_query.get('year_min'):
            year = parsed_query['year_min']
            related.extend([
                f"cars newer than {year}",
                f"{year} or newer sedan",
                f"{year} or newer SUV"
            ])
        
        # Add generic popular searches
        popular_searches = [
            "Honda Civic",
            "Toyota Camry",
            "Tesla Model 3",
            "Ford F-150",
            "BMW 3 Series",
            "reliable family car",
            "fuel efficient car",
            "luxury sedan",
            "pickup truck"
        ]
        
        # Filter out searches too similar to original
        filtered_related = []
        for search in related + popular_searches:
            if search.lower() not in original_query.lower():
                filtered_related.append(search)
        
        return filtered_related[:8]  # Return top 8 suggestions
    
    def get_search_suggestions(self, query: str, limit: int = 8) -> List[Dict[str, str]]:
        """Get search suggestions based on partial query"""
        suggestions = []
        
        # Popular makes and models
        popular_cars = [
            {'text': 'Honda Civic', 'type': 'popular', 'icon': 'fas fa-car'},
            {'text': 'Toyota Camry', 'type': 'popular', 'icon': 'fas fa-car'},
            {'text': 'Tesla Model 3', 'type': 'popular', 'icon': 'fas fa-bolt'},
            {'text': 'Ford F-150', 'type': 'popular', 'icon': 'fas fa-truck'},
            {'text': 'BMW 3 Series', 'type': 'popular', 'icon': 'fas fa-star'},
            {'text': 'Mercedes-Benz C-Class', 'type': 'popular', 'icon': 'fas fa-star'},
            {'text': 'Audi A4', 'type': 'popular', 'icon': 'fas fa-car'},
            {'text': 'Jeep Wrangler', 'type': 'popular', 'icon': 'fas fa-mountain'},
            {'text': 'Subaru Outback', 'type': 'popular', 'icon': 'fas fa-car'},
            {'text': 'Mazda CX-5', 'type': 'popular', 'icon': 'fas fa-car'}
        ]
        
        # Filter based on query
        query_lower = query.lower()
        for car in popular_cars:
            if query_lower in car['text'].lower():
                suggestions.append(car)
        
        # Add price-based suggestions
        if 'under' in query_lower or 'below' in query_lower:
            suggestions.extend([
                {'text': f'{query} under $20,000', 'type': 'price', 'icon': 'fas fa-dollar-sign'},
                {'text': f'{query} under $30,000', 'type': 'price', 'icon': 'fas fa-dollar-sign'},
                {'text': f'{query} under $40,000', 'type': 'price', 'icon': 'fas fa-dollar-sign'}
            ])
        
        # Add category suggestions
        categories = [
            {'text': 'family car', 'type': 'category', 'icon': 'fas fa-users'},
            {'text': 'luxury sedan', 'type': 'category', 'icon': 'fas fa-star'},
            {'text': 'fuel efficient', 'type': 'category', 'icon': 'fas fa-leaf'},
            {'text': 'sports car', 'type': 'category', 'icon': 'fas fa-tachometer-alt'},
            {'text': 'pickup truck', 'type': 'category', 'icon': 'fas fa-truck'},
            {'text': 'SUV', 'type': 'category', 'icon': 'fas fa-car'}
        ]
        
        for category in categories:
            if query_lower in category['text'].lower() or category['text'] in query_lower:
                suggestions.append(category)
        
        return suggestions[:limit]
    
    def save_search(self, session_id: str, query: str, filters: Dict[str, Any] = None):
        """Save search to user's search history"""
        try:
            # This would typically save to a search history table
            # For now, we'll use cache
            history_key = f"search_history:{session_id}"
            
            # Get existing history
            history = cache.get(history_key) or []
            
            # Add new search
            search_entry = {
                'query': query,
                'filters': filters or {},
                'timestamp': datetime.now().isoformat()
            }
            
            # Remove duplicate if exists
            history = [h for h in history if h['query'] != query]
            
            # Add to front
            history.insert(0, search_entry)
            
            # Keep only last 10 searches
            history = history[:10]
            
            # Save back to cache
            cache.set(history_key, history, timeout=86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Error saving search: {e}")
    
    def get_search_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's search history"""
        try:
            history_key = f"search_history:{session_id}"
            history = cache.get(history_key) or []
            return history[:limit]
        except Exception as e:
            logger.error(f"Error getting search history: {e}")
            return []


class VehicleComparison:
    """Vehicle comparison functionality"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def compare_vehicles(self, vehicle_ids: List[int]) -> Dict[str, Any]:
        """Compare multiple vehicles"""
        try:
            # Get vehicles
            vehicles = self.db.query(Vehicle).filter(Vehicle.id.in_(vehicle_ids)).all()
            
            if not vehicles:
                return {'error': 'No vehicles found'}
            
            # Generate comparison analysis
            analysis = self._generate_comparison_analysis(vehicles)
            
            return {
                'vehicles': vehicles,
                'analysis': analysis,
                'recommendations': self._generate_recommendations(vehicles)
            }
            
        except Exception as e:
            logger.error(f"Comparison error: {e}")
            return {'error': str(e)}
    
    def _generate_comparison_analysis(self, vehicles: List[Vehicle]) -> Dict[str, Any]:
        """Generate AI-powered comparison analysis"""
        analysis = {}
        
        # Find best value
        best_value = self._find_best_value(vehicles)
        if best_value:
            analysis['best_value'] = {
                'vehicle': best_value,
                'reason': self._explain_best_value(best_value, vehicles)
            }
        
        # Find lowest price
        lowest_price = min(vehicles, key=lambda v: v.price or float('inf'))
        if lowest_price.price:
            analysis['lowest_price'] = {
                'vehicle': lowest_price,
                'reason': f"Lowest price at ${lowest_price.price:,.0f}"
            }
        
        # Find newest
        newest = max(vehicles, key=lambda v: v.year or 0)
        if newest.year:
            analysis['newest'] = {
                'vehicle': newest,
                'reason': f"Newest model year: {newest.year}"
            }
        
        # Find lowest mileage
        lowest_mileage = min(vehicles, key=lambda v: v.mileage or float('inf'))
        if lowest_mileage.mileage is not None:
            analysis['lowest_mileage'] = {
                'vehicle': lowest_mileage,
                'reason': f"Lowest mileage: {lowest_mileage.mileage:,} miles"
            }
        
        return analysis
    
    def _find_best_value(self, vehicles: List[Vehicle]) -> Optional[Vehicle]:
        """Find the best value vehicle based on price, age, mileage, and condition"""
        scored_vehicles = []
        
        for vehicle in vehicles:
            score = 0
            
            # Price score (lower is better)
            if vehicle.price:
                max_price = max(v.price for v in vehicles if v.price)
                if max_price > 0:
                    price_score = (1 - (vehicle.price / max_price)) * 30
                    score += price_score
            
            # Year score (newer is better)
            if vehicle.year:
                max_year = max(v.year for v in vehicles if v.year)
                min_year = min(v.year for v in vehicles if v.year)
                if max_year > min_year:
                    year_score = ((vehicle.year - min_year) / (max_year - min_year)) * 25
                    score += year_score
            
            # Mileage score (lower is better)
            if vehicle.mileage is not None:
                max_mileage = max(v.mileage for v in vehicles if v.mileage is not None)
                if max_mileage > 0:
                    mileage_score = (1 - (vehicle.mileage / max_mileage)) * 25
                    score += mileage_score
            
            # Deal rating score
            if vehicle.deal_rating:
                deal_scores = {
                    'Great Deal': 20,
                    'Good Deal': 15,
                    'Fair Price': 10,
                    'Overpriced': 0
                }
                score += deal_scores.get(vehicle.deal_rating, 0)
            
            scored_vehicles.append((vehicle, score))
        
        if scored_vehicles:
            return max(scored_vehicles, key=lambda x: x[1])[0]
        return None
    
    def _explain_best_value(self, best_vehicle: Vehicle, all_vehicles: List[Vehicle]) -> str:
        """Explain why this vehicle is the best value"""
        reasons = []
        
        if best_vehicle.deal_rating == 'Great Deal':
            reasons.append("rated as a Great Deal")
        elif best_vehicle.deal_rating == 'Good Deal':
            reasons.append("rated as a Good Deal")
        
        # Compare price
        prices = [v.price for v in all_vehicles if v.price]
        if prices and best_vehicle.price:
            avg_price = sum(prices) / len(prices)
            if best_vehicle.price < avg_price:
                reasons.append(f"priced below average (${best_vehicle.price:,.0f} vs ${avg_price:,.0f})")
        
        # Compare year
        years = [v.year for v in all_vehicles if v.year]
        if years and best_vehicle.year:
            avg_year = sum(years) / len(years)
            if best_vehicle.year >= avg_year:
                reasons.append(f"relatively new ({best_vehicle.year})")
        
        # Compare mileage
        mileages = [v.mileage for v in all_vehicles if v.mileage is not None]
        if mileages and best_vehicle.mileage is not None:
            avg_mileage = sum(mileages) / len(mileages)
            if best_vehicle.mileage < avg_mileage:
                reasons.append(f"lower mileage ({best_vehicle.mileage:,} miles)")
        
        if reasons:
            return f"Best overall value due to being {', '.join(reasons)}"
        else:
            return "Best overall value based on comprehensive analysis"
    
    def _generate_recommendations(self, vehicles: List[Vehicle]) -> List[str]:
        """Generate recommendations based on comparison"""
        recommendations = []
        
        # Price recommendations
        prices = [v.price for v in vehicles if v.price]
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            price_diff = max_price - min_price
            
            if price_diff > 10000:
                recommendations.append(f"Consider if the ${price_diff:,.0f} price difference is justified by features and condition")
        
        # Year recommendations
        years = [v.year for v in vehicles if v.year]
        if years:
            year_range = max(years) - min(years)
            if year_range > 5:
                recommendations.append("Consider the age difference - newer models may have better technology and safety features")
        
        # Mileage recommendations
        mileages = [v.mileage for v in vehicles if v.mileage is not None]
        if mileages:
            mileage_range = max(mileages) - min(mileages)
            if mileage_range > 50000:
                recommendations.append("Pay attention to mileage differences - lower mileage typically means less wear and tear")
        
        # Deal rating recommendations
        deal_ratings = [v.deal_rating for v in vehicles if v.deal_rating]
        if 'Great Deal' in deal_ratings:
            great_deals = [v for v in vehicles if v.deal_rating == 'Great Deal']
            if len(great_deals) == 1:
                recommendations.append(f"The {great_deals[0].title} is rated as a Great Deal - consider prioritizing it")
        
        return recommendations[:5]  # Return top 5 recommendations