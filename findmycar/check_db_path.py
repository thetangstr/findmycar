#!/usr/bin/env python3
"""Check database path"""

import os
from database_v2_sqlite import get_database_url

url = get_database_url()
print(f"Database URL: {url}")

# Extract path from SQLite URL
if url.startswith('sqlite:///'):
    db_path = url.replace('sqlite:///', '')
    print(f"Database path: {db_path}")
    print(f"Path exists: {os.path.exists(db_path)}")
    if os.path.exists(db_path):
        print(f"File size: {os.path.getsize(db_path)} bytes")
        
# Also check direct query
import sqlite3
try:
    conn = sqlite3.connect('findmycar_v2.db')
    cursor = conn.cursor()
    count = cursor.execute("SELECT COUNT(*) FROM vehicles_v2").fetchone()[0]
    print(f"\nDirect SQLite query count: {count}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")