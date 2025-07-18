#!/usr/bin/env python3
"""
Stable Flask version of the car search application.
More stable than FastAPI for this use case.
"""

import os
import logging
from flask import Flask, request, render_template, redirect, url_for, flash, make_response
from sqlalchemy.orm import Session
from database import SessionLocal, Vehicle
from nlp_search import parse_natural_language_query, enhance_query_with_use_case
from ingestion import ingest_data
from urllib.parse import quote
import uuid
import crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app with static files support
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, close in routes

@app.route('/')
def index():
    """Homepage with search form and results."""
    db = get_db()
    try:
        # Get query parameters
        message = request.args.get('message')
        error = request.args.get('error')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        sort = request.args.get('sort', 'newest')
        
        # Search filter parameters
        make = request.args.get('make')
        model = request.args.get('model')
        year_min = request.args.get('year_min', type=int)
        year_max = request.args.get('year_max', type=int)
        price_min = request.args.get('price_min', type=int)
        price_max = request.args.get('price_max', type=int)
        body_style = request.args.get('body_style')
        exterior_color = request.args.get('exterior_color')
        transmission = request.args.get('transmission')
        fuel_type = request.args.get('fuel_type')
        drivetrain = request.args.get('drivetrain')
        trim = request.args.get('trim')
        # Handle exclude_colors as comma-separated list
        exclude_colors_param = request.args.get('exclude_colors', '')
        exclude_colors = [c.strip() for c in exclude_colors_param.split(',') if c.strip()] if exclude_colors_param else []
        
        # Build search filters
        filters = {}
        if make:
            filters['make'] = make
        if model:
            filters['model'] = model
        if year_min:
            filters['year_min'] = year_min
        if year_max:
            filters['year_max'] = year_max
        if price_min:
            filters['price_min'] = price_min
        if price_max:
            filters['price_max'] = price_max
        if body_style:
            filters['body_style'] = body_style
        if exterior_color:
            filters['exterior_color'] = exterior_color
        if transmission:
            filters['transmission'] = transmission
        if fuel_type:
            filters['fuel_type'] = fuel_type
        if drivetrain:
            filters['drivetrain'] = drivetrain
        if trim:
            filters['trim'] = trim
        if exclude_colors:
            filters['exclude_colors'] = exclude_colors
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get total count (with filters if any)
        total_vehicles = crud.get_vehicle_count(db, filters=filters if filters else None)
        
        # Get paginated vehicles (with filters if any)
        vehicles = crud.get_vehicles(db, skip=offset, limit=per_page, sort_by=sort, filters=filters if filters else None)
        
        # Calculate pagination info
        total_pages = (total_vehicles + per_page - 1) // per_page
        
        return render_template('flask_index.html', 
                             vehicles=vehicles,
                             message=message,
                             error=error,
                             page=page,
                             per_page=per_page,
                             total_pages=total_pages,
                             total_vehicles=total_vehicles,
                             sort=sort)
    
    finally:
        db.close()

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests."""
    db = get_db()
    try:
        # Get form data
        query = request.form.get('query', '')
        make = request.form.get('make')
        model = request.form.get('model')
        year_min = request.form.get('year_min', type=int)
        year_max = request.form.get('year_max', type=int)
        price_min = request.form.get('price_min', type=int)
        price_max = request.form.get('price_max', type=int)
        max_mileage = request.form.get('max_mileage', type=int)
        use_fast_search = request.form.get('use_fast_search') == 'on'
        
        logger.info(f"🔍 Search request: {query} (fast={use_fast_search})")
        
        # Parse natural language query
        nlp_filters = parse_natural_language_query(query)
        logger.info(f"📊 NLP results: {nlp_filters}")
        logger.info(f"🎨 Exclude colors: {nlp_filters.get('exclude_colors', [])}")
        
        # Build filters (same logic as FastAPI version)
        filters = {}
        has_chassis_code = nlp_filters.get('chassis_code') is not None
        
        filters['make'] = make or nlp_filters.get('make')
        filters['model'] = model or nlp_filters.get('model')
        
        # Handle year filters
        if has_chassis_code and nlp_filters.get('year_min'):
            if year_min == 2000 and year_max == 2024:
                filters['year_min'] = nlp_filters.get('year_min')
                filters['year_max'] = nlp_filters.get('year_max')
            else:
                filters['year_min'] = year_min or nlp_filters.get('year_min')
                filters['year_max'] = year_max or nlp_filters.get('year_max')
        else:
            filters['year_min'] = year_min or nlp_filters.get('year_min')
            filters['year_max'] = year_max or nlp_filters.get('year_max')
        
        # Handle price filters
        query_lower = query.lower()
        has_price_terms = any(term in query_lower for term in ['$', 'price', 'cost', 'under', 'over', 'below', 'above', 'cheap', 'expensive', 'budget', 'max', 'maximum', 'min', 'minimum'])
        
        if has_price_terms:
            filters['price_min'] = nlp_filters.get('price_min')
            filters['price_max'] = nlp_filters.get('price_max')
        else:
            filters['price_min'] = price_min if price_min and price_min != 5000 else None
            filters['price_max'] = price_max if price_max and price_max != 100000 else None
        
        # Handle mileage filters
        has_mileage_terms = any(term in query_lower for term in ['miles', 'mileage', 'high mileage', 'low mileage', 'km', 'kilometers'])
        
        if has_mileage_terms:
            filters['mileage_min'] = nlp_filters.get('mileage_min')
            filters['mileage_max'] = nlp_filters.get('mileage_max')
        else:
            filters['mileage_max'] = max_mileage if max_mileage else None
        
        # Handle all additional filters from NLP
        if nlp_filters.get('body_style'):
            filters['body_style'] = nlp_filters.get('body_style')
        if nlp_filters.get('exterior_color'):
            filters['exterior_color'] = nlp_filters.get('exterior_color')
        if nlp_filters.get('exclude_colors'):
            filters['exclude_colors'] = nlp_filters.get('exclude_colors')
        if nlp_filters.get('transmission'):
            filters['transmission'] = nlp_filters.get('transmission')
        if nlp_filters.get('fuel_type'):
            filters['fuel_type'] = nlp_filters.get('fuel_type')
        if nlp_filters.get('drivetrain'):
            filters['drivetrain'] = nlp_filters.get('drivetrain')
        if nlp_filters.get('trim'):
            filters['trim'] = nlp_filters.get('trim')
        
        # Use enhanced query
        cleaned_query = nlp_filters.get('cleaned_query', query)
        enhanced_query = enhance_query_with_use_case(cleaned_query, nlp_filters.get('use_case'))
        
        # Remove None values and empty lists from filters
        filters = {k: v for k, v in filters.items() if v is not None and (not isinstance(v, list) or v)}
        
        # Perform search (eBay only for speed and stability)
        logger.info(f"🚀 Starting search with query: {enhanced_query}")
        logger.info(f"📊 Filters: {filters}")
        
        try:
            # Use threading timeout instead of signal (works in Flask)
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
            
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(ingest_data, db, enhanced_query, filters if filters else None)
                try:
                    result = future.result(timeout=15)  # 15 second timeout
                    logger.info(f"✅ Search completed: {result}")
                except FutureTimeoutError:
                    logger.error("⏱️ Search timed out")
                    return redirect("/?error=Search timed out after 15 seconds")
            
            if result['success']:
                total_found = result.get('total_found', result.get('total_available', 0))
                search_type = "⚡ Fast" if use_fast_search else "🔍 Standard"
                message = f"{search_type} search: Found {total_found} vehicles, saved {result['ingested']} new vehicles from eBay"
                
                if result['skipped'] > 0:
                    message += f" ({result['skipped']} duplicates/filtered out)"
                if result['errors'] > 0:
                    message += f" ({result['errors']} errors)"
                
                # Build redirect URL with filters
                redirect_params = [f"message={quote(message)}"]
                if filters.get('make'):
                    redirect_params.append(f"make={quote(str(filters['make']))}")
                if filters.get('model'):
                    redirect_params.append(f"model={quote(str(filters['model']))}")
                if filters.get('year_min'):
                    redirect_params.append(f"year_min={filters['year_min']}")
                if filters.get('year_max'):
                    redirect_params.append(f"year_max={filters['year_max']}")
                if filters.get('price_min'):
                    redirect_params.append(f"price_min={filters['price_min']}")
                if filters.get('price_max'):
                    redirect_params.append(f"price_max={filters['price_max']}")
                if filters.get('body_style'):
                    redirect_params.append(f"body_style={quote(str(filters['body_style']))}")
                if filters.get('exterior_color'):
                    redirect_params.append(f"exterior_color={quote(str(filters['exterior_color']))}")
                if filters.get('transmission'):
                    redirect_params.append(f"transmission={quote(str(filters['transmission']))}")
                if filters.get('fuel_type'):
                    redirect_params.append(f"fuel_type={quote(str(filters['fuel_type']))}")
                if filters.get('drivetrain'):
                    redirect_params.append(f"drivetrain={quote(str(filters['drivetrain']))}")
                if filters.get('trim'):
                    redirect_params.append(f"trim={quote(str(filters['trim']))}")
                if filters.get('exclude_colors'):
                    # Join list as comma-separated values
                    exclude_colors_str = ','.join(filters['exclude_colors'])
                    redirect_params.append(f"exclude_colors={quote(exclude_colors_str)}")
                
                redirect_url = f"/?{'&'.join(redirect_params)}"
                return redirect(redirect_url)
            else:
                error_message = result.get('error', 'Search failed')
                return redirect(f"/?error={quote(error_message)}")
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return redirect(f"/?error=Search failed: {str(e)}")
    
    finally:
        db.close()

@app.route('/health')
def health():
    """Health check endpoint."""
    return {"status": "healthy", "server": "Flask"}

@app.route('/debug')
def debug_search():
    """Debug page for search functionality."""
    db = get_db()
    try:
        # Get query from URL parameter
        query = request.args.get('q', '')
        
        # Parse the query
        nlp_results = {}
        if query:
            nlp_results = parse_natural_language_query(query)
        
        # Get sample vehicles with different attributes
        sample_queries = [
            ("Total vehicles", db.query(Vehicle).count()),
            ("Vehicles with body_style", db.query(Vehicle).filter(Vehicle.body_style.isnot(None)).filter(Vehicle.body_style != '').count()),
            ("Vehicles with exterior_color", db.query(Vehicle).filter(Vehicle.exterior_color.isnot(None)).filter(Vehicle.exterior_color != '').count()),
            ("Vehicles with transmission", db.query(Vehicle).filter(Vehicle.transmission.isnot(None)).filter(Vehicle.transmission != '').count()),
            ("Vehicles with fuel_type", db.query(Vehicle).filter(Vehicle.fuel_type.isnot(None)).filter(Vehicle.fuel_type != '').count()),
            ("Vehicles with drivetrain", db.query(Vehicle).filter(Vehicle.drivetrain.isnot(None)).filter(Vehicle.drivetrain != '').count()),
            ("Vehicles under $40k", db.query(Vehicle).filter(Vehicle.price < 40000).count()),
            ("Honda vehicles", db.query(Vehicle).filter(Vehicle.make.ilike('%honda%')).count()),
            ("Civic models", db.query(Vehicle).filter(Vehicle.model.ilike('%civic%')).count()),
        ]
        
        # Get unique values for each attribute
        unique_values = {
            "makes": db.query(Vehicle.make).distinct().limit(20).all(),
            "models": db.query(Vehicle.model).distinct().limit(20).all(),
            "body_styles": db.query(Vehicle.body_style).filter(Vehicle.body_style.isnot(None)).distinct().all(),
            "colors": db.query(Vehicle.exterior_color).filter(Vehicle.exterior_color.isnot(None)).distinct().all(),
            "transmissions": db.query(Vehicle.transmission).filter(Vehicle.transmission.isnot(None)).distinct().all(),
            "fuel_types": db.query(Vehicle.fuel_type).filter(Vehicle.fuel_type.isnot(None)).distinct().all(),
        }
        
        # Get sample vehicles
        sample_vehicles = db.query(Vehicle).limit(5).all()
        
        # If query provided, show what would be searched
        search_results = None
        if query and nlp_results:
            # Build filters from NLP results
            filters = {}
            
            # Copy logic from search route
            if nlp_results.get('make'):
                filters['make'] = nlp_results.get('make')
            if nlp_results.get('model'):
                filters['model'] = nlp_results.get('model')
            if nlp_results.get('price_max'):
                filters['price_max'] = nlp_results.get('price_max')
            if nlp_results.get('body_style'):
                filters['body_style'] = nlp_results.get('body_style')
            if nlp_results.get('exterior_color'):
                filters['exterior_color'] = nlp_results.get('exterior_color')
            if nlp_results.get('transmission'):
                filters['transmission'] = nlp_results.get('transmission')
            
            # Count vehicles that would match
            count_query = db.query(Vehicle)
            if filters.get('make'):
                count_query = count_query.filter(Vehicle.make.ilike(f"%{filters['make']}%"))
            if filters.get('model'):
                count_query = count_query.filter(Vehicle.model.ilike(f"%{filters['model']}%"))
            if filters.get('price_max'):
                count_query = count_query.filter(Vehicle.price <= filters['price_max'])
            if filters.get('body_style'):
                count_query = count_query.filter(Vehicle.body_style.ilike(f"%{filters['body_style']}%"))
            if filters.get('exterior_color'):
                count_query = count_query.filter(Vehicle.exterior_color.ilike(f"%{filters['exterior_color']}%"))
            if filters.get('transmission'):
                count_query = count_query.filter(Vehicle.transmission.ilike(f"%{filters['transmission']}%"))
            
            search_results = {
                "filters": filters,
                "match_count": count_query.count(),
                "sample_matches": count_query.limit(5).all()
            }
        
        return render_template('debug.html',
                             query=query,
                             nlp_results=nlp_results,
                             sample_queries=sample_queries,
                             unique_values=unique_values,
                             sample_vehicles=sample_vehicles,
                             search_results=search_results)
    
    finally:
        db.close()

if __name__ == '__main__':
    logger.info("🚀 Starting Flask server...")
    app.run(host='127.0.0.1', port=8601, debug=False)