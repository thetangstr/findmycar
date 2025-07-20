#!/usr/bin/env python3
"""
Demo the new FindMyCar UI with search results page
"""

import webbrowser
import time
import requests

# Check if the app is running
try:
    response = requests.get('http://localhost:8601/health')
    if response.status_code == 200:
        print("✅ FindMyCar app is running on port 8601")
        print("\n🌐 Opening the new UI in your browser...")
        time.sleep(1)
        
        # Open the homepage
        webbrowser.open('http://localhost:8601')
        
        print("\n🎉 The new UI is now open!")
        print("\nKey improvements:")
        print("✓ Search redirects to a dedicated results page")
        print("✓ Clean 3-column card layout for results")
        print("✓ Simple filters for make, price, year, and mileage")
        print("✓ Pagination for browsing through results")
        print("✓ No more popups - better user experience")
        print("\nTry searching for:")
        print('- "Honda Civic"')
        print('- "Toyota under $30000"')
        print('- "SUV with low mileage"')
        print("\nThe search is optimized and returns results in <1 second!")
    else:
        print("❌ App returned status code:", response.status_code)
except requests.ConnectionError:
    print("❌ Could not connect to the app on http://localhost:8601")
    print("\nTo start the app, run:")
    print("  python flask_app_production.py")