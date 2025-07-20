#!/usr/bin/env python3
"""Debug Flask database connection issue"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

print("=== Debugging Flask Database Connection ===")

# Test 1: Direct database connection
print("\n1. Direct database connection:")
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'findmycar_v2.db')
db_url = f'sqlite:///{db_path}'
print(f"   Database path: {db_path}")
print(f"   Database exists: {os.path.exists(db_path)}")
print(f"   Database URL: {db_url}")

engine = create_engine(db_url)
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM vehicles_v2"))
    count = result.scalar()
    print(f"   Direct query count: {count}")

# Test 2: Using database_v2_sqlite module
print("\n2. Using database_v2_sqlite module:")
from database_v2_sqlite import get_database_url, get_engine, VehicleV2
print(f"   Module database URL: {get_database_url()}")

module_engine = get_engine()
Session = sessionmaker(bind=module_engine)
session = Session()
orm_count = session.query(VehicleV2).count()
print(f"   ORM count: {orm_count}")

# Get some vehicles to verify
vehicles = session.query(VehicleV2).limit(3).all()
if vehicles:
    print(f"   Found {len(vehicles)} vehicles:")
    for v in vehicles:
        print(f"     - {v.year} {v.make} {v.model} (ID: {v.id})")
else:
    print("   No vehicles found!")
session.close()

# Test 3: Import Flask app and test
print("\n3. Testing Flask app database:")
try:
    from flask_app_v2 import engine as flask_engine, SessionLocal
    
    # Test with Flask's engine
    with flask_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM vehicles_v2"))
        flask_count = result.scalar()
        print(f"   Flask engine count: {flask_count}")
    
    # Test with Flask's session
    flask_session = SessionLocal()
    flask_orm_count = flask_session.query(VehicleV2).count()
    print(f"   Flask ORM count: {flask_orm_count}")
    
    # Check if tables exist
    from sqlalchemy import inspect
    inspector = inspect(flask_engine)
    tables = inspector.get_table_names()
    print(f"   Tables in Flask DB: {tables}")
    
    flask_session.close()
    
except Exception as e:
    print(f"   Error testing Flask app: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check for multiple database files
print("\n4. Checking for multiple database files:")
import glob
db_files = glob.glob("**/*.db", recursive=True)
for db_file in db_files:
    if 'v2' in db_file:
        size = os.path.getsize(db_file)
        print(f"   Found: {db_file} (size: {size} bytes)")