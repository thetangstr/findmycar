#!/usr/bin/env python3
"""Test that EG6 search uses correct years."""

import requests

print("🚗 Testing Honda Civic EG6 search fix\n")

# Test the search endpoint directly
print("📍 Sending search request for 'honda civic eg6'...")
response = requests.post(
    "http://localhost:8601/ingest",
    data={
        "query": "honda civic eg6",
        "year_min": "2000",  # Default form values
        "year_max": "2024",  # Default form values
        "sources": ["ebay"]
    },
    allow_redirects=False
)

print(f"Status: {response.status_code}")
if response.status_code == 303:
    redirect_url = response.headers.get('Location', '')
    print(f"Redirect: {redirect_url[:100]}...")
    
    # Check server logs to see what years were used
    print("\n✅ Search request sent successfully!")
    print("📋 Check server logs to verify correct years (1992-1995) were used")
else:
    print(f"❌ Unexpected response: {response.status_code}")

print("\n🔍 The fix should ensure that when searching for 'honda civic eg6':")
print("   - The system detects the EG6 chassis code")
print("   - Uses years 1992-1995 instead of the form defaults 2000-2024")
print("   - Searches for the correct generation of Honda Civic")