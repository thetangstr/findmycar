#!/usr/bin/env python3
"""
Celery tasks for background data updates and maintenance
"""

from celery import Celery, Task
from celery.schedules import crontab
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

from dotenv import load_dotenv
load_dotenv()

# Configure Celery
app = Celery('findmycar',
             broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
             backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

# Configure Celery settings
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3000,  # 50 minute soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configure periodic tasks
app.conf.beat_schedule = {
    'update-stale-vehicles': {
        'task': 'celery_tasks.update_stale_vehicles',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {'queue': 'updates'}
    },
    'refresh-popular-vehicles': {
        'task': 'celery_tasks.refresh_popular_vehicles',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {'queue': 'updates'}
    },
    'cleanup-expired-data': {
        'task': 'celery_tasks.cleanup_expired_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        'options': {'queue': 'maintenance'}
    },
    'generate-freshness-report': {
        'task': 'celery_tasks.generate_freshness_report',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
        'options': {'queue': 'reports'}
    },
}

logger = logging.getLogger(__name__)

class DatabaseTask(Task):
    """Base task with database connection"""
    _db = None
    _search_service = None
    _freshness_manager = None

    @property
    def db(self):
        if self._db is None:
            from database_v2_sqlite import get_session
            self._db = get_session()
        return self._db

    @property
    def search_service(self):
        if self._search_service is None:
            from production_search_service_enhanced import EnhancedProductionSearchService
            from cache_manager import CacheManager
            cache = CacheManager()
            self._search_service = EnhancedProductionSearchService(self.db, cache)
        return self._search_service
    
    @property
    def freshness_manager(self):
        if self._freshness_manager is None:
            from data_freshness_manager import DataFreshnessManager
            from cache_manager import CacheManager
            cache = CacheManager()
            self._freshness_manager = DataFreshnessManager(self.db, cache)
        return self._freshness_manager

@app.task(base=DatabaseTask, bind=True, name='celery_tasks.update_stale_vehicles')
def update_stale_vehicles(self, batch_size: int = 50) -> Dict[str, Any]:
    """Update stale vehicle data"""
    logger.info(f"Starting stale vehicle update task (batch_size={batch_size})")
    
    results = {
        'started_at': datetime.utcnow().isoformat(),
        'batch_size': batch_size,
        'updated': 0,
        'failed': 0,
        'errors': []
    }
    
    try:
        # Get batch of stale vehicles
        batch = self.freshness_manager.create_update_batch(
            batch_size=batch_size,
            strategy='hybrid'
        )
        
        logger.info(f"Processing {len(batch)} stale vehicles")
        
        # Group by source for efficient processing
        by_source = {}
        for vehicle in batch:
            source = vehicle.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(vehicle)
        
        # Process each source
        for source, vehicles in by_source.items():
            logger.info(f"Updating {len(vehicles)} vehicles from {source}")
            
            if source == 'ebay':
                updated, failed = self._update_ebay_vehicles(vehicles)
            elif source == 'carmax':
                updated, failed = self._update_carmax_vehicles(vehicles)
            elif source == 'autotrader':
                updated, failed = self._update_autotrader_vehicles(vehicles)
            else:
                updated, failed = 0, len(vehicles)
                
            results['updated'] += updated
            results['failed'] += failed
        
        results['completed_at'] = datetime.utcnow().isoformat()
        results['duration_seconds'] = (
            datetime.fromisoformat(results['completed_at']) - 
            datetime.fromisoformat(results['started_at'])
        ).total_seconds()
        
        logger.info(f"Update task completed: {results['updated']} updated, {results['failed']} failed")
        
    except Exception as e:
        logger.error(f"Error in update task: {e}")
        results['errors'].append(str(e))
        results['status'] = 'error'
    
    return results

def _update_ebay_vehicles(self, vehicles: List[Dict]) -> tuple:
    """Update vehicles from eBay"""
    from ebay_live_client import EbayLiveClient
    
    updated = 0
    failed = 0
    client = EbayLiveClient()
    
    for vehicle in vehicles:
        try:
            listing_id = vehicle.get('listing_id')
            if not listing_id:
                failed += 1
                continue
                
            # Get updated details from eBay
            details = client.get_vehicle_details(listing_id)
            
            if details:
                # Update database
                self._update_vehicle_in_db(vehicle['id'], details)
                self.freshness_manager.mark_vehicle_updated(vehicle['id'], success=True)
                updated += 1
            else:
                # Vehicle might be sold/removed
                self._mark_vehicle_inactive(vehicle['id'])
                failed += 1
                
        except Exception as e:
            logger.error(f"Error updating eBay vehicle {vehicle['id']}: {e}")
            self.freshness_manager.mark_vehicle_updated(vehicle['id'], success=False)
            failed += 1
    
    return updated, failed

def _update_carmax_vehicles(self, vehicles: List[Dict]) -> tuple:
    """Update vehicles from CarMax"""
    # Implementation would scrape CarMax for updates
    # For now, return placeholder
    return 0, len(vehicles)

def _update_autotrader_vehicles(self, vehicles: List[Dict]) -> tuple:
    """Update vehicles from AutoTrader"""
    # Implementation would scrape AutoTrader for updates
    # For now, return placeholder
    return 0, len(vehicles)

def _update_vehicle_in_db(self, vehicle_id: int, details: Dict):
    """Update vehicle details in database"""
    from sqlalchemy import text
    
    try:
        # Update relevant fields
        query = text("""
            UPDATE vehicles_v2
            SET price = :price,
                mileage = :mileage,
                title = :title,
                description = :description,
                updated_at = NOW(),
                last_seen_at = NOW()
            WHERE id = :id
        """)
        
        self.db.execute(query, {
            'id': vehicle_id,
            'price': details.get('price'),
            'mileage': details.get('mileage'),
            'title': details.get('title'),
            'description': details.get('description')
        })
        
        self.db.commit()
        
    except Exception as e:
        logger.error(f"Error updating vehicle {vehicle_id} in DB: {e}")
        self.db.rollback()

def _mark_vehicle_inactive(self, vehicle_id: int):
    """Mark vehicle as inactive (sold/removed)"""
    from sqlalchemy import text
    
    try:
        query = text("""
            UPDATE vehicles_v2
            SET is_active = false,
                updated_at = NOW()
            WHERE id = :id
        """)
        
        self.db.execute(query, {'id': vehicle_id})
        self.db.commit()
        
    except Exception as e:
        logger.error(f"Error marking vehicle {vehicle_id} inactive: {e}")
        self.db.rollback()

@app.task(base=DatabaseTask, bind=True, name='celery_tasks.refresh_popular_vehicles')
def refresh_popular_vehicles(self, top_n: int = 20) -> Dict[str, Any]:
    """Refresh most popular/frequently accessed vehicles"""
    logger.info(f"Starting popular vehicle refresh (top_n={top_n})")
    
    results = {
        'started_at': datetime.utcnow().isoformat(),
        'refreshed': 0,
        'failed': 0
    }
    
    try:
        # Get popular vehicles from cache access patterns
        # This would analyze cache access logs
        # For now, get recently viewed vehicles
        
        from sqlalchemy import text
        query = text("""
            SELECT DISTINCT id, listing_id, source
            FROM vehicles_v2
            WHERE is_active = true
                AND last_seen_at > NOW() - INTERVAL '1 hour'
            ORDER BY updated_at DESC
            LIMIT :limit
        """)
        
        popular = self.db.execute(query, {'limit': top_n}).fetchall()
        
        for vehicle in popular:
            try:
                # Trigger update for this vehicle
                update_single_vehicle.delay(vehicle.id)
                results['refreshed'] += 1
            except Exception as e:
                logger.error(f"Error queueing refresh for vehicle {vehicle.id}: {e}")
                results['failed'] += 1
        
        results['completed_at'] = datetime.utcnow().isoformat()
        
    except Exception as e:
        logger.error(f"Error in popular vehicle refresh: {e}")
        results['error'] = str(e)
    
    return results

@app.task(base=DatabaseTask, bind=True, name='celery_tasks.update_single_vehicle')
def update_single_vehicle(self, vehicle_id: int) -> Dict[str, Any]:
    """Update a single vehicle"""
    logger.info(f"Updating single vehicle: {vehicle_id}")
    
    try:
        # Get vehicle details
        from sqlalchemy import text
        query = text("""
            SELECT id, listing_id, source
            FROM vehicles_v2
            WHERE id = :id
        """)
        
        vehicle = self.db.execute(query, {'id': vehicle_id}).fetchone()
        
        if not vehicle:
            return {'status': 'not_found', 'vehicle_id': vehicle_id}
        
        # Update based on source
        vehicle_dict = {
            'id': vehicle.id,
            'listing_id': vehicle.listing_id,
            'source': vehicle.source
        }
        
        if vehicle.source == 'ebay':
            updated, _ = self._update_ebay_vehicles([vehicle_dict])
        else:
            updated = 0
        
        return {
            'status': 'success' if updated else 'failed',
            'vehicle_id': vehicle_id,
            'updated': updated > 0
        }
        
    except Exception as e:
        logger.error(f"Error updating vehicle {vehicle_id}: {e}")
        return {
            'status': 'error',
            'vehicle_id': vehicle_id,
            'error': str(e)
        }

@app.task(base=DatabaseTask, bind=True, name='celery_tasks.cleanup_expired_data')
def cleanup_expired_data(self, days_to_keep: int = 30) -> Dict[str, Any]:
    """Clean up old/expired data"""
    logger.info(f"Starting data cleanup (keeping last {days_to_keep} days)")
    
    results = {
        'started_at': datetime.utcnow().isoformat(),
        'deactivated_vehicles': 0,
        'deleted_searches': 0,
        'cleaned_cache_entries': 0
    }
    
    try:
        from sqlalchemy import text
        
        # Deactivate vehicles not seen in X days
        deactivate_query = text("""
            UPDATE vehicles_v2
            SET is_active = false,
                updated_at = NOW()
            WHERE is_active = true
                AND last_seen_at < NOW() - INTERVAL :days
        """)
        
        result = self.db.execute(deactivate_query, {'days': f'{days_to_keep} days'})
        results['deactivated_vehicles'] = result.rowcount
        
        # Clean old search history (if exists)
        # Clean old cache entries
        # etc.
        
        self.db.commit()
        results['completed_at'] = datetime.utcnow().isoformat()
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        self.db.rollback()
        results['error'] = str(e)
    
    return results

@app.task(base=DatabaseTask, bind=True, name='celery_tasks.generate_freshness_report')
def generate_freshness_report(self) -> Dict[str, Any]:
    """Generate data freshness report"""
    logger.info("Generating freshness report")
    
    try:
        stats = self.freshness_manager.get_update_statistics()
        
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'statistics': stats,
            'recommendations': []
        }
        
        # Add recommendations based on stats
        if stats.get('freshness_percentages', {}).get('expired', 0) > 20:
            report['recommendations'].append(
                "More than 20% of vehicles have expired data. Consider increasing update frequency."
            )
        
        if stats.get('freshness_percentages', {}).get('real_time', 0) < 10:
            report['recommendations'].append(
                "Less than 10% of vehicles have real-time data. Consider enabling more aggressive updates."
            )
        
        # Log report summary
        logger.info(f"Freshness Report: {stats.get('freshness_percentages', {})}")
        
        # Could send this report via email, Slack, etc.
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating freshness report: {e}")
        return {'error': str(e)}

# Worker entrypoint
if __name__ == '__main__':
    app.start()