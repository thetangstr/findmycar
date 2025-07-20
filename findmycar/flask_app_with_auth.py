#!/usr/bin/env python3
"""
Flask app with API authentication integrated
Example of how to secure endpoints
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from api_authentication import (
    require_api_key, 
    require_jwt_token, 
    optional_auth,
    AuthenticationManager,
    APIUser
)
from database_v2_sqlite import get_session, init_db
from production_search_service_enhanced import EnhancedProductionSearchService
from cache_manager import CacheManager

app = Flask(__name__)
CORS(app)

# Initialize cache manager
cache_manager = CacheManager()
app.cache_manager = cache_manager

# Public endpoints (no auth required)
@app.route('/api/public/search', methods=['GET'])
def public_search():
    """Public search endpoint with limited results"""
    db = get_session()
    search_service = EnhancedProductionSearchService(db, cache_manager)
    
    try:
        results = search_service.search(
            query=request.args.get('q'),
            page=1,
            per_page=10,  # Limited results for public
            include_live=False  # Local only for public
        )
        
        return jsonify({
            'success': True,
            'results': results['vehicles'][:5],  # Max 5 for public
            'total': min(results['total'], 5),
            'message': 'Sign up for API access to see all results'
        })
        
    finally:
        db.close()

# Authenticated endpoints
@app.route('/api/v1/search', methods=['GET'])
@require_api_key(scopes=['read'])
def authenticated_search():
    """Authenticated search with full results"""
    db = get_session()
    search_service = EnhancedProductionSearchService(db, cache_manager)
    
    try:
        # Get user from request context
        user = request.api_user
        
        # Determine limits based on user tier
        per_page = min(int(request.args.get('per_page', 20)), 100)
        if not user.is_admin:
            per_page = min(per_page, 50)  # Regular users limited to 50
        
        results = search_service.search(
            query=request.args.get('q'),
            filters={
                'make': request.args.get('make'),
                'model': request.args.get('model'),
                'year_min': request.args.get('year_min', type=int),
                'year_max': request.args.get('year_max', type=int),
                'price_min': request.args.get('price_min', type=float),
                'price_max': request.args.get('price_max', type=float),
            },
            page=int(request.args.get('page', 1)),
            per_page=per_page,
            include_live=True,  # Full access to live data
            user_id=str(user.id)
        )
        
        return jsonify({
            'success': True,
            **results,
            'user': user.username,
            'rate_limit': {
                'limit': user.rate_limit_per_hour,
                'remaining': user.rate_limit_per_hour - request.api_user.total_requests % user.rate_limit_per_hour
            }
        })
        
    finally:
        db.close()

@app.route('/api/v1/vehicle/<int:vehicle_id>', methods=['GET'])
@require_api_key(scopes=['read'])
def get_vehicle_details(vehicle_id):
    """Get detailed vehicle information"""
    db = get_session()
    search_service = EnhancedProductionSearchService(db, cache_manager)
    
    try:
        details = search_service.get_vehicle_details_safe(
            vehicle_id, 
            fetch_live=request.args.get('refresh', 'false').lower() == 'true'
        )
        
        if details:
            return jsonify({
                'success': True,
                'vehicle': details
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Vehicle not found'
            }), 404
            
    finally:
        db.close()

# Authentication endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new API user"""
    data = request.json
    
    if not all(k in data for k in ['email', 'username', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    db = get_session()
    auth_manager = AuthenticationManager(db, cache_manager)
    
    try:
        user = auth_manager.create_user(
            email=data['email'],
            username=data['username'],
            password=data['password']
        )
        
        return jsonify({
            'success': True,
            'user_id': user.id,
            'api_key': user.api_key,
            'message': 'Save your API key securely. It cannot be retrieved later.'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500
    finally:
        db.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login to get JWT token"""
    data = request.json
    
    if not all(k in data for k in ['username', 'password']):
        return jsonify({'error': 'Missing credentials'}), 400
    
    db = get_session()
    auth_manager = AuthenticationManager(db, cache_manager)
    
    try:
        user = auth_manager.authenticate_user(
            data['username'],
            data['password']
        )
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = auth_manager.create_access_token(user.id)
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': 1800  # 30 minutes
        })
        
    finally:
        db.close()

@app.route('/api/auth/refresh-api-key', methods=['POST'])
@require_jwt_token()
def refresh_api_key():
    """Generate new API key (requires JWT auth)"""
    user = request.api_user
    
    db = get_session()
    auth_manager = AuthenticationManager(db, cache_manager)
    
    try:
        # Generate new API key
        new_key = auth_manager.generate_api_key()
        user.api_key = new_key
        user.api_key_created_at = datetime.utcnow()
        db.commit()
        
        return jsonify({
            'success': True,
            'api_key': new_key,
            'message': 'API key refreshed. Previous key is now invalid.'
        })
        
    finally:
        db.close()

# Admin endpoints
@app.route('/api/admin/users', methods=['GET'])
@require_api_key(scopes=['admin'])
def list_users():
    """List all users (admin only)"""
    user = request.api_user
    
    if not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    db = get_session()
    
    try:
        users = db.query(APIUser).all()
        
        return jsonify({
            'success': True,
            'users': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'is_active': u.is_active,
                'total_requests': u.total_requests,
                'last_request': u.last_request_at.isoformat() if u.last_request_at else None,
                'created_at': u.created_at.isoformat()
            } for u in users]
        })
        
    finally:
        db.close()

@app.route('/api/usage', methods=['GET'])
@optional_auth()
def get_usage():
    """Get API usage statistics"""
    if request.api_user:
        # Authenticated user - show their usage
        user = request.api_user
        return jsonify({
            'authenticated': True,
            'username': user.username,
            'total_requests': user.total_requests,
            'monthly_usage': user.monthly_usage,
            'rate_limits': {
                'per_minute': user.rate_limit_per_minute,
                'per_hour': user.rate_limit_per_hour
            }
        })
    else:
        # Public user - show general info
        return jsonify({
            'authenticated': False,
            'message': 'Sign up for API access',
            'public_limits': {
                'results_per_search': 5,
                'searches_per_day': 10
            },
            'pricing_tiers': {
                'free': {
                    'price': 0,
                    'requests_per_hour': 100,
                    'results_per_search': 20
                },
                'pro': {
                    'price': 49,
                    'requests_per_hour': 1000,
                    'results_per_search': 100,
                    'live_data': True
                },
                'enterprise': {
                    'price': 'Contact us',
                    'requests_per_hour': 'Unlimited',
                    'results_per_search': 'Unlimited',
                    'live_data': True,
                    'priority_support': True
                }
            }
        })

# Error handlers
@app.errorhandler(401)
def unauthorized(e):
    return jsonify({'error': 'Unauthorized', 'message': 'Valid API key required'}), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({'error': 'Too Many Requests', 'message': 'Rate limit exceeded'}), 429

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Create demo user if in development
    if os.getenv('FLASK_ENV') == 'development':
        db = get_session()
        auth_manager = AuthenticationManager(db)
        
        try:
            # Check if demo user exists
            demo_user = db.query(APIUser).filter(APIUser.username == 'demo').first()
            if not demo_user:
                demo_user = auth_manager.create_user(
                    email='demo@example.com',
                    username='demo',
                    password='demo123',
                    is_admin=False
                )
                print(f"Demo user created with API key: {demo_user.api_key}")
        except Exception as e:
            print(f"Could not create demo user: {e}")
        finally:
            db.close()
    
    # Run app
    app.run(debug=True, port=8604)
    
from datetime import datetime