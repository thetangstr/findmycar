"""
Autotrader client for scraping vehicle listings
Uses Selenium WebDriver since Autotrader requires JavaScript rendering
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
from scraping_cache import cache_scraping_result, with_retry
from performance_profiler import PerformanceTimer

logger = logging.getLogger(__name__)

class AutotraderClient:
    """
    Client for scraping Autotrader vehicle listings
    Uses Selenium WebDriver since Autotrader requires JavaScript
    """
    
    def __init__(self, use_proxy=False, proxy_list=None):
        self.base_url = "https://www.autotrader.com"
        self.search_url = "https://www.autotrader.com/cars-for-sale/all-cars"
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
    
    @cache_scraping_result('autotrader')
    def search_listings(self, query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
        """
        Search for vehicle listings on Autotrader
        
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
            
            # Use the working URL from debug
            search_url = self.search_url
            
            logger.info(f"Searching Autotrader for: {query}")
            logger.info(f"Autotrader URL: {search_url}")
            
            # Navigate to search page
            driver.get(search_url)
            self._wait_random_delay()
            
            # Wait for listings to load
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cmp='inventoryListing']"))
                )
            except TimeoutException:
                logger.warning("No Autotrader listings found or page took too long to load")
                return []
            
            # Get listing cards
            listing_cards = driver.find_elements(By.CSS_SELECTOR, "[data-cmp='inventoryListing']")
            
            logger.info(f"Found {len(listing_cards)} Autotrader listing cards")
            
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
            logger.error(f"Error searching Autotrader listings: {e}")
            return []
        finally:
            # Don't close driver immediately in case we need it for detail pages
            pass
    
    def _extract_vehicle_data_from_card(self, card, driver) -> Optional[Dict]:
        """Extract vehicle data from an Autotrader listing card"""
        try:
            vehicle_data = {
                'source': 'autotrader',
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
                'autotrader_dealer': None,
                'vehicle_details': {}
            }
            
            # Extract title and vehicle info from card text
            try:
                card_text = card.text
                
                # Look for vehicle title patterns in card text lines
                card_lines = card_text.split('\n')
                for line in card_lines:
                    line = line.strip()
                    # Look for patterns like "Certified 2022 Toyota Mirai XLE" or "Used 2019 BMW 530e"
                    # Match: optional condition + year + make + model
                    title_match = re.search(r'((?:Used|New|Certified|Pre-Owned)\s+)?(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9\s\-]+)', line)
                    if title_match:
                        condition = title_match.group(1)
                        year = title_match.group(2)
                        make = title_match.group(3)
                        model = title_match.group(4).strip()
                        
                        # Set the title as the full match
                        vehicle_data['title'] = line.strip()
                        vehicle_data['year'] = int(year)
                        vehicle_data['make'] = make
                        vehicle_data['model'] = model
                        
                        if condition:
                            vehicle_data['condition'] = condition.strip()
                        
                        logger.debug(f"Extracted title: {vehicle_data['title']}, Year: {year}, Make: {make}, Model: {model}")
                        break
                
            except Exception as e:
                logger.debug(f"Could not extract title: {e}")
            
            # Extract price
            try:
                # Look for price in card text (e.g., "$24,707", "24,382", "14,382")
                # Prices usually appear after mileage and are standalone numbers
                card_lines = card.text.split('\n')
                for line in card_lines:
                    line = line.strip()
                    # Look for standalone price numbers (not years)
                    if re.match(r'^\$?([0-9,]{4,})$', line):
                        price_str = line.replace('$', '').replace(',', '')
                        price_val = float(price_str)
                        # Only accept realistic car prices (between $1000 and $500000)
                        if 1000 <= price_val <= 500000 and price_val != vehicle_data.get('year'):
                            vehicle_data['price'] = price_val
                            break
            except Exception as e:
                logger.debug(f"Could not extract price: {e}")
            
            # Extract mileage
            try:
                # Look for mileage in card text (e.g., "29,985 miles")
                mileage_match = re.search(r'([\d,]+)\s*miles?', card.text, re.IGNORECASE)
                if mileage_match:
                    vehicle_data['mileage'] = int(mileage_match.group(1).replace(',', ''))
            except Exception as e:
                logger.debug(f"Could not extract mileage: {e}")
            
            # Extract vehicle URL
            try:
                link_elements = card.find_elements(By.CSS_SELECTOR, "a")
                for link in link_elements:
                    href = link.get_attribute('href')
                    if href and '/cars-for-sale/' in href and 'autotrader.com' in href:
                        vehicle_data['view_item_url'] = href
                        
                        # Extract listing ID from URL (format: /vehicle/753676695?)
                        id_match = re.search(r'/vehicle/(\d+)', href)
                        if id_match:
                            vehicle_data['listing_id'] = id_match.group(1)
                        break
            except Exception as e:
                logger.debug(f"Could not extract vehicle URL: {e}")
            
            # Extract image
            try:
                img_element = card.find_element(By.CSS_SELECTOR, "img")
                img_url = img_element.get_attribute('src')
                if img_url and 'http' in img_url:
                    vehicle_data['image_urls'] = [img_url]
            except NoSuchElementException:
                logger.debug("Could not extract image")
            
            # Extract dealer info from card text
            try:
                # Look for dealer patterns in text
                card_lines = card.text.split('\n')
                for line in card_lines:
                    if any(dealer_word in line.lower() for dealer_word in ['dealer', 'motors', 'automotive', 'auto']):
                        if len(line.strip()) > 5 and len(line.strip()) < 50:
                            vehicle_data['autotrader_dealer'] = line.strip()
                            break
            except Exception as e:
                logger.debug(f"Could not extract dealer info: {e}")
            
            # Extract location from card text
            try:
                # Look for location patterns (City, ST)
                location_match = re.search(r'([A-Za-z\s]+,\s*[A-Z]{2})', card.text)
                if location_match:
                    vehicle_data['location'] = location_match.group(1)
            except Exception as e:
                logger.debug(f"Could not extract location: {e}")
            
            # Only return if we have essential data
            if vehicle_data.get('title') and (vehicle_data.get('price') or vehicle_data.get('listing_id')):
                return vehicle_data
            else:
                logger.debug(f"Skipping vehicle due to missing essential data. Title: {vehicle_data.get('title')}, Price: {vehicle_data.get('price')}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting vehicle data from Autotrader card: {e}")
            return None
    
    def close(self):
        """Close the client and cleanup resources"""
        self._close_driver()
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()

# Convenience function for backward compatibility
def search_autotrader_listings(query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
    """
    Search Autotrader listings (convenience function)
    
    Args:
        query: Search query
        filters: Optional filters dict
        limit: Maximum results
        offset: Pagination offset
        
    Returns:
        List of vehicle dictionaries
    """
    client = AutotraderClient()
    try:
        return client.search_listings(query, filters, limit, offset)
    finally:
        client.close()