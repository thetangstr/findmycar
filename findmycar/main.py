from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base, UserSession, Vehicle
from ingestion import ingest_data, ingest_multi_source_data, ingest_autodev_data
from nlp_search import parse_natural_language_query, enhance_query_with_use_case
from communication import communication_assistant
import crud
import logging
import uuid
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI()

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
    db: Session = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    total_vehicles = crud.get_vehicle_count(db)
    
    # Get paginated vehicles
    vehicles = crud.get_vehicles(db, skip=offset, limit=per_page, sort_by=sort)
    
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
    
    # Build filters dict, preferring manual inputs over NLP
    filters = {}
    
    # Use manual inputs if provided, otherwise use NLP results
    filters['make'] = make or nlp_filters.get('make')
    filters['model'] = model or nlp_filters.get('model')
    filters['year_min'] = year_min or nlp_filters.get('year_min')
    filters['year_max'] = year_max or nlp_filters.get('year_max')
    filters['price_min'] = price_min or nlp_filters.get('price_min')
    filters['price_max'] = price_max or nlp_filters.get('price_max')
    
    # Add additional NLP-detected filters
    if nlp_filters.get('body_style'):
        filters['body_style'] = nlp_filters['body_style']
    if nlp_filters.get('fuel_type'):
        filters['fuel_type'] = nlp_filters['fuel_type']
    if nlp_filters.get('transmission'):
        filters['transmission'] = nlp_filters['transmission']
    
    # Enhance query based on use case if detected
    enhanced_query = enhance_query_with_use_case(query, nlp_filters.get('use_case'))
    
    # Remove None values from filters
    filters = {k: v for k, v in filters.items() if v is not None}
    
    # Ensure we have valid sources
    if not sources or len(sources) == 0:
        sources = ['ebay']  # Default to eBay
    
    # Use multi-source ingestion if multiple sources selected
    if len(sources) > 1:
        result = ingest_multi_source_data(db, enhanced_query, filters if filters else None, sources)
        
        if result['success']:
            message = f"Successfully ingested {result['total_ingested']} vehicles from {len(sources)} sources"
            if result['total_skipped'] > 0:
                message += f" ({result['total_skipped']} duplicates skipped)"
            if result['total_errors'] > 0:
                message += f" ({result['total_errors']} errors)"
                
            # Add source breakdown
            source_details = []
            for source, source_result in result['results'].items():
                if source_result['success']:
                    source_details.append(f"{source}: {source_result['ingested']} vehicles")
            if source_details:
                message += f". Sources: {', '.join(source_details)}"
                
            return RedirectResponse(url=f"/?message={message}", status_code=303)
        else:
            # Check if any sources succeeded
            successful_sources = [src for src, res in result['results'].items() if res['success']]
            if successful_sources:
                message = f"Partial success: {result['total_ingested']} vehicles from {len(successful_sources)} source(s)"
                return RedirectResponse(url=f"/?message={message}", status_code=303)
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
        else:
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
                
            return RedirectResponse(url=f"/?message={message}", status_code=303)
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


