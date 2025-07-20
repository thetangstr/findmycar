#!/usr/bin/env python3
"""Test ORM directly"""

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from database_v2_sqlite import get_database_url, VehicleV2, Base

# Create engine
engine = create_engine(get_database_url())

# Inspect database
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tables in database: {tables}")

if 'vehicles_v2' in tables:
    columns = inspector.get_columns('vehicles_v2')
    print(f"\nColumns in vehicles_v2: {[col['name'] for col in columns[:5]]}...")

# Create session
Session = sessionmaker(bind=engine)
session = Session()

# Try to query
try:
    count = session.query(VehicleV2).count()
    print(f"\nVehicleV2 count via ORM: {count}")
    
    # Get first vehicle
    vehicle = session.query(VehicleV2).first()
    if vehicle:
        print(f"\nFirst vehicle:")
        print(f"  ID: {vehicle.id}")
        print(f"  Make: {vehicle.make}")
        print(f"  Model: {vehicle.model}")
    else:
        print("\nNo vehicles found via ORM")
        
    # Check table name
    print(f"\nVehicleV2 table name: {VehicleV2.__tablename__}")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()

session.close()