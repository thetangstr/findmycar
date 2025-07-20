#!/usr/bin/env python3
"""Debug search issue in comprehensive search engine"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from database_v2_sqlite import get_engine, VehicleV2
from comprehensive_search_engine_sqlite import ComprehensiveSearchEngine
import logging

# Enable SQLAlchemy logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Create session
engine = get_engine()
Session = sessionmaker(bind=engine)
session = Session()

print(f"Total vehicles in DB: {session.query(VehicleV2).count()}")
print(f"Active vehicles: {session.query(VehicleV2).filter(VehicleV2.is_active == True).count()}")

# Test direct queries
print("\nDirect queries:")
honda_count = session.query(VehicleV2).filter(func.lower(VehicleV2.make) == 'honda').count()
print(f"Honda vehicles (lower): {honda_count}")

honda_count2 = session.query(VehicleV2).filter(VehicleV2.make == 'Honda').count()
print(f"Honda vehicles (exact): {honda_count2}")

# Test search engine
print("\n\nTesting search engine:")
search_engine = ComprehensiveSearchEngine(session)

# Debug the search method
print("\n1. Empty search:")
results = search_engine.search(query="", page=1, per_page=10)
print(f"   Results: {results['total']} total, {len(results['vehicles'])} returned")

print("\n2. Honda search:")
results = search_engine.search(query="honda", page=1, per_page=10)
print(f"   Results: {results['total']} total")
print(f"   Applied filters: {results['applied_filters']}")

# Let's trace through the search method
print("\n3. Manual filter test:")
query = session.query(VehicleV2)
# Start with base query
print(f"   Base query count: {query.count()}")

# Add is_active filter
query = query.filter(VehicleV2.is_active == True)
print(f"   After is_active filter: {query.count()}")

# Add make filter
query = query.filter(func.lower(VehicleV2.make) == 'honda')
print(f"   After make filter: {query.count()}")

# Check the SQL being generated
print("\n4. SQL query check:")
test_query = session.query(VehicleV2).filter(VehicleV2.is_active == True).filter(func.lower(VehicleV2.make) == 'honda')
print(f"   SQL: {test_query}")

session.close()