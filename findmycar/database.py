from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///./findmycar.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(String, unique=True, index=True)
    source = Column(String, default="ebay")
    title = Column(String)
    price = Column(Float)
    location = Column(String)
    image_urls = Column(JSON)
    view_item_url = Column(String)
    
    # Vehicle Specifics
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    mileage = Column(Integer)
    trim = Column(String)
    condition = Column(String)
    body_style = Column(String)
    transmission = Column(String)
    drivetrain = Column(String)
    fuel_type = Column(String)
    exterior_color = Column(String)
    interior_color = Column(String)
    vin = Column(String)

    # Raw data from source
    vehicle_details = Column(JSON)
    
    # Valuation data
    estimated_value = Column(Float)
    market_min = Column(Float)
    market_max = Column(Float)
    deal_rating = Column(String)  # "Great Deal", "Good Deal", "Fair Price", "High Price"
    valuation_confidence = Column(Float)  # 0.0 to 1.0
    valuation_source = Column(String)
    last_valuation_update = Column(DateTime)
    
    # AI-generated questions
    buyer_questions = Column(JSON)  # List of questions for buyers to ask
    
    # User engagement
    view_count = Column(Integer, default=0)
    is_featured = Column(String, default='false')  # Boolean stored as string for SQLite compatibility
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class UserSession(Base):
    """Simple session-based user tracking for favorites"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    favorites = Column(JSON)  # List of vehicle IDs
    search_history = Column(JSON)  # List of recent searches
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
