#!/usr/bin/env python3
"""
Detailed debug of Autotrader card structure
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def debug_autotrader_detailed():
    print("🔍 Debugging Autotrader Card Structure")
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
        
        # Navigate to Autotrader
        url = "https://www.autotrader.com/cars-for-sale/all-cars"
        print(f"Navigating to: {url}")
        driver.get(url)
        time.sleep(5)
        
        # Find listing cards
        listing_cards = driver.find_elements(By.CSS_SELECTOR, "[data-cmp='inventoryListing']")
        print(f"\nFound {len(listing_cards)} listing cards")
        
        if listing_cards:
            # Examine the first few cards
            for i, card in enumerate(listing_cards[:3]):
                print(f"\n🚗 Autotrader Card {i+1}:")
                print("-" * 40)
                
                # Get the full text of the card
                card_text = card.text
                print(f"Card Text Length: {len(card_text)} characters")
                print(f"Card Text (first 300 chars):")
                print(card_text[:300])
                print("...")
                
                # Look for links
                try:
                    links = card.find_elements(By.CSS_SELECTOR, "a")
                    if links:
                        for j, link in enumerate(links[:3]):
                            href = link.get_attribute('href')
                            if href:
                                print(f"   Link {j+1}: {href}")
                except:
                    pass
                
                # Look for images
                try:
                    imgs = card.find_elements(By.CSS_SELECTOR, "img")
                    if imgs:
                        for j, img in enumerate(imgs[:2]):
                            src = img.get_attribute('src')
                            if src:
                                print(f"   Image {j+1}: {src}")
                except:
                    pass
                
                if i >= 2:  # Only show first 3 cards
                    break
        
        else:
            print("❌ No listing cards found")
        
    except Exception as e:
        print(f"❌ Error during detailed debugging: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    debug_autotrader_detailed()