#!/usr/bin/env python3
"""
Test source-specific search syntax
"""

from nlp_search import parse_natural_language_query

def test_source_syntax():
    print("🔍 Testing Source-Specific Search Syntax")
    print("=" * 60)
    
    test_queries = [
        "Tesla Model 3 source:ebay",
        "Honda Civic from:carmax", 
        "BMW X5 on:cargurus",
        "Porsche 911 source:bat",
        "Ford F-150 from:truecar",
        "Toyota Camry on:cars.com",
        "Audi A4 source:autodev",
        "Tesla Model S under $50k source:ebay",
        "Honda Civic 2020-2022 from:cargurus price under $30k"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        parsed = parse_natural_language_query(query)
        
        print(f"   Sources: {parsed.get('sources', 'None detected')}")
        print(f"   Cleaned Query: '{parsed.get('cleaned_query', query)}'")
        
        if parsed.get('make'):
            print(f"   Make: {parsed['make']}")
        if parsed.get('model'):
            print(f"   Model: {parsed['model']}")
        if parsed.get('price_max'):
            print(f"   Max Price: ${parsed['price_max']:,}")
        if parsed.get('year_min') or parsed.get('year_max'):
            year_range = f"{parsed.get('year_min', '')}-{parsed.get('year_max', '')}"
            print(f"   Year Range: {year_range}")

    print("\n" + "=" * 60)
    print("✅ All supported source syntaxes:")
    print("   • source:ebay")
    print("   • from:carmax") 
    print("   • on:cargurus")
    print("   • source:bat (maps to bringatrailer)")
    print("   • from:truecar")
    print("   • on:cars (maps to cars.com)")
    print("   • source:autodev")
    
    print("\n💡 Example searches you can try:")
    print("   Tesla Model 3 source:ebay")
    print("   Honda Civic under $25k from:carmax")
    print("   BMW X5 2020-2022 on:cargurus")

if __name__ == "__main__":
    test_source_syntax()