#!/usr/bin/env python3
"""Test color exclusion functionality"""

from database import SessionLocal, Vehicle
from sqlalchemy import or_
import crud

db = SessionLocal()

print("Testing color exclusion for SUVs under 40k, not white\n")

# First, show all SUVs under 40k with their colors
print("All SUVs under 40k:")
all_suvs = db.query(Vehicle).filter(
    Vehicle.body_style == 'suv',
    Vehicle.price < 40000
).order_by(Vehicle.price).limit(10).all()

for v in all_suvs:
    color = v.exterior_color or "no color"
    print(f"ID {v.id}: {v.year} {v.make} {v.model} - ${v.price:,.0f} - Color: {color}")

print(f"\nTotal SUVs under 40k: {db.query(Vehicle).filter(Vehicle.body_style == 'suv', Vehicle.price < 40000).count()}")

# Count by color
print("\nColor distribution:")
from sqlalchemy import text
color_counts = db.execute(text("""
    SELECT exterior_color, COUNT(*) as count 
    FROM vehicles 
    WHERE body_style = 'suv' AND price < 40000 
    GROUP BY exterior_color
""")).fetchall()

for color, count in color_counts:
    color_name = color or "no color"
    print(f"  {color_name}: {count}")

# Now test the CRUD function
print("\n\nTesting CRUD function with exclude_colors filter:")
filters = {
    'body_style': 'suv',
    'price_max': 40000,
    'exclude_colors': ['white']
}

vehicles = crud.get_vehicles(db, filters=filters, limit=10)
print(f"\nFound {len(vehicles)} vehicles (should not include white ones):")

for v in vehicles:
    color = v.exterior_color or "no color"
    print(f"ID {v.id}: {v.year} {v.make} {v.model} - ${v.price:,.0f} - Color: {color}")

# Check if any white vehicles are in the results
white_vehicles = [v for v in vehicles if v.exterior_color == 'white']
if white_vehicles:
    print(f"\n❌ ERROR: Found {len(white_vehicles)} white vehicles in results!")
else:
    print("\n✅ Success: No white vehicles in results")

# Total count with filter
total_with_filter = crud.get_vehicle_count(db, filters=filters)
print(f"\nTotal vehicles with filter: {total_with_filter}")
print(f"Expected: 28 (33 total - 5 white)")

db.close()