#!/usr/bin/env python3
"""
Test CarMax ingestion directly to see where it's failing
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from database import SessionLocal, Vehicle
from ingestion import ingest_carmax_data
import logging

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_carmax_ingestion():
    print("🧪 Testing CarMax Ingestion Pipeline")
    print("=" * 60)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Test ingestion
        print("\n🔍 Running CarMax ingestion...")
        result = ingest_carmax_data(db, "Honda Civic", limit=3)
        
        print(f"\n📊 Ingestion Result:")
        print(f"   Success: {result.get('success', 'Unknown')}")
        print(f"   Added: {result.get('added', 0)}")
        print(f"   Skipped: {result.get('skipped', 0)}")
        print(f"   Errors: {result.get('errors', 0)}")
        if result.get('error'):
            print(f"   Error: {result.get('error')}")
        
        # Check what's actually in the database
        print(f"\n🗄️ Database Check:")
        carmax_vehicles = db.query(Vehicle).filter(Vehicle.source == 'carmax').all()
        print(f"   Total CarMax vehicles in DB: {len(carmax_vehicles)}")
        
        if carmax_vehicles:
            print(f"\n🚗 Sample CarMax vehicles:")
            for i, vehicle in enumerate(carmax_vehicles[:3]):
                print(f"   {i+1}. {vehicle.year} {vehicle.make} {vehicle.model} - ${vehicle.price:,}")
                print(f"      ID: {vehicle.listing_id}, Source: {vehicle.source}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_carmax_ingestion()