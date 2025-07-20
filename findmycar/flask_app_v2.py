#!/usr/bin/env python3
"""
Enhanced Flask application with comprehensive search support
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_v2_sqlite import get_database_url, init_db
from comprehensive_search_engine_sqlite import ComprehensiveSearchEngine
from ebay_enhanced_extractor import EbayEnhancedExtractor
# from ebay_client import EbayClient  # Not needed for now

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Enable CORS
CORS(app, origins=['http://localhost:*', 'http://127.0.0.1:*'])

# Database setup
from database_v2_sqlite import get_engine
engine = get_engine()
SessionLocal = sessionmaker(bind=engine)

# Initialize components
ebay_extractor = EbayEnhancedExtractor()
# ebay_client = EbayClient()  # Not needed for now


@app.route('/')
def index():
    """Home page with comprehensive search interface"""
    db = SessionLocal()
    try:
        search_engine = ComprehensiveSearchEngine(db)
        
        # Get smart presets for UI
        presets = [
            {
                'id': key,
                'name': key.replace('_', ' ').title(),
                'description': value['description']
            }
            for key, value in search_engine.smart_presets.items()
        ]
        
        # Get popular searches
        popular_searches = search_engine.get_popular_searches(limit=5)
        
        return render_template('comprehensive_search.html',
                             presets=presets,
                             popular_searches=popular_searches)
    finally:
        db.close()


@app.route('/api/search/v2', methods=['GET', 'POST'])
def search_v2():
    """Comprehensive search API endpoint"""
    db = SessionLocal()
    try:
        search_engine = ComprehensiveSearchEngine(db)
        
        # Get parameters from either GET or POST
        if request.method == 'POST':
            data = request.get_json() or request.form.to_dict()
        else:
            data = request.args.to_dict()
        
        # Extract search parameters
        query = data.get('query')
        preset = data.get('preset')
        sort_by = data.get('sort_by', 'relevance')
        page = int(data.get('page', 1))
        per_page = int(data.get('per_page', 20))
        
        # Build filters from request
        filters = {}
        
        # Core filters
        for field in ['make', 'model', 'body_style', 'fuel_type', 'transmission', 'drivetrain']:
            if data.get(field):
                # Handle comma-separated values as lists
                value = data.get(field)
                if ',' in value:
                    filters[field] = [v.strip() for v in value.split(',')]
                else:
                    filters[field] = value
        
        # Range filters
        for field in ['year_min', 'year_max', 'price_min', 'price_max', 'mileage_min', 'mileage_max']:
            if data.get(field):
                try:
                    filters[field] = float(data.get(field)) if 'price' in field else int(data.get(field))
                except ValueError:
                    pass
        
        # Color filters
        if data.get('exterior_color'):
            filters['exterior_color'] = data.get('exterior_color').split(',')
        if data.get('exclude_colors'):
            filters['exclude_colors'] = data.get('exclude_colors').split(',')
        
        # Feature filters
        if data.get('required_features'):
            filters['required_features'] = data.get('required_features').split(',')
        
        # Attribute filters
        attributes = {}
        for attr_field in ['mpg_city_min', 'mpg_highway_min', 'mpg_combined_min', 
                          'seating_capacity_min', 'horsepower_min', 'electric_range_min']:
            if data.get(attr_field):
                try:
                    attributes[attr_field] = int(data.get(attr_field))
                except ValueError:
                    pass
        
        if attributes:
            filters['attributes'] = attributes
        
        # Boolean filters
        for bool_field in ['clean_title_only', 'no_accidents', 'one_owner_only', 'certified_only']:
            if data.get(bool_field) in ['true', 'True', '1', 'on']:
                filters[bool_field] = True
        
        # User tracking (from session or parameter)
        user_id = data.get('user_id') or session.get('user_id')
        
        # Save search option
        save_search = data.get('save_search') == 'true'
        search_name = data.get('search_name')
        
        # Perform search
        results = search_engine.search(
            query=query,
            filters=filters,
            preset=preset,
            sort_by=sort_by,
            page=page,
            per_page=per_page,
            user_id=user_id,
            save_search=save_search,
            search_name=search_name
        )
        
        # Convert vehicles to JSON-serializable format
        vehicles_data = []
        for vehicle in results['vehicles']:
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
                'interior_color': vehicle.interior_color,
                'transmission': vehicle.transmission,
                'drivetrain': vehicle.drivetrain,
                'fuel_type': vehicle.fuel_type,
                'location': vehicle.location,
                'title': vehicle.title,
                'description': vehicle.description,
                'view_item_url': vehicle.view_item_url,
                'image_urls': vehicle.image_urls or [],
                'attributes': vehicle.attributes or {},
                'features': vehicle.features or [],
                'created_at': vehicle.created_at.isoformat() if vehicle.created_at else None
            }
            vehicles_data.append(vehicle_dict)
        
        return jsonify({
            'success': True,
            'vehicles': vehicles_data,
            'total': results['total'],
            'page': results['page'],
            'pages': results['pages'],
            'applied_filters': results['applied_filters'],
            'search_id': results.get('search_id'),
            'search_time': results.get('search_time')
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()


@app.route('/api/search/suggestions')
def search_suggestions():
    """Get search suggestions based on partial query"""
    db = SessionLocal()
    try:
        search_engine = ComprehensiveSearchEngine(db)
        
        query = request.args.get('q', '')
        if len(query) < 2:
            return jsonify({'suggestions': []})
        
        suggestions = search_engine.get_search_suggestions(query)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"Suggestion error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()


@app.route('/api/saved-searches')
def get_saved_searches():
    """Get user's saved searches"""
    db = SessionLocal()
    try:
        user_id = request.args.get('user_id') or session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User ID required'
            }), 400
        
        search_engine = ComprehensiveSearchEngine(db)
        saved_searches = search_engine.get_saved_searches(user_id)
        
        # Convert to JSON format
        searches_data = [
            {
                'id': s.id,
                'name': s.name,
                'search_params': s.search_params,
                'created_at': s.created_at.isoformat(),
                'last_run_at': s.last_run_at.isoformat() if s.last_run_at else None
            }
            for s in saved_searches
        ]
        
        return jsonify({
            'success': True,
            'saved_searches': searches_data
        })
        
    except Exception as e:
        logger.error(f"Error getting saved searches: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()


@app.route('/api/saved-searches/<int:search_id>/run', methods=['POST'])
def run_saved_search(search_id):
    """Run a saved search"""
    db = SessionLocal()
    try:
        user_id = request.get_json().get('user_id') or session.get('user_id')
        
        search_engine = ComprehensiveSearchEngine(db)
        results = search_engine.run_saved_search(search_id, user_id)
        
        # Format results same as regular search
        vehicles_data = [
            {
                'id': vehicle.id,
                'listing_id': vehicle.listing_id,
                'make': vehicle.make,
                'model': vehicle.model,
                'year': vehicle.year,
                'price': vehicle.price,
                'mileage': vehicle.mileage,
                'body_style': vehicle.body_style,
                'exterior_color': vehicle.exterior_color,
                'view_item_url': vehicle.view_item_url,
                'image_urls': vehicle.image_urls or []
            }
            for vehicle in results['vehicles']
        ]
        
        return jsonify({
            'success': True,
            'vehicles': vehicles_data,
            'total': results['total'],
            'page': results['page'],
            'pages': results['pages']
        })
        
    except Exception as e:
        logger.error(f"Error running saved search: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()


@app.route('/api/ingest/ebay/<listing_id>', methods=['POST'])
def ingest_ebay_listing(listing_id):
    """Ingest a single eBay listing with enhanced extraction"""
    return jsonify({
        'success': False,
        'error': 'eBay ingestion temporarily disabled'
    }), 503
    
    # TODO: Re-enable when ebay_client is properly set up
    # db = SessionLocal()
    # try:
    #     # Fetch from eBay API
    #     ebay_item = ebay_client.get_item(listing_id)
    #     if not ebay_item:
    #         return jsonify({
    #             'success': False,
    #             'error': 'Item not found'
    #         }), 404
    #     
    #     # Extract with enhanced extractor
    #     extracted_data = ebay_extractor.extract_all_data(ebay_item)
    #     
    #     # Save to database
    #     from database_v2_sqlite import VehicleV2
    #     
    #     # Check if already exists
    #     existing = db.query(VehicleV2).filter_by(
    #         listing_id=extracted_data['listing_id']
    #     ).first()
    #     
    #     if existing:
    #         # Update existing
    #         for key, value in extracted_data.items():
    #             if hasattr(existing, key):
    #                 setattr(existing, key, value)
    #         existing.updated_at = datetime.utcnow()
    #     else:
    #         # Create new
    #         vehicle = VehicleV2(**extracted_data)
    #         db.add(vehicle)
    #     
    #     db.commit()
    #     
    #     return jsonify({
    #         'success': True,
    #         'message': 'Vehicle ingested successfully',
    #         'vehicle_id': extracted_data['listing_id']
    #     })
    #     
    # except Exception as e:
    #     logger.error(f"Ingestion error: {e}")
    #     db.rollback()
    #     return jsonify({
    #         'success': False,
    #         'error': str(e)
    #     }), 500
    # finally:
    #     db.close()


@app.route('/api/vehicle/<int:vehicle_id>')
def get_vehicle_details(vehicle_id):
    """Get detailed vehicle information"""
    db = SessionLocal()
    try:
        from database_v2_sqlite import VehicleV2
        
        vehicle = db.query(VehicleV2).filter_by(id=vehicle_id).first()
        if not vehicle:
            return jsonify({
                'success': False,
                'error': 'Vehicle not found'
            }), 404
        
        # Full vehicle data
        vehicle_data = {
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
            'interior_color': vehicle.interior_color,
            'transmission': vehicle.transmission,
            'drivetrain': vehicle.drivetrain,
            'fuel_type': vehicle.fuel_type,
            'location': vehicle.location,
            'zip_code': vehicle.zip_code,
            'dealer_name': vehicle.dealer_name,
            'title': vehicle.title,
            'description': vehicle.description,
            'view_item_url': vehicle.view_item_url,
            'image_urls': vehicle.image_urls or [],
            'attributes': vehicle.attributes or {},
            'features': vehicle.features or [],
            'history': vehicle.history or {},
            'pricing_analysis': vehicle.pricing_analysis or {},
            'created_at': vehicle.created_at.isoformat() if vehicle.created_at else None,
            'updated_at': vehicle.updated_at.isoformat() if vehicle.updated_at else None
        }
        
        return jsonify({
            'success': True,
            'vehicle': vehicle_data
        })
        
    except Exception as e:
        logger.error(f"Error getting vehicle details: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'findmycar-v2',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/debug/db')
def debug_db():
    """Debug database connection"""
    db = SessionLocal()
    try:
        from database_v2_sqlite import VehicleV2
        from sqlalchemy import text
        
        # Test raw query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM vehicles_v2"))
            raw_count = result.scalar()
        
        # Test ORM
        orm_count = db.query(VehicleV2).count()
        active_count = db.query(VehicleV2).filter(VehicleV2.is_active == True).count()
        honda_count = db.query(VehicleV2).filter(VehicleV2.make == 'Honda').count()
        
        # Get sample vehicles
        vehicles = db.query(VehicleV2).limit(3).all()
        
        return jsonify({
            'raw_count': raw_count,
            'orm_count': orm_count,
            'active_count': active_count,
            'honda_count': honda_count,
            'sample_vehicles': [
                {
                    'id': v.id,
                    'make': v.make,
                    'model': v.model,
                    'year': v.year,
                    'is_active': v.is_active
                } for v in vehicles
            ],
            'db_url': str(engine.url),
            'db_file': engine.url.database if hasattr(engine.url, 'database') else None
        })
    finally:
        db.close()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8602))
    app.run(host='0.0.0.0', port=port, debug=True)