#!/usr/bin/env python3
"""Debug the comprehensive search engine"""

import logging
from database_v2_sqlite import get_session, VehicleV2
from comprehensive_search_engine_sqlite import ComprehensiveSearchEngine

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_search():
    # Get database session
    session = get_session()
    
    # Check total vehicles
    total = session.query(VehicleV2).count()
    print(f"Total vehicles in DB: {total}")
    
    # Check Honda vehicles
    honda_count = session.query(VehicleV2).filter(VehicleV2.make.ilike('%honda%')).count()
    print(f"Honda vehicles: {honda_count}")
    
    # Sample Honda vehicle
    honda = session.query(VehicleV2).filter(VehicleV2.make.ilike('%honda%')).first()
    if honda:
        print(f"\nSample Honda vehicle:")
        print(f"  ID: {honda.id}")
        print(f"  Make: {honda.make}")
        print(f"  Model: {honda.model}")
        print(f"  Year: {honda.year}")
        print(f"  Price: {honda.price}")
        print(f"  Body Style: {honda.body_style}")
        print(f"  Fuel Type: {honda.fuel_type}")
        print(f"  Transmission: {honda.transmission}")
        print(f"  Active: {honda.is_active}")
    
    # Test search engine
    print("\n--- Testing Search Engine ---")
    search_engine = ComprehensiveSearchEngine(session)
    
    # Test 1: Basic search
    print("\nTest 1: Search for 'honda'")
    results = search_engine.search(query="honda", per_page=5)
    print(f"Total found: {results['total']}")
    print(f"Applied filters: {results['applied_filters']}")
    
    if results['vehicles']:
        print("First vehicle:")
        v = results['vehicles'][0]
        print(f"  {v.year} {v.make} {v.model} - ${v.price}")
    
    # Test 2: Direct make filter
    print("\nTest 2: Direct make filter")
    results = search_engine.search(filters={'make': 'Honda'}, per_page=5)
    print(f"Total found: {results['total']}")
    
    # Test 3: Check why no results
    print("\nTest 3: Checking query construction...")
    
    # Manual query test
    from sqlalchemy import func
    query = session.query(VehicleV2).filter(VehicleV2.is_active == True)
    print(f"Active vehicles: {query.count()}")
    
    # Check is_active values
    inactive = session.query(VehicleV2).filter(VehicleV2.is_active == False).count()
    null_active = session.query(VehicleV2).filter(VehicleV2.is_active == None).count()
    print(f"Inactive vehicles: {inactive}")
    print(f"Null active vehicles: {null_active}")
    
    # Test with make filter
    query = session.query(VehicleV2).filter(
        VehicleV2.is_active == True,
        func.lower(VehicleV2.make) == 'honda'
    )
    print(f"\nHonda vehicles (active only): {query.count()}")
    
    # Check make values
    print("\nUnique makes in DB:")
    makes = session.query(VehicleV2.make).distinct().limit(10).all()
    for make in makes:
        print(f"  '{make[0]}'")
    
    session.close()

if __name__ == "__main__":
    debug_search()