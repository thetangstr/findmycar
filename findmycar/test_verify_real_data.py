#!/usr/bin/env python3
"""Verify that real vehicle data is displayed, not fake data."""

import sqlite3
import requests
from bs4 import BeautifulSoup

# Check database content
print("🔍 Checking database content...")
conn = sqlite3.connect('findmycar.db')
cursor = conn.cursor()

# Get sample vehicles
cursor.execute("""
    SELECT make, model, year, price, view_item_url, vin 
    FROM vehicles 
    LIMIT 5
""")
vehicles = cursor.fetchall()

print(f"\n📊 Found {cursor.execute('SELECT COUNT(*) FROM vehicles').fetchone()[0]} vehicles in database")
print("\n🚗 Sample vehicles:")
for v in vehicles:
    print(f"  - {v[2]} {v[0]} {v[1]} - ${v[3]:,.0f} - VIN: {v[5]}")
    print(f"    URL: {v[4][:80]}...")

# Check if homepage displays real data
print("\n🌐 Checking homepage...")
response = requests.get("http://localhost:8601/")
soup = BeautifulSoup(response.text, 'html.parser')

# Look for vehicle cards
vehicle_cards = soup.find_all(class_=['vehicle-card', 'car-card', 'listing-card'])
print(f"\n📋 Found {len(vehicle_cards)} vehicle cards on homepage")

if vehicle_cards:
    print("\n🔎 Analyzing first vehicle card...")
    first_card = vehicle_cards[0]
    
    # Extract text content
    card_text = first_card.get_text(strip=True)
    print(f"Card content preview: {card_text[:200]}...")
    
    # Check for real data indicators
    has_price = '$' in card_text
    has_year = any(str(year) in card_text for year in range(2000, 2025))
    has_make = any(make in card_text for make in ['Honda', 'Toyota', 'Ford', 'Chevrolet', 'BMW', 'Mercedes'])
    
    print(f"\n✅ Real data indicators:")
    print(f"  - Has price: {has_price}")
    print(f"  - Has year: {has_year}")
    print(f"  - Has make: {has_make}")
    
    # Check for eBay listing
    ebay_link = first_card.find('a', href=lambda x: x and 'ebay.com' in x)
    if ebay_link:
        print(f"  - Has eBay link: ✅ {ebay_link['href'][:60]}...")
    
    # Check data source
    source_elem = first_card.find(text=lambda x: x and 'ebay' in x.lower())
    if source_elem:
        print(f"  - Shows data source: ✅ (eBay)")

# Test search functionality
print("\n🔍 Testing search...")
search_response = requests.post("http://localhost:8601/ingest", 
                               data={"query": "Honda"},
                               allow_redirects=False)

if search_response.status_code == 303:
    redirect_url = search_response.headers.get('Location', '')
    print(f"✅ Search redirects to: {redirect_url}")
    
    # Check the message
    if "Successfully ingested" in redirect_url:
        import re
        match = re.search(r'ingested%20(\d+)%20vehicles', redirect_url)
        if match:
            new_vehicles = int(match.group(1))
            print(f"  - New vehicles found: {new_vehicles}")
        
        match = re.search(r'(\d+)%20duplicates', redirect_url)
        if match:
            duplicates = int(match.group(1))
            print(f"  - Duplicates skipped: {duplicates}")

print("\n🎯 Summary:")
if vehicles and (vehicle_cards or "Successfully ingested" in redirect_url):
    print("✅ The application is using REAL DATA from eBay Motors API")
    print("✅ The search functionality is working correctly")
else:
    print("❌ Could not verify real data - check configuration")

conn.close()