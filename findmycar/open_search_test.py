#!/usr/bin/env python3
"""
Open search test page in browser
"""

import webbrowser
import time

print("Opening search results page for 'honda'...")
print("\nIMPORTANT: Open the browser's Developer Console (F12) to see debug output")
print("\nLook for:")
print("1. 'Page loaded, initializing...'")
print("2. 'Query from URL: honda'")
print("3. 'Search response:' with the API data")
print("\nIf you see 'No vehicles found', check what the console logs show.")

time.sleep(1)
webbrowser.open('http://localhost:8601/search?q=honda')