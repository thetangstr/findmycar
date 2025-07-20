#!/usr/bin/env python3
"""Test NLP parser"""

from nlp_search import parse_natural_language_query

# Test queries
queries = [
    "honda",
    "Honda Civic",
    "2020 honda accord",
    "red SUV under 30000",
    ""
]

for query in queries:
    print(f"\nQuery: '{query}'")
    result = parse_natural_language_query(query)
    print(f"Parsed: {result}")