"""
Input validation schemas using Pydantic for security and data integrity
Prevents injection attacks and ensures data quality
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import re
from datetime import datetime

class SearchQuerySchema(BaseModel):
    """Validation for search queries"""
    
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    make: Optional[str] = Field(None, max_length=50, description="Vehicle make")
    model: Optional[str] = Field(None, max_length=50, description="Vehicle model")
    year_min: Optional[int] = Field(None, ge=1900, le=datetime.now().year + 2, description="Minimum year")
    year_max: Optional[int] = Field(None, ge=1900, le=datetime.now().year + 2, description="Maximum year")
    price_min: Optional[int] = Field(None, ge=0, le=10000000, description="Minimum price")
    price_max: Optional[int] = Field(None, ge=0, le=10000000, description="Maximum price")
    max_mileage: Optional[int] = Field(None, ge=0, le=1000000, description="Maximum mileage")
    condition: Optional[str] = Field(None, description="Vehicle condition")
    fuel_type: Optional[str] = Field(None, description="Fuel type")
    transmission: Optional[str] = Field(None, description="Transmission type")
    sources: List[str] = Field(default=["ebay"], description="Data sources to search")
    
    @validator('query')
    def sanitize_query(cls, v):
        # Remove potentially dangerous characters but allow normal search terms
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        
        # Remove SQL injection patterns
        dangerous_patterns = [
            r';\s*drop\s+table',
            r';\s*delete\s+from',
            r';\s*update\s+',
            r';\s*insert\s+into',
            r'union\s+select',
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
        ]
        
        query_lower = v.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower):
                raise ValueError("Query contains invalid characters")
        
        return v.strip()
    
    @validator('make', 'model')
    def sanitize_make_model(cls, v):
        if v is None:
            return v
        
        # Only allow alphanumeric, spaces, hyphens, and common punctuation
        if not re.match(r'^[a-zA-Z0-9\s\-\.]+$', v):
            raise ValueError("Invalid characters in make/model")
        
        return v.strip()
    
    @validator('year_min', 'year_max')
    def validate_year_range(cls, v):
        if v is not None and (v < 1900 or v > datetime.now().year + 2):
            raise ValueError("Year must be between 1900 and current year + 2")
        return v
    
    @validator('condition')
    def validate_condition(cls, v):
        if v is None:
            return v
        
        valid_conditions = ['new', 'used', 'certified', 'salvage', 'damaged']
        if v.lower() not in valid_conditions:
            raise ValueError(f"Condition must be one of: {valid_conditions}")
        
        return v.lower()
    
    @validator('fuel_type')
    def validate_fuel_type(cls, v):
        if v is None:
            return v
        
        valid_fuels = ['gasoline', 'diesel', 'hybrid', 'electric', 'flex', 'cng']
        if v.lower() not in valid_fuels:
            raise ValueError(f"Fuel type must be one of: {valid_fuels}")
        
        return v.lower()
    
    @validator('transmission')
    def validate_transmission(cls, v):
        if v is None:
            return v
        
        valid_transmissions = ['automatic', 'manual', 'cvt', 'semi-automatic']
        if v.lower() not in valid_transmissions:
            raise ValueError(f"Transmission must be one of: {valid_transmissions}")
        
        return v.lower()
    
    @validator('sources')
    def validate_sources(cls, v):
        if not v:
            return ['ebay']  # Default fallback
        
        valid_sources = ['ebay', 'carmax', 'bringatrailer', 'cargurus', 'truecar', 'auto.dev']
        invalid_sources = [s for s in v if s not in valid_sources]
        
        if invalid_sources:
            raise ValueError(f"Invalid sources: {invalid_sources}. Valid sources: {valid_sources}")
        
        return v

class MessageGenerationSchema(BaseModel):
    """Validation for message generation requests"""
    
    vehicle_id: int = Field(..., gt=0, description="Vehicle ID")
    message_type: str = Field(..., description="Type of message to generate")
    offer_price: Optional[float] = Field(None, gt=0, le=10000000, description="Offer price")
    custom_message: Optional[str] = Field(None, max_length=1000, description="Custom message content")
    
    @validator('message_type')
    def validate_message_type(cls, v):
        valid_types = ['inquiry', 'offer', 'followup', 'inspection']
        if v.lower() not in valid_types:
            raise ValueError(f"Message type must be one of: {valid_types}")
        return v.lower()
    
    @validator('custom_message')
    def sanitize_custom_message(cls, v):
        if v is None:
            return v
        
        # Remove HTML tags and scripts
        v = re.sub(r'<[^>]+>', '', v)
        v = re.sub(r'javascript:', '', v, flags=re.IGNORECASE)
        
        return v.strip()

class FavoriteToggleSchema(BaseModel):
    """Validation for favorite toggle requests"""
    
    vehicle_id: int = Field(..., gt=0, description="Vehicle ID")

class PaginationSchema(BaseModel):
    """Validation for pagination parameters"""
    
    page: int = Field(default=1, ge=1, le=1000, description="Page number")
    per_page: int = Field(default=12, ge=1, le=100, description="Items per page")
    sort: str = Field(default="newest", description="Sort order")
    
    @validator('sort')
    def validate_sort(cls, v):
        valid_sorts = ['newest', 'oldest', 'price_low', 'price_high', 'mileage_low', 'mileage_high']
        if v not in valid_sorts:
            raise ValueError(f"Sort must be one of: {valid_sorts}")
        return v

class BackgroundIngestSchema(BaseModel):
    """Validation for background ingestion requests"""
    
    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    sources: str = Field(default="ebay", description="Comma-separated list of sources")
    limit: int = Field(default=25, ge=1, le=100, description="Number of results to fetch")
    
    @validator('query')
    def sanitize_query(cls, v):
        # Same sanitization as SearchQuerySchema
        return SearchQuerySchema.sanitize_query(v)
    
    @validator('sources')
    def validate_sources_string(cls, v):
        sources_list = [s.strip() for s in v.split(',')]
        valid_sources = ['ebay', 'carmax', 'bringatrailer', 'cargurus', 'truecar']
        invalid = [s for s in sources_list if s not in valid_sources]
        
        if invalid:
            raise ValueError(f"Invalid sources: {invalid}")
        
        return v

class VehicleFilterSchema(BaseModel):
    """Validation for vehicle filtering"""
    
    make: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=50)
    year_min: Optional[int] = Field(None, ge=1900, le=datetime.now().year + 2)
    year_max: Optional[int] = Field(None, ge=1900, le=datetime.now().year + 2)
    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)
    mileage_max: Optional[int] = Field(None, ge=0)
    condition: Optional[str] = Field(None)
    source: Optional[str] = Field(None)
    
    class Config:
        # Allow extra fields to be ignored instead of raising error
        extra = "ignore"

def validate_search_input(
    query: str,
    make: str = None,
    model: str = None,
    year_min: int = None,
    year_max: int = None,
    price_min: int = None,
    price_max: int = None,
    max_mileage: int = None,
    condition: str = None,
    fuel_type: str = None,
    transmission: str = None,
    sources: List[str] = None
) -> SearchQuerySchema:
    """Validate search input and return sanitized data"""
    
    return SearchQuerySchema(
        query=query,
        make=make,
        model=model,
        year_min=year_min,
        year_max=year_max,
        price_min=price_min,
        price_max=price_max,
        max_mileage=max_mileage,
        condition=condition,
        fuel_type=fuel_type,
        transmission=transmission,
        sources=sources or ["ebay"]
    )

# Security utilities
def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove path traversal attempts
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    # Keep only alphanumeric, dots, hyphens, underscores
    filename = re.sub(r'[^a-zA-Z0-9.\-_]', '', filename)
    return filename[:100]  # Limit length

def sanitize_html_input(text: str) -> str:
    """Basic HTML sanitization for user inputs"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove JavaScript
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    # Remove event handlers
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    return text.strip()

def validate_ip_address(ip: str) -> bool:
    """Validate IP address format"""
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False