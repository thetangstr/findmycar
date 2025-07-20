#!/usr/bin/env python3
"""Test Flask database connection"""

from flask_app_v2 import SessionLocal, engine
from database_v2_sqlite import VehicleV2
from sqlalchemy import text

print("Testing Flask database connection...")

# Test raw query
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM vehicles_v2"))
    count = result.scalar()
    print(f"Raw query count: {count}")

# Test ORM
session = SessionLocal()
orm_count = session.query(VehicleV2).count()
print(f"ORM count: {orm_count}")

# Check a vehicle
vehicle = session.query(VehicleV2).first()
if vehicle:
    print(f"\nFirst vehicle:")
    print(f"  ID: {vehicle.id}")
    print(f"  Make: {vehicle.make}")
    print(f"  Model: {vehicle.model}")
    print(f"  Active: {vehicle.is_active}")

# Test search
from comprehensive_search_engine_sqlite import ComprehensiveSearchEngine
search_engine = ComprehensiveSearchEngine(session)
results = search_engine.search(query="honda")
print(f"\nSearch results for 'honda': {results['total']}")

session.close()