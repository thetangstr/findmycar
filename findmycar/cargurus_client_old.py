"""
CarGurus client for scraping vehicle listings
Uses Selenium WebDriver since CarGurus requires JavaScript rendering
"""

import re
import json
import logging
import time
import random
from typing import List, Dict, Optional
from urllib.parse import urlencode, quote_plus
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class CarGurusClient:
    """
    Client for scraping CarGurus vehicle listings
    Uses Selenium WebDriver since CarGurus requires JavaScript
    """
    
    def __init__(self, use_proxy=False, proxy_list=None):
        self.base_url = "https://www.cargurus.com"
        self.search_url = "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action"
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.current_proxy_index = 0
        
        # Request delay to be respectful
        self.request_delay = random.uniform(2, 4)
        
        # Set up Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
        # Add realistic user agent
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
        
        # Anti-detection measures
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = None
        
    def _get_driver(self):
        """Get or create Selenium WebDriver with proxy rotation if enabled"""
        if self.driver is None:
            if self.use_proxy and self.proxy_list:
                proxy = self.proxy_list[self.current_proxy_index % len(self.proxy_list)]
                self.chrome_options.add_argument(f"--proxy-server={proxy}")
                self.current_proxy_index += 1
                logger.info(f"Using proxy: {proxy}")
            
            self.driver = webdriver.Chrome(options=self.chrome_options)
            
            # Execute script to hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        return self.driver
    
    def _close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def _wait_random_delay(self):
        """Wait a random delay between requests"""
        delay = random.uniform(2, 4)
        time.sleep(delay)
    
    def search_listings(self, query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
        """
        Search for vehicle listings on CarGurus
        
        Args:
            query: Search query (make/model/keywords)
            filters: Optional filters (year_min, year_max, price_min, price_max, zip_code)
            limit: Number of results to return
            offset: Pagination offset
            
        Returns:
            List of vehicle dictionaries
        """
        try:
            driver = self._get_driver()
            vehicles = []
            
            # Build search URL - use the working URL from debug
            search_url = f"{self.search_url}?sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity=&zip=10001#resultsPage=1"
            
            logger.info(f"Searching CarGurus for: {query}")
            logger.info(f"CarGurus URL: {search_url}")
            
            # Navigate to search page
            driver.get(search_url)
            self._wait_random_delay()
            
            # Wait for listings to load
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cg-ft='srp-listing-blade']"))
                )
            except TimeoutException:
                logger.warning("No CarGurus listings found or page took too long to load")
                return []
            
            # Get listing cards
            listing_cards = driver.find_elements(By.CSS_SELECTOR, "[data-cg-ft='srp-listing-blade']")
            
            logger.info(f"Found {len(listing_cards)} CarGurus listing cards")
            
            for i, card in enumerate(listing_cards[:limit]):
                try:
                    vehicle_data = self._extract_vehicle_data_from_card(card, driver)
                    if vehicle_data:
                        vehicles.append(vehicle_data)
                        logger.debug(f"Extracted vehicle {i+1}: {vehicle_data.get('title', 'Unknown')}")
                    
                    # Random delay between extractions
                    if i < len(listing_cards) - 1:
                        time.sleep(random.uniform(0.5, 1.0))
                        
                except Exception as e:
                    logger.error(f"Error extracting vehicle data from card {i}: {e}")
                    continue
            
            return vehicles
            
        except Exception as e:
            logger.error(f"Error searching CarGurus listings: {e}")
            return []
        finally:
            # Don't close driver immediately in case we need it for detail pages
            pass
    
    def _build_search_params(self, query: str, filters: Optional[Dict]) -> Dict:
        """Build URL parameters for CarGurus search"""
        params = {
            'sourceContext': 'carGurusHomePageModel',
            'inventorySearchWidgetType': 'AUTO',
            'searchChanged': 'true',
        }
        
        # Parse query for make/model
        query_parts = query.lower().split()
        
        # Common makes to match
        makes = ['honda', 'toyota', 'ford', 'chevrolet', 'nissan', 'bmw', 'mercedes', 
                 'audi', 'volkswagen', 'hyundai', 'kia', 'mazda', 'subaru', 'lexus',
                 'acura', 'infiniti', 'tesla', 'jeep', 'dodge', 'ram', 'gmc']
        
        # Try to extract make
        for part in query_parts:
            if part in makes:
                params['selectedEntity'] = part.title()
                # Remove make from query parts to find model
                remaining = [p for p in query_parts if p != part]
                if remaining:
                    # Assume next word is model
                    params['selectedEntity'] = f"{part.title()} {remaining[0].title()}"
                break
        
        # If no specific make found, use generic search
        if 'selectedEntity' not in params:
            params['searchText'] = query
        
        # Apply filters if provided
        if filters:
            if filters.get('zip_code'):
                params['zip'] = filters['zip_code']
            else:
                params['zip'] = '10001'  # Default to NYC
                
            if filters.get('year_min'):
                params['minModelYear'] = filters['year_min']
            if filters.get('year_max'):
                params['maxModelYear'] = filters['year_max']
                
            if filters.get('price_min'):
                params['minPrice'] = filters['price_min']
            if filters.get('price_max'):
                params['maxPrice'] = filters['price_max']
                
            if filters.get('distance'):
                params['distance'] = filters['distance']
            else:
                params['distance'] = '50'  # 50 mile radius default
        
        return params
    
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
                    continue
            
            # Remove duplicates based on listing_id
            seen = set()
            unique_vehicles = []
            for v in vehicles:
                if v['listing_id'] not in seen:
                    seen.add(v['listing_id'])
                    unique_vehicles.append(v)
            
            return unique_vehicles
            
        except Exception as e:
            logger.error(f"Error parsing CarGurus search results: {e}")
            return []
    
    def _extract_vehicle_from_json(self, item: Dict) -> Optional[Dict]:
        """Extract vehicle data from JSON-LD structured data"""
        try:
            if not isinstance(item, dict):
                return None
                
            # Get the actual item data
            item_data = item.get('item', {})
            if not item_data:
                return None
                
            vehicle = {
                'source': 'cargurus',
                'listing_id': f"cargurus_{item_data.get('sku', '')}",
                'title': item_data.get('name', ''),
                'price': None,
                'location': None,
                'image_urls': [],
                'view_item_url': item_data.get('url', ''),
                'make': None,
                'model': None,
                'year': None,
                'mileage': None,
                'condition': 'Used',
                'vehicle_details': {},
                'deal_rating': None,
                'dealer_name': None
            }
            
            # Extract price
            offers = item_data.get('offers', {})
            if offers and isinstance(offers, dict):
                vehicle['price'] = float(offers.get('price', 0))
                vehicle['location'] = offers.get('availableAtOrFrom', {}).get('address', {}).get('addressLocality', '')
                vehicle['dealer_name'] = offers.get('seller', {}).get('name', '')
            
            # Extract vehicle details
            car = item_data.get('itemOffered', {})
            if car:
                vehicle['make'] = car.get('manufacturer', '')
                vehicle['model'] = car.get('model', '')
                vehicle['year'] = car.get('modelDate', '')
                vehicle['mileage'] = car.get('mileageFromOdometer', {}).get('value', '')
                
                # Extract images
                if car.get('image'):
                    if isinstance(car['image'], list):
                        vehicle['image_urls'] = car['image']
                    else:
                        vehicle['image_urls'] = [car['image']]
            
            # Only return if we have essential data
            if vehicle['title'] and vehicle['price']:
                return vehicle
                
        except Exception as e:
            logger.debug(f"Error extracting vehicle from JSON: {e}")
            
        return None
    
    def _extract_vehicle_from_html(self, card) -> Optional[Dict]:
        """Extract vehicle data from HTML card element"""
        try:
            vehicle = {
                'source': 'cargurus',
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
                'deal_rating': None,
                'dealer_name': None
            }
            
            # Extract title
            title_elem = card.find(['h4', 'h3'], class_=re.compile(r'title|heading|car-name'))
            if not title_elem:
                title_elem = card.find('a', class_=re.compile(r'title|vehicle'))
            
            if title_elem:
                vehicle['title'] = title_elem.get_text(strip=True)
                
                # Parse year, make, model from title
                title_match = re.match(r'(\d{4})\s+([A-Za-z]+)\s+(.+)', vehicle['title'])
                if title_match:
                    vehicle['year'] = int(title_match.group(1))
                    vehicle['make'] = title_match.group(2)
                    vehicle['model'] = title_match.group(3).split()[0]
            
            # Extract price
            price_elem = card.find(class_=re.compile(r'price|cost'))
            if price_elem:
                price_text = price_elem.get_text()
                price_match = re.search(r'\$?([\d,]+)', price_text)
                if price_match:
                    vehicle['price'] = float(price_match.group(1).replace(',', ''))
            
            # Extract mileage
            mileage_elem = card.find(text=re.compile(r'\d+[,\d]*\s*(mi|miles)', re.I))
            if mileage_elem:
                mileage_match = re.search(r'([\d,]+)\s*(mi|miles)', str(mileage_elem), re.I)
                if mileage_match:
                    vehicle['mileage'] = int(mileage_match.group(1).replace(',', ''))
            
            # Extract location
            location_elem = card.find(class_=re.compile(r'location|dealer-location|distance'))
            if location_elem:
                vehicle['location'] = location_elem.get_text(strip=True)
            
            # Extract dealer
            dealer_elem = card.find(class_=re.compile(r'dealer-name|seller'))
            if dealer_elem:
                vehicle['dealer_name'] = dealer_elem.get_text(strip=True)
            
            # Extract deal rating
            deal_elem = card.find(class_=re.compile(r'deal-badge|deal-rating|price-badge'))
            if deal_elem:
                vehicle['deal_rating'] = deal_elem.get_text(strip=True)
            
            # Extract image
            img_elem = card.find('img', class_=re.compile(r'vehicle|car|listing'))
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
                id_match = re.search(r'/listing/(\d+)', href)
                if id_match:
                    vehicle['listing_id'] = f"cargurus_{id_match.group(1)}"
                else:
                    import hashlib
                    vehicle['listing_id'] = f"cargurus_{hashlib.md5(href.encode()).hexdigest()[:8]}"
            
            # Only return if we have essential data
            if vehicle['title'] and vehicle['price'] and vehicle['listing_id']:
                return vehicle
                
        except Exception as e:
            logger.debug(f"Error extracting vehicle from HTML: {e}")
            
        return None

def search_cargurus_listings(query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
    """
    Public interface for searching CarGurus listings
    """
    client = CarGurusClient()
    return client.search_listings(query, filters, limit, offset)