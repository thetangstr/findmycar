"""
CarGurus client for scraping vehicle listings
Uses Selenium WebDriver since CarGurus requires JavaScript rendering
"""

import re
import logging
import time
import random
from typing import List, Dict, Optional
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