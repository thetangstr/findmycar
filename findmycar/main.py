from fastapi import FastAPI, Depends, Request, Form, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base, UserSession, Vehicle
from ingestion import ingest_data, ingest_multi_source_data, ingest_autodev_data
from parallel_ingestion import ingest_multi_source_parallel
from nlp_search import parse_natural_language_query, enhance_query_with_use_case
from communication import communication_assistant
from performance_profiler import PerformanceTimer, print_performance_report
from websocket_progress import progress_manager
import crud
import logging
import uuid
import json
from urllib.parse import quote
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# WebSocket endpoint for real-time progress updates
@app.websocket("/ws/progress/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time search progress updates."""
    await progress_manager.connect(websocket, session_id)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        progress_manager.disconnect(session_id)

# Performance monitoring
from io import StringIO
import sys

@app.get("/performance", response_class=HTMLResponse)
async def performance_report():
    """Display performance metrics"""
    # Capture performance report to string
    old_stdout = sys.stdout
    sys.stdout = buffer = StringIO()
    
    print_performance_report()
    
    report_text = buffer.getvalue()
    sys.stdout = old_stdout
    
    # Convert to HTML
    html_content = f"""
    <html>
    <head>
        <title>Performance Report</title>
        <style>
            body {{ font-family: monospace; padding: 20px; background-color: #f5f5f5; }}
            pre {{ background-color: white; padding: 20px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>🚀 Performance Report</h1>
        <pre>{report_text}</pre>
        <a href="/">← Back to Search</a>
    </body>
    </html>
    """
    return html_content

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_session(request: Request, db: Session) -> UserSession:
    """Get or create user session for favorites functionality"""
    session_id = request.cookies.get("session_id")
    
    if session_id:
        user_session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
        if user_session:
            return user_session
    
    # Create new session
    session_id = str(uuid.uuid4())
    user_session = UserSession(
        session_id=session_id,
        favorites=[],
        search_history=[]
    )
    db.add(user_session)
    db.commit()
    db.refresh(user_session)
    return user_session

@app.get("/", response_class=HTMLResponse)
async def read_root(
    request: Request, 
    message: str = None, 
    error: str = None, 
    page: int = 1,
    per_page: int = 12,
    sort: str = "newest",
    # Search filter parameters
    make: str = None,
    model: str = None,
    year_min: int = None,
    year_max: int = None,
    price_min: int = None,
    price_max: int = None,
    db: Session = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * per_page
    
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
    
    # Get total count (with filters if any)
    total_vehicles = crud.get_vehicle_count(db, filters=filters if filters else None)
    
    # Get paginated vehicles (with filters if any)
    vehicles = crud.get_vehicles(db, skip=offset, limit=per_page, sort_by=sort, filters=filters if filters else None)
    
    # Calculate pagination info
    total_pages = (total_vehicles + per_page - 1) // per_page
    
    # Get user session for favorites
    user_session = get_or_create_session(request, db)
    favorites = user_session.favorites or []
    
    response = templates.TemplateResponse("index.html", {
        "request": request, 
        "vehicles": vehicles,
        "message": message,
        "error": error,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "total_vehicles": total_vehicles,
        "sort": sort,
        "favorites": favorites
    })
    
    # Set session cookie if new session
    response.set_cookie("session_id", user_session.session_id, max_age=30*24*60*60)  # 30 days
    return response

async def perform_search_with_progress(
    session_id: str,
    query: str,
    filters: dict,
    sources: List[str],
    db: Session
):
    """Perform search with real-time progress updates."""
    try:
        # Initialize progress tracking
        progress_manager.start_search(session_id, query, sources)
        
        # Enhanced query based on use case
        nlp_filters = parse_natural_language_query(query)
        enhanced_query = enhance_query_with_use_case(nlp_filters.get('cleaned_query', query), nlp_filters.get('use_case'))
        
        # Start search with progress tracking
        await progress_manager.update_source_progress(session_id, "all", "starting", {
            "message": f"Starting search for '{query}' across {len(sources)} sources..."
        })
        
        if len(sources) > 1:
            with PerformanceTimer("web_request.multi_source_search"):
                result = ingest_multi_source_parallel(db, enhanced_query, filters, sources, session_id)
        else:
            # Single source search
            source = sources[0]
            await progress_manager.update_source_progress(session_id, source, "starting")
            
            if source == 'ebay':
                result = ingest_data(db, enhanced_query, filters)
            # Add other single source handlers here
            
            await progress_manager.update_source_progress(session_id, source, "completed", {
                "ingested": result.get('ingested', 0),
                "skipped": result.get('skipped', 0),
                "errors": result.get('errors', 0)
            })
        
        await progress_manager.update_source_progress(session_id, "all", "completed", {
            "total_ingested": result.get('total_ingested', result.get('ingested', 0)),
            "message": "Search completed successfully!"
        })
        
    except Exception as e:
        await progress_manager.add_error(session_id, "system", f"Search failed: {str(e)}")
        logger.error(f"Search error for session {session_id}: {e}")

@app.post("/search/async")
async def trigger_async_search(
    background_tasks: BackgroundTasks,
    query: str = Form(...), 
    make: str = Form(None),
    model: str = Form(None),
    year_min: int = Form(None),
    year_max: int = Form(None),
    price_min: int = Form(None),
    price_max: int = Form(None),
    sources: List[str] = Form(['ebay']),  # Default to eBay only
    db: Session = Depends(get_db)
):
    """Trigger asynchronous search with real-time progress updates."""
    # Generate session ID for this search
    session_id = str(uuid.uuid4())
    
    # Parse natural language query
    nlp_filters = parse_natural_language_query(query)
    logger.info(f"🔍 NLP parsing results for '{query}': {nlp_filters}")
    
    # Build filters (same logic as before)
    filters = {}
    has_chassis_code = nlp_filters.get('chassis_code') is not None
    
    filters['make'] = make or nlp_filters.get('make')
    filters['model'] = model or nlp_filters.get('model')
    
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
    
    filters['price_min'] = price_min or nlp_filters.get('price_min')
    filters['price_max'] = price_max or nlp_filters.get('price_max')
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    # Check for NLP-detected sources
    if nlp_filters.get('sources'):
        sources = nlp_filters['sources']
    
    if not sources:
        sources = ['ebay']
    
    # Start background search
    background_tasks.add_task(perform_search_with_progress, session_id, query, filters, sources, db)
    
    # Return search progress page
    filters_text = ", ".join([f"{k}={v}" for k, v in filters.items() if v is not None])
    return templates.TemplateResponse("search_progress.html", {
        "request": {"method": "GET", "url": f"/search/progress/{session_id}"},
        "session_id": session_id,
        "query": query,
        "sources": sources,
        "filters": filters,
        "filters_text": filters_text or "No filters applied"
    })

@app.post("/ingest", response_class=HTMLResponse)
async def trigger_ingestion(
    query: str = Form(...), 
    make: str = Form(None),
    model: str = Form(None),
    year_min: int = Form(None),
    year_max: int = Form(None),
    price_min: int = Form(None),
    price_max: int = Form(None),
    sources: List[str] = Form(['ebay']),  # Default to eBay only
    db: Session = Depends(get_db)
):
    # Parse natural language query first
    nlp_filters = parse_natural_language_query(query)
    logger.info(f"🔍 NLP parsing results for '{query}': {nlp_filters}")
    
    # Build filters dict, preferring manual inputs over NLP
    filters = {}
    
    # Check if we detected a chassis code - if so, use NLP years instead of form defaults
    has_chassis_code = nlp_filters.get('chassis_code') is not None
    
    # Use manual inputs if provided, otherwise use NLP results
    filters['make'] = make or nlp_filters.get('make')
    filters['model'] = model or nlp_filters.get('model')
    
    # For years, if we have a chassis code, prefer NLP results over form defaults
    if has_chassis_code and nlp_filters.get('year_min'):
        # Don't use form year values if they're the defaults and we have chassis code
        if year_min == 2000 and year_max == 2024:
            filters['year_min'] = nlp_filters.get('year_min')
            filters['year_max'] = nlp_filters.get('year_max')
        else:
            # User explicitly changed the year sliders
            filters['year_min'] = year_min or nlp_filters.get('year_min')
            filters['year_max'] = year_max or nlp_filters.get('year_max')
    else:
        # No chassis code, use form values
        filters['year_min'] = year_min or nlp_filters.get('year_min')
        filters['year_max'] = year_max or nlp_filters.get('year_max')
    
    filters['price_min'] = price_min or nlp_filters.get('price_min')
    filters['price_max'] = price_max or nlp_filters.get('price_max')
    
    logger.info(f"📊 Final filters being used: {filters}")
    
    # Add additional NLP-detected filters
    if nlp_filters.get('body_style'):
        filters['body_style'] = nlp_filters['body_style']
    if nlp_filters.get('fuel_type'):
        filters['fuel_type'] = nlp_filters['fuel_type']
    if nlp_filters.get('transmission'):
        filters['transmission'] = nlp_filters['transmission']
    
    # Use cleaned query if available (removes source: syntax)
    cleaned_query = nlp_filters.get('cleaned_query', query)
    
    # Enhance query based on use case if detected
    enhanced_query = enhance_query_with_use_case(cleaned_query, nlp_filters.get('use_case'))
    
    # Remove None values from filters
    filters = {k: v for k, v in filters.items() if v is not None}
    
    # Check if NLP parser detected source filters
    if nlp_filters.get('sources'):
        # Override form sources with NLP-detected sources
        sources = nlp_filters['sources']
    
    # Ensure we have valid sources
    if not sources or len(sources) == 0:
        sources = ['ebay']  # Default to eBay
    
    # Use parallel multi-source ingestion for better performance
    if len(sources) > 1:
        with PerformanceTimer("web_request.multi_source_search"):
            result = ingest_multi_source_parallel(db, enhanced_query, filters if filters else None, sources)
        
        if result['success']:
            message = f"Successfully ingested {result['total_ingested']} vehicles from {len(sources)} sources"
            if result['total_skipped'] > 0:
                message += f" ({result['total_skipped']} duplicates skipped)"
            if result['total_errors'] > 0:
                message += f" ({result['total_errors']} errors)"
                
            # Add source breakdown
            source_details = []
            for source, source_result in result.get('sources', {}).items():
                if source_result.get('success'):
                    source_details.append(f"{source}: {source_result['ingested']} vehicles")
            if source_details:
                message += f". Sources: {', '.join(source_details)}"
                
            # Build redirect URL with search filters for multi-source
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
            
            redirect_url = f"/?{'&'.join(redirect_params)}"
            return RedirectResponse(url=redirect_url, status_code=303)
        else:
            # Check if any sources succeeded
            successful_sources = [src for src, res in result.get('sources', {}).items() if res.get('success')]
            if successful_sources:
                message = f"Partial success: {result['total_ingested']} vehicles from {len(successful_sources)} source(s)"
                # Build redirect URL with search filters for partial success
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
                
                redirect_url = f"/?{'&'.join(redirect_params)}"
                return RedirectResponse(url=redirect_url, status_code=303)
            else:
                error_message = "All sources failed to return results"
                return RedirectResponse(url=f"/?error={error_message}", status_code=303)
    else:
        # Single source ingestion
        if sources[0] == 'cars.com':
            from ingestion import ingest_cars_data
            result = ingest_cars_data(db, enhanced_query, filters if filters else None)
        elif sources[0] == 'auto.dev':
            result = ingest_autodev_data(db, enhanced_query, filters if filters else None)
        elif sources[0] == 'carmax':
            from ingestion import ingest_carmax_data
            result = ingest_carmax_data(db, enhanced_query, filters if filters else None)
        elif sources[0] == 'cargurus':
            from ingestion import ingest_cargurus_data
            result = ingest_cargurus_data(db, enhanced_query, filters if filters else None)
        elif sources[0] == 'bringatrailer' or sources[0] == 'bat':
            from ingestion import ingest_bat_data
            result = ingest_bat_data(db, enhanced_query, filters if filters else None)
        elif sources[0] == 'truecar':
            from ingestion import ingest_truecar_data
            result = ingest_truecar_data(db, enhanced_query, filters if filters else None)
        else:  # Default to eBay
            result = ingest_data(db, enhanced_query, filters if filters else None)
        
        # Store result in session or query param for display
        if result['success']:
            message = f"Successfully ingested {result['ingested']} vehicles from {sources[0]}"
            if result['skipped'] > 0:
                message += f" ({result['skipped']} duplicates skipped)"
            if result['errors'] > 0:
                message += f" ({result['errors']} errors)"
            
            # Add total available info
            if result.get('total_available', 0) > result['ingested'] + result['skipped']:
                message += f". Total available: {result['total_available']}"
                
            # Build redirect URL with search filters for single source
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
            
            redirect_url = f"/?{'&'.join(redirect_params)}"
            return RedirectResponse(url=redirect_url, status_code=303)
        else:
            error_message = result.get('error', 'Unknown error occurred')
            return RedirectResponse(url=f"/?error={error_message}", status_code=303)

@app.post("/generate-message")
async def generate_message(
    vehicle_id: int = Form(...),
    message_type: str = Form(...),  # "inquiry" or "offer"
    offer_price: float = Form(None),
    db: Session = Depends(get_db)
):
    """
    Generate communication templates for contacting sellers.
    """
    vehicle = crud.get_vehicle(db, vehicle_id)
    if not vehicle:
        return JSONResponse({"error": "Vehicle not found"}, status_code=404)
    
    # Convert SQLAlchemy object to dict for processing
    vehicle_data = {
        'year': vehicle.year,
        'make': vehicle.make,
        'model': vehicle.model,
        'title': vehicle.title,
        'price': vehicle.price,
        'mileage': vehicle.mileage,
        'condition': vehicle.condition,
        'deal_rating': vehicle.deal_rating,
        'estimated_value': vehicle.estimated_value
    }
    
    try:
        if message_type == "inquiry":
            message = communication_assistant.generate_inquiry_message(
                vehicle_data, 
                vehicle.buyer_questions[:5] if vehicle.buyer_questions else []
            )
        elif message_type == "offer" and offer_price:
            negotiation_points = communication_assistant.suggest_negotiation_points(vehicle_data)
            message = communication_assistant.generate_offer_message(
                vehicle_data, 
                offer_price, 
                negotiation_points
            )
        else:
            return JSONResponse({"error": "Invalid message type or missing offer price"}, status_code=400)
        
        return JSONResponse({
            "message": message,
            "negotiation_points": communication_assistant.suggest_negotiation_points(vehicle_data) if message_type == "offer" else []
        })
        
    except Exception as e:
        return JSONResponse({"error": f"Failed to generate message: {str(e)}"}, status_code=500)

@app.post("/favorites/toggle")
async def toggle_favorite(
    request: Request,
    vehicle_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Toggle vehicle in user's favorites list"""
    try:
        user_session = get_or_create_session(request, db)
        favorites = user_session.favorites or []
        
        if vehicle_id in favorites:
            favorites.remove(vehicle_id)
            action = "removed"
        else:
            favorites.append(vehicle_id)
            action = "added"
        
        user_session.favorites = favorites
        db.commit()
        
        return JSONResponse({
            "success": True,
            "action": action,
            "is_favorite": vehicle_id in favorites,
            "total_favorites": len(favorites)
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/favorites", response_class=HTMLResponse)
async def view_favorites(
    request: Request,
    db: Session = Depends(get_db)
):
    """View user's favorites page"""
    user_session = get_or_create_session(request, db)
    favorites = user_session.favorites or []
    
    if favorites:
        # Get favorite vehicles
        vehicles = db.query(Vehicle).filter(Vehicle.id.in_(favorites)).all()
    else:
        vehicles = []
    
    response = templates.TemplateResponse("favorites.html", {
        "request": request,
        "vehicles": vehicles,
        "total_favorites": len(favorites)
    })
    
    response.set_cookie("session_id", user_session.session_id, max_age=30*24*60*60)
    return response

@app.get("/vehicle/{vehicle_id}", response_class=HTMLResponse)
async def view_vehicle_detail(
    request: Request,
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """View detailed information for a specific vehicle"""
    vehicle = crud.get_vehicle(db, vehicle_id)
    
    if not vehicle:
        return RedirectResponse(url="/?error=Vehicle not found", status_code=303)
    
    # Get user session for favorites
    user_session = get_or_create_session(request, db)
    favorites = user_session.favorites or []
    
    # Get similar vehicles (same make/model, different year)
    similar_vehicles = []
    if vehicle.make and vehicle.model:
        similar_vehicles = db.query(Vehicle).filter(
            Vehicle.make == vehicle.make,
            Vehicle.model == vehicle.model,
            Vehicle.id != vehicle.id
        ).limit(6).all()
    
    response = templates.TemplateResponse("vehicle_detail.html", {
        "request": request,
        "vehicle": vehicle,
        "is_favorite": vehicle.id in favorites,
        "similar_vehicles": similar_vehicles,
        "favorites": favorites
    })
    
    # Update view count
    vehicle.view_count = (vehicle.view_count or 0) + 1
    db.commit()
    
    response.set_cookie("session_id", user_session.session_id, max_age=30*24*60*60)
    return response


