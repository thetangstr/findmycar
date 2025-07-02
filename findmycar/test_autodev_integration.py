#!/usr/bin/env python3

"""
Test Auto.dev integration with database
"""

from sqlalchemy.orm import Session
from database import SessionLocal, Vehicle
from ingestion import ingest_autodev_data
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_autodev_integration():
    """Test Auto.dev integration end-to-end"""
    
    print("🧪 Testing Auto.dev Integration...")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Count existing vehicles
        existing_count = db.query(Vehicle).count()
        autodev_count = db.query(Vehicle).filter(Vehicle.source == 'auto.dev').count()
        
        print(f"📊 Before test: {existing_count} total vehicles, {autodev_count} Auto.dev")
        
        # Test Auto.dev ingestion
        print("\n🔍 Testing Auto.dev ingestion...")
        
        test_queries = [
            "Honda Civic 2020",
            "Tesla Model 3",
            "BMW 3 Series"
        ]
        
        for query in test_queries:
            print(f"\n📝 Testing query: {query}")
            
            result = ingest_autodev_data(db, query, limit=5)
            
            if result['success']:
                print(f"  ✅ Success: {result['ingested']} ingested, {result['skipped']} skipped")
                print(f"  📊 Total available: {result['total_available']}")
            else:
                print(f"  ❌ Failed: {result['error']}")
        
        # Check final counts
        final_count = db.query(Vehicle).count()
        final_autodev_count = db.query(Vehicle).filter(Vehicle.source == 'auto.dev').count()
        
        print(f"\n📊 After test: {final_count} total vehicles, {final_autodev_count} Auto.dev")
        print(f"📈 Added {final_count - existing_count} new vehicles")
        
        # Show sample Auto.dev vehicles
        if final_autodev_count > 0:
            print(f"\n📄 Sample Auto.dev vehicles:")
            sample_vehicles = db.query(Vehicle).filter(Vehicle.source == 'auto.dev').limit(3).all()
            
            for vehicle in sample_vehicles:
                print(f"  🚗 {vehicle.title} - ${vehicle.price:,.0f}")
                print(f"     📍 {vehicle.location}")
                print(f"     🔗 {vehicle.view_item_url}")
                print(f"     💎 Deal: {vehicle.deal_rating or 'Not rated'}")
                print()
        
        print("✅ Auto.dev integration test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_autodev_integration()