"""Debug search functionality"""
import logging
from database_v2_sqlite import get_session
from production_search_service_v3 import EnhancedProductionSearchService

logging.basicConfig(level=logging.DEBUG)

def test_search():
    db = get_session()
    try:
        search_service = EnhancedProductionSearchService(db)
        print("Service initialized")
        
        results = search_service.search(
            query="honda civic",
            filters={},
            page=1,
            per_page=10
        )
        
        print(f"Results: {results}")
        print(f"Total found: {results.get('total', 0)}")
        print(f"Sources searched: {results.get('sources_searched', [])}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_search()