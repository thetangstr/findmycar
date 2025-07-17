#!/usr/bin/env python3
"""
Test and demonstrate performance improvements
"""

import time
import sys
import os
sys.path.append(os.path.dirname(__file__))

from database import SessionLocal
from ingestion import ingest_multi_source_data
from parallel_ingestion import ingest_multi_source_parallel
from performance_profiler import print_performance_report, reset_performance_data

def test_sequential_vs_parallel():
    """Compare sequential vs parallel source searching"""
    
    print("🚀 PERFORMANCE COMPARISON TEST")
    print("="*60)
    
    query = "Honda Civic"
    sources = ['ebay', 'carmax', 'autotrader']
    
    # Test 1: Sequential search (old method)
    print("\n📊 Test 1: Sequential Search (Old Method)")
    print("-"*40)
    reset_performance_data()
    
    try:
        db = SessionLocal()
        start_time = time.time()
        
        result = ingest_multi_source_data(db, query, None, sources)
        
        sequential_time = time.time() - start_time
        print(f"✅ Sequential search completed in {sequential_time:.2f}s")
        print(f"   Total vehicles: {result.get('total_ingested', 0)}")
        
    except Exception as e:
        print(f"❌ Sequential search error: {e}")
        sequential_time = 0
    finally:
        db.close()
    
    # Test 2: Parallel search (new method)
    print("\n📊 Test 2: Parallel Search (New Method)")
    print("-"*40)
    reset_performance_data()
    
    try:
        db = SessionLocal()
        start_time = time.time()
        
        result = ingest_multi_source_parallel(db, query, None, sources)
        
        parallel_time = time.time() - start_time
        print(f"✅ Parallel search completed in {parallel_time:.2f}s")
        print(f"   Total vehicles: {result.get('total_ingested', 0)}")
        
        # Show per-source timing
        if 'sources' in result:
            print("\n   Source breakdown:")
            for source, source_result in result['sources'].items():
                elapsed = source_result.get('elapsed_time', 0)
                vehicles = source_result.get('ingested', 0)
                print(f"   - {source}: {elapsed:.2f}s ({vehicles} vehicles)")
        
    except Exception as e:
        print(f"❌ Parallel search error: {e}")
        parallel_time = 0
    finally:
        db.close()
    
    # Show improvement
    print("\n🎯 PERFORMANCE IMPROVEMENT")
    print("-"*40)
    if sequential_time > 0 and parallel_time > 0:
        improvement = ((sequential_time - parallel_time) / sequential_time) * 100
        speedup = sequential_time / parallel_time
        print(f"⚡ Speed improvement: {improvement:.1f}%")
        print(f"⚡ Speedup factor: {speedup:.1f}x faster")
        print(f"⏱️  Time saved: {sequential_time - parallel_time:.2f}s")
    
    # Test 3: Cached search (should be instant)
    print("\n📊 Test 3: Cached Search (With Caching)")
    print("-"*40)
    
    try:
        db = SessionLocal()
        start_time = time.time()
        
        # This should hit the cache
        result = ingest_multi_source_parallel(db, query, None, sources)
        
        cached_time = time.time() - start_time
        print(f"✅ Cached search completed in {cached_time:.2f}s")
        print(f"⚡ Cache speedup: {parallel_time / cached_time:.1f}x faster than first run")
        
    except Exception as e:
        print(f"❌ Cached search error: {e}")
    finally:
        db.close()
    
    # Print detailed performance report
    print("\n" + "="*60)
    print_performance_report()

if __name__ == "__main__":
    test_sequential_vs_parallel()