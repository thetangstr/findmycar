#!/usr/bin/env python3
"""
Performance profiler to identify bottlenecks in the search process
"""

import time
import functools
import logging
from contextlib import contextmanager
from typing import Dict, List
import statistics

# Global performance data
performance_data = {}

class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = time.time() - self.start_time
        
        if self.operation_name not in performance_data:
            performance_data[self.operation_name] = []
        
        performance_data[self.operation_name].append(elapsed_time)
        
        # Log if operation took more than 1 second
        if elapsed_time > 1.0:
            logging.warning(f"⚠️  SLOW OPERATION: {self.operation_name} took {elapsed_time:.2f}s")

def time_function(func):
    """Decorator to time function execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with PerformanceTimer(f"{func.__module__}.{func.__name__}"):
            return func(*args, **kwargs)
    return wrapper

def print_performance_report():
    """Print a detailed performance report"""
    print("\n" + "="*80)
    print("📊 PERFORMANCE ANALYSIS REPORT")
    print("="*80)
    
    if not performance_data:
        print("No performance data collected yet.")
        return
    
    # Sort by total time spent
    sorted_ops = sorted(
        performance_data.items(),
        key=lambda x: sum(x[1]),
        reverse=True
    )
    
    print(f"{'Operation':<50} {'Count':>8} {'Total(s)':>10} {'Avg(s)':>10} {'Max(s)':>10}")
    print("-"*80)
    
    total_time = 0
    for operation, times in sorted_ops:
        count = len(times)
        total = sum(times)
        avg = statistics.mean(times)
        max_time = max(times)
        total_time += total
        
        # Highlight slow operations
        marker = "🔴" if avg > 5.0 else "🟡" if avg > 2.0 else "🟢"
        
        print(f"{marker} {operation:<47} {count:>8} {total:>10.2f} {avg:>10.2f} {max_time:>10.2f}")
    
    print("-"*80)
    print(f"{'TOTAL TIME':<50} {total_time:>30.2f}s")
    
    # Identify bottlenecks
    print("\n🎯 TOP BOTTLENECKS:")
    for i, (operation, times) in enumerate(sorted_ops[:5]):
        total = sum(times)
        percentage = (total / total_time) * 100 if total_time > 0 else 0
        print(f"{i+1}. {operation}: {total:.2f}s ({percentage:.1f}% of total time)")

def reset_performance_data():
    """Reset performance data"""
    global performance_data
    performance_data = {}

# Export utilities
__all__ = ['PerformanceTimer', 'time_function', 'print_performance_report', 'reset_performance_data']