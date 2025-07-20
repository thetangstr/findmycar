#!/usr/bin/env python3
"""Check SUV data in database"""

from database_v2_sqlite import get_database_url, VehicleV2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine(get_database_url())
Session = sessionmaker(bind=engine)
db = Session()

# Count SUVs under 25000
count = db.execute(text("""
    SELECT COUNT(*) 
    FROM vehicles_v2 
    WHERE body_style = 'suv' 
    AND price <= 25000 
    AND price IS NOT NULL
""")).scalar()

print(f'SUVs under $25,000: {count}')

# Count all SUVs
all_suvs = db.execute(text("""
    SELECT COUNT(*) 
    FROM vehicles_v2 
    WHERE body_style = 'suv'
""")).scalar()

print(f'Total SUVs in database: {all_suvs}')

# Check body styles
print('\nBody styles in database:')
body_styles = db.execute(text("""
    SELECT body_style, COUNT(*) as count 
    FROM vehicles_v2 
    WHERE body_style IS NOT NULL
    GROUP BY body_style 
    ORDER BY count DESC
""")).fetchall()

for style, count in body_styles:
    print(f'  {style}: {count}')

# Get some cheap vehicles
print('\nCheapest vehicles:')
cheap = db.execute(text("""
    SELECT make, model, year, price, body_style
    FROM vehicles_v2 
    WHERE price < 30000 
    AND price IS NOT NULL
    ORDER BY price ASC
    LIMIT 10
""")).fetchall()

for r in cheap:
    print(f'  {r.year} {r.make} {r.model} ({r.body_style}) - ${r.price:,.0f}')

db.close()