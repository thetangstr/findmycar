"""
Revy Autos Vehicle Marketplace Client
Modern platform with clean JSON API endpoints
"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class RevyAutosClient:
    """
    Client for accessing Revy Autos vehicle listings
    Uses their modern JSON API for searching vehicles
    """
    BASE_URL = "https://www.revyautos.com"
    API_URL = "https://api.revyautos.com/v1"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Referer': 'https://www.revyautos.com/'
        })
    
    def search_vehicles(self, query: str = "", make: Optional[str] = None,
                       model: Optional[str] = None, year_min: Optional[int] = None,
                       year_max: Optional[int] = None, price_min: Optional[float] = None,
                       price_max: Optional[float] = None, mileage_max: Optional[int] = None,
                       page: int = 1, per_page: int = 20) -> Dict:
        """
        Search Revy Autos vehicle listings
        """
        try:
            logger.info(f"Searching Revy Autos for: {query or 'all vehicles'}")
            
            # Build search request
            search_data = self._build_search_request(query, make, model, year_min, year_max,
                                                    price_min, price_max, mileage_max, page, per_page)
            
            # Make API request
            url = f"{self.API_URL}/listings/search"
            response = self.session.post(url, json=search_data, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Revy Autos API returned status {response.status_code}")
                return self._empty_response()
            
            data = response.json()
            
            # Parse vehicles
            vehicles = []
            for listing in data.get('listings', []):
                vehicle = self._parse_listing(listing)
                if vehicle:
                    vehicles.append(vehicle)
            
            return {
                'vehicles': vehicles,
                'total': data.get('total', len(vehicles)),
                'page': page,
                'per_page': per_page,
                'source': 'revy_autos'
            }
            
        except Exception as e:
            logger.error(f"Error searching Revy Autos: {str(e)}")
            return self._empty_response()
    
    def _build_search_request(self, query: str, make: Optional[str], model: Optional[str],
                            year_min: Optional[int], year_max: Optional[int],
                            price_min: Optional[float], price_max: Optional[float],
                            mileage_max: Optional[int], page: int, per_page: int) -> Dict:
        """
        Build search request for Revy Autos API
        """
        request_data = {
            'page': page,
            'per_page': per_page,
            'sort': 'listed_at_desc',  # Newest first
            'filters': {}
        }
        
        # Keywords search
        if query:
            request_data['query'] = query
        
        # Vehicle filters
        filters = request_data['filters']
        
        if make:
            filters['make'] = make
        if model:
            filters['model'] = model
        
        # Year range
        if year_min or year_max:
            filters['year'] = {}
            if year_min:
                filters['year']['min'] = year_min
            if year_max:
                filters['year']['max'] = year_max
        
        # Price range
        if price_min or price_max:
            filters['price'] = {}
            if price_min:
                filters['price']['min'] = int(price_min)
            if price_max:
                filters['price']['max'] = int(price_max)
        
        # Mileage
        if mileage_max:
            filters['mileage'] = {'max': mileage_max}
        
        return request_data
    
    def _parse_listing(self, listing: Dict) -> Optional[Dict]:
        """
        Parse API listing response into vehicle dict
        """
        try:
            vehicle_data = listing.get('vehicle', {})
            pricing = listing.get('pricing', {})
            location_data = listing.get('location', {})
            seller_data = listing.get('seller', {})
            
            # Get primary image
            images = listing.get('images', [])
            primary_image = None
            if images:
                primary_image = images[0].get('url')
                # Ensure full URL
                if primary_image and not primary_image.startswith('http'):
                    primary_image = f"{self.BASE_URL}{primary_image}"
            
            # Build title
            year = vehicle_data.get('year')
            make = vehicle_data.get('make')
            model = vehicle_data.get('model')
            trim = vehicle_data.get('trim', '')
            
            title_parts = [str(year), make, model]
            if trim:
                title_parts.append(trim)
            title = ' '.join(filter(None, title_parts))
            
            # Get location
            city = location_data.get('city', '')
            state = location_data.get('state', '')
            location = f"{city}, {state}".strip(', ') if city or state else 'USA'
            
            # Determine seller type
            seller_type = 'Dealer' if seller_data.get('type') == 'dealer' else 'Private Party'
            
            return {
                'id': f"revy_{listing.get('id', '')}",
                'title': title,
                'price': pricing.get('price'),
                'year': year,
                'make': make,
                'model': model,
                'trim': trim,
                'mileage': vehicle_data.get('mileage'),
                'location': location,
                'link': f"{self.BASE_URL}/listings/{listing.get('id', '')}",
                'image': primary_image,
                'description': listing.get('description', ''),
                'source': 'revy_autos',
                'condition': vehicle_data.get('condition', 'Used'),
                'seller_type': seller_type,
                'created_date': listing.get('listed_at', datetime.now().isoformat()),
                'body_style': vehicle_data.get('body_style'),
                'exterior_color': vehicle_data.get('exterior_color'),
                'interior_color': vehicle_data.get('interior_color'),
                'engine': vehicle_data.get('engine'),
                'transmission': vehicle_data.get('transmission'),
                'drivetrain': vehicle_data.get('drivetrain'),
                'fuel_type': vehicle_data.get('fuel_type'),
                'vin': vehicle_data.get('vin'),
                'features': listing.get('features', []),
                'dealer_name': seller_data.get('name'),
                'price_analysis': pricing.get('analysis', {})  # May include fair/good/great deal indicator
            }
            
        except Exception as e:
            logger.error(f"Error parsing Revy Autos listing: {str(e)}")
            return None
    
    def _empty_response(self) -> Dict:
        """
        Return empty response structure
        """
        return {
            'vehicles': [],
            'total': 0,
            'page': 1,
            'per_page': 20,
            'source': 'revy_autos'
        }
    
    def get_vehicle_details(self, vehicle_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific vehicle
        """
        try:
            # Extract listing ID
            if vehicle_id.startswith('revy_'):
                listing_id = vehicle_id.replace('revy_', '')
                url = f"{self.API_URL}/listings/{listing_id}"
                
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    listing_data = response.json()
                    return self._parse_listing(listing_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting vehicle details: {str(e)}")
            return None
    
    def get_price_insights(self, make: str, model: str, year: int) -> Optional[Dict]:
        """
        Get pricing insights for a specific vehicle
        """
        try:
            url = f"{self.API_URL}/insights/pricing"
            params = {
                'make': make,
                'model': model,
                'year': year
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting price insights: {str(e)}")
            return None
    
    def check_health(self) -> Dict:
        """
        Check if Revy Autos API is accessible
        """
        try:
            url = f"{self.API_URL}/health"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get('status', 'unknown')
                message = health_data.get('message', 'API is responsive')
            else:
                status = 'unhealthy'
                message = f"API returned status {response.status_code}"
            
            return {
                'source': 'revy_autos',
                'status': 'healthy' if status == 'ok' else 'unhealthy',
                'response_time': response.elapsed.total_seconds(),
                'message': message
            }
        except Exception as e:
            return {
                'source': 'revy_autos',
                'status': 'unhealthy',
                'response_time': 0,
                'message': str(e)
            }