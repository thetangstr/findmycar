#!/usr/bin/env python3
"""
Test chassis code parsing
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from nlp_search import parse_natural_language_query
from chassis_codes import parse_chassis_code

def test_chassis_parsing():
    """Test various chassis code queries"""
    
    test_queries = [
        "honda civic eg6",
        "EG6 civic",
        "looking for an eg6",
        "JDM EK9 Type R",
        "NA miata under 10k",
        "FD RX7 for sale",
        "E46 M3",
        "skyline r34"
    ]
    
    print("🧪 Testing Chassis Code Parsing")
    print("="*60)
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        
        # Test direct chassis parsing
        chassis_info = parse_chassis_code(query)
        if chassis_info.get('found'):
            print(f"   ✅ Chassis code found: {chassis_info['chassis_code']}")
            print(f"      {chassis_info['year_min']}-{chassis_info['year_max']} {chassis_info['make']} {chassis_info['model']}")
            if chassis_info.get('variant'):
                print(f"      Variant: {chassis_info['variant']}")
        else:
            print("   ❌ No chassis code found")
        
        # Test full NLP parsing
        filters = parse_natural_language_query(query)
        print(f"   📊 NLP Results:")
        print(f"      Make: {filters.get('make')}")
        print(f"      Model: {filters.get('model')}")
        print(f"      Years: {filters.get('year_min')}-{filters.get('year_max')}")
        if filters.get('chassis_code'):
            print(f"      Chassis Code: {filters.get('chassis_code')}")

if __name__ == "__main__":
    test_chassis_parsing()