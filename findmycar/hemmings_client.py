"""
Hemmings Classic Car Marketplace Client
Due to anti-bot protection, RSS feeds are currently unavailable.
Returns fallback static data until alternative access method is found.
"""
import feedparser
import logging
from typing import List, Dict, Optional
from datetime import datetime
import re
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class HemmingsClient:
    """
    Client for accessing Hemmings classic car listings
    NOTE: RSS feeds blocked by Incapsula DDoS protection as of July 2024
    Currently returns mock data to maintain API compatibility
    """
    BASE_URL = "https://www.hemmings.com"
    
    # RSS feeds are blocked by robots.txt and Incapsula protection
    BLOCKED_RSS_FEEDS = {
        'all': "https://www.hemmings.com/classifieds/rss",
        'cars': "https://www.hemmings.com/classifieds/cars-for-sale/rss",
        'parts': "https://www.hemmings.com/classifieds/parts/rss",
        'muscle': "https://www.hemmings.com/classifieds/dealer-showcases/rss",
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self._fallback_data = self._generate_fallback_data()
    
    def search_vehicles(self, query: str = "", make: Optional[str] = None,
                       model: Optional[str] = None, year_min: Optional[int] = None,
                       year_max: Optional[int] = None, price_min: Optional[float] = None,
                       price_max: Optional[float] = None, page: int = 1,
                       per_page: int = 20) -> Dict:
        """
        Search Hemmings listings - currently returns fallback data due to RSS blocking
        """
        try:
            logger.warning("Hemmings RSS feeds blocked by anti-bot protection - returning fallback data")
            
            # Use fallback data until RSS access is restored
            vehicles = []
            for vehicle in self._fallback_data:
                if self._matches_filters(vehicle, query, make, model, 
                                       year_min, year_max, price_min, price_max):
                    vehicles.append(vehicle)
            
            # Apply pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_vehicles = vehicles[start_idx:end_idx]
            
            return {
                'vehicles': paginated_vehicles,
                'total': len(vehicles),
                'page': page,
                'per_page': per_page,
                'source': 'hemmings',
                'warning': 'Using fallback data - RSS feeds currently blocked'
            }
            
        except Exception as e:
            logger.error(f"Error searching Hemmings: {str(e)}")
            return self._empty_response()
    
    def _parse_rss_entry(self, entry: Dict) -> Optional[Dict]:
        """
        Parse RSS entry into vehicle dict
        """
        try:
            # Extract basic info from title and description
            title = entry.get('title', '')
            description = entry.get('description', '')
            link = entry.get('link', '')
            
            # Parse year, make, model from title (typically "YYYY Make Model")
            year_match = re.search(r'(\d{4})', title)
            year = int(year_match.group(1)) if year_match else None
            
            # Extract price from description if available
            price = None
            price_match = re.search(r'\$([0-9,]+)', description)
            if price_match:
                price = float(price_match.group(1).replace(',', ''))
            
            # Get additional details by fetching the listing page
            details = self._fetch_listing_details(link) if link else {}
            
            # Clean title to get make/model
            title_parts = title.strip().split()
            make = None
            model = None
            
            if year and len(title_parts) > 1:
                # Remove year from title parts
                title_parts = [p for p in title_parts if p != str(year)]
                if title_parts:
                    make = title_parts[0]
                    model = ' '.join(title_parts[1:]) if len(title_parts) > 1 else None
            
            return {
                'id': f"hemmings_{link.split('/')[-1] if link else entry.get('id', '')}",
                'title': title,
                'price': price or details.get('price'),
                'year': year or details.get('year'),
                'make': make or details.get('make'),
                'model': model or details.get('model'),
                'mileage': details.get('mileage'),
                'location': details.get('location', 'USA'),
                'link': link,
                'image': details.get('image') or entry.get('media_thumbnail', [{}])[0].get('url'),
                'description': description[:200] + '...' if len(description) > 200 else description,
                'source': 'hemmings',
                'condition': 'Used',  # Hemmings focuses on classic cars
                'seller_type': 'Private Party',
                'created_date': entry.get('published', datetime.now().isoformat()),
                'body_style': details.get('body_style'),
                'exterior_color': details.get('color'),
                'engine': details.get('engine'),
                'transmission': details.get('transmission')
            }
            
        except Exception as e:
            logger.error(f"Error parsing Hemmings RSS entry: {str(e)}")
            return None
    
    def _fetch_listing_details(self, url: str) -> Dict:
        """
        Fetch additional details from the listing page
        """
        try:
            response = self.session.get(url, timeout=5)
            if response.status_code != 200:
                return {}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            details = {}
            
            # Extract structured data if available
            specs_section = soup.find('div', class_='vehicle-specs')
            if specs_section:
                for spec in specs_section.find_all('div', class_='spec-item'):
                    label = spec.find('span', class_='label')
                    value = spec.find('span', class_='value')
                    if label and value:
                        key = label.text.strip().lower().replace(' ', '_')
                        details[key] = value.text.strip()
            
            # Extract price
            price_elem = soup.find('span', class_='price') or soup.find('div', class_='asking-price')
            if price_elem:
                price_text = price_elem.text.strip()
                price_match = re.search(r'\$([0-9,]+)', price_text)
                if price_match:
                    details['price'] = float(price_match.group(1).replace(',', ''))
            
            # Extract main image
            image_elem = soup.find('img', class_='main-photo') or soup.find('meta', property='og:image')
            if image_elem:
                details['image'] = image_elem.get('src') or image_elem.get('content')
            
            # Extract location
            location_elem = soup.find('span', class_='location') or soup.find('div', class_='seller-location')
            if location_elem:
                details['location'] = location_elem.text.strip()
            
            return details
            
        except Exception as e:
            logger.debug(f"Could not fetch listing details: {str(e)}")
            return {}
    
    def _matches_filters(self, vehicle: Dict, query: str, make: Optional[str],
                        model: Optional[str], year_min: Optional[int],
                        year_max: Optional[int], price_min: Optional[float],
                        price_max: Optional[float]) -> bool:
        """
        Check if vehicle matches search filters
        """
        # Text search
        if query:
            searchable_text = f"{vehicle.get('title', '')} {vehicle.get('description', '')}".lower()
            if query.lower() not in searchable_text:
                return False
        
        # Make filter
        if make and vehicle.get('make'):
            if make.lower() != vehicle['make'].lower():
                return False
        
        # Model filter
        if model and vehicle.get('model'):
            if model.lower() not in vehicle['model'].lower():
                return False
        
        # Year filters
        if year_min and vehicle.get('year'):
            if vehicle['year'] < year_min:
                return False
        if year_max and vehicle.get('year'):
            if vehicle['year'] > year_max:
                return False
        
        # Price filters
        if price_min and vehicle.get('price'):
            if vehicle['price'] < price_min:
                return False
        if price_max and vehicle.get('price'):
            if vehicle['price'] > price_max:
                return False
        
        return True
    
    def _generate_fallback_data(self) -> List[Dict]:
        """
        Generate fallback vehicle data for when RSS feeds are unavailable
        Returns representative classic car listings
        """
        fallback_vehicles = [
            {
                'id': 'hemmings_fallback_1',
                'title': '1967 Ford Mustang Fastback',
                'price': 45000,
                'year': 1967,
                'make': 'Ford',
                'model': 'Mustang',
                'mileage': 78000,
                'location': 'Michigan, USA',
                'link': 'https://www.hemmings.com/classifieds/dealer/ford/mustang/2342567.html',
                'image': 'https://via.placeholder.com/300x200.png?text=1967+Ford+Mustang',
                'description': 'Classic 1967 Mustang Fastback in excellent condition. Recent restoration with original 289 V8 engine.',
                'source': 'hemmings',
                'condition': 'Used',
                'seller_type': 'Private Party',
                'created_date': datetime.now().isoformat(),
                'body_style': 'Fastback',
                'exterior_color': 'Red',
                'engine': '289 V8',
                'transmission': '4-Speed Manual'
            },
            {
                'id': 'hemmings_fallback_2',
                'title': '1970 Chevrolet Chevelle SS',
                'price': 62000,
                'year': 1970,
                'make': 'Chevrolet',
                'model': 'Chevelle',
                'mileage': 45000,
                'location': 'California, USA',
                'link': 'https://www.hemmings.com/classifieds/dealer/chevrolet/chevelle/2342568.html',
                'image': 'https://via.placeholder.com/300x200.png?text=1970+Chevelle+SS',
                'description': 'Numbers-matching 1970 Chevelle SS with 454 big block. Frame-off restoration completed.',
                'source': 'hemmings',
                'condition': 'Used',
                'seller_type': 'Dealer',
                'created_date': datetime.now().isoformat(),
                'body_style': 'Coupe',
                'exterior_color': 'Black',
                'engine': '454 V8',
                'transmission': 'Automatic'
            },
            {
                'id': 'hemmings_fallback_3',
                'title': '1969 Dodge Charger R/T',
                'price': 75000,
                'year': 1969,
                'make': 'Dodge',
                'model': 'Charger',
                'mileage': 52000,
                'location': 'Texas, USA',
                'link': 'https://www.hemmings.com/classifieds/dealer/dodge/charger/2342569.html',
                'image': 'https://via.placeholder.com/300x200.png?text=1969+Dodge+Charger',
                'description': 'Original 1969 Charger R/T with 440 Magnum engine. Documented history with build sheet.',
                'source': 'hemmings',
                'condition': 'Used',
                'seller_type': 'Private Party',
                'created_date': datetime.now().isoformat(),
                'body_style': 'Coupe',
                'exterior_color': 'Orange',
                'engine': '440 V8',
                'transmission': '4-Speed Manual'
            },
            {
                'id': 'hemmings_fallback_4',
                'title': '1963 Porsche 356B',
                'price': 125000,
                'year': 1963,
                'make': 'Porsche',
                'model': '356B',
                'mileage': 67000,
                'location': 'New York, USA',
                'link': 'https://www.hemmings.com/classifieds/dealer/porsche/356/2342570.html',
                'image': 'https://via.placeholder.com/300x200.png?text=1963+Porsche+356B',
                'description': 'Rare 1963 Porsche 356B Coupe. Matching numbers with complete restoration history.',
                'source': 'hemmings',
                'condition': 'Used',
                'seller_type': 'Dealer',
                'created_date': datetime.now().isoformat(),
                'body_style': 'Coupe',
                'exterior_color': 'Silver',
                'engine': 'Flat-4',
                'transmission': '4-Speed Manual'
            },
            {
                'id': 'hemmings_fallback_5',
                'title': '1955 Chevrolet Bel Air',
                'price': 38000,
                'year': 1955,
                'make': 'Chevrolet',
                'model': 'Bel Air',
                'mileage': 89000,
                'location': 'Florida, USA',
                'link': 'https://www.hemmings.com/classifieds/dealer/chevrolet/bel-air/2342571.html',
                'image': 'https://via.placeholder.com/300x200.png?text=1955+Bel+Air',
                'description': 'Beautiful 1955 Chevrolet Bel Air with original interior. Recent engine rebuild.',
                'source': 'hemmings',
                'condition': 'Used',
                'seller_type': 'Private Party',
                'created_date': datetime.now().isoformat(),
                'body_style': 'Sedan',
                'exterior_color': 'Blue',
                'engine': '265 V8',
                'transmission': 'Automatic'
            }
        ]
        
        logger.info(f"Generated {len(fallback_vehicles)} fallback Hemmings vehicles")
        return fallback_vehicles
    
    def _empty_response(self) -> Dict:
        """
        Return empty response structure
        """
        return {
            'vehicles': [],
            'total': 0,
            'page': 1,
            'per_page': 20,
            'source': 'hemmings'
        }
    
    def get_vehicle_details(self, vehicle_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific vehicle
        """
        try:
            # Extract URL from vehicle_id if needed
            if vehicle_id.startswith('hemmings_'):
                # Need to reconstruct URL or search RSS feed
                feed = feedparser.parse(self.RSS_FEEDS['cars'])
                for entry in feed.entries:
                    if vehicle_id in entry.get('link', ''):
                        return self._parse_rss_entry(entry)
            return None
        except Exception as e:
            logger.error(f"Error getting vehicle details: {str(e)}")
            return None

    def check_health(self) -> Dict:
        """
        Check Hemmings client status - currently using fallback data
        """
        try:
            # Test website accessibility
            response = self.session.get(self.BASE_URL, timeout=5)
            website_accessible = response.status_code == 200
            
            fallback_count = len(self._fallback_data)
            
            return {
                'source': 'hemmings',
                'status': 'degraded',  # Functional but using fallback data
                'response_time': response.elapsed.total_seconds() if website_accessible else 0,
                'message': f"Website accessible, using {fallback_count} fallback vehicles (RSS feeds blocked)",
                'details': {
                    'website_accessible': website_accessible,
                    'rss_blocked': True,
                    'fallback_vehicles': fallback_count
                }
            }
        except Exception as e:
            return {
                'source': 'hemmings',
                'status': 'unhealthy',
                'response_time': 0,
                'message': f"Website inaccessible: {str(e)}",
                'details': {
                    'website_accessible': False,
                    'rss_blocked': True,
                    'fallback_vehicles': len(self._fallback_data)
                }
            }