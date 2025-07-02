#!/usr/bin/env python3

"""
Simple test to verify Auto.dev is working
"""

import requests
import time

def test_autodev_simple():
    """Simple test of Auto.dev functionality"""
    
    print("🔍 Testing Auto.dev search via HTTP...")
    
    # Test search request
    url = "http://localhost:8000/ingest"
    data = {
        'query': 'Toyota Prius 2022',
        'sources': ['auto.dev']
    }
    
    try:
        print(f"📤 Sending search request: {data}")
        response = requests.post(url, data=data, timeout=30, allow_redirects=False)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 303:
            print("✅ Search completed successfully (redirect)")
            
            # Check redirect location
            location = response.headers.get('location', '')
            print(f"📍 Redirect to: {location}")
            
            if 'message=' in location:
                print("✅ Success message in redirect")
            elif 'error=' in location:
                print("❌ Error message in redirect")
            
        elif response.status_code == 200:
            print("✅ Search completed successfully")
            
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"📄 Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    # Check database for Auto.dev vehicles
    print("\n📊 Checking database...")
    
    try:
        from sqlalchemy.orm import Session
        from database import SessionLocal, Vehicle
        
        db = SessionLocal()
        autodev_count = db.query(Vehicle).filter(Vehicle.source == 'auto.dev').count()
        total_count = db.query(Vehicle).count()
        
        print(f"📈 Database: {autodev_count} Auto.dev vehicles, {total_count} total")
        
        if autodev_count > 0:
            # Show latest Auto.dev vehicle
            latest = db.query(Vehicle).filter(Vehicle.source == 'auto.dev').order_by(Vehicle.id.desc()).first()
            print(f"📄 Latest Auto.dev vehicle: {latest.title}")
            print(f"   💰 Price: ${latest.price:,.0f}")
            print(f"   📍 Location: {latest.location}")
            print(f"   🔗 URL: {latest.view_item_url}")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")

if __name__ == "__main__":
    test_autodev_simple()