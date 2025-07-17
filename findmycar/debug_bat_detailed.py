#!/usr/bin/env python3
"""
Detailed debug of BaT auction structure
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def debug_bat_detailed():
    print("🔍 Debugging BaT Auction Elements Structure")
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
        
        # Test current auctions page
        print("\n🔍 Testing main auctions page...")
        driver.get("https://bringatrailer.com/auctions/")
        time.sleep(5)
        
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Look for actual auction listings
        selectors_to_check = [
            ".auction-item",
            ".listing-item", 
            ".auction-tile",
            ".listing-tile",
            ".card",
            ".tile",
            "[class*='auction']",
            "[class*='listing']",
            "article",
            ".post",
            "[data-auction]",
            "[data-listing]"
        ]
        
        found_elements = []
        
        for selector in selectors_to_check:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) < 100:  # Filter out too-generic selectors
                    found_elements.append((selector, elements))
                    print(f"✅ {selector}: {len(elements)} elements")
            except Exception as e:
                pass
        
        # Examine the most promising selectors
        for selector, elements in found_elements[:3]:
            print(f"\n🚗 Examining {selector} elements:")
            print("-" * 40)
            
            for i, elem in enumerate(elements[:3]):
                print(f"\nElement {i+1}:")
                
                # Get element text
                elem_text = elem.text.strip()
                if elem_text:
                    print(f"   Text (first 200 chars): {elem_text[:200]}")
                
                # Look for links
                try:
                    links = elem.find_elements(By.CSS_SELECTOR, "a")
                    if links:
                        href = links[0].get_attribute('href')
                        if href and 'auction' in href:
                            print(f"   Auction Link: {href}")
                except:
                    pass
                
                # Look for images
                try:
                    imgs = elem.find_elements(By.CSS_SELECTOR, "img")
                    if imgs:
                        src = imgs[0].get_attribute('src')
                        if src:
                            print(f"   Image: {src}")
                except:
                    pass
                
                # Look for price/bid info
                price_selectors = [".price", ".bid", ".current-bid", "[class*='price']", "[class*='bid']"]
                for price_sel in price_selectors:
                    try:
                        price_elem = elem.find_element(By.CSS_SELECTOR, price_sel)
                        if price_elem.text.strip():
                            print(f"   Price/Bid: {price_elem.text.strip()}")
                            break
                    except:
                        pass
        
        # Try searching for a specific car
        print(f"\n🔍 Testing search functionality...")
        try:
            search_box = driver.find_element(By.CSS_SELECTOR, "input[type='search'], .search-input, #search")
            if search_box:
                print("✅ Found search box")
                search_box.clear()
                search_box.send_keys("Porsche 911")
                
                # Look for search button
                search_buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], .search-button, .search-submit")
                if search_buttons:
                    search_buttons[0].click()
                    time.sleep(3)
                    print("✅ Submitted search")
                    
                    # Check results
                    new_url = driver.current_url
                    print(f"New URL after search: {new_url}")
        except Exception as e:
            print(f"❌ Search test failed: {e}")
        
    except Exception as e:
        print(f"❌ Error during detailed debugging: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    debug_bat_detailed()