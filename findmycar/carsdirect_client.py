"""
CarsDirect Vehicle Marketplace Client
Accesses vehicle listings via CarsDirect Affiliate API
"""
import os
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json
from urllib.parse import urlencode, quote

logger = logging.getLogger(__name__)

class CarsDirectClient:
    """
    Client for accessing CarsDirect vehicle listings via their Affiliate API
    CarsDirect focuses on lead generation and dealer connections
    """
    BASE_URL = "https://api.carsdirect.com/v2"
    SEARCH_URL = "https://www.carsdirect.com/api/listings"
    
    def __init__(self, affiliate_id: Optional[str] = None, api_key: Optional[str] = None):
        self.affiliate_id = affiliate_id or os.getenv('CARSDIRECT_AFFILIATE_ID')
        self.api_key = api_key or os.getenv('CARSDIRECT_API_KEY')
        
        if not self.affiliate_id:
            logger.warning("CarsDirect affiliate ID not provided. CarsDirect searches will fail.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'FindMyCar/1.0',
            'X-Affiliate-ID': self.affiliate_id or ''
        })
    
    def search_vehicles(self, query: str = "", make: Optional[str] = None,
                       model: Optional[str] = None, year_min: Optional[int] = None,
                       year_max: Optional[int] = None, price_min: Optional[float] = None,
                       price_max: Optional[float] = None, mileage_max: Optional[int] = None,
                       page: int = 1, per_page: int = 20, zip_code: str = "90001") -> Dict:
        """
        Search CarsDirect vehicle inventory
        """
        if not self.affiliate_id:
            logger.error("CarsDirect affiliate ID not configured")
            return self._empty_response()
        
        try:
            logger.info(f"Searching CarsDirect for: {query or 'all vehicles'}")
            
            # Build query parameters
            params = self._build_search_params(query, make, model, year_min, year_max,
                                             price_min, price_max, mileage_max, page, per_page, zip_code)
            
            # Search endpoint
            url = f"{self.SEARCH_URL}/search"
            
            # Add authentication if API key is provided
            headers = {**self.session.headers}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 401:
                logger.error("Invalid CarsDirect credentials")
                return self._empty_response()
            
            if response.status_code != 200:
                logger.warning(f"CarsDirect API returned status {response.status_code}")
                return self._empty_response()
            
            data = response.json()
            
            # Parse vehicles
            vehicles = []
            listings = data.get('listings', [])
            
            for listing_data in listings[:per_page]:
                vehicle = self._parse_vehicle(listing_data)
                if vehicle:
                    vehicles.append(vehicle)
            
            total_count = data.get('total_results', len(vehicles))
            
            return {
                'vehicles': vehicles,
                'total': total_count,
                'page': page,
                'per_page': per_page,
                'source': 'carsdirect'
            }
            
        except Exception as e:
            logger.error(f"Error searching CarsDirect: {str(e)}")
            return self._empty_response()
    
    def _build_search_params(self, query: str, make: Optional[str], model: Optional[str],
                           year_min: Optional[int], year_max: Optional[int],
                           price_min: Optional[float], price_max: Optional[float],
                           mileage_max: Optional[int], page: int, per_page: int,
                           zip_code: str) -> Dict:
        """
        Build search parameters for CarsDirect API
        """
        params = {
            'affiliate_id': self.affiliate_id,
            'zip': zip_code,
            'radius': 100,
            'sort': 'price_asc',
            'page': page,
            'per_page': per_page,
            'condition': 'used'  # Focus on used cars
        }
        
        # Add search query
        if query:
            params['keywords'] = query
        
        # Make and model
        if make:
            params['make'] = make.lower()
        if model:
            params['model'] = model.lower()
        
        # Year range
        if year_min:
            params['year_min'] = year_min
        if year_max:
            params['year_max'] = year_max
        
        # Price range
        if price_min:
            params['price_min'] = int(price_min)
        if price_max:
            params['price_max'] = int(price_max)
        
        # Mileage
        if mileage_max:
            params['mileage_max'] = mileage_max
        
        # Include dealer info
        params['include_dealer'] = 'true'
        params['include_features'] = 'true'
        
        return params
    
    def _parse_vehicle(self, listing_data: Dict) -> Optional[Dict]:
        """
        Parse CarsDirect vehicle data into standard format
        """
        try:
            # Extract basic info
            listing_id = listing_data.get('listing_id')
            vin = listing_data.get('vin')
            
            # Vehicle info
            vehicle = listing_data.get('vehicle', {})
            make = vehicle.get('make')
            model = vehicle.get('model')
            year = vehicle.get('year')
            trim = vehicle.get('trim')
            
            # Build title
            title_parts = [str(year), make, model]
            if trim:
                title_parts.append(trim)
            title = ' '.join(filter(None, title_parts))
            
            # Pricing
            pricing = listing_data.get('pricing', {})
            price = pricing.get('asking_price') or pricing.get('list_price')
            
            # Details
            details = listing_data.get('details', {})
            mileage = details.get('mileage')
            exterior_color = details.get('exterior_color')
            interior_color = details.get('interior_color')
            
            # Location
            location_data = listing_data.get('location', {})
            city = location_data.get('city', '')
            state = location_data.get('state', '')
            location = f"{city}, {state}" if city and state else "Location not specified"
            
            # Images
            images = listing_data.get('images', [])
            image_urls = []
            
            for img in images:
                if isinstance(img, dict):
                    url = img.get('url') or img.get('large')
                else:
                    url = img
                if url:
                    image_urls.append(url)
            
            # Generate CarsDirect URL
            if make and model and year:
                slug = f"{year}-{make}-{model}".lower().replace(' ', '-')
                vehicle_url = f"https://www.carsdirect.com/used-cars/{slug}/{listing_id}"
            else:
                vehicle_url = f"https://www.carsdirect.com/used-cars/listing/{listing_id}"
            
            # Features
            features = details.get('features', [])
            options = details.get('options', [])
            all_features = features + options
            
            # Dealer info
            dealer = listing_data.get('dealer', {})
            
            return {
                'id': f"carsdirect_{vin or listing_id}",
                'title': title,
                'price': price,
                'year': year,
                'make': make,
                'model': model,
                'trim': trim,
                'mileage': mileage,
                'location': location,
                'link': vehicle_url,
                'image': image_urls[0] if image_urls else None,
                'image_urls': image_urls,
                'description': listing_data.get('description', ''),
                'source': 'carsdirect',
                'condition': details.get('condition', 'Used'),
                'seller_type': 'Dealer',
                'created_date': datetime.now().isoformat(),
                'vin': vin,
                'listing_id': listing_id,
                'exterior_color': exterior_color,
                'interior_color': interior_color,
                'body_style': vehicle.get('body_style'),
                'engine': details.get('engine'),
                'transmission': details.get('transmission'),
                'drivetrain': details.get('drivetrain'),
                'fuel_type': details.get('fuel_type'),
                'mpg_city': details.get('mpg_city'),
                'mpg_highway': details.get('mpg_highway'),
                'features': all_features,
                'dealer_info': {
                    'name': dealer.get('name'),
                    'phone': dealer.get('phone'),
                    'website': dealer.get('website'),
                    'address': dealer.get('address'),
                    'city': dealer.get('city'),
                    'state': dealer.get('state'),
                    'zip': dealer.get('zip'),
                    'rating': dealer.get('rating'),
                    'reviews_count': dealer.get('reviews_count')
                },
                'carsdirect_data': {
                    'savings': pricing.get('savings'),
                    'market_price': pricing.get('market_price'),
                    'price_rating': pricing.get('price_rating'),
                    'days_on_market': listing_data.get('days_on_market'),
                    'views': listing_data.get('view_count'),
                    'inquiries': listing_data.get('inquiry_count'),
                    'carfax_available': listing_data.get('carfax_available', False),
                    'financing_available': listing_data.get('financing_available', False)
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing CarsDirect vehicle: {str(e)}")
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
            'source': 'carsdirect'
        }
    
    def get_vehicle_details(self, vehicle_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific vehicle
        """
        if not self.affiliate_id:
            logger.error("CarsDirect affiliate ID not configured")
            return None
        
        try:
            # Extract listing ID from vehicle_id
            if vehicle_id.startswith('carsdirect_'):
                listing_id = vehicle_id.replace('carsdirect_', '')
                
                url = f"{self.SEARCH_URL}/listing/{listing_id}"
                
                params = {
                    'affiliate_id': self.affiliate_id,
                    'include_dealer': 'true',
                    'include_features': 'true',
                    'include_history': 'true'
                }
                
                headers = {**self.session.headers}
                if self.api_key:
                    headers['Authorization'] = f'Bearer {self.api_key}'
                
                response = self.session.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_vehicle(data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting vehicle details: {str(e)}")
            return None
    
    def get_price_analysis(self, make: str, model: str, year: int, zip_code: str = "90001") -> Optional[Dict]:
        """
        Get price analysis for a specific make/model/year
        """
        if not self.affiliate_id:
            logger.error("CarsDirect affiliate ID not configured")
            return None
        
        try:
            url = f"{self.BASE_URL}/pricing/analysis"
            
            params = {
                'affiliate_id': self.affiliate_id,
                'make': make,
                'model': model,
                'year': year,
                'zip': zip_code
            }
            
            headers = {**self.session.headers}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'average_price': data.get('average_price'),
                    'price_range': data.get('price_range'),
                    'market_days': data.get('average_days_on_market'),
                    'inventory_count': data.get('total_inventory'),
                    'price_trends': data.get('price_trends', []),
                    'recommendations': data.get('recommendations', [])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting price analysis: {str(e)}")
            return None
    
    def get_dealer_info(self, dealer_id: str) -> Optional[Dict]:
        """
        Get detailed dealer information
        """
        if not self.affiliate_id:
            return None
        
        try:
            url = f"{self.BASE_URL}/dealer/{dealer_id}"
            
            params = {'affiliate_id': self.affiliate_id}
            headers = {**self.session.headers}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting dealer info: {str(e)}")
            return None
    
    def check_health(self) -> Dict:
        """
        Check if CarsDirect API is accessible
        """
        if not self.affiliate_id:
            return {
                'source': 'carsdirect',
                'status': 'unhealthy',
                'response_time': 0,
                'message': 'Affiliate ID not configured'
            }
        
        try:
            # Test with a simple search
            url = f"{self.SEARCH_URL}/search"
            params = {
                'affiliate_id': self.affiliate_id,
                'zip': '90001',
                'radius': 10,
                'per_page': 1
            }
            
            headers = {**self.session.headers}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = self.session.get(url, params=params, headers=headers, timeout=5)
            is_healthy = response.status_code == 200
            
            if is_healthy:
                data = response.json()
                total = data.get('total_results', 0)
                message = f"Found {total} vehicles available"
            else:
                message = f"API returned status {response.status_code}"
            
            return {
                'source': 'carsdirect',
                'status': 'healthy' if is_healthy else 'unhealthy',
                'response_time': response.elapsed.total_seconds() if response else 0,
                'message': message
            }
        except Exception as e:
            return {
                'source': 'carsdirect',
                'status': 'unhealthy',
                'response_time': 0,
                'message': str(e)
            }