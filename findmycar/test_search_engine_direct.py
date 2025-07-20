#!/usr/bin/env python3
"""Test search engine directly"""

from sqlalchemy.orm import sessionmaker
from database_v2_sqlite import get_engine, VehicleV2
from comprehensive_search_engine_sqlite import ComprehensiveSearchEngine

# Create session
engine = get_engine()
Session = sessionmaker(bind=engine)
session = Session()

print(f"Total vehicles in DB: {session.query(VehicleV2).count()}")

# Test search engine
search_engine = ComprehensiveSearchEngine(session)

# Test 1: Empty search (should return all)
print("\n1. Testing empty search:")
results = search_engine.search(query="")
print(f"   Found: {results['total']} vehicles")
print(f"   Returned: {len(results['vehicles'])} vehicles")

# Test 2: Honda search
print("\n2. Testing 'honda' search:")
results = search_engine.search(query="honda")
print(f"   Found: {results['total']} vehicles")
if results['total'] > 0:
    print(f"   First result: {results['vehicles'][0].year} {results['vehicles'][0].make} {results['vehicles'][0].model}")

# Test 3: Search with filters
print("\n3. Testing search with filters:")
results = search_engine.search(
    filters={'year_min': 2015, 'year_max': 2020}
)
print(f"   Found: {results['total']} vehicles with year 2015-2020")

# Test 4: Direct query for Honda
print("\n4. Direct query for Honda vehicles:")
honda_count = session.query(VehicleV2).filter(VehicleV2.make.ilike('%honda%')).count()
print(f"   Honda vehicles in DB: {honda_count}")

# Check the actual make values
print("\n5. Sample make values in DB:")
makes = session.query(VehicleV2.make).distinct().limit(10).all()
for make in makes:
    print(f"   - {make[0]}")

session.close()