"""
Carvana Vehicle Marketplace Client
Accesses vehicle listings via their semi-public API
"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class CarvanaClient:
    """
    Client for accessing Carvana vehicle listings
    Uses their internal API endpoints (reverse-engineered)
    """
    BASE_URL = "https://www.carvana.com"
    API_URL = "https://apim.carvana.io"
    INVENTORY_API = "https://inventory-api.carvana.io"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://www.carvana.com',
            'Referer': 'https://www.carvana.com/',
            'x-carvana-version': '2.0',
            'x-client-type': 'web'
        })
    
    def search_vehicles(self, query: str = "", make: Optional[str] = None,
                       model: Optional[str] = None, year_min: Optional[int] = None,
                       year_max: Optional[int] = None, price_min: Optional[float] = None,
                       price_max: Optional[float] = None, mileage_max: Optional[int] = None,
                       page: int = 1, per_page: int = 20) -> Dict:
        """
        Search Carvana vehicle inventory
        """
        try:
            logger.info(f"Searching Carvana for: {query or 'all vehicles'}")
            
            # Build search payload
            payload = self._build_search_payload(query, make, model, year_min, year_max,
                                               price_min, price_max, mileage_max, page, per_page)
            
            # Search endpoint
            url = f"{self.INVENTORY_API}/api/v3/vehicles/search"
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Carvana API returned status {response.status_code}")
                return self._empty_response()
            
            data = response.json()
            
            # Parse vehicles
            vehicles = []
            inventory = data.get('inventory', {})
            results = inventory.get('results', [])
            
            for vehicle_data in results[:per_page]:
                vehicle = self._parse_vehicle(vehicle_data)
                if vehicle:
                    vehicles.append(vehicle)
            
            total_count = inventory.get('totalCount', len(vehicles))
            
            return {
                'vehicles': vehicles,
                'total': total_count,
                'page': page,
                'per_page': per_page,
                'source': 'carvana'
            }
            
        except Exception as e:
            logger.error(f"Error searching Carvana: {str(e)}")
            return self._empty_response()
    
    def _build_search_payload(self, query: str, make: Optional[str], model: Optional[str],
                            year_min: Optional[int], year_max: Optional[int],
                            price_min: Optional[float], price_max: Optional[float],
                            mileage_max: Optional[int], page: int, per_page: int) -> Dict:
        """
        Build search payload for Carvana API
        """
        # Base payload structure
        payload = {
            "searchArea": {
                "city": "",
                "state": "",
                "zip": "",
                "radius": 0,
                "lat": 0,
                "lng": 0
            },
            "searchRequest": {
                "facets": [],
                "filters": [],
                "sort": "BestMatch",
                "offset": (page - 1) * per_page,
                "limit": per_page
            }
        }
        
        filters = []
        
        # Text search
        if query:
            filters.append({
                "type": "keyword",
                "value": query
            })
        
        # Make filter
        if make:
            filters.append({
                "type": "make",
                "value": make.title()
            })
        
        # Model filter
        if model:
            filters.append({
                "type": "model", 
                "value": model.title()
            })
        
        # Year range
        if year_min or year_max:
            filters.append({
                "type": "year",
                "min": year_min or 1990,
                "max": year_max or datetime.now().year
            })
        
        # Price range
        if price_min or price_max:
            filters.append({
                "type": "price",
                "min": int(price_min) if price_min else 0,
                "max": int(price_max) if price_max else 999999
            })
        
        # Mileage
        if mileage_max:
            filters.append({
                "type": "mileage",
                "max": mileage_max
            })
        
        payload["searchRequest"]["filters"] = filters
        
        return payload
    
    def _parse_vehicle(self, vehicle_data: Dict) -> Optional[Dict]:
        """
        Parse Carvana vehicle data into standard format
        """
        try:
            vehicle = vehicle_data.get('vehicle', {})
            
            # Extract basic info
            vin = vehicle.get('vin')
            make = vehicle.get('make')
            model = vehicle.get('model')
            year = vehicle.get('year')
            trim = vehicle.get('trim')
            
            # Build title
            title_parts = [str(year), make, model]
            if trim:
                title_parts.append(trim)
            title = ' '.join(filter(None, title_parts))
            
            # Extract pricing
            pricing = vehicle.get('pricing', {})
            price = pricing.get('price')
            
            # Extract details
            mileage = vehicle.get('mileage')
            exterior_color = vehicle.get('exteriorColor')
            interior_color = vehicle.get('interiorColor')
            
            # Location - Carvana delivers nationwide
            location = "Available for delivery"
            
            # Images
            images = vehicle.get('images', {})
            image_urls = []
            
            # Get hero image
            hero_image = images.get('hero')
            if hero_image:
                image_urls.append(hero_image)
            
            # Get additional images
            for img_type in ['frontLeft', 'front', 'frontRight', 'left', 'right', 'rearLeft', 'rear', 'rearRight']:
                img_url = images.get(img_type)
                if img_url:
                    image_urls.append(img_url)
            
            # Features
            features = vehicle.get('features', [])
            
            # Vehicle URL
            stock_number = vehicle.get('stockNumber')
            vehicle_url = f"{self.BASE_URL}/vehicle/{stock_number}" if stock_number else None
            
            return {
                'id': f"carvana_{vin or stock_number}",
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
                'description': f"{exterior_color} exterior, {interior_color} interior" if exterior_color and interior_color else "",
                'source': 'carvana',
                'condition': 'Used',
                'seller_type': 'Dealer',
                'created_date': datetime.now().isoformat(),
                'vin': vin,
                'exterior_color': exterior_color,
                'interior_color': interior_color,
                'body_style': vehicle.get('bodyStyle'),
                'engine': vehicle.get('engine'),
                'transmission': vehicle.get('transmission'),
                'drivetrain': vehicle.get('drivetrain'),
                'fuel_type': vehicle.get('fuelType'),
                'mpg_city': vehicle.get('mpgCity'),
                'mpg_highway': vehicle.get('mpgHighway'),
                'features': features,
                'carvana_features': {
                    'free_delivery': True,
                    'return_policy': '7-day',
                    'warranty': vehicle.get('warranty'),
                    'certified': vehicle.get('certified', False),
                    'accident_free': vehicle.get('accidentFree'),
                    'one_owner': vehicle.get('oneOwner')
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing Carvana vehicle: {str(e)}")
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
            'source': 'carvana'
        }
    
    def get_vehicle_details(self, vehicle_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific vehicle
        """
        try:
            # Extract stock number from vehicle_id
            if vehicle_id.startswith('carvana_'):
                stock_number = vehicle_id.replace('carvana_', '')
                
                url = f"{self.API_URL}/api/v1/vehicles/{stock_number}"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_vehicle(data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting vehicle details: {str(e)}")
            return None
    
    def check_health(self) -> Dict:
        """
        Check if Carvana API is accessible
        """
        try:
            # Test with a simple search
            url = f"{self.INVENTORY_API}/api/v3/vehicles/search"
            payload = {
                "searchArea": {"city": "", "state": "", "zip": "", "radius": 0},
                "searchRequest": {"filters": [], "sort": "BestMatch", "offset": 0, "limit": 1}
            }
            
            response = self.session.post(url, json=payload, timeout=5)
            is_healthy = response.status_code == 200
            
            if is_healthy:
                data = response.json()
                total = data.get('inventory', {}).get('totalCount', 0)
                message = f"Found {total} vehicles in inventory"
            else:
                message = f"API returned status {response.status_code}"
            
            return {
                'source': 'carvana',
                'status': 'healthy' if is_healthy else 'unhealthy',
                'response_time': response.elapsed.total_seconds() if response else 0,
                'message': message
            }
        except Exception as e:
            return {
                'source': 'carvana',
                'status': 'unhealthy',
                'response_time': 0,
                'message': str(e)
            }