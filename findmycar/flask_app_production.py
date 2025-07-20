#!/usr/bin/env python3
"""
Production Flask application with live data integration
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from database_v2_sqlite import get_database_url, init_db
from production_search_service_v3 import EnhancedProductionSearchService as ProductionSearchService
from cache_manager import CacheManager
from comprehensive_health_monitor import ComprehensiveHealthMonitor, health_monitor as comprehensive_monitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Sentry for error tracking (if configured)
if os.environ.get('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN'),
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.1,
        environment=os.environ.get('ENVIRONMENT', 'production')
    )

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Enable CORS with specific origins
CORS(app, origins=os.environ.get('ALLOWED_ORIGINS', 'http://localhost:*').split(','))

# Rate limiting (only if Redis available)
limiter = None
try:
    import redis
    r = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))
    r.ping()
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.environ.get('REDIS_URL', 'redis://localhost:6379')
    )
    logger.info("Rate limiting enabled with Redis")
except Exception as e:
    logger.warning(f"Rate limiting disabled: {e}")
    # Create a dummy limiter that doesn't do anything
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
    limiter = DummyLimiter()

# Database setup
engine = create_engine(
    get_database_url(),
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
SessionLocal = sessionmaker(bind=engine)

# Initialize services
cache_manager = CacheManager()
# Use the comprehensive health monitor
health_monitor = comprehensive_monitor

# Request context management
@app.before_request
def before_request():
    """Set up request context"""
    request.start_time = datetime.utcnow()
    request.request_id = os.urandom(16).hex()
    request.endpoint_name = request.endpoint or 'unknown'

@app.after_request
def after_request(response):
    """Log request metrics and track performance"""
    if hasattr(request, 'start_time'):
        duration = (datetime.utcnow() - request.start_time).total_seconds()
        logger.info(f"Request {request.request_id} completed in {duration:.3f}s")
        
        # Record metrics for monitoring
        if hasattr(request, 'endpoint_name') and request.endpoint_name != 'static':
            health_monitor.metrics.record_response_time(request.endpoint_name, duration)
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response

@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler with metrics tracking"""
    logger.error(f"Unhandled error: {error}", exc_info=True)
    
    # Record error for monitoring
    health_monitor.metrics.record_error(type(error).__name__, str(error))
    
    # Don't expose internal errors in production
    if app.config.get('DEBUG'):
        return jsonify({
            'success': False,
            'error': str(error),
            'type': type(error).__name__
        }), 500
    else:
        return jsonify({
            'success': False,
            'error': 'An internal error occurred',
            'request_id': getattr(request, 'request_id', None)
        }), 500

@app.route('/search')
def search_page():
    """Search results page with filters"""
    query = request.args.get('q', '')
    return render_template('search_results.html', query=query)

@app.route('/')
def index():
    """Home page with search interface"""
    db = SessionLocal()
    try:
        # Get system stats for display
        # Track database query performance
        import time
        start_time = time.time()
        total_vehicles = cache_manager.get_or_set(
            'stats:total_vehicles',
            lambda: db.execute(text("SELECT COUNT(*) FROM vehicles_v2")).scalar(),
            ttl=300
        )
        query_duration = time.time() - start_time
        health_monitor.metrics.record_db_query('count', query_duration)
        
        stats = {
            'total_vehicles': total_vehicles,
            'data_sources': ['eBay Motors', 'CarMax', 'AutoTrader'],  # Active sources
            'last_update': cache_manager.get('stats:last_update') or 'Never'
        }
        
        # Define search presets
        presets = [
            {
                'id': 'family_suv',
                'name': 'Family SUV',
                'description': 'Spacious SUVs perfect for families',
                'icon': '👨‍👩‍👧‍👦'
            },
            {
                'id': 'fuel_efficient',
                'name': 'Fuel Efficient',
                'description': 'Economy cars with great MPG',
                'icon': '⛽'
            },
            {
                'id': 'luxury_sedan',
                'name': 'Luxury Sedan',
                'description': 'Premium sedans with luxury features',
                'icon': '💎'
            },
            {
                'id': 'first_car',
                'name': 'First Car',
                'description': 'Reliable and affordable starter cars',
                'icon': '🎓'
            },
            {
                'id': 'off_road',
                'name': 'Off-Road',
                'description': '4WD vehicles for adventure',
                'icon': '⛰️'
            },
            {
                'id': 'electric',
                'name': 'Electric',
                'description': 'Zero-emission electric vehicles',
                'icon': '🔋'
            }
        ]
        
        # Use modern landing page
        return render_template('modern_landing.html', stats=stats, presets=presets)
    finally:
        db.close()

@app.route('/api/search/v2', methods=['GET', 'POST'])
@limiter.limit("30 per minute")
def search_v2():
    """Production search endpoint with live data"""
    db = SessionLocal()
    try:
        # Parse request data
        if request.method == 'POST':
            data = request.get_json() or request.form.to_dict()
        else:
            data = request.args.to_dict()
        
        # Extract parameters
        query = data.get('query', '').strip()
        preset = data.get('preset')
        sort_by = data.get('sort_by', 'relevance')
        page = int(data.get('page', 1))
        per_page = min(int(data.get('per_page', 20)), 100)  # Max 100 per page
        include_live = data.get('include_live', 'true').lower() == 'true'
        
        # Build filters
        filters = {}
        
        # String filters
        for field in ['make', 'model', 'body_style', 'fuel_type', 'transmission', 'drivetrain']:
            if data.get(field):
                filters[field] = data.get(field).strip()
        
        # Numeric filters
        for field in ['year_min', 'year_max', 'price_min', 'price_max', 'mileage_min', 'mileage_max']:
            if data.get(field):
                try:
                    filters[field] = float(data.get(field)) if 'price' in field else int(data.get(field))
                except ValueError:
                    pass
        
        # List filters
        for field in ['exterior_color', 'required_features']:
            if data.get(field):
                filters[field] = [x.strip() for x in data.get(field).split(',') if x.strip()]
        
        # Create cache key for results
        cache_key = cache_manager.create_key('search', {
            'query': query,
            'filters': filters,
            'preset': preset,
            'sort_by': sort_by,
            'page': page,
            'per_page': per_page,
            'include_live': include_live
        })
        
        # Check cache first
        cached_results = cache_manager.get(cache_key)
        if cached_results and not include_live:  # Only use cache for non-live searches
            cached_results['cached'] = True
            health_monitor.metrics.record_cache_hit()
            return jsonify(cached_results)
        else:
            health_monitor.metrics.record_cache_miss()
        
        # Perform search
        search_service = ProductionSearchService(db)
        results = search_service.search(
            query=query,
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        # Convert vehicles to JSON-safe format
        vehicles_data = []
        for vehicle in results['vehicles']:
            # Handle both dict and SQLAlchemy objects
            if isinstance(vehicle, dict):
                vehicle_dict = vehicle
            else:
                vehicle_dict = {
                    'id': vehicle.id,
                    'listing_id': vehicle.listing_id,
                    'source': vehicle.source,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'year': vehicle.year,
                    'price': vehicle.price,
                    'mileage': vehicle.mileage,
                    'body_style': vehicle.body_style,
                    'exterior_color': vehicle.exterior_color,
                    'location': vehicle.location,
                    'title': vehicle.title,
                    'view_item_url': vehicle.view_item_url,
                    'image_urls': vehicle.image_urls or [],
                    'created_at': vehicle.created_at.isoformat() if hasattr(vehicle.created_at, 'isoformat') else vehicle.created_at
                }
            
            # Ensure all values are JSON serializable
            for key, value in vehicle_dict.items():
                if hasattr(value, 'isoformat'):
                    vehicle_dict[key] = value.isoformat()
            
            vehicles_data.append(vehicle_dict)
        
        response_data = {
            'success': True,
            'vehicles': vehicles_data,
            'total': results['total'],
            'page': results['page'],
            'per_page': results['per_page'],
            'pages': results.get('pages', (results.get('total', 0) + per_page - 1) // per_page),
            'sources_used': results.get('sources_used', ['local']),
            'sources_searched': results.get('sources_searched', []),
            'sources_failed': results.get('sources_failed', []),
            'local_count': results.get('local_count', 0),
            'live_count': results.get('live_count', 0),
            'search_time': results.get('search_time', 0),
            'applied_filters': filters,
            'cached': False
        }
        
        # Cache the results
        cache_manager.set(cache_key, response_data, ttl=300)  # 5 minutes
        
        # Update stats
        cache_manager.set('stats:last_update', datetime.utcnow().isoformat())
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Search failed',
            'request_id': getattr(request, 'request_id', None)
        }), 500
    finally:
        db.close()

@app.route('/api/vehicle/<int:vehicle_id>')
@limiter.limit("60 per minute")
def get_vehicle_details(vehicle_id):
    """Get detailed vehicle information with live data"""
    db = SessionLocal()
    try:
        fetch_live = request.args.get('fetch_live', 'true').lower() == 'true'
        
        search_service = ProductionSearchService(db)
        vehicle_data = search_service.get_vehicle_details(vehicle_id, fetch_live=fetch_live)
        
        if not vehicle_data:
            return jsonify({
                'success': False,
                'error': 'Vehicle not found'
            }), 404
        
        return jsonify({
            'success': True,
            'vehicle': vehicle_data
        })
        
    except Exception as e:
        logger.error(f"Error getting vehicle details: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to get vehicle details'
        }), 500
    finally:
        db.close()

@app.route('/health')
def health_check():
    """Basic health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'findmycar-production',
        'timestamp': datetime.utcnow().isoformat(),
        'version': os.environ.get('APP_VERSION', '1.0.0')
    })

@app.route('/health/detailed')
def health_check_detailed():
    """Detailed health check with component status"""
    db = SessionLocal()
    try:
        health_status = health_monitor.get_detailed_status(db)
        
        # Determine overall status
        if all(component['status'] == 'healthy' for component in health_status['components']):
            status_code = 200
        elif any(component['status'] == 'unhealthy' for component in health_status['components']):
            status_code = 503
        else:
            status_code = 200
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503
    finally:
        db.close()

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint with comprehensive monitoring data"""
    try:
        # Get Prometheus formatted metrics from health monitor
        prometheus_metrics = health_monitor.get_prometheus_metrics()
        
        # Add database metrics
        db = SessionLocal()
        try:
            total_vehicles = db.execute(text("SELECT COUNT(*) FROM vehicles_v2")).scalar()
            active_vehicles = db.execute(text("SELECT COUNT(*) FROM vehicles_v2 WHERE is_active = 1")).scalar()
            
            # Append database metrics to the output
            prometheus_metrics += f'\n\n# HELP database_total_vehicles Total vehicles in database\n'
            prometheus_metrics += f'# TYPE database_total_vehicles gauge\n'
            prometheus_metrics += f'database_total_vehicles {total_vehicles}\n'
            
            prometheus_metrics += f'\n# HELP database_active_vehicles Active vehicles in database\n'
            prometheus_metrics += f'# TYPE database_active_vehicles gauge\n'
            prometheus_metrics += f'database_active_vehicles {active_vehicles}\n'
            
        finally:
            db.close()
        
        return prometheus_metrics, 200, {'Content-Type': 'text/plain; version=0.0.4'}
        
    except Exception as e:
        logger.error(f"Metrics error: {e}", exc_info=True)
        return 'Error generating metrics', 500

@app.route('/api/featured-vehicles', methods=['GET'])
def get_featured_vehicles():
    """Get featured vehicles for the landing page"""
    db = SessionLocal()
    try:
        # Get a mix of popular vehicles from different categories
        featured_query = text("""
            SELECT DISTINCT ON (make, body_style) 
                id, listing_id, source, make, model, year, price, mileage,
                body_style, location, title, view_item_url, image_urls
            FROM vehicles_v2
            WHERE is_active = true 
                AND price IS NOT NULL 
                AND price < 50000
                AND mileage IS NOT NULL
                AND image_urls IS NOT NULL
                AND json_array_length(image_urls) > 0
            ORDER BY make, body_style, updated_at DESC
            LIMIT 8
        """)
        
        results = db.execute(featured_query)
        vehicles = []
        
        for row in results:
            vehicle = {
                'id': row.id,
                'listing_id': row.listing_id,
                'source': row.source,
                'make': row.make,
                'model': row.model,
                'year': row.year,
                'price': float(row.price) if row.price else None,
                'mileage': int(row.mileage) if row.mileage else None,
                'body_style': row.body_style,
                'location': row.location,
                'title': row.title or f"{row.year} {row.make} {row.model}",
                'view_item_url': row.view_item_url,
                'image_urls': row.image_urls or []
            }
            vehicles.append(vehicle)
        
        return jsonify({
            'success': True,
            'vehicles': vehicles
        })
        
    except Exception as e:
        logger.error(f"Error getting featured vehicles: {e}")
        # Return mock data as fallback
        mock_vehicles = [
            {
                'id': 1,
                'title': '2021 Honda CR-V EX-L',
                'make': 'Honda',
                'model': 'CR-V',
                'year': 2021,
                'price': 28995,
                'mileage': 32000,
                'location': 'Los Angeles, CA',
                'image_urls': ['https://images.unsplash.com/photo-1568844293986-8d0400bd4745?w=400&h=300&fit=crop']
            },
            {
                'id': 2,
                'title': '2020 Toyota Camry SE',
                'make': 'Toyota',
                'model': 'Camry',
                'year': 2020,
                'price': 24500,
                'mileage': 28000,
                'location': 'San Francisco, CA',
                'image_urls': ['https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=400&h=300&fit=crop']
            }
        ]
        return jsonify({
            'success': True,
            'vehicles': mock_vehicles[:4]
        })
    finally:
        db.close()

@app.route('/health/dashboard')
def health_dashboard():
    """Health monitoring dashboard with visual representation"""
    db = SessionLocal()
    try:
        # Get detailed health status
        health_status = health_monitor.get_detailed_status(db)
        
        # Get additional metrics for the dashboard
        metrics_summary = health_monitor.metrics.get_metrics_summary()
        
        # Format the data for the dashboard
        dashboard_data = {
            'status': health_status['status'],
            'timestamp': health_status['timestamp'],
            'uptime': health_status['uptime_human'],
            'components': health_status['components'],
            'metrics': {
                'response_times': {
                    'average': f"{metrics_summary['response_times']['avg']:.2f}ms" if metrics_summary['response_times']['avg'] > 0 else "N/A",
                    'p95': f"{metrics_summary['response_times']['p95']:.2f}ms" if metrics_summary['response_times']['p95'] > 0 else "N/A",
                    'p99': f"{metrics_summary['response_times']['p99']:.2f}ms" if metrics_summary['response_times']['p99'] > 0 else "N/A"
                },
                'error_rate': f"{metrics_summary['error_rate']:.2%}",
                'cache_hit_rate': f"{metrics_summary['cache_hit_rate']:.2%}",
                'api_performance': metrics_summary['api_performance'],
                'database_performance': {
                    'avg_query_time': f"{metrics_summary['database_performance']['avg_duration']*1000:.2f}ms",
                    'query_count': metrics_summary['database_performance']['query_count']
                }
            }
        }
        
        # If request accepts JSON, return JSON data
        if request.headers.get('Accept') == 'application/json':
            return jsonify(dashboard_data)
        
        # Otherwise, render HTML dashboard
        return render_template('health_dashboard.html', data=dashboard_data)
        
    except Exception as e:
        logger.error(f"Health dashboard error: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate health dashboard',
            'error': str(e)
        }), 500
    finally:
        db.close()

@app.route('/api/search/suggestions')
@limiter.limit("60 per minute")
def search_suggestions():
    """Get search suggestions"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify({'suggestions': []})
    
    # In production, this would use a proper suggestion engine
    # For now, return common makes/models that match
    suggestions = []
    
    makes = ['Honda', 'Toyota', 'Ford', 'Chevrolet', 'Nissan', 'BMW', 'Mercedes-Benz', 
             'Audi', 'Volkswagen', 'Mazda', 'Subaru', 'Hyundai', 'Kia', 'Tesla']
    
    for make in makes:
        if query.lower() in make.lower():
            suggestions.append({
                'type': 'make',
                'value': make,
                'display': f"{make} (Make)"
            })
    
    # Add popular models if make is specified
    if any(make.lower() in query.lower() for make in ['honda', 'toyota', 'ford']):
        models = {
            'honda': ['Civic', 'Accord', 'CR-V', 'Pilot'],
            'toyota': ['Camry', 'Corolla', 'RAV4', 'Highlander'],
            'ford': ['F-150', 'Mustang', 'Explorer', 'Escape']
        }
        
        for make, model_list in models.items():
            if make in query.lower():
                for model in model_list:
                    suggestions.append({
                        'type': 'model',
                        'value': f"{make.title()} {model}",
                        'display': f"{make.title()} {model}"
                    })
    
    return jsonify({
        'suggestions': suggestions[:10]  # Limit to 10 suggestions
    })

@app.route('/sources')
def source_management():
    """Source management UI"""
    return render_template('source_management.html')

@app.route('/api/sources/stats')
def get_source_stats():
    """Get source statistics"""
    db = SessionLocal()
    try:
        search_service = ProductionSearchService(db)
        stats = search_service.get_source_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting source stats: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/sources/<source_name>/toggle', methods=['POST'])
def toggle_source(source_name):
    """Enable or disable a source"""
    db = SessionLocal()
    try:
        data = request.get_json()
        enabled = data.get('enabled', False)
        
        search_service = ProductionSearchService(db)
        
        if enabled:
            search_service.source_manager.enable_source(source_name)
        else:
            search_service.source_manager.disable_source(source_name)
        
        return jsonify({'success': True, 'source': source_name, 'enabled': enabled})
    except Exception as e:
        logger.error(f"Error toggling source {source_name}: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/sources/health-check', methods=['POST'])
def run_health_check():
    """Run health check on all sources"""
    db = SessionLocal()
    try:
        search_service = ProductionSearchService(db)
        health_status = search_service.source_manager.check_all_sources_health()
        
        return jsonify({
            'success': True,
            'health_status': health_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error running health check: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

if __name__ == '__main__':
    # Production server should use gunicorn or similar
    # This is just for development
    port = int(os.environ.get('PORT', 8603))
    debug = os.environ.get('ENVIRONMENT') != 'production'
    
    if not debug:
        logger.warning("Running Flask development server in production mode is not recommended!")
    
    app.run(host='0.0.0.0', port=port, debug=debug)