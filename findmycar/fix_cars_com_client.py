#!/usr/bin/env python3
"""
Fix the Cars.com client to use Universe Marketcheck API properly
"""
import os
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class CarsComClientFixed:
    """
    Updated Cars.com client using Universe Marketcheck API
    """
    
    def __init__(self):
        self.api_key = os.getenv('MARKETCHECK_API_KEY')
        if not self.api_key:
            logger.warning("No Marketcheck API key provided. Cars.com searches will fail.")
        
        # Universe Marketcheck API base URL (updated)
        self.API_BASE_URL = "https://universe.marketcheck.com/api/v1"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FindMyCar/1.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9'
        })
    
    def search_vehicles(self, query: str = "", make: Optional[str] = None,
                       model: Optional[str] = None, year_min: Optional[int] = None,
                       year_max: Optional[int] = None, price_min: Optional[float] = None,
                       price_max: Optional[float] = None, mileage_max: Optional[int] = None,
                       page: int = 1, per_page: int = 20) -> Dict:
        """
        Search Cars.com via Universe Marketcheck API
        """
        try:
            logger.info(f"Searching Cars.com via Universe for: {query or 'all vehicles'}")
            
            if not self.api_key:
                logger.error("Marketcheck API key not configured")
                return self._empty_response()
            
            # Build search parameters for Universe API
            params = self._build_search_params(query, make, model, year_min, year_max,
                                             price_min, price_max, mileage_max, page, per_page)
            
            # Universe API endpoint
            url = f"{self.API_BASE_URL}/search"
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Universe API returned status {response.status_code}")
                return self._empty_response()
            
            # Check if response is JSON
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/json' not in content_type:
                # Try to extract data from HTML response
                logger.info("Universe API returned HTML, attempting to parse")
                return self._parse_html_response(response.text, per_page)
            
            # Parse JSON response
            data = response.json()
            vehicles = self._parse_universe_response(data)
            
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
    
    def _build_search_params(self, query: str, make: Optional[str], model: Optional[str],
                           year_min: Optional[int], year_max: Optional[int],
                           price_min: Optional[float], price_max: Optional[float],
                           mileage_max: Optional[int], page: int, per_page: int) -> Dict:
        """
        Build search parameters for Universe Marketcheck API
        """
        params = {
            'api_key': self.api_key,
            'rows': per_page,
            'start': (page - 1) * per_page,
            'sort_by': 'price_asc'
        }
        
        # Keywords search
        if query:
            params['keywords'] = query
        
        # Make and model
        if make:
            params['make'] = make.title()
        if model:
            params['model'] = model.title()
        
        # Year range
        if year_min:
            params['year_from'] = year_min
        if year_max:
            params['year_to'] = year_max
        
        # Price range
        if price_min:
            params['price_from'] = int(price_min)
        if price_max:
            params['price_to'] = int(price_max)
        
        # Mileage
        if mileage_max:
            params['miles_to'] = mileage_max
        
        # Source filter (Cars.com only)
        params['source'] = 'cars.com'
        
        return params
    
    def _parse_universe_response(self, data: Dict) -> List[Dict]:
        """
        Parse Universe Marketcheck API response
        """
        vehicles = []
        
        try:
            # Universe API may have different response structure
            listings = data.get('listings', [])
            if not listings:
                # Try alternative keys
                listings = data.get('results', [])
            if not listings:
                listings = data.get('data', [])
            
            for listing in listings:
                vehicle = self._parse_universe_listing(listing)
                if vehicle:
                    vehicles.append(vehicle)
                    
        except Exception as e:
            logger.error(f"Error parsing Universe response: {str(e)}")
        
        return vehicles
    
    def _parse_universe_listing(self, listing: Dict) -> Optional[Dict]:
        """
        Parse a single vehicle listing from Universe API
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
            price = listing.get('price') or listing.get('list_price')
            
            # Extract other details
            mileage = listing.get('miles') or listing.get('mileage')
            exterior_color = listing.get('exterior_color')
            location = listing.get('city')
            if location:
                state = listing.get('state')
                if state:
                    location = f"{location}, {state}"
            
            # Vehicle URL
            listing_id = listing.get('id')
            vehicle_url = listing.get('vdp_url') or f"https://www.cars.com/vehicledetail/{listing_id}/" if listing_id else None
            
            # Images
            image_url = listing.get('photo_links', [])
            if isinstance(image_url, list) and image_url:
                image_url = image_url[0]
            elif not image_url:
                image_url = listing.get('image_url')
            
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
                'image': image_url,
                'image_urls': [image_url] if image_url else [],
                'description': f"{exterior_color} exterior" if exterior_color else "",
                'source': 'cars_com',
                'condition': 'Used',
                'seller_type': 'Dealer',
                'created_date': datetime.now().isoformat(),
                'vin': vin,
                'exterior_color': exterior_color,
                'transmission': listing.get('transmission'),
                'drivetrain': listing.get('drivetrain'),
                'fuel_type': listing.get('fuel_type'),
                'body_style': listing.get('body_style')
            }
            
        except Exception as e:
            logger.error(f"Error parsing Universe listing: {str(e)}")
            return None
    
    def _parse_html_response(self, html_content: str, per_page: int) -> Dict:
        """
        Parse HTML response if JSON is not available (fallback)
        """
        # For now, return empty response if HTML
        # Could implement HTML parsing if needed
        logger.info("HTML response received, returning empty results")
        return self._empty_response()
    
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
        Check if Universe Marketcheck API is accessible
        """
        try:
            if not self.api_key:
                return {
                    'source': 'cars_com',
                    'status': 'unhealthy',
                    'response_time': 0,
                    'message': 'API key not configured'
                }
            
            # Test with a simple search
            url = f"{self.API_BASE_URL}/search"
            params = {
                'api_key': self.api_key,
                'make': 'Honda',
                'rows': 1,
                'source': 'cars.com'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            is_healthy = response.status_code == 200
            
            return {
                'source': 'cars_com',
                'status': 'healthy' if is_healthy else 'unhealthy',
                'response_time': response.elapsed.total_seconds() if response else 0,
                'message': f'Universe API accessible' if is_healthy else f'API returned status {response.status_code}'
            }
        except Exception as e:
            return {
                'source': 'cars_com',
                'status': 'unhealthy',
                'response_time': 0,
                'message': str(e)
            }

def test_fixed_client():
    """Test the fixed Cars.com client"""
    print("🔍 Testing Fixed Cars.com Client")
    print("=" * 50)
    
    client = CarsComClientFixed()
    
    # Test health check
    print("\n1. Health check:")
    health = client.check_health()
    print(f"   Status: {health['status']}")
    print(f"   Message: {health['message']}")
    
    # Test search
    print("\n2. Vehicle search:")
    results = client.search_vehicles(
        make="Honda",
        year_min=2020,
        per_page=5
    )
    
    print(f"   Found: {results['total']} vehicles")
    print(f"   Source: {results['source']}")
    
    if results['vehicles']:
        print("\n   Sample vehicle:")
        sample = results['vehicles'][0]
        print(f"   Title: {sample.get('title', 'N/A')}")
        print(f"   Price: ${sample.get('price', 0):,}")
    
    return results['total'] > 0

if __name__ == "__main__":
    success = test_fixed_client()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")