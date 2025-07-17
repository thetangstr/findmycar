#!/usr/bin/env python3
"""
Debug TrueCar integration to see what's happening
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def debug_truecar():
    print("🔍 Debugging TrueCar Integration")
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
        
        # Test different TrueCar URLs
        urls_to_try = [
            "https://www.truecar.com/used-cars-for-sale/listings",
            "https://www.truecar.com/used-cars-for-sale/listings/?searchRadius=50&zip=10001",
            "https://www.truecar.com/used-cars-for-sale/",
            "https://www.truecar.com/"
        ]
        
        for i, url in enumerate(urls_to_try):
            print(f"\n{i+1}️⃣ Testing URL: {url}")
            
            try:
                driver.get(url)
                time.sleep(3)
                
                print(f"   Page title: {driver.title}")
                print(f"   Current URL: {driver.current_url}")
                
                # Check for blocks or errors
                page_source = driver.page_source[:500].lower()
                if any(block_word in page_source for block_word in ['blocked', 'captcha', 'access denied', 'forbidden']):
                    print("   ❌ Page appears to be blocked")
                    continue
                else:
                    print("   ✅ Page appears accessible")
                
                # Look for car listing elements
                selectors_to_try = [
                    "[data-test='vehicle-card']",
                    ".vehicle-card",
                    ".listing-card", 
                    ".car-card",
                    ".result-card",
                    "[class*='listing']",
                    "[class*='vehicle']",
                    "[class*='car']"
                ]
                
                found_elements = False
                for selector in selectors_to_try:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"   ✅ Found {len(elements)} elements with: {selector}")
                            found_elements = True
                            
                            # Show sample content
                            if elements[0].text.strip():
                                sample = elements[0].text.strip()[:100]
                                print(f"      Sample: {sample}")
                    except Exception as e:
                        pass
                
                if found_elements:
                    print(f"   🎯 This URL has listings: {url}")
                    break
                else:
                    print("   ❌ No listing elements found")
                    
            except Exception as e:
                print(f"   ❌ Error loading URL: {e}")
        
        # Test search functionality 
        print(f"\n🔍 Testing search...")
        try:
            driver.get("https://www.truecar.com/")
            time.sleep(3)
            
            # Look for search inputs
            search_selectors = [
                "input[placeholder*='make']",
                "input[placeholder*='search']",
                "input[type='search']",
                "input[name='make']",
                "input[id*='search']"
            ]
            
            for selector in search_selectors:
                try:
                    search_input = driver.find_element(By.CSS_SELECTOR, selector)
                    if search_input:
                        print(f"   ✅ Found search input: {selector}")
                        break
                except:
                    pass
                    
        except Exception as e:
            print(f"   ❌ Search test failed: {e}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    debug_truecar()