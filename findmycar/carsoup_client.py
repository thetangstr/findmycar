"""
CarSoup.com Vehicle Listings Client
Regional marketplace focused on Midwest US
"""
import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
from datetime import datetime
import re
from urllib.parse import urlencode, urljoin

logger = logging.getLogger(__name__)

class CarSoupClient:
    """
    Client for accessing CarSoup vehicle listings
    Simple scraping approach as the site has minimal bot protection
    """
    BASE_URL = "https://www.carsoup.com"
    SEARCH_URL = "https://www.carsoup.com/used-vehicles"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_vehicles(self, query: str = "", make: Optional[str] = None,
                       model: Optional[str] = None, year_min: Optional[int] = None,
                       year_max: Optional[int] = None, price_min: Optional[float] = None,
                       price_max: Optional[float] = None, mileage_max: Optional[int] = None,
                       page: int = 1, per_page: int = 20) -> Dict:
        """
        Search CarSoup vehicle listings
        """
        try:
            logger.info(f"Searching CarSoup for: {query or 'all vehicles'}")
            
            # Build search parameters
            params = self._build_search_params(query, make, model, year_min, year_max,
                                             price_min, price_max, mileage_max, page)
            
            # Make search request
            url = f"{self.SEARCH_URL}?{urlencode(params)}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"CarSoup returned status {response.status_code}")
                return self._empty_response()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find vehicle listings
            vehicles = []
            listings = soup.find_all('div', class_='vehicle-card') or \
                      soup.find_all('div', class_='listing-item') or \
                      soup.find_all('article', class_='vehicle')
            
            for listing in listings[:per_page]:
                vehicle = self._parse_listing(listing)
                if vehicle:
                    vehicles.append(vehicle)
            
            # Get total count if available
            total_element = soup.find('span', class_='results-count') or \
                           soup.find('div', class_='total-results')
            total = len(vehicles)  # Default to current count
            
            if total_element:
                total_match = re.search(r'(\d+)', total_element.text)
                if total_match:
                    total = int(total_match.group(1))
            
            return {
                'vehicles': vehicles,
                'total': total,
                'page': page,
                'per_page': per_page,
                'source': 'carsoup'
            }
            
        except Exception as e:
            logger.error(f"Error searching CarSoup: {str(e)}")
            return self._empty_response()
    
    def _build_search_params(self, query: str, make: Optional[str], model: Optional[str],
                           year_min: Optional[int], year_max: Optional[int],
                           price_min: Optional[float], price_max: Optional[float],
                           mileage_max: Optional[int], page: int) -> Dict:
        """
        Build search parameters for CarSoup
        """
        params = {
            'page': page,
            'sort': 'date_desc'  # Newest first
        }
        
        # Keywords
        if query:
            params['keywords'] = query
        
        # Make/Model
        if make:
            params['make'] = make
        if model:
            params['model'] = model
        
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
        
        return params
    
    def _parse_listing(self, listing_element) -> Optional[Dict]:
        """
        Parse a vehicle listing from HTML
        """
        try:
            # Extract title
            title_elem = listing_element.find(['h3', 'h4'], class_=['title', 'vehicle-title']) or \
                        listing_element.find('a', class_='vehicle-link')
            title = title_elem.text.strip() if title_elem else ''
            
            # Extract link
            link_elem = listing_element.find('a', href=True)
            link = urljoin(self.BASE_URL, link_elem['href']) if link_elem else None
            
            # Extract price
            price = None
            price_elem = listing_element.find(['span', 'div'], class_=['price', 'vehicle-price'])
            if price_elem:
                price_text = price_elem.text.strip()
                price_match = re.search(r'\$([0-9,]+)', price_text)
                if price_match:
                    price = float(price_match.group(1).replace(',', ''))
            
            # Extract year, make, model from title
            year = None
            make = None
            model = None
            
            year_match = re.search(r'\b(19|20)\d{2}\b', title)
            if year_match:
                year = int(year_match.group(0))
                
                # Remove year and parse make/model
                title_no_year = title.replace(year_match.group(0), '').strip()
                parts = title_no_year.split()
                if parts:
                    make = parts[0]
                    if len(parts) > 1:
                        model = ' '.join(parts[1:])
            
            # Extract mileage
            mileage = None
            mileage_elem = listing_element.find(['span', 'div'], string=re.compile(r'\d+[,\d]*\s*miles?', re.I))
            if mileage_elem:
                mileage_match = re.search(r'(\d+[,\d]*)', mileage_elem.text)
                if mileage_match:
                    mileage = int(mileage_match.group(1).replace(',', ''))
            
            # Extract location
            location_elem = listing_element.find(['span', 'div'], class_=['location', 'dealer-location'])
            location = location_elem.text.strip() if location_elem else 'Midwest, USA'
            
            # Extract image
            image = None
            image_elem = listing_element.find('img', class_=['vehicle-image', 'listing-image'])
            if image_elem:
                image = image_elem.get('src') or image_elem.get('data-src')
                if image and not image.startswith('http'):
                    image = urljoin(self.BASE_URL, image)
            
            # Extract dealer info
            dealer_elem = listing_element.find(['span', 'div'], class_=['dealer-name', 'seller'])
            seller_type = 'Dealer' if dealer_elem else 'Private Party'
            
            # Generate ID from link or title
            vehicle_id = link.split('/')[-1] if link else title.replace(' ', '_')[:20]
            
            return {
                'id': f"carsoup_{vehicle_id}",
                'title': title,
                'price': price,
                'year': year,
                'make': make,
                'model': model,
                'mileage': mileage,
                'location': location,
                'link': link,
                'image': image,
                'description': f"{year} {make} {model}" if all([year, make, model]) else title,
                'source': 'carsoup',
                'condition': 'Used',
                'seller_type': seller_type,
                'created_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing CarSoup listing: {str(e)}")
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
            'source': 'carsoup'
        }
    
    def get_vehicle_details(self, vehicle_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific vehicle
        """
        try:
            # Extract URL from vehicle_id if needed
            if vehicle_id.startswith('carsoup_'):
                # Would need to maintain URL mapping or search for the vehicle
                return None
            
            # Could implement scraping of detail page here
            return None
            
        except Exception as e:
            logger.error(f"Error getting vehicle details: {str(e)}")
            return None
    
    def check_health(self) -> Dict:
        """
        Check if CarSoup website is accessible
        """
        try:
            response = self.session.get(self.BASE_URL, timeout=5)
            is_healthy = response.status_code == 200
            
            return {
                'source': 'carsoup',
                'status': 'healthy' if is_healthy else 'unhealthy',
                'response_time': response.elapsed.total_seconds(),
                'message': 'Website accessible' if is_healthy else f"Status code: {response.status_code}"
            }
        except Exception as e:
            return {
                'source': 'carsoup',
                'status': 'unhealthy',
                'response_time': 0,
                'message': str(e)
            }