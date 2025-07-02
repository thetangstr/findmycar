#!/usr/bin/env python3

"""
Auto.dev Vehicle Listings API Client
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import time

logger = logging.getLogger(__name__)

class AutoDevClient:
    """Client for Auto.dev Vehicle Listings API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://auto.dev/api/listings"
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set headers if API key provided
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
    
    def search_vehicles(self, query: str, filters: Optional[Dict] = None, limit: int = 20) -> Dict[str, Any]:
        """
        Search for vehicles using Auto.dev API
        
        Args:
            query: Search query (will be parsed for make/model/year)
            filters: Additional filters (year_min, year_max, price_min, price_max, etc.)
            limit: Number of results to return (max 100)
            
        Returns:
            Dict with success, vehicles list, total count, etc.
        """
        
        try:
            logger.info(f"Auto.dev search attempt for query: {query}")
            
            # Build API parameters
            params = self._build_search_params(query, filters, limit)
            
            # Make API request
            response = self.session.get(self.base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response
                vehicles = self._parse_vehicles(data.get('records', []))
                total_count = data.get('totalCount', 0)
                
                logger.info(f"Auto.dev search successful: {len(vehicles)} vehicles, {total_count} total")
                
                return {
                    'success': True,
                    'vehicles': vehicles,
                    'total_available': total_count,
                    'source': 'auto.dev'
                }
                
            elif response.status_code == 401:
                logger.warning("Auto.dev authentication failed")
                return {
                    'success': False,
                    'error': 'Authentication required - get free API key from auto.dev',
                    'vehicles': []
                }
                
            else:
                logger.error(f"Auto.dev API error {response.status_code}: {response.text[:500]}")
                return {
                    'success': False,
                    'error': f'API error {response.status_code}',
                    'vehicles': []
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Auto.dev request failed: {e}")
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
                'vehicles': []
            }
    
    def _build_search_params(self, query: str, filters: Optional[Dict], limit: int) -> Dict[str, Any]:
        """Build API parameters from query and filters"""
        
        params = {
            'page': 1
        }
        
        # Parse query for make/model/year
        query_parts = query.lower().split()
        
        # Common make mappings
        make_keywords = {
            'honda': 'Honda',
            'toyota': 'Toyota', 
            'ford': 'Ford',
            'chevrolet': 'Chevrolet',
            'chevy': 'Chevrolet',
            'bmw': 'BMW',
            'mercedes': 'Mercedes-Benz',
            'audi': 'Audi',
            'volkswagen': 'Volkswagen',
            'vw': 'Volkswagen',
            'nissan': 'Nissan',
            'hyundai': 'Hyundai',
            'kia': 'Kia',
            'mazda': 'Mazda',
            'subaru': 'Subaru',
            'tesla': 'Tesla',
            'lexus': 'Lexus',
            'acura': 'Acura',
            'infiniti': 'Infiniti'
        }
        
        # Look for make in query
        for keyword, make in make_keywords.items():
            if keyword in query_parts:
                params['make'] = make
                break
        
        # Look for common models
        model_keywords = {
            'civic': 'Civic',
            'accord': 'Accord',
            'camry': 'Camry',
            'corolla': 'Corolla',
            'prius': 'Prius',
            'f-150': 'F-150',
            'f150': 'F-150',
            'mustang': 'Mustang',
            'model': 'Model',  # For Tesla Model S/3/X/Y
            'series': 'Series',  # For BMW 3 Series, etc.
            'class': 'Class'  # For Mercedes C-Class, etc.
        }
        
        for keyword, model in model_keywords.items():
            if keyword in query_parts:
                # Special handling for Tesla models
                if keyword == 'model' and params.get('make') == 'Tesla':
                    idx = query_parts.index(keyword)
                    if idx + 1 < len(query_parts):
                        next_part = query_parts[idx + 1].upper()
                        if next_part in ['S', '3', 'X', 'Y']:
                            params['model'] = f'Model {next_part}'
                        break
                # Special handling for BMW/Mercedes series
                elif keyword in ['series', 'class']:
                    idx = query_parts.index(keyword)
                    if idx > 0:
                        prev_part = query_parts[idx - 1]
                        if prev_part.isdigit():
                            params['model'] = f'{prev_part} {model}'
                        break
                else:
                    params['model'] = model
                    break
        
        # Look for years (4-digit numbers between 1990-2025)
        for part in query_parts:
            if part.isdigit() and len(part) == 4:
                year = int(part)
                if 1990 <= year <= 2025:
                    params['year_min'] = year
                    params['year_max'] = year
                    break
        
        # Add filters if provided
        if filters:
            for key, value in filters.items():
                if value is not None:
                    params[key] = value
        
        # Handle price filters
        if 'price_min' in params:
            params['price_min'] = int(params['price_min'])
        if 'price_max' in params:
            params['price_max'] = int(params['price_max'])
        
        # Set condition to used by default
        if 'condition' not in params:
            params['condition'] = 'used'
        
        logger.info(f"Auto.dev search params: {params}")
        return params
    
    def _parse_vehicles(self, records: List[Dict]) -> List[Dict]:
        """Parse Auto.dev vehicle records into our format"""
        
        vehicles = []
        
        for record in records:
            try:
                # Extract basic info
                year = record.get('year')
                make = record.get('make', '')
                model = record.get('model', '')
                trim = record.get('trim', '')
                
                # Build title
                title_parts = [str(year) if year else '', make, model]
                if trim:
                    title_parts.append(trim)
                title = ' '.join(filter(None, title_parts))
                
                # Parse price (remove $ and commas)
                price_str = record.get('price', '0')
                try:
                    price = float(price_str.replace('$', '').replace(',', ''))
                except (ValueError, AttributeError):
                    price = 0.0
                
                # Parse mileage
                mileage_str = record.get('mileage', '0')
                try:
                    # Extract numbers from "60,026 Miles"
                    mileage = int(''.join(filter(str.isdigit, mileage_str)))
                except (ValueError, AttributeError):
                    mileage = 0
                
                # Build location
                city = record.get('city', '')
                state = record.get('state', '')
                location = f"{city}, {state}" if city and state else city or state or 'Unknown'
                
                # Get images
                image_urls = []
                if record.get('primaryPhotoUrl'):
                    image_urls.append(record['primaryPhotoUrl'])
                if record.get('photoUrls'):
                    image_urls.extend(record['photoUrls'])
                
                # Build view URL
                view_url = record.get('vdpUrl') or record.get('clickoffUrl', '')
                if view_url and not view_url.startswith('http'):
                    view_url = f"https://{view_url}"
                
                vehicle = {
                    'external_id': str(record.get('id', '')),
                    'vin': record.get('vin', ''),
                    'title': title,
                    'year': year,
                    'make': make,
                    'model': model,
                    'trim': trim,
                    'price': price,
                    'mileage': mileage,
                    'condition': record.get('condition', 'used'),
                    'body_style': record.get('bodyStyle') or record.get('bodyType', ''),
                    'exterior_color': record.get('displayColor', ''),
                    'location': location,
                    'dealer_name': record.get('dealerName', ''),
                    'view_item_url': view_url,
                    'image_urls': image_urls,
                    'source': 'auto.dev',
                    'listing_date': record.get('createdAt', ''),
                    'last_updated': record.get('updatedAt', '')
                }
                
                vehicles.append(vehicle)
                
            except Exception as e:
                logger.warning(f"Failed to parse Auto.dev vehicle record: {e}")
                continue
        
        return vehicles

# Test function
def test_autodev_client():
    """Test the Auto.dev client"""
    
    print("🧪 Testing Auto.dev Client...")
    
    client = AutoDevClient()
    
    test_queries = [
        "Honda Civic 2020",
        "Toyota Prius",
        "BMW 3 Series 2021",
        "Tesla Model 3"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        
        result = client.search_vehicles(query, limit=5)
        
        if result['success']:
            print(f"  ✅ Found {len(result['vehicles'])} vehicles (of {result['total_available']} total)")
            
            if result['vehicles']:
                vehicle = result['vehicles'][0]
                print(f"  📄 Sample: {vehicle['title']} - ${vehicle['price']:,.0f}")
                print(f"  📍 Location: {vehicle['location']}")
                print(f"  🔗 URL: {vehicle['view_item_url']}")
        else:
            print(f"  ❌ Error: {result['error']}")

if __name__ == "__main__":
    test_autodev_client()