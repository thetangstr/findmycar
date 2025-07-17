#!/usr/bin/env python3
"""
Verify EG6 chassis code parsing
"""

from nlp_search import parse_natural_language_query
from chassis_codes import parse_chassis_code

# Test the parsing
queries = [
    "honda civic eg6",
    "EG6",
    "looking for eg6 civic"
]

for query in queries:
    print(f"\n🔍 Testing: '{query}'")
    
    # Direct chassis code parsing
    chassis = parse_chassis_code(query)
    print(f"Chassis parsing: {chassis}")
    
    # Full NLP parsing
    result = parse_natural_language_query(query)
    print(f"NLP result: Make={result.get('make')}, Model={result.get('model')}, Years={result.get('year_min')}-{result.get('year_max')}")
    
# Expected: Honda Civic 1992-1995 for all queries