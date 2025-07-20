#!/usr/bin/env python3
"""Test raw query"""

from sqlalchemy import create_engine, text
from database_v2_sqlite import get_database_url

# Create engine
engine = create_engine(get_database_url())

# Test raw query
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM vehicles_v2"))
    count = result.scalar()
    print(f"Count from raw query: {count}")
    
    # Get sample vehicles
    result = conn.execute(text("SELECT id, make, model, year, is_active FROM vehicles_v2 LIMIT 5"))
    print("\nSample vehicles:")
    for row in result:
        print(f"  ID: {row[0]}, Make: {row[1]}, Model: {row[2]}, Year: {row[3]}, Active: {row[4]}")
    
    # Check active vehicles
    result = conn.execute(text("SELECT COUNT(*) FROM vehicles_v2 WHERE is_active = 1"))
    active_count = result.scalar()
    print(f"\nActive vehicles: {active_count}")
    
    # Check Honda vehicles
    result = conn.execute(text("SELECT COUNT(*) FROM vehicles_v2 WHERE LOWER(make) = 'honda'"))
    honda_count = result.scalar()
    print(f"Honda vehicles: {honda_count}")