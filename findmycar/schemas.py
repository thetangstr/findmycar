from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Vehicle(BaseModel):
    listing_id: str
    title: str
    price: float
    location: str
    image_urls: List[str]
    view_item_url: str
    make: Optional[str]
    model: Optional[str]
    year: Optional[int]
    mileage: Optional[int]
    trim: Optional[str]
    condition: Optional[str]
    body_style: Optional[str]
    transmission: Optional[str]
    drivetrain: Optional[str]
    fuel_type: Optional[str]
    exterior_color: Optional[str]
    interior_color: Optional[str]
    vin: Optional[str]
    
    # Valuation fields
    estimated_value: Optional[float]
    market_min: Optional[float]
    market_max: Optional[float]
    deal_rating: Optional[str]
    valuation_confidence: Optional[float]
    valuation_source: Optional[str]
    last_valuation_update: Optional[datetime]
    
    # AI-generated questions
    buyer_questions: Optional[List[str]]

    class Config:
        from_attributes = True