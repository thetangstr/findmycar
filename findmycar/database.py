from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, Float, Text, Index, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os
import hashlib
from database_config import engine, SessionLocal
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
    
    # Source-specific fields
    # CarMax specific fields
    carmax_store = Column(String)  # CarMax store location
    carmax_stock_number = Column(String)  # CarMax internal stock number
    carmax_warranty = Column(String)  # CarMax warranty information
    features = Column(JSON)  # List of vehicle features
    seller_notes = Column(String)  # Additional seller notes/description
    
    # Bring a Trailer (BaT) specific fields
    bat_auction_id = Column(String)  # BaT auction identifier
    current_bid = Column(Float)  # Current highest bid amount
    bid_count = Column(Integer)  # Number of bids placed
    time_left = Column(String)  # Time remaining in auction
    auction_status = Column(String)  # 'active', 'ended', 'sold', 'no_sale'
    reserve_met = Column(String)  # Whether reserve price has been met
    comment_count = Column(Integer)  # Number of comments on listing
    bat_category = Column(String)  # BaT category (cars, motorcycles, trucks, etc.)
    seller_name = Column(String)  # Seller name/username
    detailed_description = Column(String)  # Full auction description
    vehicle_history = Column(String)  # Vehicle history information
    recent_work = Column(String)  # Recent work performed on vehicle
    
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
    comparison_list = Column(JSON)  # List of vehicle IDs for comparison
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)

class SearchCache(Base):
    """Database cache for popular search results (warm cache layer)"""
    __tablename__ = "search_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, index=True)
    query_hash = Column(String(64), index=True)
    query_text = Column(String(500))  # Store original query for debugging
    filters_json = Column(Text)  # JSON string of filters
    results = Column(JSON)  # Cached search results
    source = Column(String(50))  # Data source (ebay, carmax, etc.)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, index=True)
    access_count = Column(Integer, default=1)
    last_accessed = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.query_text and self.filters_json:
            # Generate cache key and hash
            key_data = f"{self.query_text}:{self.filters_json}"
            self.query_hash = hashlib.md5(key_data.encode()).hexdigest()
            self.cache_key = f"search_{self.query_hash}"

class QueryAnalytics(Base):
    """Track search query popularity for intelligent caching decisions"""
    __tablename__ = "query_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    query_normalized = Column(String(255), unique=True, index=True)
    search_count = Column(Integer, default=1)
    last_searched = Column(DateTime, default=datetime.datetime.utcnow)
    avg_results = Column(Integer)  # Average number of results returned
    cache_hits = Column(Integer, default=0)  # Number of times served from cache
    cache_misses = Column(Integer, default=0)  # Number of times fetched fresh
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Computed cache efficiency
    @property
    def cache_hit_rate(self):
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total) if total > 0 else 0.0

class SavedSearch(Base):
    """User's saved searches with alert functionality"""
    __tablename__ = "saved_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)  # Links to user session
    name = Column(String(255))  # User-friendly name for the search
    query = Column(String(500))  # Original search query
    filters = Column(JSON)  # Search filters
    alerts_enabled = Column(String, default='false')  # Boolean as string
    alert_frequency = Column(String, default='daily')  # daily, weekly, immediate
    last_run = Column(DateTime)  # When search was last executed
    last_results_count = Column(Integer, default=0)  # Number of results from last run
    new_results_count = Column(Integer, default=0)  # New results since last check
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Alert tracking
    last_alert_sent = Column(DateTime)
    alert_count = Column(Integer, default=0)
    
    @property
    def is_alerts_enabled(self):
        return self.alerts_enabled == 'true'

# User Management Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True)  # Firebase UID
    email = Column(String, unique=True, index=True)
    display_name = Column(String)
    photo_url = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    searches = relationship("UserSearch", back_populates="user", cascade="all, delete-orphan")
    saved_vehicles = relationship("SavedVehicle", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")

class UserSearch(Base):
    __tablename__ = "user_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(String)
    filters = Column(JSON)  # Store search filters
    results_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="searches")

class SavedVehicle(Base):
    __tablename__ = "saved_vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="saved_vehicles")
    vehicle = relationship("Vehicle")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    preference_key = Column(String)
    preference_value = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="preferences")

# Create indexes for performance
Index('idx_search_cache_expires', SearchCache.expires_at)
Index('idx_search_cache_accessed', SearchCache.last_accessed)
Index('idx_query_analytics_count', QueryAnalytics.search_count.desc())
Index('idx_user_uid', User.uid)
Index('idx_user_email', User.email)
Index('idx_user_search_created', UserSearch.created_at.desc())
Index('idx_saved_vehicle_user', SavedVehicle.user_id)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
