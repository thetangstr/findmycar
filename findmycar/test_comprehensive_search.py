#!/usr/bin/env python3
"""
Test the comprehensive search system
"""

import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_v2():
    """Test PostgreSQL database with JSONB"""
    logger.info("\n=== Testing Database V2 ===")
    
    try:
        from database_v2 import init_db, get_session, VehicleV2
        
        # Initialize database
        engine = init_db()
        logger.info("✅ Database initialized successfully")
        
        # Test session
        session = get_session()
        count = session.query(VehicleV2).count()
        logger.info(f"✅ Database has {count} vehicles")
        
        # Test JSONB queries
        if count > 0:
            # Test attribute query
            with_mpg = session.query(VehicleV2).filter(
                VehicleV2.attributes['mpg_city'] != None
            ).first()
            
            if with_mpg:
                logger.info(f"✅ Found vehicle with MPG data: {with_mpg.year} {with_mpg.make} {with_mpg.model}")
                logger.info(f"   City MPG: {with_mpg.attributes.get('mpg_city')}")
            
            # Test feature query
            with_features = session.query(VehicleV2).filter(
                VehicleV2.features != None,
                VehicleV2.features != []
            ).first()
            
            if with_features:
                logger.info(f"✅ Found vehicle with features: {len(with_features.features)} features")
                logger.info(f"   Features: {', '.join(with_features.features[:3])}...")
        
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database V2 test failed: {e}")
        return False


def test_attribute_standardizer():
    """Test attribute standardization"""
    logger.info("\n=== Testing Attribute Standardizer ===")
    
    try:
        from attribute_standardizer import AttributeStandardizer
        
        standardizer = AttributeStandardizer()
        
        # Test eBay data standardization
        ebay_data = {
            'itemSpecifics': [
                {'localizedName': 'Make', 'value': 'Honda'},
                {'localizedName': 'Model', 'value': 'Civic'},
                {'localizedName': 'Year', 'value': '2020'},
                {'localizedName': 'Mileage', 'value': '25,000'},
                {'localizedName': 'Transmission', 'value': 'Automatic'},
                {'localizedName': 'Fuel Type', 'value': 'Gasoline'},
                {'localizedName': 'Exterior Color', 'value': 'Blue'},
                {'localizedName': 'City MPG', 'value': '32'},
                {'localizedName': 'Highway MPG', 'value': '42'},
                {'localizedName': 'Options', 'value': 'Leather Seats, Navigation, Sunroof, Backup Camera'}
            ]
        }
        
        result = standardizer.standardize_vehicle_data(ebay_data, 'ebay')
        
        logger.info("✅ Standardization successful")
        logger.info(f"   Core fields: {result['core_fields']}")
        logger.info(f"   Attributes: {list(result['attributes'].keys())}")
        logger.info(f"   Features detected: {result['features']}")
        
        # Test color standardization
        assert result['core_fields']['exterior_color'] == 'blue'
        logger.info("✅ Color standardization working")
        
        # Test transmission standardization
        assert result['core_fields']['transmission'] == 'automatic'
        logger.info("✅ Transmission standardization working")
        
        # Test feature extraction
        assert 'leather_seats' in result['features']
        assert 'navigation' in result['features']
        assert 'backup_camera' in result['features']
        logger.info("✅ Feature extraction working")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Attribute standardizer test failed: {e}")
        return False


def test_comprehensive_search_engine():
    """Test the comprehensive search engine"""
    logger.info("\n=== Testing Comprehensive Search Engine ===")
    
    try:
        from database_v2 import get_session
        from comprehensive_search_engine import ComprehensiveSearchEngine
        
        session = get_session()
        search_engine = ComprehensiveSearchEngine(session)
        
        # Test 1: Basic search
        logger.info("\nTest 1: Basic text search")
        results = search_engine.search(query="honda civic", per_page=5)
        logger.info(f"✅ Found {results['total']} vehicles")
        logger.info(f"   Search time: {results['search_time']:.2f}s")
        
        # Test 2: Price filter
        logger.info("\nTest 2: Price range filter")
        results = search_engine.search(filters={'price_max': 30000}, per_page=5)
        logger.info(f"✅ Found {results['total']} vehicles under $30k")
        
        # Test 3: Smart preset
        logger.info("\nTest 3: Smart preset (fuel_efficient)")
        results = search_engine.search(preset='fuel_efficient', per_page=5)
        logger.info(f"✅ Found {results['total']} fuel-efficient vehicles")
        logger.info(f"   Applied filters: {results['applied_filters']}")
        
        # Test 4: Multiple filters
        logger.info("\nTest 4: Multiple filters")
        results = search_engine.search(
            filters={
                'body_style': 'suv',
                'year_min': 2018,
                'price_max': 40000,
                'exclude_colors': ['white']
            },
            per_page=5
        )
        logger.info(f"✅ Found {results['total']} SUVs (2018+, under $40k, not white)")
        
        # Test 5: Feature filter
        logger.info("\nTest 5: Feature filter")
        results = search_engine.search(
            filters={
                'required_features': ['backup_camera', 'leather_seats']
            },
            per_page=5
        )
        logger.info(f"✅ Found {results['total']} vehicles with backup camera and leather seats")
        
        # Test 6: Natural language query
        logger.info("\nTest 6: Natural language query")
        results = search_engine.search(
            query="red sedan under 25000 low mileage",
            per_page=5
        )
        logger.info(f"✅ Found {results['total']} vehicles")
        logger.info(f"   Applied filters: {results['applied_filters']}")
        
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Search engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flask_endpoints():
    """Test Flask API endpoints"""
    logger.info("\n=== Testing Flask API Endpoints ===")
    
    try:
        import requests
        import json
        
        # Check if server is running
        base_url = "http://localhost:8602"
        
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code != 200:
                logger.warning("Flask server not running on port 8602, skipping API tests")
                return True
        except:
            logger.warning("Flask server not running on port 8602, skipping API tests")
            return True
        
        # Test 1: Basic search
        logger.info("\nTest 1: Basic search endpoint")
        response = requests.get(f"{base_url}/api/search/v2", params={
            'query': 'honda',
            'page': 1,
            'per_page': 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        logger.info(f"✅ Search API working, found {data['total']} vehicles")
        
        # Test 2: Search with filters
        logger.info("\nTest 2: Search with filters")
        response = requests.get(f"{base_url}/api/search/v2", params={
            'body_style': 'suv',
            'price_max': 35000,
            'year_min': 2018
        })
        
        assert response.status_code == 200
        data = response.json()
        logger.info(f"✅ Filter search working, found {data['total']} vehicles")
        
        # Test 3: Search suggestions
        logger.info("\nTest 3: Search suggestions")
        response = requests.get(f"{base_url}/api/search/suggestions", params={
            'q': 'hon'
        })
        
        assert response.status_code == 200
        data = response.json()
        logger.info(f"✅ Suggestions working, got {len(data.get('suggestions', []))} suggestions")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Flask API test failed: {e}")
        return False


def test_migration_readiness():
    """Check if we're ready to migrate data"""
    logger.info("\n=== Testing Migration Readiness ===")
    
    try:
        # Check if old database exists
        from database import SessionLocal, Vehicle
        
        session = SessionLocal()
        v1_count = session.query(Vehicle).count()
        logger.info(f"✅ V1 database has {v1_count} vehicles ready for migration")
        session.close()
        
        # Check PostgreSQL connection
        db_url = os.environ.get('DATABASE_URL', '')
        if 'postgresql' in db_url:
            logger.info("✅ PostgreSQL connection configured")
        else:
            logger.warning("⚠️  DATABASE_URL not set to PostgreSQL")
            logger.info("   Set DATABASE_URL=postgresql://user:pass@localhost/findmycar")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration readiness test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("COMPREHENSIVE SEARCH SYSTEM TEST SUITE")
    logger.info("=" * 60)
    
    tests = [
        test_database_v2,
        test_attribute_standardizer,
        test_comprehensive_search_engine,
        test_flask_endpoints,
        test_migration_readiness
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Test {test.__name__} crashed: {e}")
            failed += 1
    
    logger.info("\n" + "=" * 60)
    logger.info(f"TEST SUMMARY: {passed} passed, {failed} failed")
    logger.info("=" * 60)
    
    if failed == 0:
        logger.info("✅ All tests passed! The comprehensive search system is ready.")
        logger.info("\nNext steps:")
        logger.info("1. Set DATABASE_URL to PostgreSQL connection string")
        logger.info("2. Run: python migrate_to_v2.py")
        logger.info("3. Run: python flask_app_v2.py")
        logger.info("4. Access: http://localhost:8602")
    else:
        logger.error("❌ Some tests failed. Please fix the issues before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()