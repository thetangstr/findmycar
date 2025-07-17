import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import logging
import time
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class CarsComClient:
    """
    Client for scraping Cars.com vehicle listings.
    Uses web scraping since Cars.com doesn't have a public API.
    """
    
    def __init__(self):
        self.base_url = "https://www.cars.com"
        self.search_url = "https://www.cars.com/shopping/results/"
        
        # More realistic browser headers to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.verify = True
        
        # Add some delay between requests to be respectful
        self.request_delay = 2
    
    def search_listings(self, query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
        """
        Search for vehicle listings on Cars.com
        
        Args:
            query: Search query (make/model/keywords)
            filters: Dict with optional filters (make, model, year_min, year_max, price_min, price_max)
            limit: Number of results to return
            offset: Pagination offset
            
        Returns:
            List of vehicle dictionaries
        """
        try:
            # Build search parameters
            params = self._build_search_params(query, filters, limit, offset)
            
            # Add delay to be respectful
            time.sleep(self.request_delay)
            
            # Make request with retry logic
            for attempt in range(3):
                try:
                    logger.info(f"Cars.com search attempt {attempt + 1} for query: {query}")
                    response = self.session.get(self.search_url, params=params, timeout=45)
                    
                    logger.info(f"Cars.com response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        logger.info(f"Cars.com search successful, response size: {len(response.text)} chars")
                        break
                    elif response.status_code == 403:
                        logger.warning(f"Cars.com blocked request (403), attempt {attempt + 1}")
                        time.sleep(5)  # Longer delay for 403
                    else:
                        logger.warning(f"Cars.com search attempt {attempt + 1} failed with status {response.status_code}")
                        time.sleep(3)
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Cars.com search attempt {attempt + 1} failed: {e}")
                    time.sleep(3)
            else:
                logger.error("All Cars.com search attempts failed")
                # Cars.com is currently unavailable - return empty results
                logger.warning("Cars.com integration is currently unavailable due to access restrictions")
                return []
            
            # Parse the response
            vehicles = self._parse_search_results(response.text)
            return vehicles[:limit]  # Ensure we don't exceed limit
            
        except Exception as e:
            logger.error(f"Error searching Cars.com: {e}")
            logger.warning("Cars.com integration is currently unavailable")
            return []
    
    def _build_search_params(self, query: str, filters: Optional[Dict], limit: int, offset: int) -> Dict:
        """Build URL parameters for Cars.com search"""
        params = {
            'page': 1,
            'per_page': min(limit, 100),  # Cars.com typically uses per_page
            'sort': 'relevance',
            'stock_type': 'used'  # Focus on used cars
        }
        
        # Use query as keyword search - simpler approach
        if query:
            params['keyword'] = query.strip()
        
        # Apply filters if provided
        if filters:
            if filters.get('year_min'):
                params['year_min'] = filters['year_min']
            if filters.get('year_max'):
                params['year_max'] = filters['year_max']
            if filters.get('price_min'):
                params['price_min'] = filters['price_min']
            if filters.get('price_max'):
                params['price_max'] = filters['price_max']
        
        # Handle pagination
        if offset > 0:
            params['page'] = (offset // params['per_page']) + 1
        
        return params
    
    def _generate_realistic_cars_data(self, query: str, limit: int) -> List[Dict]:
        """Generate realistic Cars.com-style vehicle data"""
        try:
            logger.info(f"Generating realistic Cars.com data for: {query}")
            
            # Import the realistic data generator
            from cars_api_client import search_cars_listings as generate_realistic_data
            vehicles = generate_realistic_data(query, limit=limit)
            
            logger.info(f"Generated {len(vehicles)} realistic Cars.com vehicles")
            return vehicles
            
        except Exception as e:
            logger.error(f"Failed to generate realistic data: {e}")
            return self._get_sample_data(query, limit)
    
    def _parse_search_results(self, html: str) -> List[Dict]:
        """Parse vehicle listings from Cars.com search results HTML"""
        vehicles = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Debug: Save HTML snippet for analysis
            logger.debug(f"HTML snippet: {html[:1000]}...")
            
            # Try multiple selectors for Cars.com vehicle cards
            selectors_to_try = [
                'div[data-testid="result-tile"]',
                'div[class*="vehicle-card"]',
                'div[class*="listing-row"]',
                'div[class*="result-tile"]',
                'div[class*="vehicle-result"]',
                'article[class*="result"]',
                'div[class*="srp-list-item"]'
            ]
            
            vehicle_cards = []
            for selector in selectors_to_try:
                cards = soup.select(selector)
                if cards:
                    logger.info(f"Found {len(cards)} vehicles using selector: {selector}")
                    vehicle_cards = cards
                    break
            
            if not vehicle_cards:
                # Try more generic approach
                logger.warning("No vehicle cards found with specific selectors, trying generic approach")
                # Look for any div that contains price and title patterns
                all_divs = soup.find_all('div')
                for div in all_divs:
                    text = div.get_text() if div else ""
                    if ('$' in text and any(word in text.lower() for word in ['honda', 'toyota', 'bmw', 'ford', 'chevrolet', 'audi', 'lexus', 'nissan'])):
                        vehicle_cards.append(div)
                        if len(vehicle_cards) >= 10:  # Limit to prevent too many false positives
                            break
                logger.info(f"Generic approach found {len(vehicle_cards)} potential vehicle cards")
            
            for card in vehicle_cards:
                try:
                    vehicle_data = self._extract_vehicle_data(card)
                    if vehicle_data:
                        vehicles.append(vehicle_data)
                except Exception as e:
                    logger.debug(f"Error parsing vehicle card: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(vehicles)} vehicles from Cars.com")
            
        except Exception as e:
            logger.error(f"Error parsing Cars.com search results: {e}")
        
        return vehicles
    
    def _extract_vehicle_data(self, card) -> Optional[Dict]:
        """Extract vehicle data from a single Cars.com listing card"""
        try:
            vehicle = {
                'source': 'cars.com',
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
                'vehicle_details': {}
            }
            
            # Get all text for analysis
            card_text = card.get_text() if card else ""
            
            # Extract title - try multiple approaches
            title_selectors = ['h2', 'h3', 'h4', '[data-testid*="title"]', 'a[href*="/vehicledetail/"]']
            title = None
            for selector in title_selectors:
                title_elem = card.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 10:  # Reasonable title length
                        break
            
            if not title:
                # Fallback: look for patterns in text
                lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                for line in lines:
                    # Look for year + make pattern
                    if re.match(r'\d{4}\s+[A-Za-z]+', line) and len(line) > 10:
                        title = line
                        break
            
            if title:
                vehicle['title'] = title
                
                # Extract year, make, model from title
                title_match = re.match(r'(\d{4})\s+([A-Za-z-]+)\s+(.+)', title)
                if title_match:
                    vehicle['year'] = int(title_match.group(1))
                    vehicle['make'] = title_match.group(2)
                    vehicle['model'] = title_match.group(3).split()[0]
            
            # Extract price - more robust approach
            price_patterns = [
                r'\$(\d{1,3}(?:,\d{3})*)',
                r'(\d{1,3}(?:,\d{3})*)\s*dollars?',
                r'Price:?\s*\$?(\d{1,3}(?:,\d{3})*)'
            ]
            
            for pattern in price_patterns:
                price_match = re.search(pattern, card_text, re.IGNORECASE)
                if price_match:
                    try:
                        price_str = price_match.group(1).replace(',', '')
                        price = float(price_str)
                        if 1000 <= price <= 500000:  # Reasonable price range
                            vehicle['price'] = price
                            break
                    except ValueError:
                        continue
            
            # Extract mileage
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi\.?)',
                r'Mileage:?\s*(\d{1,3}(?:,\d{3})*)',
                r'(\d{1,3})k\s*(?:miles?|mi\.?)'
            ]
            
            for pattern in mileage_patterns:
                mileage_match = re.search(pattern, card_text, re.IGNORECASE)
                if mileage_match:
                    try:
                        mileage_str = mileage_match.group(1).replace(',', '')
                        mileage = int(mileage_str)
                        if 'k' in mileage_match.group(0).lower():
                            mileage *= 1000
                        if mileage <= 500000:  # Reasonable mileage
                            vehicle['mileage'] = mileage
                            break
                    except ValueError:
                        continue
            
            # Extract location
            location_patterns = [
                r'([A-Za-z\s]+,\s*[A-Z]{2})',  # City, ST format
                r'Location:?\s*([A-Za-z\s,]+)'
            ]
            
            for pattern in location_patterns:
                location_match = re.search(pattern, card_text)
                if location_match:
                    location = location_match.group(1).strip()
                    if len(location) > 3:
                        vehicle['location'] = location
                        break
            
            # Extract image URL
            img_elem = card.find('img')
            if img_elem and img_elem.get('src'):
                src = img_elem['src']
                if src.startswith('http') or src.startswith('//'):
                    vehicle['image_urls'] = [src]
            
            # Extract listing URL
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    vehicle['view_item_url'] = self.base_url + href
                elif href.startswith('http'):
                    vehicle['view_item_url'] = href
                
                # Generate listing ID
                if href:
                    id_match = re.search(r'/(\d+)/', href)
                    if id_match:
                        vehicle['listing_id'] = f"cars_{id_match.group(1)}"
                    else:
                        # Generate ID from URL hash
                        import hashlib
                        vehicle['listing_id'] = f"cars_{hashlib.md5(href.encode()).hexdigest()[:8]}"
            
            # Generate fallback listing ID if none found
            if not vehicle['listing_id'] and vehicle['title']:
                import hashlib
                vehicle['listing_id'] = f"cars_{hashlib.md5(vehicle['title'].encode()).hexdigest()[:8]}"
            
            # Only return if we have essential data
            if vehicle['title'] and vehicle['price']:
                return vehicle
            
        except Exception as e:
            logger.debug(f"Error extracting vehicle data: {e}")
        
        return None
    
    def _get_sample_data(self, query: str, limit: int) -> List[Dict]:
        """Generate sample Cars.com data for testing when site is unavailable"""
        import random
        
        # Extract make/model from query if possible
        query_lower = query.lower()
        sample_make = "Honda"
        sample_model = "Civic"
        
        if "honda" in query_lower:
            sample_make = "Honda"
            if "civic" in query_lower:
                sample_model = "Civic"
            elif "accord" in query_lower:
                sample_model = "Accord"
            elif "crv" in query_lower or "cr-v" in query_lower:
                sample_model = "CR-V"
        elif "toyota" in query_lower:
            sample_make = "Toyota"
            if "camry" in query_lower:
                sample_model = "Camry"
            elif "corolla" in query_lower:
                sample_model = "Corolla"
            elif "prius" in query_lower:
                sample_model = "Prius"
        elif "ford" in query_lower:
            sample_make = "Ford"
            sample_model = "Focus"
        
        sample_vehicles = []
        for i in range(min(limit, 5)):  # Generate up to 5 sample vehicles
            year = random.randint(2018, 2023)
            price = random.randint(15000, 35000)
            mileage = random.randint(20000, 80000)
            
            vehicle = {
                'source': 'cars.com',
                'listing_id': f'cars_sample_{i+1}_{random.randint(100000, 999999)}',
                'title': f'{year} {sample_make} {sample_model}',
                'price': price,
                'location': random.choice(['Los Angeles, CA', 'New York, NY', 'Chicago, IL', 'Houston, TX', 'Phoenix, AZ']),
                'image_urls': ['https://via.placeholder.com/300x200?text=Sample+Car'],
                'view_item_url': f'https://www.cars.com/vehicledetail/sample-{i+1}/',
                'make': sample_make,
                'model': sample_model,
                'year': year,
                'mileage': mileage,
                'condition': 'Used',
                'vehicle_details': {
                    'sample': True,
                    'note': 'This is sample data used when Cars.com is unavailable'
                }
            }
            sample_vehicles.append(vehicle)
        
        logger.info(f"Generated {len(sample_vehicles)} sample Cars.com vehicles")
        return sample_vehicles

def search_cars_listings(query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
    """
    Public interface for searching Cars.com listings
    """
    client = CarsComClient()
    return client.search_listings(query, filters, limit, offset)