#!/usr/bin/env python3

"""
Debug script to test multi-source search
"""

import logging
from sqlalchemy.orm import Session
from database import SessionLocal
from ingestion import ingest_multi_source_data, ingest_cars_data
from cars_client import search_cars_listings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cars_only():
    """Test Cars.com integration directly"""
    print("=== Testing Cars.com Client ===")
    results = search_cars_listings("Honda Civic", limit=3)
    print(f"Cars.com returned {len(results)} results")
    
    for i, vehicle in enumerate(results):
        print(f"\nVehicle {i+1}:")
        print(f"  Title: {vehicle.get('title')}")
        print(f"  Source: {vehicle.get('source')}")
        print(f"  Price: ${vehicle.get('price')}")
        print(f"  Listing ID: {vehicle.get('listing_id')}")

def test_cars_ingestion():
    """Test Cars.com ingestion into database"""
    print("\n=== Testing Cars.com Ingestion ===")
    db = SessionLocal()
    try:
        result = ingest_cars_data(db, "Honda Civic", limit=3)
        print(f"Ingestion result: {result}")
    finally:
        db.close()

def test_multi_source():
    """Test multi-source ingestion"""
    print("\n=== Testing Multi-Source Ingestion ===")
    db = SessionLocal()
    try:
        result = ingest_multi_source_data(db, "Honda Civic", sources=['ebay', 'cars.com'])
        print(f"Multi-source result: {result}")
    finally:
        db.close()

if __name__ == "__main__":
    test_cars_only()
    test_cars_ingestion()
    test_multi_source()