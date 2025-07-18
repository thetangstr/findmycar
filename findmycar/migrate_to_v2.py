#!/usr/bin/env python3
"""
Migrate existing vehicle data to the new PostgreSQL schema with standardized attributes
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Import old and new models
from database import Vehicle as VehicleV1, SessionLocal as SessionLocalV1
from database_v2 import VehicleV2, Base, get_database_url, init_db
from attribute_standardizer import AttributeStandardizer
from vehicle_attribute_inference import VehicleAttributeInference

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VehicleMigrator:
    """Migrates vehicles from V1 schema to V2 with attribute standardization"""
    
    def __init__(self):
        # Initialize connections
        self.v1_session = SessionLocalV1()
        
        # Create V2 engine and session
        self.v2_engine = init_db()
        SessionLocalV2 = sessionmaker(bind=self.v2_engine)
        self.v2_session = SessionLocalV2()
        
        # Initialize helpers
        self.standardizer = AttributeStandardizer()
        self.inference_engine = VehicleAttributeInference()
        
        # Track migration stats
        self.stats = {
            'total': 0,
            'migrated': 0,
            'skipped': 0,
            'errors': 0,
            'attributes_enriched': 0,
            'features_detected': 0
        }
    
    def migrate_all(self, batch_size: int = 100):
        """Migrate all vehicles in batches"""
        logger.info("Starting vehicle migration to V2 schema...")
        
        # Get total count
        total_count = self.v1_session.query(VehicleV1).count()
        logger.info(f"Found {total_count} vehicles to migrate")
        
        self.stats['total'] = total_count
        
        # Process in batches
        offset = 0
        while offset < total_count:
            vehicles = self.v1_session.query(VehicleV1).offset(offset).limit(batch_size).all()
            
            for vehicle in vehicles:
                try:
                    self.migrate_vehicle(vehicle)
                except Exception as e:
                    logger.error(f"Error migrating vehicle {vehicle.id}: {e}")
                    self.stats['errors'] += 1
            
            # Commit batch
            try:
                self.v2_session.commit()
                logger.info(f"Migrated batch {offset}-{offset + batch_size}")
            except Exception as e:
                logger.error(f"Error committing batch: {e}")
                self.v2_session.rollback()
            
            offset += batch_size
        
        # Print final stats
        self.print_stats()
    
    def migrate_vehicle(self, v1_vehicle: VehicleV1):
        """Migrate a single vehicle"""
        try:
            # Check if already exists
            existing = self.v2_session.query(VehicleV2).filter_by(
                listing_id=v1_vehicle.listing_id
            ).first()
            
            if existing:
                logger.debug(f"Vehicle {v1_vehicle.listing_id} already migrated, skipping")
                self.stats['skipped'] += 1
                return
            
            # Parse vehicle details
            vehicle_details = {}
            if v1_vehicle.vehicle_details:
                try:
                    vehicle_details = json.loads(v1_vehicle.vehicle_details)
                except:
                    vehicle_details = {}
            
            # Prepare raw data for standardization
            raw_data = {
                'title': v1_vehicle.title,
                'price': v1_vehicle.price,
                'location': v1_vehicle.location,
                'condition': v1_vehicle.condition,
                'view_item_url': v1_vehicle.view_item_url,
                'image_url': v1_vehicle.image_url,
                **vehicle_details
            }
            
            # Get source from listing_id prefix
            source = self._detect_source(v1_vehicle.listing_id)
            
            # Standardize the data
            standardized = self.standardizer.standardize_vehicle_data(raw_data, source)
            
            # Use inference to fill missing attributes
            inferred_data = self.inference_engine.infer_from_vehicle({
                'title': v1_vehicle.title,
                'make': v1_vehicle.make,
                'model': v1_vehicle.model,
                'year': v1_vehicle.year,
                **standardized['attributes']
            })
            
            # Merge standardized and inferred data
            final_attributes = {**standardized['attributes'], **inferred_data}
            
            # Count enrichments
            if len(final_attributes) > len(standardized['attributes']):
                self.stats['attributes_enriched'] += 1
            if standardized['features']:
                self.stats['features_detected'] += 1
            
            # Create V2 vehicle
            v2_vehicle = VehicleV2(
                listing_id=v1_vehicle.listing_id,
                source=source,
                
                # Core fields from V1
                make=v1_vehicle.make,
                model=v1_vehicle.model,
                year=v1_vehicle.year,
                price=v1_vehicle.price,
                mileage=v1_vehicle.mileage,
                
                # Standardized core fields
                body_style=standardized['core_fields'].get('body_style') or inferred_data.get('body_style'),
                exterior_color=standardized['core_fields'].get('exterior_color'),
                interior_color=standardized['core_fields'].get('interior_color'),
                transmission=standardized['core_fields'].get('transmission') or inferred_data.get('transmission'),
                drivetrain=standardized['core_fields'].get('drivetrain') or inferred_data.get('drivetrain'),
                fuel_type=standardized['core_fields'].get('fuel_type') or inferred_data.get('fuel_type'),
                
                # Location
                location=v1_vehicle.location,
                zip_code=self._extract_zip_code(v1_vehicle.location),
                
                # Listing details
                title=v1_vehicle.title,
                description=vehicle_details.get('shortDescription', ''),
                view_item_url=v1_vehicle.view_item_url,
                image_urls=self._convert_image_urls(v1_vehicle),
                
                # JSONB fields
                attributes=final_attributes,
                features=standardized['features'],
                history=standardized['history'],
                
                # Preserve raw data
                raw_data=raw_data,
                
                # Timestamps
                created_at=v1_vehicle.created_at or datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Add to session
            self.v2_session.add(v2_vehicle)
            self.stats['migrated'] += 1
            
            if self.stats['migrated'] % 100 == 0:
                logger.info(f"Progress: {self.stats['migrated']}/{self.stats['total']} migrated")
            
        except Exception as e:
            logger.error(f"Error processing vehicle {v1_vehicle.id}: {e}")
            raise
    
    def _detect_source(self, listing_id: str) -> str:
        """Detect source from listing ID format"""
        if listing_id.startswith('v1|'):
            # eBay format
            return 'ebay'
        elif listing_id.startswith('carmax_'):
            return 'carmax'
        elif listing_id.startswith('cargurus_'):
            return 'cargurus'
        elif listing_id.startswith('bat_'):
            return 'bat'
        else:
            return 'unknown'
    
    def _extract_zip_code(self, location: Optional[str]) -> Optional[str]:
        """Extract ZIP code from location string"""
        if not location:
            return None
        
        import re
        # Look for 5-digit ZIP code
        match = re.search(r'\b\d{5}\b', location)
        return match.group() if match else None
    
    def _convert_image_urls(self, vehicle: VehicleV1) -> List[str]:
        """Convert image URL to array format"""
        urls = []
        
        # Primary image
        if vehicle.image_url:
            urls.append(vehicle.image_url)
        
        # Additional images from details
        if vehicle.vehicle_details:
            try:
                details = json.loads(vehicle.vehicle_details)
                # eBay additional images
                if 'additionalImages' in details:
                    for img in details['additionalImages']:
                        if 'imageUrl' in img:
                            urls.append(img['imageUrl'])
                # CarMax images
                elif 'images' in details:
                    urls.extend(details['images'])
            except:
                pass
        
        return urls
    
    def update_search_vectors(self):
        """Update full-text search vectors after migration"""
        logger.info("Updating search vectors...")
        
        # PostgreSQL-specific: Update search vectors
        update_query = """
        UPDATE vehicles_v2 
        SET search_vector = to_tsvector('english',
            COALESCE(make, '') || ' ' ||
            COALESCE(model, '') || ' ' ||
            COALESCE(title, '') || ' ' ||
            COALESCE(description, '') || ' ' ||
            COALESCE(body_style, '') || ' ' ||
            COALESCE(exterior_color, '') || ' ' ||
            COALESCE(transmission, '') || ' ' ||
            COALESCE(fuel_type, '')
        )
        """
        
        try:
            self.v2_session.execute(update_query)
            self.v2_session.commit()
            logger.info("Search vectors updated successfully")
        except Exception as e:
            logger.error(f"Error updating search vectors: {e}")
            self.v2_session.rollback()
    
    def print_stats(self):
        """Print migration statistics"""
        logger.info("\n" + "="*50)
        logger.info("Migration Complete!")
        logger.info("="*50)
        logger.info(f"Total vehicles: {self.stats['total']}")
        logger.info(f"Successfully migrated: {self.stats['migrated']}")
        logger.info(f"Skipped (already exists): {self.stats['skipped']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"Vehicles with enriched attributes: {self.stats['attributes_enriched']}")
        logger.info(f"Vehicles with detected features: {self.stats['features_detected']}")
        logger.info("="*50)
    
    def cleanup(self):
        """Close database connections"""
        self.v1_session.close()
        self.v2_session.close()


def verify_migration():
    """Verify migration results"""
    logger.info("\nVerifying migration...")
    
    # Connect to both databases
    v1_session = SessionLocalV1()
    engine = create_engine(get_database_url())
    SessionLocalV2 = sessionmaker(bind=engine)
    v2_session = SessionLocalV2()
    
    # Compare counts
    v1_count = v1_session.query(VehicleV1).count()
    v2_count = v2_session.query(VehicleV2).count()
    
    logger.info(f"V1 vehicles: {v1_count}")
    logger.info(f"V2 vehicles: {v2_count}")
    
    if v1_count == v2_count:
        logger.info("✅ Count matches!")
    else:
        logger.warning(f"⚠️ Count mismatch: {v1_count - v2_count} vehicles not migrated")
    
    # Sample some vehicles to check data quality
    sample_vehicles = v2_session.query(VehicleV2).limit(5).all()
    
    logger.info("\nSample migrated vehicles:")
    for v in sample_vehicles:
        logger.info(f"\n{v.year} {v.make} {v.model}")
        logger.info(f"  Body Style: {v.body_style}")
        logger.info(f"  Transmission: {v.transmission}")
        logger.info(f"  Fuel Type: {v.fuel_type}")
        logger.info(f"  Attributes: {len(v.attributes)} fields")
        logger.info(f"  Features: {len(v.features)} items")
    
    v1_session.close()
    v2_session.close()


def main():
    """Run the migration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate vehicles to V2 schema')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size for migration')
    parser.add_argument('--verify-only', action='store_true', help='Only verify migration')
    
    args = parser.parse_args()
    
    if args.verify_only:
        verify_migration()
    else:
        # Check if V2 database URL is set
        db_url = get_database_url()
        if 'postgresql' not in db_url:
            logger.warning("⚠️ WARNING: DATABASE_URL should point to PostgreSQL for V2 schema")
            logger.warning(f"Current URL: {db_url}")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return
        
        # Run migration
        migrator = VehicleMigrator()
        try:
            migrator.migrate_all(batch_size=args.batch_size)
            migrator.update_search_vectors()
        finally:
            migrator.cleanup()
        
        # Verify results
        verify_migration()


if __name__ == "__main__":
    main()