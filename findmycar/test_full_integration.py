"""
Test the full integration with all 16 sources
"""
import logging
from datetime import datetime
from database_v2_sqlite import get_session
from production_search_service_v3 import EnhancedProductionSearchService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_search_integration():
    """Test searching with the enhanced production service"""
    print("\n" + "="*70)
    print("Testing FindMyCar Enhanced Search Integration")
    print("="*70)
    
    # Get database session
    db = get_session()
    
    try:
        # Initialize enhanced search service
        search_service = EnhancedProductionSearchService(db)
        
        # Get source statistics
        print("\nSource Statistics:")
        stats = search_service.get_source_stats()
        print(f"Total sources configured: {stats['total_sources']}")
        print(f"Enabled sources: {stats['enabled_sources']}")
        print(f"\nEnabled source list:")
        for source in search_service.source_manager.get_enabled_sources():
            config = search_service.source_manager.source_config[source]
            print(f"  - {source}: {config['description']}")
        
        # Test searches
        test_queries = [
            {
                'query': 'honda civic',
                'filters': {'price_max': 20000}
            },
            {
                'query': 'classic mustang',
                'filters': {'year_min': 1960, 'year_max': 1970}
            },
            {
                'query': 'family SUV under 30000',
                'filters': {}
            }
        ]
        
        for test in test_queries:
            print(f"\n\n{'='*70}")
            print(f"Test Query: {test['query']}")
            print(f"Filters: {test['filters']}")
            print("="*70)
            
            start_time = datetime.now()
            
            # Perform search
            results = search_service.search(
                query=test['query'],
                filters=test['filters'],
                page=1,
                per_page=10
            )
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            print(f"\nResults Summary:")
            print(f"Total vehicles found: {results['total']}")
            print(f"Local results: {results['local_count']}")
            print(f"Live results: {results['live_count']}")
            print(f"Sources searched: {results['sources_searched']}")
            print(f"Sources failed: {results['sources_failed']}")
            print(f"Search time: {search_time:.2f}s (reported: {results.get('search_time', 0):.2f}s)")
            
            # Display first few vehicles
            print(f"\nFirst {min(3, len(results['vehicles']))} vehicles:")
            for i, vehicle in enumerate(results['vehicles'][:3]):
                print(f"\n{i+1}. {vehicle.get('title', 'No title')}")
                print(f"   Price: ${vehicle.get('price', 'N/A')}")
                print(f"   Year: {vehicle.get('year', 'N/A')}")
                print(f"   Location: {vehicle.get('location', 'N/A')}")
                print(f"   Source: {vehicle.get('source', 'unknown')}")
                if 'relevance_score' in vehicle:
                    print(f"   Relevance: {vehicle['relevance_score']}")
        
        print("\n\n" + "="*70)
        print("Integration Test Complete!")
        print("="*70)
        
    except Exception as e:
        print(f"\nERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

def test_source_health():
    """Test health check for all sources"""
    print("\n" + "="*70)
    print("Testing Source Health Checks")
    print("="*70)
    
    db = get_session()
    
    try:
        search_service = EnhancedProductionSearchService(db)
        
        print("\nChecking health of all sources...")
        health_results = search_service.source_manager.check_all_sources_health()
        
        healthy_count = 0
        unhealthy_count = 0
        
        for source, health in health_results.items():
            status = health.get('status', 'unknown')
            if status == 'healthy':
                healthy_count += 1
                emoji = "✅"
            else:
                unhealthy_count += 1
                emoji = "❌"
            
            print(f"\n{emoji} {source}:")
            print(f"   Status: {status}")
            print(f"   Message: {health.get('message', 'N/A')}")
            if 'response_time' in health:
                print(f"   Response time: {health['response_time']:.2f}s")
        
        print(f"\n\nSummary:")
        print(f"Healthy sources: {healthy_count}")
        print(f"Unhealthy sources: {unhealthy_count}")
        
    except Exception as e:
        print(f"\nERROR during health check: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    print("FindMyCar Enhanced Integration Test")
    print("===================================")
    print(f"Test started at: {datetime.now()}")
    
    # Test health checks first
    test_source_health()
    
    # Then test search integration
    test_search_integration()
    
    print(f"\nTest completed at: {datetime.now()}")