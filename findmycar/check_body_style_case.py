#!/usr/bin/env python3
"""Check body_style case sensitivity"""

from database_v2_sqlite import get_database_url
from sqlalchemy import create_engine, text

engine = create_engine(get_database_url())
conn = engine.connect()

# Check case of body_style values
result = conn.execute(text("""
    SELECT DISTINCT body_style, COUNT(*) as count
    FROM vehicles_v2
    WHERE body_style LIKE '%suv%' OR body_style LIKE '%SUV%'
    GROUP BY body_style
"""))

print('SUV body_style variations:')
for row in result:
    print(f'  "{row.body_style}": {row.count}')

# Check if any have uppercase
result = conn.execute(text("""
    SELECT COUNT(*) as count
    FROM vehicles_v2
    WHERE body_style = 'SUV'
"""))
uppercase_count = result.scalar()
print(f'\nUppercase "SUV": {uppercase_count}')

result = conn.execute(text("""
    SELECT COUNT(*) as count
    FROM vehicles_v2
    WHERE body_style = 'suv'
"""))
lowercase_count = result.scalar()
print(f'Lowercase "suv": {lowercase_count}')

# Get some examples with price
result = conn.execute(text("""
    SELECT make, model, year, price, body_style
    FROM vehicles_v2
    WHERE body_style IN ('suv', 'SUV')
    AND price <= 25000
    AND price IS NOT NULL
    ORDER BY price ASC
    LIMIT 10
"""))

print('\nSUVs under $25k with exact body_style:')
for row in result:
    print(f'  {row.year} {row.make} {row.model} - ${row.price:,.0f} (body_style: "{row.body_style}")')

conn.close()