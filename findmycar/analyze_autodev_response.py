#!/usr/bin/env python3

"""
Analyze Auto.dev API response structure
"""

import requests
import json
from typing import Dict, List, Optional

def analyze_autodev_response():
    """Analyze the structure of Auto.dev API response"""
    
    print("🔍 Analyzing Auto.dev API Response Structure...")
    
    # Test basic request
    url = "https://auto.dev/api/listings"
    params = {
        'make': 'Honda',
        'model': 'Civic',
        'year_min': 2020,
        'page': 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Success! Analyzing response structure...")
            print(f"📊 Top-level keys: {list(data.keys())}")
            
            # Analyze each section
            if 'records' in data:
                records = data['records']
                print(f"\n🚗 Found {len(records)} vehicle records")
                
                if records:
                    first_record = records[0]
                    print(f"📋 Record structure: {list(first_record.keys())}")
                    
                    # Show sample vehicle data
                    print("\n📄 Sample vehicle data:")
                    sample_fields = ['year', 'make', 'model', 'trim', 'price', 'mileage', 'location', 'dealer', 'url', 'vin', 'body_style', 'exterior_color', 'interior_color', 'transmission', 'drivetrain', 'fuel_type', 'engine', 'photos']
                    
                    for field in sample_fields:
                        if field in first_record:
                            value = first_record[field]
                            if isinstance(value, (str, int, float)):
                                print(f"  {field}: {value}")
                            elif isinstance(value, list):
                                print(f"  {field}: [{len(value)} items] {value[:2] if value else '[]'}")
                            elif isinstance(value, dict):
                                print(f"  {field}: {{{list(value.keys())}}}")
                            else:
                                print(f"  {field}: {type(value)}")
                    
                    # Show full first record structure (truncated)
                    print(f"\n📦 Full first record (truncated):")
                    print(json.dumps(first_record, indent=2)[:1500] + "...")
            
            # Check other top-level fields
            for key in ['totalCount', 'totalCountFormatted', 'hitsCount', 'promotedAggregations']:
                if key in data:
                    print(f"\n📊 {key}: {data[key]}")
                    
        else:
            print(f"❌ Error {response.status_code}: {response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_different_searches():
    """Test different search queries"""
    
    print("\n" + "="*50)
    print("🧪 Testing Different Search Queries...")
    
    test_queries = [
        {'make': 'Toyota', 'model': 'Prius'},
        {'make': 'BMW', 'model': '3 Series'},
        {'year_min': 2021, 'make': 'Tesla'},
        {'make': 'Ford', 'model': 'F-150', 'year_min': 2020}
    ]
    
    url = "https://auto.dev/api/listings"
    
    for i, params in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {params}")
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                total_count = data.get('totalCount', 0)
                records_count = len(data.get('records', []))
                
                print(f"  ✅ Success: {total_count} total, {records_count} returned")
                
                if data.get('records'):
                    first_record = data['records'][0]
                    title = f"{first_record.get('year', 'N/A')} {first_record.get('make', 'N/A')} {first_record.get('model', 'N/A')}"
                    price = first_record.get('price', 'N/A')
                    print(f"  📄 Sample: {title} - ${price}")
                    
            else:
                print(f"  ❌ Error {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request failed: {e}")

if __name__ == "__main__":
    analyze_autodev_response()
    test_different_searches()
    print("\n✅ Analysis completed!")