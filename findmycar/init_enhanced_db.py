#!/usr/bin/env python3
"""
Initialize database with enhanced schema including new tables
"""

from database import Base, engine, SessionLocal
from database import Vehicle, UserSession, SavedSearch, SearchCache, QueryAnalytics
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_enhanced_database():
    """Initialize database with all tables including new enhanced features"""
    try:
        logger.info("Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully!")
        
        # Test database connection
        db = SessionLocal()
        try:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            logger.info("Database connection test successful!")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise
        finally:
            db.close()
            
        # Display created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info("Created tables:")
        for table in tables:
            logger.info(f"  - {table}")
            
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Initializing Enhanced CarGPT Database")
    print("=" * 50)
    
    success = init_enhanced_database()
    
    if success:
        print("✅ Database initialization completed successfully!")
    else:
        print("❌ Database initialization failed!")
        exit(1)