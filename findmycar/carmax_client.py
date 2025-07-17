import requests
import re
import json
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse, parse_qs
from typing import List, Dict, Optional
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scraping_cache import cache_scraping_result, with_retry
from performance_profiler import PerformanceTimer

logger = logging.getLogger(__name__)

class CarMaxClient:
    """
    Client for scraping CarMax vehicle listings.
    Uses Selenium WebDriver since CarMax is heavily JavaScript-based.
    """
    
    def __init__(self, use_proxy=False, proxy_list=None):
        self.base_url = "https://www.carmax.com"
        self.search_url = "https://www.carmax.com/cars"
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
    
    @cache_scraping_result('carmax')
    def search_listings(self, query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
        """
        Search for vehicle listings on CarMax
        
        Args:
            query: Search query (make/model/keywords)
            filters: Dict with optional filters (make, model, year_min, year_max, price_min, price_max)
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            List of vehicle dictionaries
        """
        try:
            driver = self._get_driver()
            vehicles = []
            
            # Build search URL
            search_params = self._build_search_params(query, filters, limit, offset)
            search_url = f"{self.search_url}?{urlencode(search_params)}"
            
            logger.info(f"Searching CarMax with URL: {search_url}")
            
            # Navigate to search page
            driver.get(search_url)
            self._wait_random_delay()
            
            # Wait for results to load - try multiple selectors
            vehicle_cards = []
            selectors_to_try = [".car-tile", "[data-test='search-result']", ".vehicle-card"]
            
            for selector in selectors_to_try:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    vehicle_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                    if vehicle_cards:
                        logger.info(f"Found {len(vehicle_cards)} vehicles using selector: {selector}")
                        break
                except TimeoutException:
                    continue
            
            if not vehicle_cards:
                logger.warning("No search results found or page took too long to load")
                return []
            
            logger.info(f"Found {len(vehicle_cards)} vehicle cards")
            
            for i, card in enumerate(vehicle_cards[:limit]):
                try:
                    vehicle_data = self._extract_vehicle_data_from_card(card, driver)
                    if vehicle_data:
                        vehicles.append(vehicle_data)
                        logger.debug(f"Extracted vehicle {i+1}: {vehicle_data.get('make')} {vehicle_data.get('model')}")
                    
                    # Random delay between extractions
                    if i < len(vehicle_cards) - 1:
                        time.sleep(random.uniform(0.5, 1.0))
                        
                except Exception as e:
                    logger.error(f"Error extracting vehicle data from card {i}: {e}")
                    continue
            
            return vehicles
            
        except Exception as e:
            logger.error(f"Error searching CarMax listings: {e}")
            return []
        finally:
            # Don't close driver immediately in case we need it for detail pages
            pass
    
    def _build_search_params(self, query: str, filters: Optional[Dict], limit: int, offset: int) -> Dict:
        """Build search parameters for CarMax URL"""
        params = {
            'page': offset // limit + 1,
            'sort': 'best_match_desc'
        }
        
        # Parse query for make/model
        if query:
            query_parts = query.lower().split()
            for part in query_parts:
                if part in ['honda', 'toyota', 'ford', 'chevrolet', 'bmw', 'mercedes', 'audi', 'nissan']:
                    params['make'] = part.title()
                    break
        
        # Apply filters
        if filters:
            logger.debug(f"CarMax filters received: {filters}")
            if filters.get('make'):
                params['make'] = filters['make']
            if filters.get('model'):
                params['model'] = filters['model']
            if filters.get('year_min'):
                params['year_min'] = filters['year_min']
            if filters.get('year_max'):
                params['year_max'] = filters['year_max']
            if filters.get('price_min'):
                params['price_min'] = filters['price_min']
            if filters.get('price_max'):
                params['price_max'] = filters['price_max']
        else:
            # Add default year range if no filters provided
            params['year_min'] = 2000
            params['year_max'] = 2024
            params['price_min'] = 5000
            params['price_max'] = 100000
        
        return params
    
    def _extract_vehicle_data_from_card(self, card, driver) -> Optional[Dict]:
        """Extract vehicle data from a CarMax search result card"""
        try:
            vehicle_data = {
                'source': 'carmax',
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
                'carmax_store': None,
                'carmax_stock_number': None,
                'carmax_warranty': None,
                'vehicle_details': {}
            }
            
            # Extract listing ID from data-id attribute
            try:
                listing_id = card.get_attribute('data-id')
                if listing_id:
                    vehicle_data['listing_id'] = listing_id
                    vehicle_data['carmax_stock_number'] = listing_id
            except Exception as e:
                logger.debug(f"Could not extract listing ID: {e}")
            
            # Extract title from h3 element
            try:
                title_element = card.find_element(By.CSS_SELECTOR, "h3")
                vehicle_data['title'] = title_element.text.strip().replace('\n', ' ')
                
                # Parse make, model, year from title (e.g., "2018 Honda Civic LX")
                title_parts = vehicle_data['title'].split()
                if len(title_parts) >= 3:
                    if title_parts[0].isdigit():
                        vehicle_data['year'] = int(title_parts[0])
                        vehicle_data['make'] = title_parts[1]
                        # Everything after make is model + trim
                        model_and_trim = ' '.join(title_parts[2:])
                        vehicle_data['model'] = model_and_trim
                        vehicle_data['trim'] = title_parts[-1] if len(title_parts) > 3 else None
                
            except (NoSuchElementException, ValueError) as e:
                logger.debug(f"Could not extract title: {e}")
            
            # Extract price and other data from data-clickprops attribute
            try:
                clickprops = card.get_attribute('data-clickprops')
                if clickprops:
                    # Parse price from clickprops (e.g., "Price: 16998")
                    price_match = re.search(r'Price:\s*(\d+)', clickprops)
                    if price_match:
                        vehicle_data['price'] = float(price_match.group(1))
                    
                    # Parse YMM from clickprops (e.g., "YMM: 2018 Honda Civic")
                    ymm_match = re.search(r'YMM:\s*([^,]+)', clickprops)
                    if ymm_match and not vehicle_data.get('title'):
                        vehicle_data['title'] = ymm_match.group(1).strip()
                        
            except Exception as e:
                logger.debug(f"Could not extract data from clickprops: {e}")
            
            # Extract vehicle URL from any a element
            try:
                link_element = card.find_element(By.CSS_SELECTOR, "a")
                href = link_element.get_attribute('href')
                if href and '/car/' in href:
                    vehicle_data['view_item_url'] = href
                    
                    # Extract listing ID from URL if not already found
                    if not vehicle_data['listing_id']:
                        url_parts = href.split('/')
                        if len(url_parts) > 0:
                            vehicle_data['listing_id'] = url_parts[-1]
            except NoSuchElementException:
                logger.debug("Could not extract vehicle URL")
            
            # Extract image
            try:
                img_element = card.find_element(By.CSS_SELECTOR, "img")
                img_url = img_element.get_attribute('src')
                if img_url:
                    vehicle_data['image_urls'] = [img_url]
            except NoSuchElementException:
                logger.debug("Could not extract image")
            
            # Extract additional details from span elements
            try:
                span_elements = card.find_elements(By.CSS_SELECTOR, "span")
                for span in span_elements:
                    span_text = span.text.strip().lower()
                    if span_text:
                        # Look for mileage (e.g., "45,000 miles")
                        mileage_match = re.search(r'([\d,]+)\s*miles?', span_text)
                        if mileage_match and not vehicle_data.get('mileage'):
                            vehicle_data['mileage'] = int(mileage_match.group(1).replace(',', ''))
                        
                        # Look for transmission info
                        if 'automatic' in span_text and not vehicle_data.get('transmission'):
                            vehicle_data['transmission'] = 'Automatic'
                        elif 'manual' in span_text and not vehicle_data.get('transmission'):
                            vehicle_data['transmission'] = 'Manual'
                        
                        # Look for drivetrain
                        if any(dt in span_text for dt in ['awd', 'fwd', 'rwd', '4wd']) and not vehicle_data.get('drivetrain'):
                            vehicle_data['drivetrain'] = span.text.strip()
                        
                        # Look for fuel type
                        if any(ft in span_text for ft in ['gas', 'hybrid', 'electric', 'diesel']) and not vehicle_data.get('fuel_type'):
                            vehicle_data['fuel_type'] = span.text.strip()
                        
                        # Look for location info (e.g., "Test drive today at CarMax Capitol Expressway, CA")
                        if ('test drive' in span_text or 'carmax' in span_text) and (',' in span_text) and not vehicle_data.get('location'):
                            # Extract location after "at" or "CarMax"
                            location_match = re.search(r'(?:at\s+|carmax\s+)([^,]+,\s*[a-z]{2})', span_text, re.IGNORECASE)
                            if location_match:
                                vehicle_data['location'] = location_match.group(1).strip()
                                vehicle_data['carmax_store'] = vehicle_data['location']
                            
            except Exception as e:
                logger.debug(f"Could not extract additional details: {e}")
            
            # Only return if we have essential data
            if vehicle_data.get('title') and (vehicle_data.get('price') or vehicle_data.get('listing_id')):
                return vehicle_data
            else:
                logger.debug(f"Skipping vehicle due to missing essential data. Title: {vehicle_data.get('title')}, Price: {vehicle_data.get('price')}, ID: {vehicle_data.get('listing_id')}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting vehicle data from card: {e}")
            return None
    
    def get_vehicle_details(self, vehicle_url: str) -> Optional[Dict]:
        """
        Get detailed information for a specific CarMax vehicle
        
        Args:
            vehicle_url: URL to the vehicle detail page
            
        Returns:
            Dictionary with detailed vehicle information
        """
        try:
            driver = self._get_driver()
            
            logger.info(f"Getting details for vehicle: {vehicle_url}")
            
            # Navigate to vehicle detail page
            driver.get(vehicle_url)
            self._wait_random_delay()
            
            # Wait for page to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='vehicle-overview']"))
                )
            except TimeoutException:
                logger.warning("Vehicle detail page took too long to load")
                return None
            
            details = {
                'vin': None,
                'stock_number': None,
                'warranty_info': None,
                'features': [],
                'seller_notes': None,
                'additional_images': []
            }
            
            # Extract VIN
            try:
                vin_element = driver.find_element(By.CSS_SELECTOR, "[data-test='vin']")
                details['vin'] = vin_element.text.strip()
            except NoSuchElementException:
                logger.debug("Could not extract VIN")
            
            # Extract stock number
            try:
                stock_element = driver.find_element(By.CSS_SELECTOR, "[data-test='stock-number']")
                details['stock_number'] = stock_element.text.strip()
            except NoSuchElementException:
                logger.debug("Could not extract stock number")
            
            # Extract warranty information
            try:
                warranty_element = driver.find_element(By.CSS_SELECTOR, "[data-test='warranty-info']")
                details['warranty_info'] = warranty_element.text.strip()
            except NoSuchElementException:
                logger.debug("Could not extract warranty info")
            
            # Extract features
            try:
                feature_elements = driver.find_elements(By.CSS_SELECTOR, "[data-test='vehicle-features'] li")
                details['features'] = [elem.text.strip() for elem in feature_elements]
            except NoSuchElementException:
                logger.debug("Could not extract features")
            
            # Extract additional images
            try:
                img_elements = driver.find_elements(By.CSS_SELECTOR, "[data-test='additional-images'] img")
                details['additional_images'] = [img.get_attribute('src') for img in img_elements if img.get_attribute('src')]
            except NoSuchElementException:
                logger.debug("Could not extract additional images")
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting vehicle details: {e}")
            return None
    
    def close(self):
        """Close the client and cleanup resources"""
        self._close_driver()
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()

# Convenience function for backward compatibility
def search_carmax_listings(query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
    """
    Search CarMax listings (convenience function)
    
    Args:
        query: Search query
        filters: Optional filters dict
        limit: Maximum results
        offset: Pagination offset
        
    Returns:
        List of vehicle dictionaries
    """
    client = CarMaxClient()
    try:
        return client.search_listings(query, filters, limit, offset)
    finally:
        client.close()