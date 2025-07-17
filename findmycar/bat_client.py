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
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BringATrailerClient:
    """
    Client for scraping Bring a Trailer (BaT) auction listings.
    BaT specializes in enthusiast and collector vehicles with auction-style listings.
    """
    
    def __init__(self, use_proxy=False, proxy_list=None):
        self.base_url = "https://bringatrailer.com"
        self.search_url = "https://bringatrailer.com/auctions/"
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.current_proxy_index = 0
        
        # Request delay to be respectful to BaT servers
        self.request_delay = random.uniform(3, 6)  # Higher delay for auction site
        
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
        delay = random.uniform(3, 6)  # Higher delay for auction site
        time.sleep(delay)
    
    def search_listings(self, query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
        """
        Search for auction listings on Bring a Trailer
        
        Args:
            query: Search query (make/model/keywords)
            filters: Dict with optional filters (make, model, year_min, year_max, price_min, price_max)
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            List of vehicle auction dictionaries
        """
        try:
            driver = self._get_driver()
            vehicles = []
            
            # Build search URL - BaT uses different URL structure
            search_url = self._build_search_url(query, filters, limit, offset)
            
            logger.info(f"Searching BaT with URL: {search_url}")
            
            # Navigate to search page
            driver.get(search_url)
            self._wait_random_delay()
            
            # Wait for auction listings to load - look for elements with bid info
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='listing']"))
                )
            except TimeoutException:
                logger.warning("No BaT auction results found or page took too long to load")
                return []
            
            # Get auction cards - BaT uses listing elements
            auction_cards = driver.find_elements(By.CSS_SELECTOR, "[class*='listing']")
            
            # Filter to actual auction listings (those with bid info or images)
            filtered_cards = []
            for card in auction_cards:
                card_text = card.text.lower()
                if any(keyword in card_text for keyword in ['bid:', '$', 'auction', 'ending']) and len(card_text) > 50:
                    filtered_cards.append(card)
            
            auction_cards = filtered_cards
            
            logger.info(f"Found {len(auction_cards)} BaT auction cards")
            
            for i, card in enumerate(auction_cards[:limit]):
                try:
                    vehicle_data = self._extract_auction_data_from_card(card, driver)
                    if vehicle_data:
                        vehicles.append(vehicle_data)
                        logger.debug(f"Extracted auction {i+1}: {vehicle_data.get('title', 'Unknown')}")
                    
                    # Random delay between extractions
                    if i < len(auction_cards) - 1:
                        time.sleep(random.uniform(1.0, 2.0))
                        
                except Exception as e:
                    logger.error(f"Error extracting auction data from card {i}: {e}")
                    continue
            
            return vehicles
            
        except Exception as e:
            logger.error(f"Error searching BaT listings: {e}")
            return []
        finally:
            # Don't close driver immediately in case we need it for detail pages
            pass
    
    def _build_search_url(self, query: str, filters: Optional[Dict], limit: int, offset: int) -> str:
        """Build search URL for BaT"""
        # BaT main auctions page - no longer uses /cars/ subdirectory
        base_url = f"{self.base_url}/auctions/"
        
        params = {}
        
        # Parse query for specific terms but don't change base URL since /cars/ gives 404
        if query:
            # BaT doesn't support direct search in URL, we'll filter client-side
            # Just use the main auctions page and filter by make/model in extraction
            pass
        
        # Apply filters
        if filters:
            if filters.get('year_min'):
                params['year_min'] = filters['year_min']
            if filters.get('year_max'):
                params['year_max'] = filters['year_max']
            if filters.get('make'):
                params['make'] = filters['make']
        
        # Add pagination
        if offset > 0:
            page = (offset // limit) + 1
            params['page'] = page
        
        # Build final URL
        if params:
            return f"{base_url}?{urlencode(params)}"
        else:
            return base_url
    
    def _extract_auction_data_from_card(self, card, driver) -> Optional[Dict]:
        """Extract auction data from a BaT auction card"""
        try:
            vehicle_data = {
                'source': 'bringatrailer',
                'listing_id': None,
                'title': None,
                'make': None,
                'model': None,
                'year': None,
                'price': None,  # Current bid
                'mileage': None,
                'condition': 'Used',  # BaT typically has used/collector vehicles
                'body_style': None,
                'exterior_color': None,
                'location': None,
                'image_urls': [],
                'view_item_url': None,
                # BaT-specific fields
                'bat_auction_id': None,
                'current_bid': None,
                'bid_count': None,
                'time_left': None,
                'auction_status': None,  # 'active', 'ended', 'sold', 'no_sale'
                'reserve_met': None,
                'comment_count': None,
                'bat_category': None,
                'vehicle_details': {}
            }
            
            # Extract auction URL and ID
            try:
                # Look for any link with auction in href
                link_elements = card.find_elements(By.CSS_SELECTOR, "a")
                for link in link_elements:
                    href = link.get_attribute('href')
                    if href and '/auction' in href and href != 'https://bringatrailer.com/auctions/':
                        vehicle_data['view_item_url'] = href
                        
                        # Extract auction ID from URL
                        # BaT URLs are typically like: /auctions/1990-porsche-911-carrera-4/
                        url_parts = href.split('/')
                        for part in url_parts:
                            if part and part != 'auctions' and len(part) > 5:
                                vehicle_data['listing_id'] = part
                                vehicle_data['bat_auction_id'] = part
                                break
                        break
            except Exception as e:
                logger.debug(f"Could not extract auction URL: {e}")
            
            # Extract title and parse vehicle info
            try:
                title_selectors = [
                    ".auction-title",
                    ".listing-title", 
                    ".card-title",
                    "h3",
                    "h2",
                    ".title"
                ]
                
                title_element = None
                for selector in title_selectors:
                    try:
                        title_element = card.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if title_element:
                    vehicle_data['title'] = title_element.text.strip()
                    
                    # Parse make, model, year from BaT title format
                    # BaT titles are typically: "1990 Porsche 911 Carrera 4"
                    if vehicle_data['title']:
                        title_parts = vehicle_data['title'].split()
                        if len(title_parts) >= 3:
                            # First part is usually year
                            if title_parts[0].isdigit() and len(title_parts[0]) == 4:
                                vehicle_data['year'] = int(title_parts[0])
                                vehicle_data['make'] = title_parts[1]
                                vehicle_data['model'] = ' '.join(title_parts[2:])
                
            except Exception as e:
                logger.debug(f"Could not extract title: {e}")
            
            # Extract current bid
            try:
                bid_selectors = [
                    ".current-bid",
                    ".bid-amount",
                    ".price",
                    "[class*='bid']",
                    "[class*='price']"
                ]
                
                for selector in bid_selectors:
                    try:
                        bid_element = card.find_element(By.CSS_SELECTOR, selector)
                        bid_text = bid_element.text.strip()
                        
                        # Extract numeric value from bid text
                        bid_match = re.search(r'\$([0-9,]+)', bid_text)
                        if bid_match:
                            vehicle_data['current_bid'] = float(bid_match.group(1).replace(',', ''))
                            vehicle_data['price'] = vehicle_data['current_bid']  # Use current bid as price
                            break
                    except NoSuchElementException:
                        continue
                
                # Fallback: extract from card text (e.g., "Bid: USD $45,000")
                if not vehicle_data.get('current_bid'):
                    card_text = card.text
                    bid_match = re.search(r'(?:Bid|Current).*?\$([0-9,]+)', card_text, re.IGNORECASE)
                    if bid_match:
                        vehicle_data['current_bid'] = float(bid_match.group(1).replace(',', ''))
                        vehicle_data['price'] = vehicle_data['current_bid']
                        
            except Exception as e:
                logger.debug(f"Could not extract bid amount: {e}")
            
            # Extract bid count
            try:
                bid_count_selectors = [
                    ".bid-count",
                    ".bids",
                    "[class*='bid'][class*='count']"
                ]
                
                for selector in bid_count_selectors:
                    try:
                        count_element = card.find_element(By.CSS_SELECTOR, selector)
                        count_text = count_element.text.strip()
                        
                        # Extract number from text like "15 bids"
                        count_match = re.search(r'(\d+)', count_text)
                        if count_match:
                            vehicle_data['bid_count'] = int(count_match.group(1))
                            break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.debug(f"Could not extract bid count: {e}")
            
            # Extract time remaining
            try:
                time_selectors = [
                    ".time-left",
                    ".time-remaining", 
                    ".countdown",
                    "[class*='time']"
                ]
                
                for selector in time_selectors:
                    try:
                        time_element = card.find_element(By.CSS_SELECTOR, selector)
                        vehicle_data['time_left'] = time_element.text.strip()
                        break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.debug(f"Could not extract time remaining: {e}")
            
            # Extract comment count
            try:
                comment_selectors = [
                    ".comment-count",
                    ".comments",
                    "[class*='comment']"
                ]
                
                for selector in comment_selectors:
                    try:
                        comment_element = card.find_element(By.CSS_SELECTOR, selector)
                        comment_text = comment_element.text.strip()
                        
                        # Extract number from text like "42 comments"
                        comment_match = re.search(r'(\d+)', comment_text)
                        if comment_match:
                            vehicle_data['comment_count'] = int(comment_match.group(1))
                            break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.debug(f"Could not extract comment count: {e}")
            
            # Extract auction status
            try:
                status_selectors = [
                    ".auction-status",
                    ".status",
                    ".badge",
                    "[class*='status']"
                ]
                
                for selector in status_selectors:
                    try:
                        status_element = card.find_element(By.CSS_SELECTOR, selector)
                        status_text = status_element.text.strip().lower()
                        
                        if 'sold' in status_text:
                            vehicle_data['auction_status'] = 'sold'
                        elif 'ended' in status_text or 'closed' in status_text:
                            vehicle_data['auction_status'] = 'ended'
                        elif 'active' in status_text or 'live' in status_text:
                            vehicle_data['auction_status'] = 'active'
                        elif 'no sale' in status_text or 'reserve not met' in status_text:
                            vehicle_data['auction_status'] = 'no_sale'
                        
                        break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.debug(f"Could not extract auction status: {e}")
            
            # Extract main image
            try:
                img_selectors = [
                    ".auction-image img",
                    ".listing-image img",
                    ".card-img-top",
                    "img"
                ]
                
                for selector in img_selectors:
                    try:
                        img_element = card.find_element(By.CSS_SELECTOR, selector)
                        img_url = img_element.get_attribute('src')
                        if img_url and 'placeholder' not in img_url:
                            vehicle_data['image_urls'] = [img_url]
                            break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.debug(f"Could not extract image: {e}")
            
            # Only return if we have essential data
            if vehicle_data.get('title') and (vehicle_data.get('current_bid') or vehicle_data.get('view_item_url')):
                return vehicle_data
            else:
                logger.debug("Skipping auction due to missing essential data")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting auction data from card: {e}")
            return None
    
    def get_auction_details(self, auction_url: str) -> Optional[Dict]:
        """
        Get detailed information for a specific BaT auction
        
        Args:
            auction_url: URL to the auction detail page
            
        Returns:
            Dictionary with detailed auction information
        """
        try:
            driver = self._get_driver()
            
            logger.info(f"Getting details for auction: {auction_url}")
            
            # Navigate to auction detail page
            driver.get(auction_url)
            self._wait_random_delay()
            
            # Wait for page to load
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".auction-body, .listing-details, .content"))
                )
            except TimeoutException:
                logger.warning("BaT auction detail page took too long to load")
                return None
            
            details = {
                'detailed_description': None,
                'seller_comments': None,
                'vehicle_history': None,
                'recent_work': None,
                'additional_images': [],
                'bid_history': [],
                'reserve_status': None,
                'seller_name': None,
                'location': None,
                'vin': None,
                'engine_specs': None,
                'drivetrain_specs': None,
                'features': []
            }
            
            # Extract detailed description
            try:
                desc_selectors = [
                    ".auction-description",
                    ".seller-comments",
                    ".description",
                    ".content p"
                ]
                
                for selector in desc_selectors:
                    try:
                        desc_element = driver.find_element(By.CSS_SELECTOR, selector)
                        details['detailed_description'] = desc_element.text.strip()
                        break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.debug(f"Could not extract detailed description: {e}")
            
            # Extract seller information
            try:
                seller_selectors = [
                    ".seller-name",
                    ".seller-info",
                    "[class*='seller']"
                ]
                
                for selector in seller_selectors:
                    try:
                        seller_element = driver.find_element(By.CSS_SELECTOR, selector)
                        details['seller_name'] = seller_element.text.strip()
                        break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                logger.debug(f"Could not extract seller info: {e}")
            
            # Extract additional images
            try:
                img_elements = driver.find_elements(By.CSS_SELECTOR, ".gallery img, .auction-images img, .photos img")
                details['additional_images'] = [
                    img.get_attribute('src') 
                    for img in img_elements 
                    if img.get_attribute('src') and 'placeholder' not in img.get_attribute('src')
                ]
            except Exception as e:
                logger.debug(f"Could not extract additional images: {e}")
            
            # Extract vehicle specifications
            try:
                spec_elements = driver.find_elements(By.CSS_SELECTOR, ".specs dd, .specifications li, .vehicle-details li")
                details['features'] = [elem.text.strip() for elem in spec_elements if elem.text.strip()]
            except Exception as e:
                logger.debug(f"Could not extract specifications: {e}")
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting auction details: {e}")
            return None
    
    def close(self):
        """Close the client and cleanup resources"""
        self._close_driver()
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()

# Convenience function for backward compatibility
def search_bat_listings(query: str, filters: Optional[Dict] = None, limit: int = 25, offset: int = 0) -> List[Dict]:
    """
    Search Bring a Trailer listings (convenience function)
    
    Args:
        query: Search query
        filters: Optional filters dict
        limit: Maximum results
        offset: Pagination offset
        
    Returns:
        List of auction dictionaries
    """
    client = BringATrailerClient()
    try:
        return client.search_listings(query, filters, limit, offset)
    finally:
        client.close()