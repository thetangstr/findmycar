#!/usr/bin/env python3
"""
Update existing vehicles in the database with inferred attributes.
This script processes vehicles that have missing body_style, transmission, etc.
"""

import logging
from sqlalchemy.orm import Session
from database import SessionLocal, Vehicle
from vehicle_attribute_inference import VehicleAttributeInferencer
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_vehicle_attributes():
    """Update vehicles with inferred attributes."""
    db = SessionLocal()
    inferencer = VehicleAttributeInferencer()
    
    try:
        # Get vehicles with missing attributes
        vehicles_to_update = db.query(Vehicle).filter(
            (Vehicle.body_style == None) | 
            (Vehicle.body_style == '') |
            (Vehicle.transmission == None) |
            (Vehicle.transmission == '') |
            (Vehicle.fuel_type == None) |
            (Vehicle.fuel_type == '')
        ).all()
        
        logger.info(f"Found {len(vehicles_to_update)} vehicles to update")
        
        updated_count = 0
        for vehicle in vehicles_to_update:
            try:
                # Prepare data for inference
                vehicle_data = {
                    'title': vehicle.title or '',
                    'model': vehicle.model or '',
                    'description': '',  # Could extract from vehicle_details if available
                }
                
                # Add any existing specifics from vehicle_details
                if vehicle.vehicle_details:
                    if isinstance(vehicle.vehicle_details, dict):
                        # For eBay items, check for itemSpecifics
                        if 'itemSpecifics' in vehicle.vehicle_details:
                            vehicle_data['item_specifics'] = {}
                            for spec in vehicle.vehicle_details['itemSpecifics']:
                                if 'localizedName' in spec and 'value' in spec:
                                    vehicle_data['item_specifics'][spec['localizedName']] = spec['value']
                
                # Infer attributes
                inferred = inferencer.infer_attributes(vehicle_data, vehicle.source or 'ebay')
                
                # Update vehicle if we inferred new values
                changes = []
                if not vehicle.body_style and inferred.get('body_style'):
                    vehicle.body_style = inferred['body_style']
                    changes.append(f"body_style={inferred['body_style']}")
                
                if not vehicle.transmission and inferred.get('transmission'):
                    vehicle.transmission = inferred['transmission']
                    changes.append(f"transmission={inferred['transmission']}")
                
                if not vehicle.fuel_type and inferred.get('fuel_type'):
                    vehicle.fuel_type = inferred['fuel_type']
                    changes.append(f"fuel_type={inferred['fuel_type']}")
                
                if not vehicle.drivetrain and inferred.get('drivetrain'):
                    vehicle.drivetrain = inferred['drivetrain']
                    changes.append(f"drivetrain={inferred['drivetrain']}")
                
                if not vehicle.exterior_color and inferred.get('exterior_color'):
                    vehicle.exterior_color = inferred['exterior_color']
                    changes.append(f"color={inferred['exterior_color']}")
                
                if changes:
                    db.commit()
                    updated_count += 1
                    logger.info(f"Updated {vehicle.year} {vehicle.make} {vehicle.model}: {', '.join(changes)}")
                
            except Exception as e:
                logger.error(f"Error updating vehicle {vehicle.id}: {e}")
                db.rollback()
        
        logger.info(f"Successfully updated {updated_count} vehicles")
        
        # Show statistics
        stats = {
            'total_vehicles': db.query(Vehicle).count(),
            'with_body_style': db.query(Vehicle).filter(Vehicle.body_style != None, Vehicle.body_style != '').count(),
            'with_transmission': db.query(Vehicle).filter(Vehicle.transmission != None, Vehicle.transmission != '').count(),
            'with_fuel_type': db.query(Vehicle).filter(Vehicle.fuel_type != None, Vehicle.fuel_type != '').count(),
            'with_color': db.query(Vehicle).filter(Vehicle.exterior_color != None, Vehicle.exterior_color != '').count(),
        }
        
        logger.info("Database statistics after update:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
    finally:
        db.close()

if __name__ == "__main__":
    update_vehicle_attributes()