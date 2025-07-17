#!/usr/bin/env python3
"""
Debug CarMax integration to see what's actually happening
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def debug_carmax():
    print("🔍 Debugging CarMax Integration")
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
        
        # Test 1: Basic page load
        print("\n1️⃣ Testing basic page load...")
        url = "https://www.carmax.com/cars?make=Honda&model=Civic"
        print(f"   URL: {url}")
        
        driver.get(url)
        time.sleep(3)
        
        print(f"   Page title: {driver.title}")
        print(f"   Current URL: {driver.current_url}")
        
        # Test 2: Check for any error/blocked pages
        print("\n2️⃣ Checking for blocks/errors...")
        page_source = driver.page_source[:500]
        print(f"   Page source (first 500 chars): {page_source}")
        
        if "blocked" in page_source.lower() or "captcha" in page_source.lower():
            print("   ❌ Page appears to be blocked")
        else:
            print("   ✅ Page appears to load normally")
        
        # Test 3: Look for any vehicle elements
        print("\n3️⃣ Looking for vehicle elements...")
        
        # Try various selectors that might contain vehicles
        selectors_to_try = [
            "[data-test='search-result']",
            ".vehicle-card",
            ".car-tile",
            ".search-result",
            "[data-qa='vehicle-tile']",
            ".km-card",
            ".vehicle-listing",
            "[class*='vehicle']",
            "[class*='car']",
            "[class*='listing']"
        ]
        
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   ✅ Found {len(elements)} elements with selector: {selector}")
                else:
                    print(f"   ❌ No elements found with selector: {selector}")
            except Exception as e:
                print(f"   ❌ Error with selector {selector}: {e}")
        
        # Test 4: Check for loading indicators
        print("\n4️⃣ Checking for loading indicators...")
        loading_selectors = [
            ".loading",
            ".spinner",
            "[class*='loading']",
            "[class*='spinner']"
        ]
        
        for selector in loading_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"   ⏳ Found loading indicator: {selector}")
        
        # Test 5: Wait and check again
        print("\n5️⃣ Waiting 10 seconds and checking again...")
        time.sleep(10)
        
        # Re-check for vehicle elements
        for selector in ["[data-test='search-result']", ".vehicle-card", "[class*='vehicle']"]:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"   ✅ After wait, found {len(elements)} elements with: {selector}")
                break
        else:
            print("   ❌ Still no vehicle elements found after waiting")
        
        # Test 6: Try a more specific search
        print("\n6️⃣ Trying direct navigation to search page...")
        driver.get("https://www.carmax.com/cars")
        time.sleep(5)
        
        # Look for any cars on the general page
        all_links = driver.find_elements(By.TAG_NAME, "a")
        car_links = [link for link in all_links if "cars/" in link.get_attribute("href") or ""]
        print(f"   Found {len(car_links)} potential car links")
        
        if car_links:
            print("   ✅ CarMax appears to be working - found car links")
            print(f"   Sample link: {car_links[0].get_attribute('href')}")
        else:
            print("   ❌ No car links found")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass
    
    print("\n" + "=" * 60)
    print("🔧 Recommendations:")
    print("1. Check if CarMax has updated their page structure")
    print("2. May need to update CSS selectors in carmax_client.py")
    print("3. Consider increasing wait times for dynamic content")
    print("4. Verify anti-bot detection isn't triggering")

if __name__ == "__main__":
    debug_carmax()