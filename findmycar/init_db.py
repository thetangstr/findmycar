#!/usr/bin/env python
"""
Database initialization and migration script
Creates all tables and indexes for production deployment
"""
import logging
import sys
from sqlalchemy import text
from database import Base, Vehicle, SearchCache, QueryAnalytics
from database_config import engine, get_database_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_indexes():
    """Create additional indexes for performance"""
    with engine.connect() as conn:
        # Create indexes for common queries
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_vehicles_make_model ON vehicles(make, model);",
            "CREATE INDEX IF NOT EXISTS idx_vehicles_year_price ON vehicles(year, price);",
            "CREATE INDEX IF NOT EXISTS idx_vehicles_source_created ON vehicles(source, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_search_cache_expires ON search_cache(expires_at);",
            "CREATE INDEX IF NOT EXISTS idx_query_analytics_popular ON query_analytics(search_count DESC);"
        ]
        
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                logger.info(f"Created index: {index_sql.split(' ')[5]}")
            except Exception as e:
                logger.warning(f"Index creation skipped (may already exist): {e}")
        
        conn.commit()

def create_database():
    """Create database if it doesn't exist (PostgreSQL only)"""
    database_url = get_database_url()
    
    if database_url.startswith("postgresql"):
        # Extract database name and create connection to postgres database
        import re
        match = re.search(r'/([^/]+)$', database_url)
        if match:
            db_name = match.group(1).split('?')[0]
            postgres_url = database_url.rsplit('/', 1)[0] + '/postgres'
            
            try:
                from sqlalchemy import create_engine
                temp_engine = create_engine(postgres_url, isolation_level='AUTOCOMMIT')
                with temp_engine.connect() as conn:
                    # Check if database exists
                    result = conn.execute(
                        text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                        {"dbname": db_name}
                    )
                    if not result.fetchone():
                        conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                        logger.info(f"Created database: {db_name}")
                    else:
                        logger.info(f"Database already exists: {db_name}")
            except Exception as e:
                logger.warning(f"Could not create database (may already exist): {e}")

def init_db():
    """Initialize database with all tables"""
    try:
        # Create database if needed
        create_database()
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create additional indexes
        create_indexes()
        
        # Verify tables exist
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' OR table_schema = 'main' "
                "ORDER BY table_name;"
            ))
            tables = [row[0] for row in result]
            logger.info(f"Created tables: {', '.join(tables)}")
            
            # Count existing records
            for table in ['vehicles', 'search_cache', 'query_analytics']:
                if table in tables:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    logger.info(f"Table '{table}' has {count} records")
        
        logger.info("Database initialization complete!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)