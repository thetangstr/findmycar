"""
Enhanced TrueCar client with advanced anti-bot evasion and geographic workarounds
Designed to bypass TrueCar's restrictions and anti-bot measures
"""

import requests
import re
import json
import logging
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urlencode, quote
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class TrueCarClient:
    """
    Enhanced TrueCar client with advanced anti-bot evasion
    Uses multiple strategies to bypass geographic and anti-bot restrictions
    """
    
    def __init__(self, use_proxy=False, proxy_list=None, use_selenium=True):
        self.base_url = "https://www.truecar.com"
        self.search_url = "https://www.truecar.com/used-cars-for-sale/listings"
        
        # Enhanced anti-bot measures
        self.ua = UserAgent()
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.current_proxy_index = 0
        self.use_selenium = use_selenium
        
        # Session management
        self.session = requests.Session()
        self.failed_requests = 0
        self.max_failures = 3
        
        # Request delays with randomization
        self.request_delays = [2.0, 2.5, 3.0, 3.5, 4.0]
        
        # Setup enhanced headers
        self._setup_session_headers()
        
        # Chrome options for Selenium fallback
        self.chrome_options = Options()
        self._setup_chrome_options()
        
        self.driver = None
        
        # Geographic workaround - use multiple ZIP codes
        self.zip_codes = ['10001', '90210', '60601', '30301', '77001', '94101', '02101']
        
    def _setup_session_headers(self):
        """Setup session with enhanced anti-detection headers"""
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
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
            'sec-ch-ua': '"Google Chrome";v="121", "Not A(Brand";v="99", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.session.headers.update(headers)
        
    def _setup_chrome_options(self):
        """Setup Chrome options for enhanced stealth"""
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
        # Enhanced stealth
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-plugins")
        
        # Random user agent
        self.chrome_options.add_argument(f"--user-agent={self.ua.random}")
        
        # Anti-detection
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Geographic spoofing
        prefs = {
            "profile.default_content_setting_values.geolocation": 1,
            "profile.managed_default_content_settings.geolocation": 1
        }
        self.chrome_options.add_experimental_option("prefs", prefs)
    
    def _get_driver(self):
        """Get or create Selenium WebDriver with geographic spoofing"""
        if self.driver is None:
            try:
                # Use proxy if configured
                if self.use_proxy and self.proxy_list:
                    proxy = self.proxy_list[self.current_proxy_index % len(self.proxy_list)]
                    self.chrome_options.add_argument(f"--proxy-server={proxy}")
                    self.current_proxy_index += 1
                    logger.info(f"Using proxy: {proxy}")
                
                # Auto-manage ChromeDriver
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
                
                # Enhanced stealth and geographic spoofing
                stealth_scripts = [
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
                    "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
                    "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
                    "window.chrome = {runtime: {}}",
                    """Object.defineProperty(navigator, 'geolocation', {
                        get: () => ({
                            getCurrentPosition: (success) => {
                                setTimeout(() => {
                                    success({
                                        coords: {
                                            latitude: 40.7128,
                                            longitude: -74.0060,
                                            accuracy: 20
                                        }
                                    });
                                }, 100);
                            }
                        })
                    })"""
                ]
                
                for script in stealth_scripts:
                    try:
                        self.driver.execute_script(script)
                    except:
                        pass
                        
            except Exception as e:
                logger.error(f"Failed to create Chrome driver: {e}")
                # Fallback to basic options
                basic_options = Options()
                basic_options.add_argument("--headless")
                basic_options.add_argument("--no-sandbox")
                self.driver = webdriver.Chrome(options=basic_options)
        
        return self.driver
    
    def search_listings(self, query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
        """
        Enhanced search with multiple fallback strategies and geographic workarounds
        
        Args:
            query: Search query (make/model/keywords)
            filters: Optional filters (year_min, year_max, price_min, price_max, zip_code)
            limit: Number of results to return
            offset: Pagination offset
            
        Returns:
            List of vehicle dictionaries
        """
        # Try multiple geographic locations to bypass restrictions
        for zip_code in self.zip_codes:
            try:
                # Update filters with current ZIP code
                current_filters = filters.copy() if filters else {}
                current_filters['zip_code'] = zip_code
                
                logger.info(f"TrueCar: Attempting search with ZIP {zip_code}")
                
                # Try requests-based approach first (faster)
                if not self.use_selenium:
                    vehicles = self._search_with_requests(query, current_filters, limit, offset)
                    if vehicles:
                        logger.info(f"TrueCar: Found {len(vehicles)} vehicles via requests (ZIP: {zip_code})")
                        return vehicles
                
                # Fallback to Selenium
                vehicles = self._search_with_selenium(query, current_filters, limit, offset)
                if vehicles:
                    logger.info(f"TrueCar: Found {len(vehicles)} vehicles via Selenium (ZIP: {zip_code})")
                    return vehicles
                    
            except Exception as e:
                logger.debug(f"TrueCar search failed for ZIP {zip_code}: {e}")
                continue
        
        logger.warning("TrueCar: All geographic locations failed")
        return []
    
    def _search_with_requests(self, query: str, filters: Dict, limit: int, offset: int) -> List[Dict]:
        """Try to search using requests first (faster if successful)"""
        try:
            # Random delay with failure adaptation
            delay = random.choice(self.request_delays)
            if self.failed_requests > 0:
                delay *= (1 + (self.failed_requests * 0.3))
            time.sleep(delay)
            
            # Build search URL
            search_url = self._build_search_url(query, filters, offset)
            
            logger.info(f"TrueCar requests: {search_url}")
            
            # Rotate user agent and add geographic headers
            self.session.headers['User-Agent'] = self.ua.random
            self.session.headers['X-Forwarded-For'] = self._get_fake_ip()
            
            response = self.session.get(search_url, timeout=30)
            
            if response.status_code == 200:
                # Check for geographic blocking
                if 'not available in your area' in response.text.lower() or 'geographic restriction' in response.text.lower():
                    logger.warning("TrueCar: Geographic restriction detected")
                    return []
                
                # Try to extract from HTML
                vehicles = self._parse_html_listings(response.text)
                if vehicles:
                    return vehicles[:limit]
            elif response.status_code == 403:
                logger.warning("TrueCar: Blocked by anti-bot (403)")
                self.failed_requests += 1
            elif response.status_code == 451:
                logger.warning("TrueCar: Geographic restriction (451)")
                return []
            
        except Exception as e:
            logger.debug(f"TrueCar requests failed: {e}")
            self.failed_requests += 1
        
        return []
    
    def _search_with_selenium(self, query: str, filters: Dict, limit: int, offset: int) -> List[Dict]:
        """Enhanced Selenium search with geographic spoofing"""
        try:
            driver = self._get_driver()
            vehicles = []
            
            # Build search URL
            search_url = self._build_search_url(query, filters, offset)
            
            logger.info(f"TrueCar Selenium: {search_url}")
            
            # Navigate with human-like behavior
            driver.get(search_url)
            
            # Check for geographic blocking
            page_source = driver.page_source.lower()
            if 'not available in your area' in page_source or 'geographic restriction' in page_source:
                logger.warning("TrueCar: Geographic restriction detected in Selenium")
                return []
            
            # Wait for content to load
            time.sleep(random.uniform(3, 6))
            
            # Try multiple selectors for listings
            listing_selectors = [
                "[data-test*='listing']",
                ".vehicle-card",
                ".listing-card",
                "[class*='listing']",
                "[data-testid*='vehicle']",
                ".search-result"
            ]
            
            listing_cards = []
            for selector in listing_selectors:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    listing_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                    if listing_cards:
                        logger.info(f"Found {len(listing_cards)} TrueCar listings with selector: {selector}")
                        break
                except TimeoutException:
                    continue
            
            if not listing_cards:
                # Try JSON extraction from page source
                vehicles = self._extract_json_from_page_source(driver.page_source)
                if vehicles:
                    return vehicles[:limit]
                
                logger.warning("No TrueCar listings found with any selector")
                return []
            
            # Extract vehicle data
            for i, card in enumerate(listing_cards[:limit]):
                try:
                    vehicle_data = self._extract_vehicle_data_from_selenium_card(card, driver)
                    if vehicle_data:
                        vehicles.append(vehicle_data)
                        logger.debug(f"Extracted TrueCar vehicle {i+1}: {vehicle_data.get('title', 'Unknown')}")
                    
                    # Human-like delays
                    if i < len(listing_cards) - 1:
                        time.sleep(random.uniform(0.3, 0.8))
                        
                except Exception as e:
                    logger.debug(f"Error extracting TrueCar vehicle data from card {i}: {e}")
                    continue
            
            logger.info(f"TrueCar Selenium: Successfully extracted {len(vehicles)} vehicles")
            return vehicles
            
        except Exception as e:
            logger.error(f"TrueCar Selenium error: {e}")
            return []
    
    def _build_search_url(self, query: str, filters: Dict, offset: int) -> str:
        """Build optimized TrueCar search URL"""
        # Parse query for make/model
        query_parts = query.lower().split()
        
        # Extract make and model
        make = None
        model = None
        
        make_mapping = {
            'honda': 'honda', 'toyota': 'toyota', 'ford': 'ford',
            'chevrolet': 'chevrolet', 'chevy': 'chevrolet', 'nissan': 'nissan',
            'bmw': 'bmw', 'mercedes': 'mercedes-benz', 'benz': 'mercedes-benz',
            'audi': 'audi', 'volkswagen': 'volkswagen', 'vw': 'volkswagen',
            'hyundai': 'hyundai', 'kia': 'kia', 'mazda': 'mazda',
            'subaru': 'subaru', 'lexus': 'lexus', 'acura': 'acura',
            'infiniti': 'infiniti', 'tesla': 'tesla', 'jeep': 'jeep',
            'dodge': 'dodge', 'ram': 'ram', 'gmc': 'gmc'
        }
        
        for part in query_parts:
            if part in make_mapping and not make:
                make = make_mapping[part]
            elif make and not model:
                model = part
                break
        
        # Build URL path
        path_parts = []
        if make:
            path_parts.append(make)
            if model:
                path_parts.append(model)
        
        # Base URL construction
        if path_parts:
            url = f"{self.search_url}/{'/'.join(path_parts)}/"
        else:
            url = self.search_url + "/"
        
        # Add query parameters
        params = {
            'zipcode': filters.get('zip_code', '10001')
        }
        
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
            params['page'] = (offset // 20) + 1
        
        if params:
            url += '?' + urlencode(params)
            
        return url
    
    def _get_fake_ip(self) -> str:
        """Generate a fake US IP for geographic spoofing"""
        # Generate random US IP addresses
        us_ip_ranges = [
            "73.{}.{}.{}",   # Comcast
            "108.{}.{}.{}",  # AT&T
            "76.{}.{}.{}",   # Verizon
            "98.{}.{}.{}"    # Various US ISPs
        ]
        
        ip_template = random.choice(us_ip_ranges)
        return ip_template.format(
            random.randint(1, 254),
            random.randint(1, 254),
            random.randint(1, 254)
        )
    
    def _parse_html_listings(self, html: str) -> List[Dict]:
        """Parse listings from HTML (requests fallback)"""
        vehicles = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for JSON data in script tags
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('listings' in script.string or 'searchResults' in script.string or 'inventory' in script.string):
                    try:
                        # Try different JSON extraction patterns
                        json_patterns = [
                            r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
                            r'window\.__PRELOADED_STATE__\s*=\s*({.+?});',
                            r'"listings"\s*:\s*(\[.+?\])',
                            r'"inventory"\s*:\s*({.+?})',
                            r'"searchResults"\s*:\s*({.+?})'
                        ]
                        
                        for pattern in json_patterns:
                            match = re.search(pattern, script.string, re.DOTALL)
                            if match:
                                try:
                                    data = json.loads(match.group(1))
                                    extracted_vehicles = self._extract_vehicles_from_json(data)
                                    vehicles.extend(extracted_vehicles)
                                    if vehicles:
                                        break
                                except:
                                    continue
                        
                        if vehicles:
                            break
                            
                    except Exception as e:
                        logger.debug(f"Error parsing script JSON: {e}")
                        continue
            
            # Fallback to HTML parsing
            if not vehicles:
                vehicles = self._parse_html_cards(soup)
            
            return vehicles
            
        except Exception as e:
            logger.debug(f"Error parsing HTML listings: {e}")
            return []
    
    def _extract_json_from_page_source(self, page_source: str) -> List[Dict]:
        """Extract vehicles from page source JSON data"""
        return self._parse_html_listings(page_source)
    
    def _extract_vehicles_from_json(self, data: Dict) -> List[Dict]:
        """Extract vehicles from JSON data structure"""
        vehicles = []
        
        try:
            # Navigate through different possible data structures
            listings = []
            
            if isinstance(data, list):
                listings = data
            elif 'listings' in data:
                listings = data['listings']
            elif 'searchResults' in data:
                search_results = data['searchResults']
                if isinstance(search_results, dict):
                    listings = search_results.get('listings', search_results.get('vehicles', []))
                else:
                    listings = search_results
            elif 'inventory' in data:
                inventory = data['inventory']
                if isinstance(inventory, dict):
                    listings = inventory.get('listings', inventory.get('vehicles', []))
                else:
                    listings = inventory
            elif 'vehicles' in data:
                listings = data['vehicles']
            
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
                'listing_id': f"truecar_{listing.get('id', listing.get('vehicleId', ''))}",
                'title': None,
                'price': None,
                'location': None,
                'image_urls': [],
                'view_item_url': None,
                'make': listing.get('make', listing.get('makeName', '')),
                'model': listing.get('model', listing.get('modelName', '')),
                'year': listing.get('year', ''),
                'mileage': listing.get('mileage', listing.get('odometer', '')),
                'condition': listing.get('condition', 'Used'),
                'vehicle_details': {},
                'truecar_price_analysis': {},
                'dealer_name': None
            }
            
            # Build title
            if vehicle['year'] and vehicle['make'] and vehicle['model']:
                vehicle['title'] = f"{vehicle['year']} {vehicle['make']} {vehicle['model']}"
                trim = listing.get('trim', listing.get('trimName', ''))
                if trim:
                    vehicle['title'] += f" {trim}"
            
            # Extract price
            price_fields = ['listPrice', 'price', 'askingPrice', 'msrp']
            for field in price_fields:
                if listing.get(field):
                    vehicle['price'] = listing[field]
                    break
            
            # TrueCar specific pricing data
            vehicle['truecar_price_analysis'] = {
                'market_average': listing.get('marketAverage', listing.get('averagePrice', 0)),
                'price_rating': listing.get('priceRating', listing.get('dealRating', '')),
                'days_on_market': listing.get('daysOnMarket', 0),
                'price_drop': listing.get('priceDrop', 0),
                'below_market': listing.get('belowMarketPrice', listing.get('savings', 0))
            }
            
            # Location and dealer
            dealer = listing.get('dealer', listing.get('seller', {}))
            if dealer:
                vehicle['dealer_name'] = dealer.get('name', dealer.get('dealerName', ''))
                location = dealer.get('location', dealer.get('address', {}))
                if location:
                    city = location.get('city', '')
                    state = location.get('state', location.get('stateCode', ''))
                    vehicle['location'] = f"{city}, {state}".strip(', ')
            
            # Images
            images = listing.get('images', listing.get('photos', []))
            if images:
                vehicle['image_urls'] = [img.get('url', img) for img in images if isinstance(img, (str, dict))]
            elif listing.get('primaryImage', listing.get('mainImage')):
                vehicle['image_urls'] = [listing.get('primaryImage', listing.get('mainImage'))]
            
            # URL
            url_fields = ['vdpUrl', 'url', 'detailUrl', 'link']
            for field in url_fields:
                if listing.get(field):
                    url = listing[field]
                    if url.startswith('/'):
                        vehicle['view_item_url'] = self.base_url + url
                    else:
                        vehicle['view_item_url'] = url
                    break
            
            # Additional details
            vehicle['vehicle_details'] = {
                'vin': listing.get('vin', ''),
                'exterior_color': listing.get('exteriorColor', listing.get('color', '')),
                'interior_color': listing.get('interiorColor', ''),
                'drivetrain': listing.get('drivetrain', listing.get('driveType', '')),
                'transmission': listing.get('transmission', listing.get('transmissionType', '')),
                'fuel_type': listing.get('fuelType', listing.get('engine', {}).get('fuelType', '')),
                'mpg_city': listing.get('mpgCity', listing.get('fuelEconomy', {}).get('city', '')),
                'mpg_highway': listing.get('mpgHighway', listing.get('fuelEconomy', {}).get('highway', '')),
                'features': listing.get('features', listing.get('options', []))
            }
            
            # Only return if we have essential data
            if vehicle['title'] and vehicle['price']:
                return vehicle
                
        except Exception as e:
            logger.debug(f"Error parsing JSON listing: {e}")
            
        return None
    
    def _parse_html_cards(self, soup) -> List[Dict]:
        """Parse vehicle cards from HTML soup"""
        vehicles = []
        
        try:
            # Try different card selectors
            card_selectors = [
                '[data-test*="listing"]',
                '.vehicle-card',
                '.listing-card',
                '[class*="listing"]',
                '[data-testid*="vehicle"]',
                '.search-result'
            ]
            
            for selector in card_selectors:
                cards = soup.select(selector)
                if cards:
                    logger.info(f"Found {len(cards)} HTML cards with selector: {selector}")
                    for card in cards[:25]:  # Limit to prevent too many
                        try:
                            vehicle = self._extract_vehicle_from_html_card(card)
                            if vehicle:
                                vehicles.append(vehicle)
                        except Exception as e:
                            logger.debug(f"Error parsing HTML card: {e}")
                            continue
                    break
            
            return vehicles
            
        except Exception as e:
            logger.debug(f"Error parsing HTML cards: {e}")
            return []
    
    def _extract_vehicle_from_html_card(self, card) -> Optional[Dict]:
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
            title_selectors = ['h3', 'h4', '[class*="heading"]', '[class*="title"]']
            for selector in title_selectors:
                title_elem = card.select_one(selector)
                if title_elem:
                    vehicle['title'] = title_elem.get_text(strip=True)
                    
                    # Parse year, make, model from title
                    title_match = re.match(r'(\d{4})\s+([A-Za-z-]+)\s+(.+)', vehicle['title'])
                    if title_match:
                        vehicle['year'] = int(title_match.group(1))
                        vehicle['make'] = title_match.group(2)
                        vehicle['model'] = title_match.group(3).split()[0]
                    break
            
            # Extract price
            price_selectors = ['[class*="price"]', '[data-test*="price"]']
            for selector in price_selectors:
                price_elem = card.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text()
                    price_match = re.search(r'\$?([\d,]+)', price_text)
                    if price_match:
                        vehicle['price'] = float(price_match.group(1).replace(',', ''))
                        break
            
            # Extract mileage
            card_text = card.get_text()
            mileage_match = re.search(r'([\d,]+)\s*(mi|miles)', card_text, re.I)
            if mileage_match:
                vehicle['mileage'] = int(mileage_match.group(1).replace(',', ''))
            
            # Extract location
            location_selectors = ['[class*="location"]', '[class*="dealer"]']
            for selector in location_selectors:
                location_elem = card.select_one(selector)
                if location_elem:
                    vehicle['location'] = location_elem.get_text(strip=True)
                    break
            
            # Extract image
            img_elem = card.select_one('img')
            if img_elem and img_elem.get('src'):
                vehicle['image_urls'] = [img_elem['src']]
            
            # Extract URL
            link_elem = card.select_one('a[href]')
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
            logger.debug(f"Error extracting vehicle from HTML card: {e}")
            
        return None
    
    def _extract_vehicle_data_from_selenium_card(self, card, driver) -> Optional[Dict]:
        """Extract vehicle data from Selenium card element"""
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
            title_selectors = ['h3', 'h4', '[class*="heading"]', '[class*="title"]']
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    vehicle['title'] = title_elem.text.strip()
                    
                    # Parse year, make, model from title
                    title_match = re.match(r'(\d{4})\s+([A-Za-z-]+)\s+(.+)', vehicle['title'])
                    if title_match:
                        vehicle['year'] = int(title_match.group(1))
                        vehicle['make'] = title_match.group(2)
                        vehicle['model'] = title_match.group(3).split()[0]
                    break
                except NoSuchElementException:
                    continue
            
            # Extract price
            price_selectors = ['[class*="price"]', '[data-test*="price"]']
            for selector in price_selectors:
                try:
                    price_elem = card.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_elem.text
                    price_match = re.search(r'\$?([\d,]+)', price_text)
                    if price_match:
                        vehicle['price'] = float(price_match.group(1).replace(',', ''))
                        break
                except NoSuchElementException:
                    continue
            
            # Extract mileage
            card_text = card.text
            mileage_match = re.search(r'([\d,]+)\s*(mi|miles)', card_text, re.I)
            if mileage_match:
                vehicle['mileage'] = int(mileage_match.group(1).replace(',', ''))
            
            # Extract location
            location_selectors = ['[class*="location"]', '[class*="dealer"]']
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    vehicle['location'] = location_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Extract image
            try:
                img_elem = card.find_element(By.CSS_SELECTOR, 'img')
                img_url = img_elem.get_attribute('src')
                if img_url:
                    vehicle['image_urls'] = [img_url]
            except NoSuchElementException:
                pass
            
            # Extract URL
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, 'a')
                href = link_elem.get_attribute('href')
                if href:
                    vehicle['view_item_url'] = href
                    
                    # Generate listing ID from URL
                    id_match = re.search(r'/(\d+)/', href)
                    if id_match:
                        vehicle['listing_id'] = f"truecar_{id_match.group(1)}"
                    else:
                        import hashlib
                        vehicle['listing_id'] = f"truecar_{hashlib.md5(href.encode()).hexdigest()[:8]}"
            except NoSuchElementException:
                pass
            
            # Only return if we have essential data
            if vehicle['title'] and vehicle['price'] and vehicle['listing_id']:
                return vehicle
                
        except Exception as e:
            logger.debug(f"Error extracting vehicle from Selenium card: {e}")
            
        return None
    
    def close(self):
        """Close the client and cleanup resources"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except:
                pass
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()


# Convenience function for backward compatibility
def search_truecar_listings(query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
    """
    Public interface for searching TrueCar listings with enhanced evasion
    """
    client = TrueCarClient()
    try:
        return client.search_listings(query, filters, limit, offset)
    finally:
        client.close()