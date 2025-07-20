#!/usr/bin/env python3
"""
Debug eBay client initialization
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_ebay_init():
    """Debug eBay client initialization"""
    print("🔍 Debugging eBay Client Initialization")
    print("=" * 50)
    
    # Check environment variables
    print("1. Environment Variables:")
    ebay_client_id = os.getenv('EBAY_CLIENT_ID')
    ebay_client_secret = os.getenv('EBAY_CLIENT_SECRET')
    
    print(f"   EBAY_CLIENT_ID: {'SET' if ebay_client_id else 'MISSING'}")
    print(f"   EBAY_CLIENT_SECRET: {'SET' if ebay_client_secret else 'MISSING'}")
    
    if ebay_client_id:
        print(f"   Client ID length: {len(ebay_client_id)}")
    if ebay_client_secret:
        print(f"   Client Secret length: {len(ebay_client_secret)}")
    
    # Try to import and initialize eBay client
    print("\n2. eBay Client Import:")
    try:
        from ebay_live_client import EbayLiveClient
        print("   ✅ eBay client import successful")
        
        # Try to initialize
        print("\n3. eBay Client Initialization:")
        try:
            ebay_client = EbayLiveClient()
            print("   ✅ eBay client initialization successful")
            
            # Try a simple health check
            print("\n4. eBay Client Health Check:")
            try:
                health = ebay_client.check_health()
                print(f"   Status: {health.get('status', 'unknown')}")
                print(f"   Message: {health.get('message', 'no message')}")
                
                # Try a simple search
                print("\n5. eBay Client Search Test:")
                try:
                    results = ebay_client.search_vehicles(
                        query="Honda",
                        per_page=1
                    )
                    print(f"   Search returned: {results.get('total', 0)} vehicles")
                    print(f"   Source: {results.get('source', 'unknown')}")
                    
                    return True
                    
                except Exception as e:
                    print(f"   ❌ Search failed: {str(e)}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Health check failed: {str(e)}")
                return False
                
        except Exception as e:
            print(f"   ❌ eBay client initialization failed: {str(e)}")
            return False
            
    except Exception as e:
        print(f"   ❌ eBay client import failed: {str(e)}")
        return False

def debug_unified_manager():
    """Debug unified source manager initialization"""
    print("\n" + "=" * 50)
    print("🔍 Debugging Unified Source Manager")
    print("=" * 50)
    
    try:
        from unified_source_manager import UnifiedSourceManager
        
        manager = UnifiedSourceManager()
        
        print(f"1. Initialized sources: {list(manager.sources.keys())}")
        print(f"2. eBay in sources: {'ebay' in manager.sources}")
        print(f"3. eBay config enabled: {manager.source_config.get('ebay', {}).get('enabled', False)}")
        
        enabled_sources = manager.get_enabled_sources()
        print(f"4. Enabled sources: {enabled_sources}")
        print(f"5. eBay in enabled: {'ebay' in enabled_sources}")
        
        # Show all source statuses
        print("\n6. All Source Status:")
        for source_name, config in manager.source_config.items():
            in_sources = source_name in manager.sources
            enabled = config['enabled']
            status = "✅ ACTIVE" if (enabled and in_sources) else f"❌ {'DISABLED' if not enabled else 'NOT_INITIALIZED'}"
            print(f"   {source_name}: {status}")
        
        return 'ebay' in enabled_sources
        
    except Exception as e:
        print(f"❌ Unified manager debug failed: {str(e)}")
        return False

def main():
    print("🔍 eBay Integration Debug")
    print("=" * 80)
    
    # Debug eBay client directly
    ebay_working = debug_ebay_init()
    
    # Debug unified manager
    manager_working = debug_unified_manager()
    
    print("\n" + "=" * 80)
    print("🔍 DEBUG SUMMARY")
    print("=" * 80)
    print(f"eBay Client Working: {'✅ YES' if ebay_working else '❌ NO'}")
    print(f"eBay in Unified Manager: {'✅ YES' if manager_working else '❌ NO'}")
    
    if ebay_working and not manager_working:
        print("\n💡 ISSUE: eBay client works but not being added to unified manager")
        print("   Possible causes:")
        print("   1. Import error in unified_source_manager.py")
        print("   2. Exception during initialization in unified manager")
        print("   3. Environment variable not loading in unified manager context")
    elif not ebay_working:
        print("\n💡 ISSUE: eBay client itself is not working")
        print("   Check credentials and network connectivity")
    else:
        print("\n✅ Everything looks good!")

if __name__ == "__main__":
    main()