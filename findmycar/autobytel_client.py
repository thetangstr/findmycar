"""
Autobytel/AutoWeb Vehicle Marketplace Client
Accesses dealer inventory via AutoWeb API
"""
import os
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class AutobytelClient:
    """
    Client for accessing Autobytel/AutoWeb dealer inventory
    AutoWeb provides B2B services for dealer inventory management
    """
    BASE_URL = "https://api.autoweb.com/v1"
    INVENTORY_URL = "https://inventory.autoweb.com/api"
    
    def __init__(self, partner_id: Optional[str] = None, api_key: Optional[str] = None):
        self.partner_id = partner_id or os.getenv('AUTOWEB_PARTNER_ID')
        self.api_key = api_key or os.getenv('AUTOWEB_API_KEY')
        
        if not self.partner_id or not self.api_key:
            logger.warning("AutoWeb credentials not provided. Autobytel searches will fail.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'FindMyCar/1.0',
            'X-Partner-ID': self.partner_id or ''
        })
    
    def search_vehicles(self, query: str = "", make: Optional[str] = None,
                       model: Optional[str] = None, year_min: Optional[int] = None,
                       year_max: Optional[int] = None, price_min: Optional[float] = None,
                       price_max: Optional[float] = None, mileage_max: Optional[int] = None,
                       page: int = 1, per_page: int = 20, zip_code: str = "90210") -> Dict:
        """
        Search Autobytel dealer inventory via AutoWeb API
        """
        if not self.partner_id or not self.api_key:
            logger.error("AutoWeb credentials not configured")
            return self._empty_response()
        
        try:
            logger.info(f"Searching Autobytel for: {query or 'all vehicles'}")
            
            # Build search payload
            payload = self._build_search_payload(query, make, model, year_min, year_max,
                                               price_min, price_max, mileage_max, page, per_page, zip_code)
            
            # Search endpoint
            url = f"{self.INVENTORY_URL}/search"
            
            # Add authentication
            headers = {
                **self.session.headers,
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = self.session.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 401:
                logger.error("Invalid AutoWeb API credentials")
                return self._empty_response()
            
            if response.status_code != 200:
                logger.warning(f"AutoWeb API returned status {response.status_code}")
                return self._empty_response()
            
            data = response.json()
            
            # Parse vehicles
            vehicles = []
            results = data.get('results', [])
            
            for vehicle_data in results[:per_page]:
                vehicle = self._parse_vehicle(vehicle_data)
                if vehicle:
                    vehicles.append(vehicle)
            
            total_count = data.get('totalResults', len(vehicles))
            
            return {
                'vehicles': vehicles,
                'total': total_count,
                'page': page,
                'per_page': per_page,
                'source': 'autobytel'
            }
            
        except Exception as e:
            logger.error(f"Error searching Autobytel: {str(e)}")
            return self._empty_response()
    
    def _build_search_payload(self, query: str, make: Optional[str], model: Optional[str],
                            year_min: Optional[int], year_max: Optional[int],
                            price_min: Optional[float], price_max: Optional[float],
                            mileage_max: Optional[int], page: int, per_page: int,
                            zip_code: str) -> Dict:
        """
        Build search payload for AutoWeb API
        """
        payload = {
            'partnerId': self.partner_id,
            'location': {
                'zipCode': zip_code,
                'radius': 100
            },
            'pagination': {
                'offset': (page - 1) * per_page,
                'limit': per_page
            },
            'sort': {
                'field': 'price',
                'order': 'asc'
            },
            'filters': {}
        }
        
        # Add search query
        if query:
            payload['searchQuery'] = query
        
        # Vehicle filters
        filters = payload['filters']
        
        if make:
            filters['make'] = make.upper()
        if model:
            filters['model'] = model.upper()
        
        # Year range
        if year_min or year_max:
            filters['yearRange'] = {
                'min': year_min or 1990,
                'max': year_max or datetime.now().year
            }
        
        # Price range
        if price_min or price_max:
            filters['priceRange'] = {
                'min': int(price_min) if price_min else 0,
                'max': int(price_max) if price_max else 999999
            }
        
        # Mileage
        if mileage_max:
            filters['mileageMax'] = mileage_max
        
        # Only show available vehicles
        filters['availability'] = 'in_stock'
        filters['condition'] = ['used', 'certified']
        
        return payload
    
    def _parse_vehicle(self, vehicle_data: Dict) -> Optional[Dict]:
        """
        Parse AutoWeb vehicle data into standard format
        """
        try:
            # Extract basic info
            vin = vehicle_data.get('vin')
            stock_number = vehicle_data.get('stockNumber')
            
            # Vehicle details
            vehicle_info = vehicle_data.get('vehicle', {})
            make = vehicle_info.get('make')
            model = vehicle_info.get('model')
            year = vehicle_info.get('year')
            trim = vehicle_info.get('trim')
            
            # Build title
            title_parts = [str(year), make, model]
            if trim:
                title_parts.append(trim)
            title = ' '.join(filter(None, title_parts))
            
            # Pricing
            pricing = vehicle_data.get('pricing', {})
            price = pricing.get('salePrice') or pricing.get('listPrice')
            
            # Details
            mileage = vehicle_info.get('odometer')
            exterior_color = vehicle_info.get('exteriorColor')
            interior_color = vehicle_info.get('interiorColor')
            
            # Dealer info
            dealer = vehicle_data.get('dealer', {})
            dealer_name = dealer.get('name')
            city = dealer.get('city', '')
            state = dealer.get('state', '')
            location = f"{city}, {state}" if city and state else dealer_name or "Location not specified"
            
            # Images
            media = vehicle_data.get('media', {})
            image_urls = []
            
            # Get photo URLs
            photos = media.get('photos', [])
            for photo in photos:
                url = photo.get('url') or photo.get('largeUrl')
                if url:
                    image_urls.append(url)
            
            # Vehicle URL
            vehicle_url = vehicle_data.get('vehicleDetailsUrl') or vehicle_data.get('dealerWebsiteUrl')
            
            # Features
            features = vehicle_info.get('features', [])
            equipment = vehicle_info.get('equipment', [])
            all_features = features + equipment
            
            return {
                'id': f"autobytel_{vin or stock_number}",
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
                'description': vehicle_data.get('description', ''),
                'source': 'autobytel',
                'condition': vehicle_data.get('condition', 'Used'),
                'seller_type': 'Dealer',
                'created_date': datetime.now().isoformat(),
                'vin': vin,
                'stock_number': stock_number,
                'exterior_color': exterior_color,
                'interior_color': interior_color,
                'body_style': vehicle_info.get('bodyStyle'),
                'engine': vehicle_info.get('engine'),
                'transmission': vehicle_info.get('transmission'),
                'drivetrain': vehicle_info.get('drivetrain'),
                'fuel_type': vehicle_info.get('fuelType'),
                'mpg_city': vehicle_info.get('mpgCity'),
                'mpg_highway': vehicle_info.get('mpgHighway'),
                'features': all_features,
                'dealer_info': {
                    'name': dealer_name,
                    'phone': dealer.get('phone'),
                    'website': dealer.get('website'),
                    'address': dealer.get('address'),
                    'city': dealer.get('city'),
                    'state': dealer.get('state'),
                    'zip': dealer.get('zipCode'),
                    'dealer_id': dealer.get('dealerId')
                },
                'autobytel_data': {
                    'certified': vehicle_data.get('certified', False),
                    'carfax_available': vehicle_data.get('carfaxAvailable', False),
                    'warranty': vehicle_data.get('warranty'),
                    'internet_price': pricing.get('internetPrice'),
                    'msrp': pricing.get('msrp'),
                    'invoice_price': pricing.get('invoicePrice')
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing Autobytel vehicle: {str(e)}")
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
            'source': 'autobytel'
        }
    
    def get_vehicle_details(self, vehicle_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific vehicle
        """
        if not self.partner_id or not self.api_key:
            logger.error("AutoWeb credentials not configured")
            return None
        
        try:
            # Extract identifier from vehicle_id
            if vehicle_id.startswith('autobytel_'):
                identifier = vehicle_id.replace('autobytel_', '')
                
                # Try VIN lookup first
                url = f"{self.INVENTORY_URL}/vehicle/vin/{identifier}"
                headers = {
                    **self.session.headers,
                    'Authorization': f'Bearer {self.api_key}'
                }
                
                response = self.session.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_vehicle(data)
                
                # Try stock number lookup
                url = f"{self.INVENTORY_URL}/vehicle/stock/{identifier}"
                response = self.session.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_vehicle(data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting vehicle details: {str(e)}")
            return None
    
    def get_dealer_inventory(self, dealer_id: str, page: int = 1, per_page: int = 50) -> Dict:
        """
        Get full inventory for a specific dealer
        """
        if not self.partner_id or not self.api_key:
            logger.error("AutoWeb credentials not configured")
            return self._empty_response()
        
        try:
            url = f"{self.INVENTORY_URL}/dealer/{dealer_id}/inventory"
            headers = {
                **self.session.headers,
                'Authorization': f'Bearer {self.api_key}'
            }
            
            params = {
                'offset': (page - 1) * per_page,
                'limit': per_page,
                'status': 'active'
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                vehicles = []
                
                for vehicle_data in data.get('inventory', []):
                    vehicle = self._parse_vehicle(vehicle_data)
                    if vehicle:
                        vehicles.append(vehicle)
                
                return {
                    'vehicles': vehicles,
                    'total': data.get('totalCount', len(vehicles)),
                    'page': page,
                    'per_page': per_page,
                    'dealer_id': dealer_id,
                    'source': 'autobytel'
                }
            
            return self._empty_response()
            
        except Exception as e:
            logger.error(f"Error getting dealer inventory: {str(e)}")
            return self._empty_response()
    
    def check_health(self) -> Dict:
        """
        Check if AutoWeb API is accessible
        """
        if not self.partner_id or not self.api_key:
            return {
                'source': 'autobytel',
                'status': 'unhealthy',
                'response_time': 0,
                'message': 'API credentials not configured'
            }
        
        try:
            # Test authentication endpoint
            url = f"{self.BASE_URL}/auth/validate"
            headers = {
                **self.session.headers,
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = self.session.get(url, headers=headers, timeout=5)
            is_healthy = response.status_code == 200
            
            if is_healthy:
                # Try a simple inventory check
                test_url = f"{self.INVENTORY_URL}/search"
                test_payload = {
                    'partnerId': self.partner_id,
                    'location': {'zipCode': '90210', 'radius': 10},
                    'pagination': {'offset': 0, 'limit': 1}
                }
                
                test_response = self.session.post(test_url, json=test_payload, headers=headers, timeout=5)
                if test_response.status_code == 200:
                    data = test_response.json()
                    total = data.get('totalResults', 0)
                    message = f"Connected to AutoWeb. {total} vehicles available"
                else:
                    message = "Authentication successful but inventory access failed"
            else:
                message = f"API returned status {response.status_code}"
            
            return {
                'source': 'autobytel',
                'status': 'healthy' if is_healthy else 'unhealthy',
                'response_time': response.elapsed.total_seconds() if response else 0,
                'message': message
            }
        except Exception as e:
            return {
                'source': 'autobytel',
                'status': 'unhealthy',
                'response_time': 0,
                'message': str(e)
            }