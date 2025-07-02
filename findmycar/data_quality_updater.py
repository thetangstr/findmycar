#!/usr/bin/env python3
"""
Data Quality Updater - Updates existing vehicle records with enhanced data extraction
"""

from sqlalchemy.orm import Session
from database import SessionLocal, Vehicle
from ingestion import extract_vehicle_info_from_title
from valuation import VehicleValuation
import datetime

def update_vehicle_data_quality(db: Session, limit: int = 50):
    """
    Update existing vehicle records with enhanced data extraction.
    """
    print(f"Updating data quality for up to {limit} vehicles...")
    
    # Get vehicles that need data improvement
    vehicles = db.query(Vehicle).filter(
        (Vehicle.model == None) | 
        (Vehicle.mileage == None) | 
        (Vehicle.deal_rating == None)
    ).limit(limit).all()
    
    print(f"Found {len(vehicles)} vehicles needing updates")
    
    valuation_service = VehicleValuation()
    updated_count = 0
    
    for vehicle in vehicles:
        try:
            print(f"Updating: {vehicle.title[:50]}...")
            
            # Extract enhanced vehicle info from title
            parsed_info = extract_vehicle_info_from_title(vehicle.title)
            
            # Update missing make/model/year
            if not vehicle.make and parsed_info.get('make'):
                vehicle.make = parsed_info['make']
                updated_count += 1
                
            if not vehicle.model and parsed_info.get('model'):
                vehicle.model = parsed_info['model']
                updated_count += 1
                
            if not vehicle.year and parsed_info.get('year'):
                vehicle.year = parsed_info['year']
                updated_count += 1
                
            if not vehicle.mileage and parsed_info.get('mileage'):
                vehicle.mileage = parsed_info['mileage']
                updated_count += 1
            
            # Add valuation if we have enough data and it's missing
            if (vehicle.make and vehicle.model and vehicle.year and vehicle.price and 
                not vehicle.deal_rating):
                try:
                    valuation = valuation_service.get_vehicle_valuation(
                        make=vehicle.make,
                        model=vehicle.model,
                        year=vehicle.year,
                        mileage=vehicle.mileage,
                        condition=vehicle.condition or 'good'
                    )
                    
                    if valuation.get('estimated_value'):
                        vehicle.estimated_value = valuation['estimated_value']
                        vehicle.market_min = valuation['market_min']
                        vehicle.market_max = valuation['market_max']
                        vehicle.valuation_confidence = valuation['confidence']
                        vehicle.valuation_source = valuation['data_source']
                        vehicle.last_valuation_update = datetime.datetime.utcnow()
                        
                        # Calculate deal rating
                        vehicle.deal_rating = valuation_service.calculate_deal_rating(
                            listing_price=vehicle.price,
                            estimated_value=valuation['estimated_value'],
                            market_min=valuation['market_min'],
                            market_max=valuation['market_max']
                        )
                        updated_count += 1
                        
                except Exception as e:
                    print(f"  Valuation failed: {e}")
            
            # Commit changes
            db.commit()
            
        except Exception as e:
            print(f"  Error updating vehicle: {e}")
            db.rollback()
    
    print(f"Data quality update complete. Updated {updated_count} fields.")
    return updated_count

if __name__ == "__main__":
    db = SessionLocal()
    try:
        update_vehicle_data_quality(db, limit=100)
    finally:
        db.close()