#!/usr/bin/env python3
"""Test Flask session issue"""

import requests

# Test the API multiple times
print("Testing Flask API repeatedly:")

for i in range(3):
    print(f"\nAttempt {i+1}:")
    
    # Test empty search
    response = requests.get("http://localhost:8602/api/search/v2", params={"query": ""})
    if response.ok:
        data = response.json()
        print(f"  Empty query: {data.get('total', 0)} vehicles")
    
    # Test Honda search
    response = requests.get("http://localhost:8602/api/search/v2", params={"query": "Honda"})
    if response.ok:
        data = response.json()
        print(f"  Honda query: {data.get('total', 0)} vehicles")
    
    # Test with explicit filter
    response = requests.get("http://localhost:8602/api/search/v2", params={"make": "Honda"})
    if response.ok:
        data = response.json()
        print(f"  Make filter: {data.get('total', 0)} vehicles")