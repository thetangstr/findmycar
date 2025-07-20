#!/usr/bin/env python3
"""
Direct Cars.com scraping client (bypasses Marketcheck)
"""
import requests
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import time
import random

logger = logging.getLogger(__name__)

class CarsComDirectClient:
    """
    Direct Cars.com client that scrapes their website API
    Bypasses the need for Marketcheck
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        # Base search URL for Cars.com
        self.search_url = "https://www.cars.com/shopping/results/"
    
    def search_vehicles(self, query: str = "", make: Optional[str] = None,
                       model: Optional[str] = None, year_min: Optional[int] = None,
                       year_max: Optional[int] = None, price_min: Optional[float] = None,
                       price_max: Optional[float] = None, mileage_max: Optional[int] = None,
                       page: int = 1, per_page: int = 20) -> Dict:
        """
        Search Cars.com directly using their web interface
        """
        try:
            logger.info(f"Searching Cars.com directly for: {query or 'all vehicles'}")
            
            # Build search parameters
            params = self._build_search_params(query, make, model, year_min, year_max,
                                             price_min, price_max, mileage_max, page, per_page)
            
            # Add delay to be respectful
            time.sleep(random.uniform(1, 3))
            
            # Make request to Cars.com
            response = self.session.get(self.search_url, params=params, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Cars.com returned status {response.status_code}")
                return self._empty_response()
            
            # Parse the response
            vehicles = self._parse_cars_com_response(response.text)
            
            return {
                'vehicles': vehicles[:per_page],
                'total': len(vehicles),
                'page': page,
                'per_page': per_page,
                'source': 'cars_com_direct'
            }
            
        except Exception as e:
            logger.error(f"Error searching Cars.com directly: {str(e)}")
            return self._empty_response()
    
    def _build_search_params(self, query: str, make: Optional[str], model: Optional[str],
                           year_min: Optional[int], year_max: Optional[int],
                           price_min: Optional[float], price_max: Optional[float],
                           mileage_max: Optional[int], page: int, per_page: int) -> Dict:
        """
        Build search parameters for Cars.com
        """
        params = {
            'page': page,
            'page_size': per_page,
            'sort': 'best_match_desc'
        }
        
        # Text search
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
            params['maximum_distance'] = 'all'  # Search nationwide
            params['mileage_max'] = mileage_max
        
        # Default location (nationwide search)
        params['zip'] = '10001'  # NYC zip for nationwide search
        
        return params
    
    def _parse_cars_com_response(self, html_content: str) -> List[Dict]:
        """
        Parse Cars.com search results from HTML
        """
        vehicles = []
        
        try:
            # Look for JSON data in the HTML (Cars.com embeds search results as JSON)
            import re
            
            # Try to find embedded JSON data
            json_pattern = r'window\.__REDUX_STATE__\s*=\s*({.*?});'
            json_match = re.search(json_pattern, html_content, re.DOTALL)
            
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    # Extract vehicles from the Redux state
                    search_results = data.get('searchResults', {})
                    listings = search_results.get('listings', [])
                    
                    for listing in listings:
                        vehicle = self._parse_cars_com_listing(listing)
                        if vehicle:
                            vehicles.append(vehicle)
                            
                except json.JSONDecodeError:
                    logger.warning("Failed to parse Cars.com JSON data")
            
            # Fallback: Parse HTML directly if JSON parsing fails
            if not vehicles:
                vehicles = self._parse_cars_com_html(html_content)
                
        except Exception as e:
            logger.error(f"Error parsing Cars.com response: {str(e)}")
        
        return vehicles
    
    def _parse_cars_com_listing(self, listing_data: Dict) -> Optional[Dict]:
        """
        Parse a single Cars.com listing from JSON data
        """
        try:
            # Extract basic info
            vin = listing_data.get('vin')
            year = listing_data.get('year')
            make = listing_data.get('make')
            model = listing_data.get('model')
            trim = listing_data.get('trim')
            
            # Build title
            title_parts = [str(year), make, model]
            if trim:
                title_parts.append(trim)
            title = ' '.join(filter(None, title_parts))
            
            # Extract pricing
            pricing = listing_data.get('pricing', {})
            price = pricing.get('salePrice') or pricing.get('listPrice')
            
            # Extract other details
            mileage = listing_data.get('mileage')
            exterior_color = listing_data.get('exteriorColor')
            location = listing_data.get('dealer', {}).get('city')
            if location:
                state = listing_data.get('dealer', {}).get('state')
                if state:
                    location = f"{location}, {state}"
            
            # Vehicle URL
            listing_id = listing_data.get('id')
            vehicle_url = f"https://www.cars.com/vehicledetail/{listing_id}/" if listing_id else None
            
            # Images
            photos = listing_data.get('photos', [])
            image_urls = [photo.get('src') for photo in photos if photo.get('src')]
            
            return {
                'id': f"cars_com_{vin or listing_id}",
                'title': title,
                'price': price,
                'year': year,
                'make': make,
                'model': model,
                'trim': trim,
                'mileage': mileage,
                'location': location or 'Location not specified',
                'link': vehicle_url,
                'image': image_urls[0] if image_urls else None,
                'image_urls': image_urls,
                'description': f"{exterior_color} exterior" if exterior_color else "",
                'source': 'cars_com_direct',
                'condition': 'Used',  # Cars.com is primarily used cars
                'seller_type': 'Dealer',
                'created_date': datetime.now().isoformat(),
                'vin': vin,
                'exterior_color': exterior_color,
                'transmission': listing_data.get('transmission'),
                'drivetrain': listing_data.get('drivetrain'),
                'fuel_type': listing_data.get('fuelType'),
                'body_style': listing_data.get('bodyStyle')
            }
            
        except Exception as e:
            logger.error(f"Error parsing Cars.com listing: {str(e)}")
            return None
    
    def _parse_cars_com_html(self, html_content: str) -> List[Dict]:
        """
        Fallback HTML parsing for Cars.com
        """
        vehicles = []
        
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for vehicle listing cards
            listing_cards = soup.find_all(['div'], class_=lambda x: x and 'vehicle-card' in x)
            
            for card in listing_cards:
                try:
                    # Extract basic info from HTML
                    title_elem = card.find(['h4', 'h3', 'a'], class_=lambda x: x and 'title' in x.lower() if x else False)
                    title = title_elem.get_text(strip=True) if title_elem else "Unknown Vehicle"
                    
                    # Extract price
                    price_elem = card.find(['span', 'div'], class_=lambda x: x and 'price' in x.lower() if x else False)
                    price_text = price_elem.get_text(strip=True) if price_elem else "$0"
                    
                    # Parse price
                    import re
                    price_match = re.search(r'\$?([\d,]+)', price_text.replace(',', ''))
                    price = int(price_match.group(1)) if price_match else 0
                    
                    # Extract link
                    link_elem = card.find('a', href=True)
                    link = link_elem.get('href') if link_elem else None
                    if link and not link.startswith('http'):
                        link = f"https://www.cars.com{link}"
                    
                    vehicles.append({
                        'id': f"cars_com_html_{len(vehicles)}",
                        'title': title,
                        'price': price,
                        'link': link,
                        'source': 'cars_com_direct',
                        'condition': 'Used',
                        'created_date': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.debug(f"Error parsing individual car card: {e}")
                    continue
                    
        except ImportError:
            logger.error("BeautifulSoup not available for HTML parsing")
        except Exception as e:
            logger.error(f"Error in HTML parsing: {e}")
        
        return vehicles
    
    def _empty_response(self) -> Dict:
        """
        Return empty response structure
        """
        return {
            'vehicles': [],
            'total': 0,
            'page': 1,
            'per_page': 20,
            'source': 'cars_com_direct'
        }
    
    def check_health(self) -> Dict:
        """
        Check if Cars.com is accessible
        """
        try:
            response = self.session.get("https://www.cars.com", timeout=10)
            is_healthy = response.status_code == 200
            
            return {
                'source': 'cars_com_direct',
                'status': 'healthy' if is_healthy else 'unhealthy',
                'response_time': response.elapsed.total_seconds() if response else 0,
                'message': 'Direct Cars.com access working' if is_healthy else f'Cars.com returned {response.status_code}'
            }
        except Exception as e:
            return {
                'source': 'cars_com_direct',
                'status': 'unhealthy',
                'response_time': 0,
                'message': str(e)
            }