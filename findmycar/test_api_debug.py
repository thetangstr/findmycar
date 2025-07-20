#!/usr/bin/env python3
"""Debug API search issue"""

import requests
import json

# Test the API
print("Testing API search...")

# Test 1: Empty query (should return all)
response = requests.get("http://localhost:8602/api/search/v2", params={"query": ""})
print(f"\n1. Empty query status: {response.status_code}")
if response.ok:
    data = response.json()
    print(f"   Total vehicles: {data.get('total', 0)}")
    print(f"   Vehicles returned: {len(data.get('vehicles', []))}")

# Test 2: Honda search
response = requests.get("http://localhost:8602/api/search/v2", params={"query": "honda"})
print(f"\n2. Honda search status: {response.status_code}")
if response.ok:
    data = response.json()
    print(f"   Total vehicles: {data.get('total', 0)}")
    print(f"   Applied filters: {json.dumps(data.get('applied_filters', {}), indent=2)}")

# Test 3: Direct database check via custom endpoint
print("\n3. Adding debug endpoint to check database...")

# Create a test file that adds a debug endpoint
debug_code = '''
@app.route('/api/debug/db')
def debug_db():
    """Debug database connection"""
    db = SessionLocal()
    try:
        from database_v2_sqlite import VehicleV2
        count = db.query(VehicleV2).count()
        vehicles = db.query(VehicleV2).limit(3).all()
        
        return jsonify({
            'total_count': count,
            'sample_vehicles': [
                {
                    'id': v.id,
                    'make': v.make,
                    'model': v.model,
                    'year': v.year
                } for v in vehicles
            ],
            'db_url': str(db.bind.url)
        })
    finally:
        db.close()
'''

print("   Would need to add debug endpoint to Flask app...")
print("\n4. Let's check the comprehensive search engine directly...")

# Import and test directly
from sqlalchemy.orm import sessionmaker
from database_v2_sqlite import get_engine, VehicleV2
from comprehensive_search_engine_sqlite import ComprehensiveSearchEngine

engine = get_engine()
Session = sessionmaker(bind=engine)
session = Session()

print(f"\n   Direct DB count: {session.query(VehicleV2).count()}")

# Test search engine
search_engine = ComprehensiveSearchEngine(session)
results = search_engine.search(query="")
print(f"   Search engine empty query: {results['total']} vehicles")

# Check if it's the is_active filter
active_count = session.query(VehicleV2).filter(VehicleV2.is_active == True).count()
print(f"   Active vehicles: {active_count}")

# Check without is_active filter
all_count = session.query(VehicleV2).count()
print(f"   All vehicles (including inactive): {all_count}")

session.close()