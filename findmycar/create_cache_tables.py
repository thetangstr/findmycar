#!/usr/bin/env python3
"""
Migration script to create the new cache tables for the intelligent caching system.
Run this script after updating the database.py file with new cache table definitions.
"""

import logging
from database import engine, Base, SearchCache, QueryAnalytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_cache_tables():
    """Create the new cache tables in the database"""
    try:
        logger.info("Creating cache tables...")
        
        # Create all tables (this will only create missing tables)
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Cache tables created successfully!")
        logger.info("New tables added:")
        logger.info("  - search_cache: For database warm cache storage")
        logger.info("  - query_analytics: For query popularity tracking")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating cache tables: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CarGPT Cache Tables Migration")
    print("=" * 40)
    
    success = create_cache_tables()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nThe intelligent caching system is now ready:")
        print("  • Redis hot cache (1-24 hours)")
        print("  • Database warm cache (1-7 days)")
        print("  • Query popularity analytics")
        print("  • Automatic cache expiration and cleanup")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        exit(1)