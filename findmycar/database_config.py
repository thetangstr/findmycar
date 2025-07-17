"""
Database configuration module for production deployment
Supports both SQLite (development) and PostgreSQL (production)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import logging

logger = logging.getLogger(__name__)

def get_database_url():
    """
    Get database URL from environment with proper formatting
    Supports both DATABASE_URL and individual connection parameters
    """
    # Check for Heroku-style DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    
    if database_url and database_url.startswith("postgres://"):
        # Fix for SQLAlchemy 1.4+ which requires postgresql:// instead of postgres://
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url
    
    # Check for individual PostgreSQL parameters
    if os.getenv("POSTGRES_HOST"):
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "findmycar")
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    # Default to SQLite for development
    return "sqlite:///./findmycar.db"

def get_engine_args():
    """
    Get engine arguments based on database type
    """
    database_url = get_database_url()
    
    if database_url.startswith("sqlite"):
        # SQLite specific args
        return {
            "connect_args": {"check_same_thread": False},
            "pool_pre_ping": True
        }
    else:
        # PostgreSQL specific args
        return {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
            "pool_recycle": 300,  # Recycle connections after 5 minutes
            "echo_pool": os.getenv("DEBUG", "false").lower() == "true"
        }

def create_db_engine():
    """
    Create database engine with appropriate configuration
    """
    database_url = get_database_url()
    engine_args = get_engine_args()
    
    logger.info(f"Connecting to database: {database_url.split('@')[0]}...")
    
    try:
        engine = create_engine(database_url, **engine_args)
        # Test connection
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return engine
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

# Create engine and session factory
engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()