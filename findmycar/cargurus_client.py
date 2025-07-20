"""
CarGurus client for scraping vehicle listings
Uses Selenium WebDriver since CarGurus requires JavaScript rendering
"""

import re
import logging
import time
import random
import json
import requests
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class CarGurusClient:
    """
    Advanced CarGurus client with enhanced anti-bot evasion
    Uses multiple strategies to bypass detection
    """
    
    def __init__(self, use_proxy=False, proxy_list=None, use_selenium=True):
        self.base_url = "https://www.cargurus.com"
        self.search_url = "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action"
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.current_proxy_index = 0
        self.use_selenium = use_selenium
        
        # Enhanced anti-bot measures
        self.ua = UserAgent()
        self.session = requests.Session()
        
        # Rotating headers and delays
        self.request_delays = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        self.failed_requests = 0
        self.max_failures = 3
        
        # Setup session headers
        self._setup_session_headers()
        
        # Chrome options for enhanced stealth
        self.chrome_options = Options()
        self._setup_chrome_options()
        
        self.driver = None
        
    def _setup_session_headers(self):
        """Setup session with rotating headers"""
        headers = {
            'User-Agent': self.ua.random,
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
        self.session.headers.update(headers)
    
    def _setup_chrome_options(self):
        """Setup enhanced Chrome options for stealth mode"""
        # Basic options
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
        # Enhanced stealth options
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-plugins")
        self.chrome_options.add_argument("--disable-images")
        self.chrome_options.add_argument("--disable-javascript")
        
        # Random user agent
        self.chrome_options.add_argument(f"--user-agent={self.ua.random}")
        
        # Anti-detection
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Additional stealth prefs
        prefs = {
            "profile.default_content_setting_values": {
                "images": 2,
                "plugins": 2,
                "popups": 2,
                "geolocation": 2,
                "notifications": 2,
                "auto_select_certificate": 2
            }
        }
        self.chrome_options.add_experimental_option("prefs", prefs)
    
    def _get_driver(self):
        """Get or create enhanced Selenium WebDriver"""
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
                
                # Enhanced stealth scripts
                stealth_scripts = [
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
                    "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
                    "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
                    "window.chrome = {runtime: {}}",
                    "Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})})"
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
    
    def _close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def _wait_random_delay(self):
        """Enhanced random delay with failure adaptation"""
        base_delay = random.choice(self.request_delays)
        
        # Increase delay if we've had failures
        if self.failed_requests > 0:
            base_delay *= (1 + (self.failed_requests * 0.5))
        
        # Add randomization
        delay = base_delay + random.uniform(-0.5, 0.5)
        time.sleep(max(delay, 1.0))  # Minimum 1 second
    
    def search_listings(self, query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
        """
        Enhanced search with multiple fallback strategies
        
        Args:
            query: Search query (make/model/keywords)
            filters: Optional filters (year_min, year_max, price_min, price_max, zip_code)
            limit: Number of results to return
            offset: Pagination offset
            
        Returns:
            List of vehicle dictionaries
        """
        # Try requests-based approach first (faster)
        if not self.use_selenium:
            vehicles = self._search_with_requests(query, filters, limit, offset)
            if vehicles:
                logger.info(f"CarGurus: Found {len(vehicles)} vehicles via requests")
                return vehicles
            else:
                logger.info("CarGurus: Requests method failed, falling back to Selenium")
        
        # Fallback to Selenium with enhanced evasion
        return self._search_with_selenium(query, filters, limit, offset)
    
    def _search_with_requests(self, query: str, filters: Optional[Dict], limit: int, offset: int) -> List[Dict]:
        """Try to search using requests first (faster if successful)"""
        try:
            # Random delay
            time.sleep(random.choice(self.request_delays))
            
            # Build search URL
            search_url = self._build_search_url(query, filters, offset)
            
            logger.info(f"CarGurus requests: {search_url}")
            
            # Rotate user agent
            self.session.headers['User-Agent'] = self.ua.random
            
            response = self.session.get(search_url, timeout=30)
            
            if response.status_code == 200:
                # Try to extract from HTML
                vehicles = self._parse_html_listings(response.text)
                if vehicles:
                    return vehicles[:limit]
            elif response.status_code == 403:
                logger.warning("CarGurus: Blocked by anti-bot (403)")
                self.failed_requests += 1
            
        except Exception as e:
            logger.debug(f"CarGurus requests failed: {e}")
            self.failed_requests += 1
        
        return []
    
    def _search_with_selenium(self, query: str, filters: Optional[Dict], limit: int, offset: int) -> List[Dict]:
        """Enhanced Selenium search with better evasion"""
        try:
            driver = self._get_driver()
            vehicles = []
            
            # Build search URL
            search_url = self._build_search_url(query, filters, offset)
            
            logger.info(f"CarGurus Selenium: {search_url}")
            
            # Navigate with human-like behavior
            driver.get(search_url)
            
            # Random delay to simulate human behavior
            time.sleep(random.uniform(3, 6))
            
            # Try multiple selectors for listings
            listing_selectors = [
                "[data-cg-ft='srp-listing-blade']",
                ".carGurus-listings-item",
                ".srp-listing",
                "[data-testid*='listing']",
                ".listing-row"
            ]
            
            listing_cards = []
            for selector in listing_selectors:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    listing_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                    if listing_cards:
                        logger.info(f"Found {len(listing_cards)} listings with selector: {selector}")
                        break
                except TimeoutException:
                    continue
            
            if not listing_cards:
                logger.warning("No CarGurus listings found with any selector")
                return []
            
            # Extract vehicle data with enhanced error handling
            for i, card in enumerate(listing_cards[:limit]):
                try:
                    vehicle_data = self._extract_vehicle_data_from_card(card, driver)
                    if vehicle_data:
                        vehicles.append(vehicle_data)
                        logger.debug(f"Extracted vehicle {i+1}: {vehicle_data.get('title', 'Unknown')}")
                    
                    # Human-like delays
                    if i < len(listing_cards) - 1:
                        time.sleep(random.uniform(0.3, 0.8))
                        
                except Exception as e:
                    logger.debug(f"Error extracting vehicle data from card {i}: {e}")
                    continue
            
            logger.info(f"CarGurus Selenium: Successfully extracted {len(vehicles)} vehicles")
            return vehicles
            
        except Exception as e:
            logger.error(f"CarGurus Selenium error: {e}")
            return []
    
    def _build_search_url(self, query: str, filters: Optional[Dict], offset: int) -> str:
        """Build optimized search URL"""
        # Parse query for make/model
        query_parts = query.lower().split()
        
        # Extract make and model from query
        make = None
        model = None
        
        make_mapping = {
            'honda': 'Honda', 'toyota': 'Toyota', 'ford': 'Ford',
            'chevrolet': 'Chevrolet', 'chevy': 'Chevrolet', 'nissan': 'Nissan',
            'bmw': 'BMW', 'mercedes': 'Mercedes-Benz', 'audi': 'Audi',
            'volkswagen': 'Volkswagen', 'vw': 'Volkswagen', 'hyundai': 'Hyundai',
            'kia': 'Kia', 'mazda': 'Mazda', 'subaru': 'Subaru',
            'lexus': 'Lexus', 'acura': 'Acura', 'infiniti': 'INFINITI'
        }
        
        for part in query_parts:
            if part in make_mapping and not make:
                make = make_mapping[part]
            elif make and not model:
                model = part.capitalize()
                break
        
        # Build base URL
        base_url = "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action"
        
        # Add parameters
        params = {
            'sourceContext': 'carGurusHomePageModel',
            'entitySelectingHelper.selectedEntity': '',
            'zip': filters.get('zip_code', '10001') if filters else '10001'
        }
        
        if make:
            params['selectedMakeName'] = make
        if model:
            params['selectedModelName'] = model
            
        if filters:
            if filters.get('year_min'):
                params['minYear'] = filters['year_min']
            if filters.get('year_max'):
                params['maxYear'] = filters['year_max']
            if filters.get('price_min'):
                params['minPrice'] = filters['price_min']
            if filters.get('price_max'):
                params['maxPrice'] = filters['price_max']
            if filters.get('mileage_max'):
                params['maxMileage'] = filters['mileage_max']
        
        # Handle pagination
        if offset > 0:
            params['offset'] = offset
        
        # Build final URL
        param_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f"{base_url}?{param_string}"
    
    def _parse_html_listings(self, html: str) -> List[Dict]:
        """Parse listings from HTML (requests fallback)"""
        from bs4 import BeautifulSoup
        
        vehicles = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for JSON data
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('listings' in script.string or 'searchResults' in script.string):
                    try:
                        # Extract JSON data from script
                        json_match = re.search(r'\{.*"listings".*\}', script.string, re.DOTALL)
                        if json_match:
                            data = json.loads(json_match.group())
                            listings = data.get('listings', [])
                            for listing in listings:
                                vehicle = self._parse_json_listing(listing)
                                if vehicle:
                                    vehicles.append(vehicle)
                    except:
                        continue
            
            return vehicles
            
        except Exception as e:
            logger.debug(f"Error parsing HTML listings: {e}")
            return []
    
    def _parse_json_listing(self, listing: Dict) -> Optional[Dict]:
        """Parse vehicle from JSON data"""
        try:
            vehicle = {
                'source': 'cargurus',
                'listing_id': str(listing.get('id', '')),
                'title': listing.get('displayTitle', ''),
                'make': listing.get('makeName', ''),
                'model': listing.get('modelName', ''),
                'year': listing.get('year', ''),
                'price': listing.get('expectedPrice', listing.get('askingPrice', 0)),
                'mileage': listing.get('mileage', 0),
                'trim': listing.get('trimName', ''),
                'condition': 'Used',
                'location': listing.get('sellerCity', ''),
                'image_urls': [listing.get('pictureUrl', '')] if listing.get('pictureUrl') else [],
                'view_item_url': f"https://www.cargurus.com{listing.get('vdpUrl', '')}",
                'cargurus_dealer': listing.get('sellerName', ''),
                'vehicle_details': {
                    'vin': listing.get('vin', ''),
                    'exterior_color': listing.get('exteriorColorName', ''),
                    'transmission': listing.get('transmissionDisplayName', ''),
                    'drivetrain': listing.get('drivetrainName', ''),
                    'fuel_type': listing.get('fuelTypeName', '')
                }
            }
            
            if vehicle['title'] and vehicle['price']:
                return vehicle
                
        except Exception as e:
            logger.debug(f"Error parsing JSON listing: {e}")
            
        return None
    
    def _extract_vehicle_data_from_card(self, card, driver) -> Optional[Dict]:
        """Extract vehicle data from a CarGurus listing card"""
        try:
            vehicle_data = {
                'source': 'cargurus',
                'listing_id': None,
                'title': None,
                'make': None,
                'model': None,
                'year': None,
                'price': None,
                'mileage': None,
                'trim': None,
                'condition': 'Used',
                'body_style': None,
                'exterior_color': None,
                'transmission': None,
                'fuel_type': None,
                'drivetrain': None,
                'location': None,
                'image_urls': [],
                'view_item_url': None,
                'cargurus_dealer': None,
                'vehicle_details': {}
            }
            
            # Extract title and vehicle info
            try:
                title_selectors = [
                    "h4[data-cg-ft='srp-listing-title']",
                    ".listing-title",
                    "h4",
                    "h3"
                ]
                
                for selector in title_selectors:
                    try:
                        title_element = card.find_element(By.CSS_SELECTOR, selector)
                        vehicle_data['title'] = title_element.text.strip()
                        break
                    except NoSuchElementException:
                        continue
                
                # Parse make, model, year from title (e.g., "2018 Nissan Rogue SV AWD")
                if vehicle_data['title']:
                    title_parts = vehicle_data['title'].split()
                    if len(title_parts) >= 3:
                        if title_parts[0].isdigit() and len(title_parts[0]) == 4:
                            vehicle_data['year'] = int(title_parts[0])
                            vehicle_data['make'] = title_parts[1]
                            vehicle_data['model'] = ' '.join(title_parts[2:])
                
            except Exception as e:
                logger.debug(f"Could not extract title: {e}")
            
            # Extract price
            try:
                price_selectors = [
                    "[data-cg-ft='srp-listing-price']",
                    ".listing-price", 
                    ".price",
                    "[class*='price']"
                ]
                
                for selector in price_selectors:
                    try:
                        price_element = card.find_element(By.CSS_SELECTOR, selector)
                        price_text = price_element.text.strip()
                        
                        # Extract numeric value from price text
                        price_match = re.search(r'\$([0-9,]+)', price_text)
                        if price_match:
                            vehicle_data['price'] = float(price_match.group(1).replace(',', ''))
                            break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.debug(f"Could not extract price: {e}")
            
            # Extract mileage
            try:
                # Look for mileage in the card text
                card_text = card.text
                mileage_match = re.search(r'([\d,]+)\s*mi', card_text, re.IGNORECASE)
                if mileage_match:
                    vehicle_data['mileage'] = int(mileage_match.group(1).replace(',', ''))
            except Exception as e:
                logger.debug(f"Could not extract mileage: {e}")
            
            # Extract vehicle URL
            try:
                link_elements = card.find_elements(By.CSS_SELECTOR, "a")
                for link in link_elements:
                    href = link.get_attribute('href')
                    if href and '/Cars/' in href and 'www.cargurus.com' in href:
                        vehicle_data['view_item_url'] = href
                        
                        # Extract listing ID from URL
                        url_parts = href.split('/')
                        for part in url_parts:
                            if part and part.isdigit() and len(part) > 5:
                                vehicle_data['listing_id'] = part
                                break
                        break
            except Exception as e:
                logger.debug(f"Could not extract vehicle URL: {e}")
            
            # Extract image
            try:
                img_element = card.find_element(By.CSS_SELECTOR, "img")
                img_url = img_element.get_attribute('src')
                if img_url:
                    vehicle_data['image_urls'] = [img_url]
            except NoSuchElementException:
                logger.debug("Could not extract image")
            
            # Extract dealer info
            try:
                dealer_selectors = [
                    "[data-cg-ft='srp-listing-dealer']", 
                    ".dealer-name",
                    "[class*='dealer']"
                ]
                
                for selector in dealer_selectors:
                    try:
                        dealer_element = card.find_element(By.CSS_SELECTOR, selector)
                        vehicle_data['cargurus_dealer'] = dealer_element.text.strip()
                        break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.debug(f"Could not extract dealer info: {e}")
            
            # Only return if we have essential data
            if vehicle_data.get('title') and (vehicle_data.get('price') or vehicle_data.get('listing_id')):
                return vehicle_data
            else:
                logger.debug(f"Skipping vehicle due to missing essential data. Title: {vehicle_data.get('title')}, Price: {vehicle_data.get('price')}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting vehicle data from CarGurus card: {e}")
            return None
    
    def close(self):
        """Close the client and cleanup resources"""
        self._close_driver()
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()

# Convenience function for backward compatibility
def search_cargurus_listings(query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
    """
    Search CarGurus listings (convenience function)
    
    Args:
        query: Search query
        filters: Optional filters dict
        limit: Maximum results
        offset: Pagination offset
        
    Returns:
        List of vehicle dictionaries
    """
    client = CarGurusClient()
    try:
        return client.search_listings(query, filters, limit, offset)
    finally:
        client.close()