#!/usr/bin/env python3
"""
Debug eBay parsing specifically
"""
import json
import re

def test_year_extraction(title: str) -> int:
    """Test the year extraction logic"""
    year_pattern = r'\b(19\d{2}|20\d{2})\b'
    year_match = re.search(year_pattern, title)
    year = int(year_match.group(1)) if year_match else None
    return year

def debug_ebay_parsing():
    """Debug why eBay vehicles are being filtered out"""
    print("🔍 Debugging eBay Vehicle Parsing")
    print("=" * 50)
    
    # Load the saved eBay response
    try:
        with open('ebay_debug_response.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ ebay_debug_response.json not found. Run debug_ebay_response.py first.")
        return
    
    print(f"Total eBay results: {data.get('total', 0)}")
    print(f"Items in response: {len(data.get('itemSummaries', []))}")
    
    # Test search parameters
    search_year_min = 2018
    search_year_max = None
    search_price_max = 35000
    
    print(f"\nSearch filters:")
    print(f"  year_min: {search_year_min}")
    print(f"  price_max: ${search_price_max:,}")
    
    # Process each item
    filtered_out = []
    passed_filter = []
    
    for i, item in enumerate(data.get('itemSummaries', [])):
        title = item.get('title', '')
        
        # Extract year like the eBay client does
        year = test_year_extraction(title)
        
        # Get price
        price = None
        if 'price' in item:
            price = float(item['price'].get('value', 0))
        
        print(f"\n{i+1}. {title}")
        print(f"   Extracted year: {year}")
        print(f"   Price: ${price:,}" if price else "   Price: N/A")
        
        # Apply the same filters as eBay client
        filtered = False
        reason = []
        
        if search_year_min and year and year < search_year_min:
            filtered = True
            reason.append(f"year {year} < {search_year_min}")
        
        if search_price_max and price and price > search_price_max:
            filtered = True
            reason.append(f"price ${price:,} > ${search_price_max:,}")
        
        if filtered:
            print(f"   ❌ FILTERED OUT: {', '.join(reason)}")
            filtered_out.append(item)
        else:
            print(f"   ✅ PASSED FILTER")
            passed_filter.append(item)
    
    print(f"\n" + "=" * 50)
    print(f"📊 FILTERING RESULTS")
    print(f"=" * 50)
    print(f"Total items: {len(data.get('itemSummaries', []))}")
    print(f"Passed filter: {len(passed_filter)}")
    print(f"Filtered out: {len(filtered_out)}")
    
    if len(filtered_out) > len(passed_filter):
        print(f"\n💡 ISSUE: Most vehicles filtered out!")
        print(f"   Consider adjusting search parameters:")
        print(f"   - Lower year_min (currently {search_year_min})")
        print(f"   - Raise price_max (currently ${search_price_max:,})")

if __name__ == "__main__":
    debug_ebay_parsing()