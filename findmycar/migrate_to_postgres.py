#!/usr/bin/env python
"""
Migration script to move data from SQLite to PostgreSQL
Usage: python migrate_to_postgres.py
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Vehicle, SearchCache, QueryAnalytics, UserSession, Base
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    
    # Source database (SQLite)
    sqlite_url = "sqlite:///./findmycar.db"
    if not os.path.exists("findmycar.db"):
        logger.error("SQLite database not found!")
        return False
        
    # Target database (PostgreSQL)
    postgres_url = os.getenv("DATABASE_URL")
    if not postgres_url:
        logger.error("DATABASE_URL environment variable not set!")
        return False
    
    # Fix postgres:// to postgresql:// if needed
    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql://", 1)
    
    try:
        # Create engines
        logger.info("Connecting to databases...")
        sqlite_engine = create_engine(sqlite_url)
        postgres_engine = create_engine(postgres_url)
        
        # Create sessions
        SqliteSession = sessionmaker(bind=sqlite_engine)
        PostgresSession = sessionmaker(bind=postgres_engine)
        
        sqlite_db = SqliteSession()
        postgres_db = PostgresSession()
        
        # Create tables in PostgreSQL if they don't exist
        logger.info("Creating PostgreSQL tables...")
        Base.metadata.create_all(bind=postgres_engine)
        
        # Migrate each table
        tables_to_migrate = [
            (Vehicle, "vehicles"),
            (SearchCache, "search_cache"),
            (QueryAnalytics, "query_analytics"),
            (UserSession, "user_sessions")
        ]
        
        for model, table_name in tables_to_migrate:
            logger.info(f"Migrating {table_name}...")
            
            # Check if table exists in SQLite
            try:
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                sqlite_count = sqlite_db.execute(count_query).scalar()
                logger.info(f"Found {sqlite_count} records in SQLite {table_name}")
                
                if sqlite_count == 0:
                    continue
                    
                # Get all records from SQLite
                records = sqlite_db.query(model).all()
                
                # Clear target table (optional - remove if appending)
                postgres_db.query(model).delete()
                postgres_db.commit()
                
                # Insert records into PostgreSQL
                batch_size = 100
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    
                    for record in batch:
                        # Create new instance with all attributes
                        new_record = model()
                        
                        # Copy all attributes
                        for column in model.__table__.columns:
                            attr_name = column.name
                            if hasattr(record, attr_name):
                                value = getattr(record, attr_name)
                                
                                # Handle JSON fields
                                if column.type.__class__.__name__ == 'JSON' and value:
                                    if isinstance(value, str):
                                        try:
                                            value = json.loads(value)
                                        except:
                                            pass
                                
                                setattr(new_record, attr_name, value)
                        
                        postgres_db.add(new_record)
                    
                    postgres_db.commit()
                    logger.info(f"Migrated batch {i//batch_size + 1} of {table_name}")
                
                # Verify migration
                postgres_count = postgres_db.query(model).count()
                logger.info(f"Migrated {postgres_count} records to PostgreSQL {table_name}")
                
                if postgres_count != sqlite_count:
                    logger.warning(f"Count mismatch for {table_name}: SQLite={sqlite_count}, PostgreSQL={postgres_count}")
                    
            except Exception as e:
                logger.error(f"Error migrating {table_name}: {e}")
                continue
        
        # Update sequences for PostgreSQL (important for auto-increment fields)
        logger.info("Updating PostgreSQL sequences...")
        sequence_updates = [
            "SELECT setval('vehicles_id_seq', (SELECT MAX(id) FROM vehicles));",
            "SELECT setval('search_cache_id_seq', (SELECT MAX(id) FROM search_cache));",
            "SELECT setval('query_analytics_id_seq', (SELECT MAX(id) FROM query_analytics));",
            "SELECT setval('user_sessions_id_seq', (SELECT MAX(id) FROM user_sessions));"
        ]
        
        for seq_update in sequence_updates:
            try:
                postgres_db.execute(text(seq_update))
                postgres_db.commit()
            except Exception as e:
                logger.warning(f"Sequence update skipped: {e}")
        
        logger.info("Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
    finally:
        sqlite_db.close()
        postgres_db.close()

if __name__ == "__main__":
    success = migrate_data()
    sys.exit(0 if success else 1)