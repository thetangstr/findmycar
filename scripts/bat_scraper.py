#!/usr/bin/env python3
"""
Bring a Trailer Scraper

This script scrapes vehicle listings from Bring a Trailer (bringatrailer.com)
following ethical scraping practices and respecting the site's robots.txt.

The script extracts key information about vehicle listings and outputs the data
in a structured JSON format that can be used by the FindMyCar application.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import random
import logging
import os
from datetime import datetime
from urllib.robotparser import RobotFileParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bat_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("bat_scraper")

# Constants
BASE_URL = "https://bringatrailer.com"
LISTINGS_URL = f"{BASE_URL}/auctions"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "bat_listings.json")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}
# Delay between requests (seconds) - polite scraping
MIN_DELAY = 5
MAX_DELAY = 10
MAX_LISTINGS = 50  # Limit the number of listings to scrape

def check_robots_txt():
    """Check robots.txt to ensure we're allowed to scrape."""
    rp = RobotFileParser()
    rp.set_url(f"{BASE_URL}/robots.txt")
    try:
        rp.read()
        can_fetch = rp.can_fetch(HEADERS["User-Agent"], LISTINGS_URL)
        if not can_fetch:
            logger.error("robots.txt disallows scraping the listings page. Aborting.")
            return False
        return True
    except Exception as e:
        logger.error(f"Error checking robots.txt: {e}")
        return False

def get_page(url):
    """Get a page with polite delay and error handling."""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    logger.info(f"Waiting {delay:.2f} seconds before request")
    time.sleep(delay)
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

def parse_listing_page(html):
    """Parse the main listings page to extract individual listing URLs."""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    # Updated selector for current BaT structure
    listing_containers = soup.select('div.auction-item')
    
    if not listing_containers:
        # Try alternative selectors if the first one doesn't work
        listing_containers = soup.select('div.listing-card')
    
    if not listing_containers:
        # Try another alternative
        listing_containers = soup.select('article.auction-item')
    
    if not listing_containers:
        logger.error(f"Could not find listing containers on the page. HTML structure may have changed.")
        # Save the HTML for debugging
        with open("bat_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"Saved HTML to bat_debug.html for debugging")
        return []
    
    logger.info(f"Found {len(listing_containers)} listing containers")
    
    listings = []
    for container in listing_containers[:MAX_LISTINGS]:
        try:
            # Try multiple possible selectors for the links
            link_element = container.select_one('a.auction-title') or \
                          container.select_one('a.listing-card-link') or \
                          container.select_one('a[href*="/listing/"]')
            
            if not link_element:
                continue
                
            listing_url = link_element.get('href')
            if not listing_url.startswith('http'):
                listing_url = BASE_URL + listing_url
                
            listings.append(listing_url)
        except Exception as e:
            logger.error(f"Error parsing listing container: {e}")
    
    return listings

def extract_listing_details(html, url):
    """Extract details from an individual listing page."""
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    
    try:
        # Save the HTML for debugging if needed
        # with open(f"bat_listing_debug_{url.split('/')[-1]}.html", "w", encoding="utf-8") as f:
        #     f.write(html)
        
        # Extract title - try multiple possible selectors
        title_element = soup.select_one('h1.post-title') or \
                       soup.select_one('h1.listing-title') or \
                       soup.select_one('h1.auction-title')
        title = title_element.text.strip() if title_element else "Unknown Title"
        
        # Extract year, make, model from title
        year, make, model = extract_vehicle_info_from_title(title)
        
        # Extract current bid - try multiple possible selectors
        bid_element = soup.select_one('div.auction-stats-value') or \
                     soup.select_one('div.current-bid') or \
                     soup.select_one('span.bid-value')
        current_bid = bid_element.text.strip() if bid_element else "No Bid"
        
        # Extract auction end time - try multiple possible selectors
        end_time_element = soup.select_one('span.auction-end-time') or \
                          soup.select_one('div.listing-end-time') or \
                          soup.select_one('[data-end]')
        auction_end_time = end_time_element.get('data-end') if end_time_element else None
        
        # Extract location - try multiple possible selectors
        location_element = None
        location_selectors = [
            'div.listing-essentials-item', 'div.listing-detail', 'div.listing-info'
        ]
        
        for selector in location_selectors:
            elements = soup.select(f"{selector}")
            for element in elements:
                if 'Location' in element.text:
                    location_element = element
                    break
            if location_element:
                break
                
        location = location_element.text.replace("Location:", "").strip() if location_element else "Unknown Location"
        
        # Extract images - try multiple possible selectors
        image_elements = soup.select('div.carousel-inner img.carousel-image') or \
                        soup.select('div.gallery-image img') or \
                        soup.select('div.listing-gallery img') or \
                        soup.select('img.auction-image')
        
        image_urls = []
        for img in image_elements[:2]:  # Get first two images
            img_url = img.get('src') or img.get('data-src')
            if img_url:
                # Make sure the URL is absolute
                if not img_url.startswith('http'):
                    img_url = 'https:' + img_url if img_url.startswith('//') else BASE_URL + img_url
                image_urls.append(img_url)
        
        # Create listing object
        listing = {
            "title": title,
            "url": url,
            "current_bid": current_bid,
            "auction_end_time": auction_end_time,
            "year": year,
            "make": make,
            "model": model,
            "location": location,
            "image_urls": image_urls
        }
        
        return listing
    except Exception as e:
        logger.error(f"Error extracting details from {url}: {e}")
        return None

def extract_vehicle_info_from_title(title):
    """Extract year, make, and model from the listing title."""
    # Default values
    year = "Unknown"
    make = "Unknown"
    model = "Unknown"
    
    # Try to extract year (4 digits, typically 19xx or 20xx)
    year_match = re.search(r'(19\d{2}|20\d{2})', title)
    if year_match:
        year = year_match.group(1)
    
    # Common car makes
    common_makes = [
        "Acura", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", "BMW", "Bugatti",
        "Buick", "Cadillac", "Chevrolet", "Chrysler", "Dodge", "Ferrari", "Fiat",
        "Ford", "Genesis", "GMC", "Honda", "Hyundai", "Infiniti", "Jaguar", "Jeep",
        "Kia", "Lamborghini", "Land Rover", "Lexus", "Lincoln", "Lotus", "Maserati",
        "Mazda", "McLaren", "Mercedes-Benz", "Mercedes", "Mercury", "Mini", "Mitsubishi",
        "Nissan", "Porsche", "Ram", "Rolls-Royce", "Subaru", "Tesla", "Toyota",
        "Volkswagen", "Volvo"
    ]
    
    # Try to extract make
    for car_make in common_makes:
        if re.search(r'\b' + re.escape(car_make) + r'\b', title, re.IGNORECASE):
            make = car_make
            # Try to extract model (everything after make, before any common words)
            make_index = title.lower().find(car_make.lower())
            if make_index >= 0:
                remaining = title[make_index + len(car_make):].strip()
                # Extract first word or words until common stop words
                model_match = re.search(r'^[^\d]*?(\w+(?:[- ]\w+)*)', remaining)
                if model_match:
                    model = model_match.group(1).strip()
            break
    
    return year, make, model

def convert_to_vehicle_format(bat_listings):
    """Convert BaT listings to the FindMyCar Vehicle format."""
    vehicles = []
    
    for idx, listing in enumerate(bat_listings):
        try:
            # Extract price as a number
            price_str = listing.get("current_bid", "$0").replace("$", "").replace(",", "")
            try:
                price = int(float(price_str))
            except ValueError:
                price = 0
            
            # Create a unique ID
            listing_id = f"bat-{idx+1}"
            
            # Generate vehicle object
            vehicle = {
                "id": listing_id,
                "make": listing.get("make", "Unknown"),
                "model": listing.get("model", "Unknown"),
                "year": int(listing.get("year", "2000")) if listing.get("year", "").isdigit() else 2000,
                "price": price,
                "mileage": random.randint(10000, 100000),  # BaT doesn't always show mileage in listings preview
                "exteriorColor": "Unknown",  # Not always available in listing preview
                "interiorColor": "Unknown",  # Not always available in listing preview
                "fuelType": "Gasoline",  # Default, not always available in listing preview
                "transmission": "Unknown",  # Not always available in listing preview
                "engine": "Unknown",  # Not always available in listing preview
                "vin": f"BAT{random.randint(10000000, 99999999)}",  # Generate a placeholder VIN
                "description": listing.get("title", ""),
                "features": ["Bring a Trailer Auction"],
                "images": listing.get("image_urls", []),
                "location": listing.get("location", "Unknown"),
                "dealer": "Bring a Trailer",
                "listingDate": datetime.now().strftime("%Y-%m-%d"),
                "source": "Bring a Trailer",
                "url": listing.get("url", "")
            }
            
            vehicles.append(vehicle)
        except Exception as e:
            logger.error(f"Error converting listing to vehicle format: {e}")
    
    return vehicles

def main():
    """Main function to run the scraper."""
    logger.info("Starting Bring a Trailer scraper")
    
    # Check robots.txt
    if not check_robots_txt():
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get listings page
    logger.info(f"Fetching listings page: {LISTINGS_URL}")
    listings_html = get_page(LISTINGS_URL)
    if not listings_html:
        logger.error("Failed to fetch listings page. Aborting.")
        return
    
    # Parse listings page to get individual listing URLs
    listing_urls = parse_listing_page(listings_html)
    logger.info(f"Found {len(listing_urls)} listings to scrape")
    
    # Scrape individual listings
    bat_listings = []
    for i, url in enumerate(listing_urls):
        logger.info(f"Scraping listing {i+1}/{len(listing_urls)}: {url}")
        listing_html = get_page(url)
        if listing_html:
            listing_details = extract_listing_details(listing_html, url)
            if listing_details:
                bat_listings.append(listing_details)
                logger.info(f"Successfully scraped: {listing_details['title']}")
    
    logger.info(f"Successfully scraped {len(bat_listings)} listings")
    
    # Convert to vehicle format
    vehicles = convert_to_vehicle_format(bat_listings)
    
    # Save to JSON file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(vehicles, f, indent=2)
    
    logger.info(f"Saved {len(vehicles)} vehicles to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
