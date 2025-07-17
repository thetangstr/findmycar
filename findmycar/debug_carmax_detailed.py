#!/usr/bin/env python3
"""
Detailed debug of CarMax car tiles to understand the HTML structure
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def debug_carmax_tiles():
    print("🔍 Debugging CarMax Car Tiles HTML Structure")
    print("=" * 60)
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to CarMax search
        url = "https://www.carmax.com/cars?make=Honda&model=Civic"
        print(f"Navigating to: {url}")
        driver.get(url)
        time.sleep(5)
        
        # Find car tiles
        car_tiles = driver.find_elements(By.CSS_SELECTOR, ".car-tile")
        print(f"\nFound {len(car_tiles)} car tiles")
        
        if car_tiles:
            # Examine the first few tiles
            for i, tile in enumerate(car_tiles[:3]):
                print(f"\n🚗 Car Tile {i+1}:")
                print("-" * 40)
                
                # Get the full HTML of the tile
                tile_html = tile.get_attribute('outerHTML')
                print(f"HTML Length: {len(tile_html)} characters")
                
                # Look for key data attributes and elements
                print("\n📋 Checking for data attributes:")
                
                # Check for common selectors used in the extraction
                selectors_to_check = [
                    "[data-test='vehicle-title']",
                    "[data-test='price']", 
                    "[data-test='mileage']",
                    "[data-test='store-location']",
                    "a[data-test='vehicle-link']",
                    "img[data-test='vehicle-image']",
                    "[data-test='vehicle-details']",
                    # Alternative selectors to try
                    ".price",
                    ".mileage", 
                    ".location",
                    ".title",
                    "a",
                    "img",
                    "h2",
                    "h3",
                    "span"
                ]
                
                for selector in selectors_to_check:
                    try:
                        elements = tile.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"   ✅ {selector}: {len(elements)} elements")
                            # Print text content of first element
                            if elements[0].text.strip():
                                print(f"      Text: '{elements[0].text.strip()}'")
                            if elements[0].get_attribute('href'):
                                print(f"      Href: '{elements[0].get_attribute('href')}'")
                            if elements[0].get_attribute('src'):
                                print(f"      Src: '{elements[0].get_attribute('src')}'")
                        else:
                            print(f"   ❌ {selector}: 0 elements")
                    except Exception as e:
                        print(f"   ❌ {selector}: Error - {e}")
                
                # Print some of the actual HTML to see structure
                print(f"\n📄 HTML Structure (first 500 chars):")
                print(tile_html[:500])
                print("...")
                
                if i >= 2:  # Only show first 3 tiles
                    break
        
        else:
            print("❌ No car tiles found")
        
    except Exception as e:
        print(f"❌ Error during detailed debugging: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    debug_carmax_tiles()