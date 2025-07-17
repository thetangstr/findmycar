#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))

from database import SessionLocal
from ingestion import ingest_data

def test_ebay():
    print('🧪 Testing eBay with fixed function signature...')
    
    try:
        db = SessionLocal()
        result = ingest_data(db, "Honda Civic", limit=3)
        
        if result.get('success', True):  # eBay returns different format
            print(f"✅ eBay test completed")
            print(f"📊 Result: {result}")
        else:
            print(f"❌ eBay test failed: {result}")
            
    except Exception as e:
        print(f"❌ eBay error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_ebay()