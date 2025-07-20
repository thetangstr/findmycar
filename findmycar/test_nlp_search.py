#!/usr/bin/env python3
"""Test NLP search functionality"""

from database_v2_sqlite import get_database_url, VehicleV2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from comprehensive_search_engine_sqlite import ComprehensiveSearchEngine

# Set up database
engine = create_engine(get_database_url())
Session = sessionmaker(bind=engine)
db = Session()

# Create search engine
search_engine = ComprehensiveSearchEngine(db)

# Test query
query = "Family SUV under $25,000"
print(f"Testing query: '{query}'")

# Perform search
results = search_engine.search(
    query=query,
    per_page=10
)

print(f"\nTotal results: {results['total']}")
print(f"Applied filters: {results.get('applied_filters', {})}")

if results['vehicles']:
    print("\nFirst few results:")
    for v in results['vehicles'][:5]:
        print(f"  {v.year} {v.make} {v.model} ({v.body_style}) - ${v.price:,.0f}")
else:
    print("\nNo vehicles found!")
    
    # Debug: Check what filters were applied
    print("\nDebug info:")
    print(f"Query parsed: {results.get('query_parsed', 'N/A')}")
    
    # Try a simpler search
    print("\n\nTrying simpler search for just 'SUV'...")
    simple_results = search_engine.search(
        query="SUV",
        per_page=10
    )
    print(f"Total SUV results: {simple_results['total']}")

db.close()