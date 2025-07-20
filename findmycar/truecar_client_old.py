"""
TrueCar client for fetching vehicle pricing and listings
TrueCar focuses on transparent pricing and market analysis
"""

import requests
import re
import json
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urlencode, quote
import time

logger = logging.getLogger(__name__)

class TrueCarClient:
    """
    Client for fetching TrueCar vehicle data and pricing information
    TrueCar specializes in market-based pricing transparency
    """
    
    def __init__(self):
        self.base_url = "https://www.truecar.com"
        self.search_url = "https://www.truecar.com/used-cars-for-sale/listings"
        
        # Browser-like headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Respectful delay between requests
        self.request_delay = 2
    
    def search_listings(self, query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
        """
        Search for vehicle listings on TrueCar
        
        Args:
            query: Search query (make/model/keywords)
            filters: Optional filters (year_min, year_max, price_min, price_max, zip_code)
            limit: Number of results to return
            offset: Pagination offset
            
        Returns:
            List of vehicle dictionaries with TrueCar pricing insights
        """
        try:
            # Build search URL with parameters
            url = self._build_search_url(query, filters, offset)
            
            # Add delay to be respectful
            time.sleep(self.request_delay)
            
            logger.info(f"Searching TrueCar for: {query}")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"TrueCar search successful, parsing results...")
                vehicles = self._parse_search_results(response.text)
                
                # Apply limit
                if vehicles:
                    vehicles = vehicles[:limit]
                    
                logger.info(f"Found {len(vehicles)} TrueCar vehicles with pricing data")
                return vehicles
            else:
                logger.warning(f"TrueCar search returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching TrueCar: {e}")
            return []
    
    def _build_search_url(self, query: str, filters: Optional[Dict], offset: int) -> str:
        """Build TrueCar search URL with parameters"""
        
        # Parse query for make/model
        query_parts = query.lower().split()
        
        # URL path components
        path_parts = []
        
        # Common makes mapping
        make_mapping = {
            'honda': 'honda',
            'toyota': 'toyota',
            'ford': 'ford',
            'chevrolet': 'chevrolet',
            'chevy': 'chevrolet',
            'nissan': 'nissan',
            'bmw': 'bmw',
            'mercedes': 'mercedes-benz',
            'benz': 'mercedes-benz',
            'audi': 'audi',
            'volkswagen': 'volkswagen',
            'vw': 'volkswagen',
            'hyundai': 'hyundai',
            'kia': 'kia',
            'mazda': 'mazda',
            'subaru': 'subaru',
            'lexus': 'lexus',
            'acura': 'acura',
            'infiniti': 'infiniti',
            'tesla': 'tesla',
            'jeep': 'jeep',
            'dodge': 'dodge',
            'ram': 'ram',
            'gmc': 'gmc'
        }
        
        # Try to extract make
        make_found = None
        model_parts = []
        
        for part in query_parts:
            if part in make_mapping:
                make_found = make_mapping[part]
            elif make_found:
                model_parts.append(part)
        
        # Build URL path
        if make_found:
            path_parts.append(make_found)
            if model_parts:
                path_parts.append('-'.join(model_parts))
        
        # Base URL construction
        if path_parts:
            url = f"{self.search_url}/{'/'.join(path_parts)}/"
        else:
            url = self.search_url + "/"
        
        # Add query parameters
        params = {}
        
        if filters:
            if filters.get('zip_code'):
                params['zipcode'] = filters['zip_code']
            else:
                params['zipcode'] = '90210'  # Default to LA
                
            if filters.get('year_min'):
                params['year_min'] = filters['year_min']
            if filters.get('year_max'):
                params['year_max'] = filters['year_max']
                
            if filters.get('price_min'):
                params['list_price_min'] = filters['price_min']
            if filters.get('price_max'):
                params['list_price_max'] = filters['price_max']
                
            if filters.get('mileage_max'):
                params['mileage_max'] = filters['mileage_max']
        
        # Handle pagination
        if offset > 0:
            params['page'] = (offset // 20) + 1  # TrueCar typically shows 20 per page
        
        if params:
            url += '?' + urlencode(params)
            
        return url
    
    def _parse_search_results(self, html: str) -> List[Dict]:
        """Parse vehicle listings from TrueCar search results HTML"""
        vehicles = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for JSON data in script tags (TrueCar often uses this)
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'window.__INITIAL_STATE__' in script.string:
                    # Extract JSON data
                    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', script.string, re.DOTALL)
                    if match:
                        try:
                            data = json.loads(match.group(1))
                            vehicles.extend(self._extract_vehicles_from_json(data))
                        except:
                            pass
            
            # Also try direct HTML parsing
            listing_cards = soup.find_all(['div', 'article'], class_=re.compile(r'card-content|listing-card|vehicle-card'))
            
            for card in listing_cards[:25]:  # Limit to prevent too many
                try:
                    vehicle = self._extract_vehicle_from_html(card)
                    if vehicle:
                        vehicles.append(vehicle)
                except Exception as e:
                    logger.debug(f"Error parsing vehicle card: {e}")
                    continue
            
            # Remove duplicates
            seen = set()
            unique_vehicles = []
            for v in vehicles:
                if v['listing_id'] not in seen:
                    seen.add(v['listing_id'])
                    unique_vehicles.append(v)
            
            return unique_vehicles
            
        except Exception as e:
            logger.error(f"Error parsing TrueCar search results: {e}")
            return []
    
    def _extract_vehicles_from_json(self, data: Dict) -> List[Dict]:
        """Extract vehicles from TrueCar's JSON data structure"""
        vehicles = []
        
        try:
            # Navigate through TrueCar's data structure
            listings = []
            
            # Try different possible paths in the data
            if 'listings' in data:
                listings = data['listings']
            elif 'searchResults' in data:
                listings = data['searchResults'].get('listings', [])
            elif 'inventory' in data:
                listings = data['inventory'].get('listings', [])
            
            for listing in listings:
                vehicle = self._parse_json_listing(listing)
                if vehicle:
                    vehicles.append(vehicle)
                    
        except Exception as e:
            logger.debug(f"Error extracting vehicles from JSON: {e}")
            
        return vehicles
    
    def _parse_json_listing(self, listing: Dict) -> Optional[Dict]:
        """Parse a single vehicle listing from JSON data"""
        try:
            vehicle = {
                'source': 'truecar',
                'listing_id': f"truecar_{listing.get('id', '')}",
                'title': None,
                'price': None,
                'location': None,
                'image_urls': [],
                'view_item_url': None,
                'make': listing.get('make', ''),
                'model': listing.get('model', ''),
                'year': listing.get('year', ''),
                'mileage': listing.get('mileage', ''),
                'condition': listing.get('condition', 'Used'),
                'vehicle_details': {},
                'truecar_price_analysis': {},
                'dealer_name': None
            }
            
            # Build title
            if vehicle['year'] and vehicle['make'] and vehicle['model']:
                vehicle['title'] = f"{vehicle['year']} {vehicle['make']} {vehicle['model']}"
                trim = listing.get('trim', '')
                if trim:
                    vehicle['title'] += f" {trim}"
            
            # Extract price
            vehicle['price'] = listing.get('listPrice', listing.get('price', 0))
            
            # TrueCar specific pricing data
            vehicle['truecar_price_analysis'] = {
                'market_average': listing.get('marketAverage', 0),
                'price_rating': listing.get('priceRating', ''),
                'days_on_market': listing.get('daysOnMarket', 0),
                'price_drop': listing.get('priceDrop', 0),
                'below_market': listing.get('belowMarketPrice', 0)
            }
            
            # Location and dealer
            dealer = listing.get('dealer', {})
            if dealer:
                vehicle['dealer_name'] = dealer.get('name', '')
                location = dealer.get('location', {})
                if location:
                    city = location.get('city', '')
                    state = location.get('state', '')
                    vehicle['location'] = f"{city}, {state}".strip(', ')
            
            # Images
            images = listing.get('images', [])
            if images:
                vehicle['image_urls'] = [img.get('url', '') for img in images if img.get('url')]
            elif listing.get('primaryImage'):
                vehicle['image_urls'] = [listing['primaryImage']]
            
            # URL
            if listing.get('vdpUrl'):
                vehicle['view_item_url'] = self.base_url + listing['vdpUrl']
            elif listing.get('url'):
                vehicle['view_item_url'] = listing['url']
            
            # Additional details
            vehicle['vehicle_details'] = {
                'vin': listing.get('vin', ''),
                'exterior_color': listing.get('exteriorColor', ''),
                'interior_color': listing.get('interiorColor', ''),
                'drivetrain': listing.get('drivetrain', ''),
                'transmission': listing.get('transmission', ''),
                'fuel_type': listing.get('fuelType', ''),
                'mpg_city': listing.get('mpgCity', ''),
                'mpg_highway': listing.get('mpgHighway', ''),
                'features': listing.get('features', [])
            }
            
            # Only return if we have essential data
            if vehicle['title'] and vehicle['price']:
                return vehicle
                
        except Exception as e:
            logger.debug(f"Error parsing JSON listing: {e}")
            
        return None
    
    def _extract_vehicle_from_html(self, card) -> Optional[Dict]:
        """Extract vehicle data from HTML card element"""
        try:
            vehicle = {
                'source': 'truecar',
                'listing_id': None,
                'title': None,
                'price': None,
                'location': None,
                'image_urls': [],
                'view_item_url': None,
                'make': None,
                'model': None,
                'year': None,
                'mileage': None,
                'condition': 'Used',
                'vehicle_details': {},
                'truecar_price_analysis': {},
                'dealer_name': None
            }
            
            # Extract title
            title_elem = card.find(['h3', 'h4'], class_=re.compile(r'heading|title|vehicle-heading'))
            if title_elem:
                vehicle['title'] = title_elem.get_text(strip=True)
                
                # Parse year, make, model from title
                title_match = re.match(r'(\d{4})\s+([A-Za-z-]+)\s+(.+)', vehicle['title'])
                if title_match:
                    vehicle['year'] = int(title_match.group(1))
                    vehicle['make'] = title_match.group(2)
                    vehicle['model'] = title_match.group(3).split()[0]
            
            # Extract price
            price_elem = card.find(class_=re.compile(r'price|list-price'))
            if price_elem:
                price_text = price_elem.get_text()
                price_match = re.search(r'\$?([\d,]+)', price_text)
                if price_match:
                    vehicle['price'] = float(price_match.group(1).replace(',', ''))
            
            # Extract TrueCar price analysis
            market_elem = card.find(class_=re.compile(r'market-price|below-market'))
            if market_elem:
                market_text = market_elem.get_text()
                below_match = re.search(r'\$([\d,]+)\s*below', market_text, re.I)
                if below_match:
                    vehicle['truecar_price_analysis']['below_market'] = float(below_match.group(1).replace(',', ''))
            
            # Extract mileage
            mileage_elem = card.find(text=re.compile(r'\d+[,\d]*\s*(mi|miles)', re.I))
            if mileage_elem:
                mileage_match = re.search(r'([\d,]+)\s*(mi|miles)', str(mileage_elem), re.I)
                if mileage_match:
                    vehicle['mileage'] = int(mileage_match.group(1).replace(',', ''))
            
            # Extract location
            location_elem = card.find(class_=re.compile(r'location|dealer-location'))
            if location_elem:
                vehicle['location'] = location_elem.get_text(strip=True)
            
            # Extract dealer
            dealer_elem = card.find(class_=re.compile(r'dealer-name'))
            if dealer_elem:
                vehicle['dealer_name'] = dealer_elem.get_text(strip=True)
            
            # Extract image
            img_elem = card.find('img')
            if img_elem and img_elem.get('src'):
                vehicle['image_urls'] = [img_elem['src']]
            
            # Extract URL
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    vehicle['view_item_url'] = self.base_url + href
                else:
                    vehicle['view_item_url'] = href
                    
                # Generate listing ID from URL
                id_match = re.search(r'/(\d+)/', href)
                if id_match:
                    vehicle['listing_id'] = f"truecar_{id_match.group(1)}"
                else:
                    import hashlib
                    vehicle['listing_id'] = f"truecar_{hashlib.md5(href.encode()).hexdigest()[:8]}"
            
            # Only return if we have essential data
            if vehicle['title'] and vehicle['price'] and vehicle['listing_id']:
                return vehicle
                
        except Exception as e:
            logger.debug(f"Error extracting vehicle from HTML: {e}")
            
        return None

def search_truecar_listings(query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
    """
    Public interface for searching TrueCar listings
    """
    client = TrueCarClient()
    return client.search_listings(query, filters, limit, offset)