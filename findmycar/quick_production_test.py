#!/usr/bin/env python3
"""
Quick Production Test - Tests only production-ready sources
"""
import os
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging to reduce noise
logging.basicConfig(level=logging.WARNING)

def quick_production_test():
    """Quick test of production configuration"""
    print("🎯 Quick Production Test")
    print("=" * 60)
    
    # Test 1: Environment
    print("1. 🔧 Environment Configuration")
    ebay_id = bool(os.getenv('EBAY_CLIENT_ID'))
    ebay_secret = bool(os.getenv('EBAY_CLIENT_SECRET'))
    db_url = bool(os.getenv('DATABASE_URL'))
    secret_key = bool(os.getenv('SECRET_KEY'))
    
    env_score = sum([ebay_id, ebay_secret, db_url, secret_key])
    print(f"   Essential variables: {env_score}/4 configured")
    
    if env_score < 4:
        print("   ❌ Missing essential environment variables")
        return False
    
    # Test 2: Source Manager Initialization
    print("\n2. 🔗 Source Manager")
    try:
        from unified_source_manager import UnifiedSourceManager
        manager = UnifiedSourceManager()
        
        # Configure for production only
        production_sources = ['ebay', 'carmax', 'autotrader']
        for source_name in manager.source_config.keys():
            if source_name in production_sources:
                manager.enable_source(source_name)
            else:
                manager.disable_source(source_name)
        
        enabled = manager.get_enabled_sources()
        production_enabled = [s for s in enabled if s in production_sources]
        
        print(f"   Production sources enabled: {len(production_enabled)}/3")
        if len(production_enabled) < 3:
            print(f"   ❌ Not all production sources enabled: {enabled}")
            return False
        
    except Exception as e:
        print(f"   ❌ Source manager failed: {str(e)}")
        return False
    
    # Test 3: Quick Search
    print("\n3. 🔍 Production Search Test")
    try:
        start_time = time.time()
        result = manager.search_all_sources(
            query="Honda",
            year_min=2010,
            price_max=50000,
            per_page=12  # 4 from each source
        )
        search_time = time.time() - start_time
        
        total_vehicles = result.get('total', 0)
        sources_succeeded = result.get('sources_searched', [])
        sources_failed = result.get('sources_failed', [])
        
        print(f"   Total vehicles: {total_vehicles}")
        print(f"   Search time: {search_time:.2f}s")
        print(f"   Sources succeeded: {len(sources_succeeded)}/3")
        print(f"   Sources failed: {len(sources_failed)}")
        
        # Check vehicle distribution
        if result.get('vehicles'):
            source_counts = {}
            for vehicle in result['vehicles']:
                source = vehicle.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            print(f"   Distribution: {source_counts}")
        
        # Success criteria
        success = (
            total_vehicles >= 30 and 
            search_time < 60 and 
            len(sources_succeeded) >= 2
        )
        
        if success:
            print("   ✅ Search test passed")
        else:
            print("   ❌ Search test failed")
            
        return success
        
    except Exception as e:
        print(f"   ❌ Search failed: {str(e)}")
        return False

def main():
    """Run quick production test"""
    success = quick_production_test()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 PRODUCTION READY!")
        print("✅ All critical tests passed")
        print("✅ System ready for deployment")
    else:
        print("⚠️ PRODUCTION NOT READY")
        print("❌ Critical tests failed")
        print("❌ Fix issues before deployment")
    
    print("=" * 60)
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)