"""
Celery tasks for background processing in AutoNavigator
"""

import os
import logging
from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import Session
from database import SessionLocal
from ingestion import ingest_multi_source_data, ingest_data, ingest_carmax_data, ingest_cars_data, ingest_autodev_data, ingest_bat_data
from valuation import valuation_service
from ai_questions import question_generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery(
    "autonavigator",
    broker=redis_url,
    backend=redis_url,
    include=["tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    'daily-data-refresh': {
        'task': 'tasks.scheduled_data_refresh',
        'schedule': crontab(hour=6, minute=0),  # Run daily at 6 AM UTC
    },
    'hourly-popular-searches': {
        'task': 'tasks.refresh_popular_searches',
        'schedule': crontab(minute=0),  # Run every hour
    },
    'weekly-valuation-update': {
        'task': 'tasks.update_stale_valuations',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Sunday at 3 AM
    },
}

def get_db():
    """Get database session for tasks"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

@celery_app.task(bind=True)
def ingest_vehicles_task(self, query: str, filters=None, sources=None, limit=50):
    """
    Background task to ingest vehicle data from multiple sources
    
    Args:
        query: Search query
        filters: Optional filters dict
        sources: List of sources to search (default: ['ebay', 'carmax'])
        limit: Maximum results per source
    """
    db = None
    try:
        db = get_db()
        
        if sources is None:
            sources = ['ebay', 'carmax']
        
        logger.info(f"Starting background ingestion for query: {query}, sources: {sources}")
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'Starting ingestion', 'progress': 0}
        )
        
        total_sources = len(sources)
        results = {}
        
        for i, source in enumerate(sources):
            try:
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current_step': f'Ingesting from {source}',
                        'progress': int((i / total_sources) * 100)
                    }
                )
                
                if source == 'ebay':
                    result = ingest_data(db, query, filters)
                elif source == 'carmax':
                    result = ingest_carmax_data(db, query, filters, limit)
                elif source == 'cars.com':
                    result = ingest_cars_data(db, query, filters, limit)
                elif source == 'auto.dev':
                    result = ingest_autodev_data(db, query, filters, limit)
                elif source == 'bringatrailer':
                    result = ingest_bat_data(db, query, filters, limit)
                else:
                    logger.warning(f"Unknown source: {source}")
                    continue
                
                results[source] = result
                logger.info(f"Completed {source}: {result}")
                
            except Exception as e:
                logger.error(f"Error ingesting from {source}: {e}")
                results[source] = {
                    'success': False,
                    'error': str(e),
                    'source': source
                }
        
        # Final summary
        total_ingested = sum(r.get('ingested', 0) for r in results.values() if r.get('success'))
        total_errors = sum(r.get('errors', 0) for r in results.values() if r.get('success'))
        
        logger.info(f"Ingestion complete: {total_ingested} vehicles ingested, {total_errors} errors")
        
        return {
            'status': 'completed',
            'total_ingested': total_ingested,
            'total_errors': total_errors,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise e
    finally:
        if db:
            db.close()

@celery_app.task(bind=True)
def update_vehicle_valuations_task(self, vehicle_ids=None, batch_size=100):
    """
    Background task to update vehicle valuations
    
    Args:
        vehicle_ids: List of vehicle IDs to update (None for all)
        batch_size: Number of vehicles to process in each batch
    """
    db = None
    try:
        db = get_db()
        
        from database import Vehicle
        import datetime
        
        # Get vehicles to update
        query = db.query(Vehicle)
        if vehicle_ids:
            query = query.filter(Vehicle.id.in_(vehicle_ids))
        else:
            # Update vehicles with old or missing valuations
            one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
            query = query.filter(
                (Vehicle.last_valuation_update < one_week_ago) | 
                (Vehicle.last_valuation_update == None)
            )
        
        vehicles = query.limit(batch_size).all()
        
        self.update_state(
            state='PROGRESS',
            meta={'current_step': 'Starting valuation updates', 'total': len(vehicles), 'progress': 0}
        )
        
        updated_count = 0
        error_count = 0
        
        for i, vehicle in enumerate(vehicles):
            try:
                if vehicle.make and vehicle.model and vehicle.year and vehicle.price:
                    valuation = valuation_service.get_vehicle_valuation(
                        make=vehicle.make,
                        model=vehicle.model,
                        year=vehicle.year,
                        mileage=vehicle.mileage,
                        condition=vehicle.condition or 'good'
                    )
                    
                    if valuation.get('estimated_value'):
                        deal_rating = valuation_service.calculate_deal_rating(
                            listing_price=vehicle.price,
                            estimated_value=valuation['estimated_value'],
                            market_min=valuation['market_min'],
                            market_max=valuation['market_max']
                        )
                        
                        # Update vehicle
                        vehicle.estimated_value = valuation['estimated_value']
                        vehicle.market_min = valuation['market_min']
                        vehicle.market_max = valuation['market_max']
                        vehicle.deal_rating = deal_rating
                        vehicle.valuation_confidence = valuation['confidence']
                        vehicle.valuation_source = valuation['data_source']
                        vehicle.last_valuation_update = datetime.datetime.utcnow()
                        
                        updated_count += 1
                
                # Update progress
                if i % 10 == 0:
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current_step': f'Updated {updated_count} vehicles',
                            'total': len(vehicles),
                            'progress': int((i / len(vehicles)) * 100)
                        }
                    )
                
            except Exception as e:
                logger.error(f"Error updating valuation for vehicle {vehicle.id}: {e}")
                error_count += 1
        
        db.commit()
        
        logger.info(f"Valuation update complete: {updated_count} updated, {error_count} errors")
        
        return {
            'status': 'completed',
            'updated': updated_count,
            'errors': error_count,
            'total_processed': len(vehicles)
        }
        
    except Exception as e:
        logger.error(f"Valuation task failed: {e}")
        raise e
    finally:
        if db:
            db.close()

@celery_app.task
def scheduled_data_refresh():
    """
    Scheduled task to refresh data from all sources daily
    """
    popular_queries = [
        "Honda Civic",
        "Toyota Camry", 
        "Tesla Model 3",
        "Ford F-150",
        "BMW 3 Series",
        "Chevrolet Silverado",
        "Jeep Wrangler",
        "Subaru Outback"
    ]
    
    results = []
    for query in popular_queries:
        try:
            task = ingest_vehicles_task.delay(
                query=query,
                sources=['ebay', 'carmax', 'bringatrailer'],
                limit=25
            )
            results.append({'query': query, 'task_id': task.id})
        except Exception as e:
            logger.error(f"Failed to start ingestion for {query}: {e}")
    
    return {
        'status': 'scheduled',
        'tasks_started': len(results),
        'tasks': results
    }

@celery_app.task
def refresh_popular_searches():
    """
    Update popular search cache based on recent activity
    """
    # This would analyze search logs and update popular searches
    # For now, just return a placeholder
    return {'status': 'completed', 'updated_searches': 8}

@celery_app.task
def update_stale_valuations():
    """
    Weekly task to update valuations for vehicles with old data
    """
    task = update_vehicle_valuations_task.delay(batch_size=500)
    return {'status': 'scheduled', 'task_id': task.id}

@celery_app.task(bind=True)
def generate_ai_questions_task(self, vehicle_ids, batch_size=50):
    """
    Background task to generate AI questions for vehicles
    
    Args:
        vehicle_ids: List of vehicle IDs to process
        batch_size: Number of vehicles to process at once
    """
    db = None
    try:
        db = get_db()
        
        from database import Vehicle
        
        vehicles = db.query(Vehicle).filter(Vehicle.id.in_(vehicle_ids)).limit(batch_size).all()
        
        updated_count = 0
        error_count = 0
        
        for i, vehicle in enumerate(vehicles):
            try:
                if vehicle.make and vehicle.model and vehicle.year:
                    vehicle_context = {
                        'make': vehicle.make,
                        'model': vehicle.model,
                        'year': vehicle.year,
                        'mileage': vehicle.mileage,
                        'condition': vehicle.condition,
                        'body_style': vehicle.body_style,
                        'exterior_color': vehicle.exterior_color,
                        'location': vehicle.location,
                        'price': vehicle.price,
                        'title': vehicle.title,
                        'estimated_value': vehicle.estimated_value,
                        'deal_rating': vehicle.deal_rating
                    }
                    
                    questions = question_generator.generate_buyer_questions(vehicle_context)
                    if questions:
                        vehicle.buyer_questions = questions
                        updated_count += 1
                
                # Update progress
                if i % 10 == 0:
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current_step': f'Generated questions for {updated_count} vehicles',
                            'total': len(vehicles),
                            'progress': int((i / len(vehicles)) * 100)
                        }
                    )
                
            except Exception as e:
                logger.error(f"Error generating questions for vehicle {vehicle.id}: {e}")
                error_count += 1
        
        db.commit()
        
        return {
            'status': 'completed',
            'updated': updated_count,
            'errors': error_count,
            'total_processed': len(vehicles)
        }
        
    except Exception as e:
        logger.error(f"AI questions task failed: {e}")
        raise e
    finally:
        if db:
            db.close()

# Health check task
@celery_app.task
def health_check():
    """Simple health check task"""
    return {'status': 'healthy', 'timestamp': str(datetime.datetime.utcnow())}

if __name__ == '__main__':
    celery_app.start()