#!/usr/bin/env python3
"""Test search with SQL logging"""

import logging
from database_v2_sqlite import get_database_url, VehicleV2
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from comprehensive_search_engine_sqlite import ComprehensiveSearchEngine

# Enable SQL logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Set up database with echo
engine = create_engine(get_database_url(), echo=True)
Session = sessionmaker(bind=engine)
db = Session()

# Create search engine
search_engine = ComprehensiveSearchEngine(db)

# Test query
query = "Family SUV under $25,000"
print(f"\n{'='*60}")
print(f"Testing query: '{query}'")
print(f"{'='*60}\n")

# Perform search
results = search_engine.search(
    query=query,
    per_page=5
)

print(f"\n{'='*60}")
print(f"Results Summary:")
print(f"Total results: {results['total']}")
print(f"Applied filters: {results.get('applied_filters', {})}")
print(f"{'='*60}")

db.close()