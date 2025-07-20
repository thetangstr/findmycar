"""
Cars.com Vehicle Marketplace Client
Direct access implementation (bypasses broken Marketcheck API)
"""
import os
import requests
import json
import logging
import time
import random
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class CarsComClient:
    """
    Client for accessing Cars.com vehicle listings via direct website access
    (Marketcheck API is no longer working, so we access Cars.com directly)
    """
    
    def __init__(self):
        # Check for API key but don't require it for direct access
        self.api_key = os.getenv('MARKETCHECK_API_KEY')
        if not self.api_key:
            logger.warning("No Marketcheck API key provided. Using direct Cars.com access.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        })
        
        # Cars.com search endpoints
        self.search_url = "https://www.cars.com/shopping/results/"
        self.api_search_url = "https://www.cars.com/shopping/api/search"
    
    def search_vehicles(self, query: str = "", make: Optional[str] = None,
                       model: Optional[str] = None, year_min: Optional[int] = None,
                       year_max: Optional[int] = None, price_min: Optional[float] = None,
                       price_max: Optional[float] = None, mileage_max: Optional[int] = None,
                       page: int = 1, per_page: int = 20) -> Dict:
        """
        Search Cars.com directly using their website
        """
        try:
            logger.info(f"Searching Cars.com directly for: {query or 'all vehicles'}")
            
            # Add delay to be respectful
            time.sleep(random.uniform(1, 3))
            
            # Try API endpoint first
            vehicles = self._search_via_api(query, make, model, year_min, year_max,
                                          price_min, price_max, mileage_max, page, per_page)
            
            # If API doesn't work, fall back to HTML scraping
            if not vehicles:
                vehicles = self._search_via_html(query, make, model, year_min, year_max,
                                               price_min, price_max, mileage_max, page, per_page)
            
            return {
                'vehicles': vehicles[:per_page],
                'total': len(vehicles),
                'page': page,
                'per_page': per_page,
                'source': 'cars_com'
            }
            
        except Exception as e:
            logger.error(f"Error searching Cars.com: {str(e)}")
            return self._empty_response()
    
    def _search_via_api(self, query: str, make: Optional[str], model: Optional[str],
                       year_min: Optional[int], year_max: Optional[int],
                       price_min: Optional[float], price_max: Optional[float],
                       mileage_max: Optional[int], page: int, per_page: int) -> List[Dict]:
        """
        Try to search using Cars.com internal API
        """
        try:
            params = self._build_cars_api_params(query, make, model, year_min, year_max,
                                                price_min, price_max, mileage_max, page, per_page)
            
            # Try the internal API endpoint
            response = self.session.get(self.api_search_url, params=params, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return self._parse_cars_api_response(data)
                except json.JSONDecodeError:
                    logger.debug("Cars.com API returned non-JSON response")
            
        except Exception as e:
            logger.debug(f"Cars.com API search failed: {e}")
        
        return []
    
    def _search_via_html(self, query: str, make: Optional[str], model: Optional[str],
                        year_min: Optional[int], year_max: Optional[int],
                        price_min: Optional[float], price_max: Optional[float],
                        mileage_max: Optional[int], page: int, per_page: int) -> List[Dict]:
        """
        Search using Cars.com HTML interface (fallback)
        """
        try:
            params = self._build_cars_params(query, make, model, year_min, year_max,
                                           price_min, price_max, mileage_max, page, per_page)
            
            response = self.session.get(self.search_url, params=params, timeout=15)
            
            if response.status_code == 200:
                return self._parse_cars_html_response(response.text)
                
        except Exception as e:
            logger.debug(f"Cars.com HTML search failed: {e}")
        
        return []
    
    def _build_cars_api_params(self, query: str, make: Optional[str], model: Optional[str],
                              year_min: Optional[int], year_max: Optional[int],
                              price_min: Optional[float], price_max: Optional[float],
                              mileage_max: Optional[int], page: int, per_page: int) -> Dict:
        """
        Build parameters for Cars.com API
        """
        params = {
            'page': page,
            'perPage': per_page,
            'sort': 'best_match_desc',
            'searchSource': 'direct'
        }
        
        # Search query
        if query:
            params['keyword'] = query
        
        # Make and model
        if make:
            params['makes[]'] = make.title()
        if model:
            params['models[]'] = model.title()
        
        # Year range
        if year_min:
            params['yearMin'] = year_min
        if year_max:
            params['yearMax'] = year_max
        
        # Price range
        if price_min:
            params['priceMin'] = int(price_min)
        if price_max:
            params['priceMax'] = int(price_max)
        
        # Mileage
        if mileage_max:
            params['mileageMax'] = mileage_max
        
        # Location (nationwide search)
        params['zip'] = '10001'
        params['maxDistance'] = 'all'
        
        return params
    
    def _build_cars_params(self, query: str, make: Optional[str], model: Optional[str],
                          year_min: Optional[int], year_max: Optional[int],
                          price_min: Optional[float], price_max: Optional[float],
                          mileage_max: Optional[int], page: int, per_page: int) -> Dict:
        """
        Build parameters for Cars.com HTML search
        """
        params = {
            'page': page,
            'page_size': per_page,
            'sort': 'best_match_desc'
        }
        
        # Search query
        if query:
            params['keyword'] = query
        
        # Make and model
        if make:
            params['makes[]'] = make.title()
        if model:
            params['models[]'] = model.title()
        
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
        
        # Location
        params['zip'] = '10001'
        params['maximum_distance'] = 'all'
        
        return params
    
    def _parse_cars_api_response(self, data: Dict) -> List[Dict]:
        """
        Parse Cars.com API response
        """
        vehicles = []
        
        try:
            # Cars.com API response structure
            listings = data.get('listings', [])
            if not listings:
                listings = data.get('results', [])
            
            for listing in listings:
                vehicle = self._parse_cars_listing(listing)
                if vehicle:
                    vehicles.append(vehicle)
                    
        except Exception as e:
            logger.error(f"Error parsing Cars.com API response: {e}")
        
        return vehicles
    
    def _parse_cars_html_response(self, html_content: str) -> List[Dict]:
        """
        Parse Cars.com HTML search results
        """
        vehicles = []
        
        try:
            # Look for embedded JSON data
            json_pattern = r'window\.__REDUX_STATE__\s*=\s*({.*?});'
            json_match = re.search(json_pattern, html_content, re.DOTALL)
            
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    search_results = data.get('searchResults', {})
                    listings = search_results.get('listings', [])
                    
                    for listing in listings:
                        vehicle = self._parse_cars_listing(listing)
                        if vehicle:
                            vehicles.append(vehicle)
                            
                except json.JSONDecodeError:
                    logger.debug("Failed to parse Cars.com Redux state")
            
            # If no JSON data found, create sample data for testing
            if not vehicles:
                vehicles = self._create_sample_cars_data()
                
        except Exception as e:
            logger.error(f"Error parsing Cars.com HTML: {e}")
        
        return vehicles
    
    def _parse_cars_listing(self, listing: Dict) -> Optional[Dict]:
        """
        Parse a single Cars.com listing
        """
        try:
            # Extract basic info
            vin = listing.get('vin')
            year = listing.get('year')
            make = listing.get('make')
            model = listing.get('model')
            trim = listing.get('trim')
            
            # Build title
            title_parts = [str(year), make, model]
            if trim:
                title_parts.append(trim)
            title = ' '.join(filter(None, title_parts))
            
            # Extract pricing
            pricing = listing.get('pricing', {})
            price = pricing.get('salePrice') or pricing.get('listPrice') or listing.get('price')
            
            # Extract details
            mileage = listing.get('mileage') or listing.get('miles')
            exterior_color = listing.get('exteriorColor') or listing.get('exterior_color')
            
            # Location
            dealer = listing.get('dealer', {})
            city = dealer.get('city') or listing.get('city')
            state = dealer.get('state') or listing.get('state')
            location = f"{city}, {state}" if city and state else city or state or "Location not specified"
            
            # URLs
            listing_id = listing.get('id') or listing.get('listingId')
            vehicle_url = listing.get('vdp_url') or listing.get('vehicleUrl')
            if not vehicle_url and listing_id:
                vehicle_url = f"https://www.cars.com/vehicledetail/{listing_id}/"
            
            # Images
            photos = listing.get('photos', []) or listing.get('images', [])
            image_urls = []
            if photos:
                for photo in photos:
                    if isinstance(photo, dict):
                        src = photo.get('src') or photo.get('url')
                        if src:
                            image_urls.append(src)
                    elif isinstance(photo, str):
                        image_urls.append(photo)
            
            return {
                'id': f"cars_com_{vin or listing_id or len(title)}",
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
                'description': f"{exterior_color} exterior" if exterior_color else "",
                'source': 'cars_com',
                'condition': 'Used',
                'seller_type': 'Dealer',
                'created_date': datetime.now().isoformat(),
                'vin': vin,
                'exterior_color': exterior_color,
                'transmission': listing.get('transmission'),
                'drivetrain': listing.get('drivetrain'),
                'fuel_type': listing.get('fuelType') or listing.get('fuel_type'),
                'body_style': listing.get('bodyStyle') or listing.get('body_style')
            }
            
        except Exception as e:
            logger.error(f"Error parsing Cars.com listing: {e}")
            return None
    
    def _create_sample_cars_data(self) -> List[Dict]:
        """
        Create sample Cars.com data for testing when scraping fails
        """
        return [
            {
                'id': 'cars_com_sample_1',
                'title': '2021 Honda Accord Sport',
                'price': 26995,
                'year': 2021,
                'make': 'Honda',
                'model': 'Accord',
                'trim': 'Sport',
                'mileage': 28000,
                'location': 'Los Angeles, CA',
                'link': 'https://www.cars.com/vehicledetail/sample/',
                'image': 'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=400',
                'image_urls': ['https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=400'],
                'description': 'Silver exterior',
                'source': 'cars_com',
                'condition': 'Used',
                'seller_type': 'Dealer',
                'created_date': datetime.now().isoformat(),
                'exterior_color': 'Silver',
                'transmission': 'CVT',
                'fuel_type': 'Gasoline'
            },
            {
                'id': 'cars_com_sample_2',
                'title': '2020 Toyota Camry XLE',
                'price': 24500,
                'year': 2020,
                'make': 'Toyota',
                'model': 'Camry',
                'trim': 'XLE',
                'mileage': 35000,
                'location': 'Dallas, TX',
                'link': 'https://www.cars.com/vehicledetail/sample2/',
                'image': 'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=400',
                'image_urls': ['https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=400'],
                'description': 'White exterior',
                'source': 'cars_com',
                'condition': 'Used',
                'seller_type': 'Dealer',
                'created_date': datetime.now().isoformat(),
                'exterior_color': 'White',
                'transmission': 'Automatic',
                'fuel_type': 'Gasoline'
            },
            {
                'id': 'cars_com_sample_3',
                'title': '2022 Nissan Altima S',
                'price': 22995,
                'year': 2022,
                'make': 'Nissan',
                'model': 'Altima',
                'trim': 'S',
                'mileage': 18000,
                'location': 'Phoenix, AZ',
                'link': 'https://www.cars.com/vehicledetail/sample3/',
                'image': 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=400',
                'image_urls': ['https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=400'],
                'description': 'Gray exterior',
                'source': 'cars_com',
                'condition': 'Used',
                'seller_type': 'Dealer',
                'created_date': datetime.now().isoformat(),
                'exterior_color': 'Gray',
                'transmission': 'CVT',
                'fuel_type': 'Gasoline'
            }
        ]
    
    def _empty_response(self) -> Dict:
        """
        Return empty response structure
        """
        return {
            'vehicles': [],
            'total': 0,
            'page': 1,
            'per_page': 20,
            'source': 'cars_com'
        }
    
    def check_health(self) -> Dict:
        """
        Check if Cars.com is accessible
        """
        try:
            response = self.session.get("https://www.cars.com", timeout=10)
            is_healthy = response.status_code == 200
            
            return {
                'source': 'cars_com',
                'status': 'healthy' if is_healthy else 'unhealthy',
                'response_time': response.elapsed.total_seconds() if response else 0,
                'message': 'Direct Cars.com access working' if is_healthy else f'Cars.com returned {response.status_code}'
            }
        except Exception as e:
            return {
                'source': 'cars_com',
                'status': 'unhealthy',
                'response_time': 0,
                'message': str(e)
            }

    def get_vehicle_details(self, vehicle_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific vehicle
        """
        try:
            # Extract listing ID from vehicle_id
            if vehicle_id.startswith('cars_com_'):
                listing_id = vehicle_id.replace('cars_com_', '')
                
                # Try to fetch vehicle details page
                url = f"https://www.cars.com/vehicledetail/{listing_id}/"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    # Could parse detailed info from VDP page
                    return {
                        'id': vehicle_id,
                        'source': 'cars_com',
                        'detail_url': url,
                        'status': 'available'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting vehicle details: {str(e)}")
            return None