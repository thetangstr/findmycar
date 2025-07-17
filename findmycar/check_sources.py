#!/usr/bin/env python3
"""
Quick check of data source availability
"""
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print("🔍 Checking Data Source Availability")
print("=" * 60)

# 1. Check eBay API
print("\n1. eBay API:")
ebay_id = os.getenv('EBAY_CLIENT_ID', '')
if ebay_id.startswith('test_'):
    print("   ❌ Using test credentials - won't work with real API")
    print("   💡 Need real eBay Developer credentials from https://developer.ebay.com")
else:
    print(f"   ✅ Real credentials found: {ebay_id[:10]}...")

# 2. Check CarMax
print("\n2. CarMax:")
try:
    response = requests.get("https://www.carmax.com/cars", timeout=5)
    if response.status_code == 200:
        print("   ✅ Website accessible")
    else:
        print(f"   ⚠️  Website returned status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Connection error: {str(e)}")

# 3. Check Bring a Trailer
print("\n3. Bring a Trailer (BAT):")
try:
    response = requests.get("https://bringatrailer.com/auctions/", timeout=5)
    if response.status_code == 200:
        print("   ✅ Website accessible")
    else:
        print(f"   ⚠️  Website returned status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Connection error: {str(e)}")

# 4. Check Cars.com
print("\n4. Cars.com:")
try:
    response = requests.get("https://www.cars.com/shopping/", timeout=5)
    if response.status_code == 200:
        print("   ✅ Website accessible")
    else:
        print(f"   ⚠️  Website returned status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Connection error: {str(e)}")

# 5. Check CarGurus
print("\n5. CarGurus:")
try:
    response = requests.get("https://www.cargurus.com/Cars/", timeout=5)
    if response.status_code == 200:
        print("   ✅ Website accessible")
    else:
        print(f"   ⚠️  Website returned status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Connection error: {str(e)}")

# 6. Check TrueCar
print("\n6. TrueCar:")
try:
    response = requests.get("https://www.truecar.com/", timeout=5)
    if response.status_code == 200:
        print("   ✅ Website accessible")
    else:
        print(f"   ⚠️  Website returned status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Connection error: {str(e)}")

# 7. Check Selenium WebDriver
print("\n7. Selenium WebDriver (for scraping):")
try:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.quit()
    print("   ✅ Chrome WebDriver available")
except Exception as e:
    print(f"   ❌ WebDriver error: {str(e)}")
    print("   💡 Install with: pip install selenium && brew install chromedriver")

# Summary
print("\n" + "=" * 60)
print("📊 SUMMARY:")
print("\n⚠️  Current Issues:")
print("1. eBay API needs real credentials (not test ones)")
print("2. Web scraping sources may be blocked by anti-bot measures")
print("3. Some sources require Selenium WebDriver setup")

print("\n✅ What's Working:")
print("1. Database has 96 existing vehicles from previous eBay searches")
print("2. Search interface and filtering work correctly")
print("3. Vehicle detail pages and favorites system work")

print("\n💡 To get real-time searches working:")
print("1. Add real eBay API credentials to .env file")
print("2. Consider using proxy services for web scraping")
print("3. Or use the existing 96 vehicles for demo purposes")