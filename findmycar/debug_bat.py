#!/usr/bin/env python3
"""
Debug Bring a Trailer integration to see what's happening
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def debug_bat():
    print("🔍 Debugging Bring a Trailer Integration")
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
        
        # Test 1: Basic page load - try different URLs
        urls_to_try = [
            "https://bringatrailer.com/cars/?search=Porsche+911",
            "https://bringatrailer.com/auctions/",
            "https://bringatrailer.com/auctions/search/?q=Porsche",
            "https://bringatrailer.com/"
        ]
        
        for i, url in enumerate(urls_to_try):
            print(f"\n{i+1}️⃣ Testing URL: {url}")
            
            driver.get(url)
            time.sleep(3)
            
            print(f"   Page title: {driver.title}")
            print(f"   Current URL: {driver.current_url}")
            
            # Check if page loads normally
            page_source = driver.page_source[:500]
            print(f"   Page source (first 500 chars): {page_source}")
            
            if "blocked" in page_source.lower() or "captcha" in page_source.lower():
                print("   ❌ Page appears to be blocked")
                continue
            else:
                print("   ✅ Page appears to load normally")
            
            # Look for auction/listing elements
            selectors_to_try = [
                ".auction-tile",
                ".listing-card", 
                ".auction-card",
                ".item",
                "[data-auction-id]",
                ".tile",
                ".card",
                ".listing",
                "[class*='auction']",
                "[class*='listing']",
                "[class*='car']"
            ]
            
            print(f"   🔍 Looking for auction elements...")
            found_any = False
            
            for selector in selectors_to_try:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"   ✅ Found {len(elements)} elements with selector: {selector}")
                        found_any = True
                        
                        # Show sample text from first element
                        if elements[0].text.strip():
                            sample_text = elements[0].text.strip()[:100]
                            print(f"      Sample text: '{sample_text}'")
                except Exception as e:
                    pass
            
            if not found_any:
                print("   ❌ No auction elements found with any selector")
            
            # If this URL worked, break
            if found_any:
                print(f"   🎯 This URL works best: {url}")
                break
        
        # Test manual navigation
        print("\n🧭 Testing manual navigation...")
        driver.get("https://bringatrailer.com")
        time.sleep(5)
        
        # Look for any car-related links
        all_links = driver.find_elements(By.TAG_NAME, "a")
        car_links = [link for link in all_links if any(keyword in link.get_attribute("href").lower() for keyword in ["car", "auction", "listing", "porsche", "bmw"]) if link.get_attribute("href")]
        
        print(f"   Found {len(car_links)} potential car/auction links")
        
        if car_links:
            print("   ✅ BaT appears to be accessible")
            print(f"   Sample link: {car_links[0].get_attribute('href')}")
        else:
            print("   ❌ No car/auction links found")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass
    
    print("\n" + "=" * 60)
    print("🔧 Recommendations:")
    print("1. Check if BaT has updated their page structure")
    print("2. May need to update CSS selectors in bat_client.py")
    print("3. Consider using BaT's search page instead of auctions page")
    print("4. Verify BaT isn't detecting automation")

if __name__ == "__main__":
    debug_bat()