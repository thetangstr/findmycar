#!/usr/bin/env python3
"""Debug make filter issue"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from database_v2_sqlite import get_engine, VehicleV2

# Create session
engine = get_engine()
Session = sessionmaker(bind=engine)
session = Session()

# Test different make queries
print("Testing make queries:")

# 1. Direct equality
count1 = session.query(VehicleV2).filter(VehicleV2.make == 'Honda').count()
print(f"1. make == 'Honda': {count1}")

# 2. Lower case
count2 = session.query(VehicleV2).filter(func.lower(VehicleV2.make) == 'honda').count()
print(f"2. lower(make) == 'honda': {count2}")

# 3. Like
count3 = session.query(VehicleV2).filter(VehicleV2.make.like('%Honda%')).count()
print(f"3. make LIKE '%Honda%': {count3}")

# 4. Check actual values
print("\n4. Sample make values:")
makes = session.query(VehicleV2.make).distinct().limit(20).all()
for make in makes:
    if make[0]:  # Skip None values
        print(f"   '{make[0]}'")

# 5. Check if there's a case issue
print("\n5. Make value analysis:")
honda_exact = session.query(VehicleV2).filter(VehicleV2.make == 'Honda').count()
honda_lower = session.query(VehicleV2).filter(VehicleV2.make == 'honda').count()
honda_upper = session.query(VehicleV2).filter(VehicleV2.make == 'HONDA').count()
print(f"   'Honda': {honda_exact}")
print(f"   'honda': {honda_lower}")
print(f"   'HONDA': {honda_upper}")

# 6. Test the comprehensive search engine's filter logic
from comprehensive_search_engine_sqlite import ComprehensiveSearchEngine
search_engine = ComprehensiveSearchEngine(session)

# Direct filter test
print("\n6. Search engine direct filter test:")
filters = {'make': 'Honda'}
query = session.query(VehicleV2).filter(VehicleV2.is_active == True)

# Apply the same filter logic as search engine
if isinstance(filters['make'], list):
    query = query.filter(VehicleV2.make.in_([m.lower() for m in filters['make']]))
else:
    query = query.filter(func.lower(VehicleV2.make) == filters['make'].lower())

result_count = query.count()
print(f"   With search engine logic: {result_count}")

session.close()