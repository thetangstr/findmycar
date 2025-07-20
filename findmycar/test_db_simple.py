#!/usr/bin/env python3
"""Simple database test"""

import sqlite3
import os
from sqlalchemy import create_engine, text

# Test 1: Direct SQLite connection
print("1. Direct SQLite connection:")
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'findmycar_v2.db')
print(f"   DB path: {db_path}")
print(f"   DB exists: {os.path.exists(db_path)}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM vehicles_v2")
count = cursor.fetchone()[0]
print(f"   SQLite count: {count}")

# Get a sample
cursor.execute("SELECT id, make, model FROM vehicles_v2 LIMIT 3")
rows = cursor.fetchall()
print(f"   Sample rows: {rows}")
conn.close()

# Test 2: SQLAlchemy with explicit path
print("\n2. SQLAlchemy with explicit path:")
db_url = f'sqlite:///{db_path}'
engine = create_engine(db_url, echo=False)
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM vehicles_v2"))
    count = result.scalar()
    print(f"   SQLAlchemy count: {count}")

# Test 3: Import and use get_engine
print("\n3. Using get_engine from module:")
from database_v2_sqlite import get_engine, get_database_url
print(f"   get_database_url(): {get_database_url()}")
engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM vehicles_v2"))
    count = result.scalar()
    print(f"   Module engine count: {count}")

# Test 4: Check if there's a schema issue
print("\n4. Checking schema:")
with engine.connect() as conn:
    result = conn.execute(text("PRAGMA table_info(vehicles_v2)"))
    columns = result.fetchall()
    print(f"   Number of columns: {len(columns)}")
    print(f"   First few columns: {[col[1] for col in columns[:5]]}")