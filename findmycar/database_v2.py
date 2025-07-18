"""
Enhanced database schema with JSONB support for comprehensive search
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Index, Boolean
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
import datetime
import os

Base = declarative_base()

class VehicleV2(Base):
    """Enhanced vehicle model with JSONB for flexible attributes"""
    __tablename__ = "vehicles_v2"

    # Primary identifiers
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(String, unique=True, index=True)
    source = Column(String, index=True)  # ebay, carmax, cargurus, etc.
    
    # Core searchable fields (indexed for performance)
    make = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer, index=True)
    price = Column(Float, index=True)
    mileage = Column(Integer, index=True)
    
    # Common attributes (frequently searched)
    body_style = Column(String, index=True)  # sedan, suv, truck, etc.
    exterior_color = Column(String, index=True)
    interior_color = Column(String)
    transmission = Column(String, index=True)  # automatic, manual, cvt
    drivetrain = Column(String, index=True)  # fwd, rwd, awd, 4wd
    fuel_type = Column(String, index=True)  # gasoline, hybrid, electric, diesel
    
    # Location
    location = Column(String)
    zip_code = Column(String, index=True)
    dealer_name = Column(String)
    
    # Listing details
    title = Column(String)
    description = Column(Text)
    view_item_url = Column(String)
    image_urls = Column(JSONB)  # ["url1", "url2", ...]
    
    # JSONB fields for flexible attributes
    attributes = Column(JSONB, default={})  # All technical specs
    features = Column(JSONB, default=[])  # List of features
    history = Column(JSONB, default={})  # Ownership, accidents, service
    pricing_analysis = Column(JSONB, default={})  # Market value, deal rating
    
    # Full-text search
    search_vector = Column(TSVECTOR)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Raw data preservation
    raw_data = Column(JSONB)  # Original data from source
    
    # Indexes
    __table_args__ = (
        Index('idx_make_model', 'make', 'model'),
        Index('idx_year_price', 'year', 'price'),
        Index('idx_attributes_gin', 'attributes', postgresql_using='gin'),
        Index('idx_features_gin', 'features', postgresql_using='gin'),
        Index('idx_search_vector_gin', 'search_vector', postgresql_using='gin'),
        Index('idx_location', 'zip_code', 'location'),
    )


class SavedSearch(Base):
    """User saved searches"""
    __tablename__ = "saved_searches"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True)  # For future user system
    name = Column(String)
    search_params = Column(JSONB)
    notification_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_run_at = Column(DateTime)
    

class SearchHistory(Base):
    """Track search queries for analytics"""
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True)
    query = Column(String)
    filters = Column(JSONB)
    result_count = Column(Integer)
    user_id = Column(String)
    ip_address = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# Attribute standardization mappings
ATTRIBUTE_MAPPINGS = {
    # Engine & Performance
    'engine_size': ['engineSize', 'engine', 'displacement', 'engineDisplacement'],
    'cylinders': ['cylinders', 'numberOfCylinders', 'engineCylinders', 'numCylinders'],
    'horsepower': ['horsepower', 'hp', 'power', 'enginePower'],
    'torque': ['torque', 'torqueLbFt', 'engineTorque'],
    
    # Fuel Economy
    'mpg_city': ['mpgCity', 'cityMPG', 'fuelEconomyCity', 'cityFuelEconomy'],
    'mpg_highway': ['mpgHighway', 'highwayMPG', 'fuelEconomyHighway', 'hwyMPG'],
    'mpg_combined': ['mpgCombined', 'combinedMPG', 'avgMPG'],
    'electric_range': ['electricRange', 'evRange', 'batteryRange', 'rangeElectric'],
    
    # Dimensions
    'seating_capacity': ['seatingCapacity', 'seats', 'numSeats', 'passengerCapacity'],
    'doors': ['doors', 'numDoors', 'numberOfDoors'],
    'length': ['length', 'vehicleLength'],
    'width': ['width', 'vehicleWidth'],
    'height': ['height', 'vehicleHeight'],
    'wheelbase': ['wheelbase', 'wheelBase'],
    'cargo_volume': ['cargoVolume', 'cargoSpace', 'trunkSpace'],
    
    # Transmission Details
    'transmission_speeds': ['gears', 'speeds', 'transmissionSpeeds'],
    'transmission_type': ['transmissionType', 'transType', 'transmission'],
    
    # Ownership
    'owners': ['owners', 'numberOfOwners', 'previousOwners', 'ownerCount'],
    'accident_count': ['accidents', 'accidentCount', 'reportedAccidents'],
    'service_records': ['serviceRecords', 'maintenanceRecords'],
    'title_status': ['titleStatus', 'title', 'titleType'],
    
    # Certification
    'certified': ['certified', 'cpo', 'certifiedPreOwned'],
    'warranty': ['warranty', 'warrantyRemaining', 'factoryWarranty'],
    'inspection_status': ['inspected', 'inspectionStatus', 'multiPointInspection'],
}

# Feature standardization
FEATURE_MAPPINGS = {
    # Safety
    'backup_camera': ['backup camera', 'rear camera', 'rearview camera', 'reversing camera'],
    'blind_spot_monitor': ['blind spot', 'bsm', 'blind spot monitoring', 'blind spot detection'],
    'lane_keep_assist': ['lane keep', 'lane keeping', 'lka', 'lane keep assist'],
    'adaptive_cruise': ['adaptive cruise', 'acc', 'radar cruise', 'dynamic cruise'],
    'automatic_braking': ['automatic braking', 'aeb', 'emergency braking', 'collision mitigation'],
    
    # Comfort
    'heated_seats': ['heated seats', 'seat heating', 'heated front seats'],
    'cooled_seats': ['cooled seats', 'ventilated seats', 'air conditioned seats'],
    'leather_seats': ['leather', 'leather seats', 'leather interior', 'leather upholstery'],
    'sunroof': ['sunroof', 'moonroof', 'panoramic roof', 'glass roof'],
    'power_seats': ['power seats', 'power adjustable seats', 'electric seats'],
    
    # Technology
    'apple_carplay': ['apple carplay', 'carplay', 'apple car play'],
    'android_auto': ['android auto', 'android automotive'],
    'navigation': ['navigation', 'gps', 'nav system', 'navigation system'],
    'premium_audio': ['premium audio', 'premium sound', 'bose', 'harman kardon', 'meridian'],
    'keyless_entry': ['keyless', 'keyless entry', 'smart key', 'proximity key'],
    'remote_start': ['remote start', 'remote engine start', 'app start'],
    
    # Convenience
    'third_row': ['third row', '3rd row', 'seven seats', '7 seats', '7 passenger'],
    'tow_package': ['tow', 'towing package', 'trailer hitch', 'tow hitch'],
    'roof_rails': ['roof rails', 'roof rack', 'cargo rails'],
}


def get_database_url():
    """Get database URL with PostgreSQL as default"""
    return os.environ.get('DATABASE_URL', 'postgresql://localhost/findmycar')


def init_db():
    """Initialize the database"""
    engine = create_engine(get_database_url())
    Base.metadata.create_all(bind=engine)
    return engine


def get_session():
    """Get database session"""
    engine = init_db()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()