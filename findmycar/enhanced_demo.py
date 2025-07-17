#!/usr/bin/env python3
"""
Enhanced Features Demo - Serves all the enhanced pages we've created
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI app
app = FastAPI(title="CarGPT Enhanced Features Demo", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Demo data - expanded for better search/filter demonstration
demo_vehicles = [
    {
        "id": 1,
        "title": "2021 Honda Civic Sport",
        "price": 25000,
        "year": 2021,
        "make": "Honda",
        "model": "Civic",
        "mileage": 15000,
        "location": "San Francisco, CA",
        "image_url": "https://via.placeholder.com/300x200?text=Honda+Civic",
        "deal_rating": "Great Deal",
        "source": "ebay",
        "estimated_value": 27000,
        "body_style": "sedan",
        "fuel_type": "gas",
        "transmission": "automatic",
        "color": "blue",
        "external_url": "#"
    },
    {
        "id": 2,
        "title": "2020 Tesla Model 3",
        "price": 45000,
        "year": 2020,
        "make": "Tesla",
        "model": "Model 3",
        "mileage": 20000,
        "location": "Los Angeles, CA",
        "image_url": "https://via.placeholder.com/300x200?text=Tesla+Model+3",
        "deal_rating": "Good Deal",
        "source": "carmax",
        "estimated_value": 48000,
        "body_style": "sedan",
        "fuel_type": "electric",
        "transmission": "automatic",
        "color": "white",
        "external_url": "#"
    },
    {
        "id": 3,
        "title": "2022 Toyota Camry LE",
        "price": 28500,
        "year": 2022,
        "make": "Toyota",
        "model": "Camry",
        "mileage": 8000,
        "location": "Chicago, IL",
        "image_url": "https://via.placeholder.com/300x200?text=Toyota+Camry",
        "deal_rating": "Fair Deal",
        "source": "ebay",
        "estimated_value": 29000,
        "body_style": "sedan",
        "fuel_type": "gas",
        "transmission": "automatic",
        "color": "silver",
        "external_url": "#"
    },
    {
        "id": 4,
        "title": "2019 Honda Accord EX",
        "price": 26900,
        "year": 2019,
        "make": "Honda",
        "model": "Accord",
        "mileage": 35000,
        "location": "Houston, TX",
        "image_url": "https://via.placeholder.com/300x200?text=Honda+Accord",
        "deal_rating": "Good Deal",
        "source": "carmax",
        "estimated_value": 28500,
        "body_style": "sedan",
        "fuel_type": "gas",
        "transmission": "automatic",
        "color": "black",
        "external_url": "#"
    },
    {
        "id": 5,
        "title": "2021 Tesla Model Y",
        "price": 52000,
        "year": 2021,
        "make": "Tesla",
        "model": "Model Y",
        "mileage": 12000,
        "location": "Seattle, WA",
        "image_url": "https://via.placeholder.com/300x200?text=Tesla+Model+Y",
        "deal_rating": "Excellent Deal",
        "source": "ebay",
        "estimated_value": 55000,
        "body_style": "suv",
        "fuel_type": "electric",
        "transmission": "automatic",
        "color": "red",
        "external_url": "#"
    },
    {
        "id": 6,
        "title": "2020 Ford F-150 XLT",
        "price": 38000,
        "year": 2020,
        "make": "Ford",
        "model": "F-150",
        "mileage": 25000,
        "location": "Dallas, TX",
        "image_url": "https://via.placeholder.com/300x200?text=Ford+F-150",
        "deal_rating": "Good Deal",
        "source": "carmax",
        "estimated_value": 40000,
        "body_style": "truck",
        "fuel_type": "gas",
        "transmission": "automatic",
        "color": "gray",
        "external_url": "#"
    },
    {
        "id": 7,
        "title": "2023 Mazda CX-5",
        "price": 32000,
        "year": 2023,
        "make": "Mazda",
        "model": "CX-5",
        "mileage": 5000,
        "location": "Phoenix, AZ",
        "image_url": "https://via.placeholder.com/300x200?text=Mazda+CX-5",
        "deal_rating": "Great Deal",
        "source": "ebay",
        "estimated_value": 34000,
        "body_style": "suv",
        "fuel_type": "gas",
        "transmission": "automatic",
        "color": "blue",
        "external_url": "#"
    },
    {
        "id": 8,
        "title": "2022 BMW 3 Series",
        "price": 42000,
        "year": 2022,
        "make": "BMW",
        "model": "3 Series",
        "mileage": 10000,
        "location": "Miami, FL",
        "image_url": "https://via.placeholder.com/300x200?text=BMW+3+Series",
        "deal_rating": "Fair Deal",
        "source": "carmax",
        "estimated_value": 43000,
        "body_style": "sedan",
        "fuel_type": "gas",
        "transmission": "automatic",
        "color": "white",
        "external_url": "#"
    },
    {
        "id": 9,
        "title": "2021 Chevrolet Silverado",
        "price": 41000,
        "year": 2021,
        "make": "Chevrolet",
        "model": "Silverado",
        "mileage": 18000,
        "location": "Denver, CO",
        "image_url": "https://via.placeholder.com/300x200?text=Chevy+Silverado",
        "deal_rating": "Good Deal",
        "source": "ebay",
        "estimated_value": 43000,
        "body_style": "truck",
        "fuel_type": "gas",
        "transmission": "automatic",
        "color": "black",
        "external_url": "#"
    },
    {
        "id": 10,
        "title": "2020 Nissan Altima",
        "price": 22000,
        "year": 2020,
        "make": "Nissan",
        "model": "Altima",
        "mileage": 30000,
        "location": "Atlanta, GA",
        "image_url": "https://via.placeholder.com/300x200?text=Nissan+Altima",
        "deal_rating": "Great Deal",
        "source": "carmax",
        "estimated_value": 24000,
        "body_style": "sedan",
        "fuel_type": "gas",
        "transmission": "automatic",
        "color": "silver",
        "external_url": "#"
    },
    {
        "id": 11,
        "title": "2019 Tesla Model S",
        "price": 48000,
        "year": 2019,
        "make": "Tesla",
        "model": "Model S",
        "mileage": 40000,
        "location": "San Diego, CA",
        "image_url": "https://via.placeholder.com/300x200?text=Tesla+Model+S",
        "deal_rating": "Good Deal",
        "source": "ebay",
        "estimated_value": 50000,
        "body_style": "sedan",
        "fuel_type": "electric",
        "transmission": "automatic",
        "color": "black",
        "external_url": "#"
    },
    {
        "id": 12,
        "title": "2022 Hyundai Tucson",
        "price": 29500,
        "year": 2022,
        "make": "Hyundai",
        "model": "Tucson",
        "mileage": 12000,
        "location": "Portland, OR",
        "image_url": "https://via.placeholder.com/300x200?text=Hyundai+Tucson",
        "deal_rating": "Excellent Deal",
        "source": "carmax",
        "estimated_value": 31000,
        "body_style": "suv",
        "fuel_type": "gas",
        "transmission": "automatic",
        "color": "green",
        "external_url": "#"
    }
]

# Routes
@app.get("/")
async def home():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CarGPT Enhanced Features Demo</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>🚗 CarGPT Enhanced Features Demo</h1>
            <p class="lead">Access all the enhanced features we've built!</p>
            
            <div class="row mt-4">
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">🔍 Enhanced Search</h5>
                            <p class="card-text">Advanced search with filters, suggestions, and real-time updates</p>
                            <a href="/enhanced-search" class="btn btn-primary">Go to Enhanced Search</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">🆚 Vehicle Comparison</h5>
                            <p class="card-text">Compare up to 4 vehicles side-by-side with AI analysis</p>
                            <a href="/comparison" class="btn btn-primary">Go to Comparison</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">💾 Saved Searches</h5>
                            <p class="card-text">Save searches and get alerts for new matches</p>
                            <a href="/saved-searches" class="btn btn-primary">Go to Saved Searches</a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-3">
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">📱 API Documentation</h5>
                            <p class="card-text">Interactive API documentation and testing</p>
                            <a href="/docs" class="btn btn-secondary">API Docs</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">❤️ Favorites</h5>
                            <p class="card-text">Your saved favorite vehicles</p>
                            <a href="/favorites" class="btn btn-secondary">Go to Favorites</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">🏥 Health Check</h5>
                            <p class="card-text">System health and monitoring</p>
                            <a href="/health" class="btn btn-secondary">Check Health</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/enhanced-search", response_class=HTMLResponse)
async def enhanced_search(request: Request):
    """Serve the enhanced search page"""
    import json
    
    # Pass demo vehicles as JavaScript data
    page_context = {
        "request": request,
        "favorites": [],
        "vehicles": demo_vehicles,
        "total_vehicles": len(demo_vehicles),
        "demo_vehicles_json": json.dumps(demo_vehicles)
    }
    
    return templates.TemplateResponse("enhanced_search.html", page_context)

@app.get("/comparison", response_class=HTMLResponse)
async def comparison(request: Request):
    """Serve the vehicle comparison page"""
    
    # Demo comparison data - show first 4 vehicles
    comparison_data = {
        "vehicles": demo_vehicles[:4],  # Compare first 4 vehicles
        "analysis": {
            "best_value": {
                "vehicle": demo_vehicles[9],  # Nissan Altima
                "reason": "Lowest price with reliable reputation and recent model year"
            },
            "lowest_price": {
                "vehicle": demo_vehicles[9],  # Nissan Altima
                "reason": "Lowest price at $22,000"
            },
            "newest": {
                "vehicle": demo_vehicles[6],  # Mazda CX-5
                "reason": "Newest model year: 2023"
            },
            "lowest_mileage": {
                "vehicle": demo_vehicles[6],  # Mazda CX-5
                "reason": "Lowest mileage: 5,000 miles"
            }
        },
        "recommendations": [
            "The Nissan Altima offers exceptional value at $22,000",
            "The Mazda CX-5 is the newest with lowest mileage",
            "Consider Tesla models for electric vehicle options",
            "Honda vehicles offer proven reliability"
        ],
        "favorites": []
    }
    
    return templates.TemplateResponse("vehicle_comparison.html", {
        "request": request,
        **comparison_data
    })

@app.get("/saved-searches", response_class=HTMLResponse)
async def saved_searches(request: Request):
    """Serve the saved searches page"""
    
    # Demo saved searches
    from datetime import datetime
    saved_searches = [
        {
            "id": 1,
            "name": "Honda Civic Search",
            "query": "Honda Civic 2020-2022",
            "filters": {"price_max": 30000, "mileage_max": 50000},
            "alerts_enabled": "true",
            "alert_frequency": "daily",
            "created_at": datetime(2024, 1, 15),
            "last_run": datetime(2024, 1, 16),
            "new_results_count": 3,
            "is_alerts_enabled": True
        },
        {
            "id": 2,
            "name": "Tesla Under 50k",
            "query": "Tesla Model 3",
            "filters": {"price_max": 50000},
            "alerts_enabled": "false",
            "alert_frequency": "weekly",
            "created_at": datetime(2024, 1, 10),
            "last_run": None,
            "new_results_count": 0,
            "is_alerts_enabled": False
        }
    ]
    
    return templates.TemplateResponse("saved_searches.html", {
        "request": request,
        "saved_searches": saved_searches
    })

@app.get("/favorites", response_class=HTMLResponse)
async def favorites(request: Request):
    """Serve the favorites page"""
    return templates.TemplateResponse("favorites.html", {
        "request": request,
        "vehicles": demo_vehicles[:1],  # Show first vehicle as favorite
        "total_favorites": 1
    })

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "cargpt-enhanced"}

# API endpoints for demonstration
@app.get("/api/search-suggestions")
async def search_suggestions(q: str = ""):
    return {
        "suggestions": [
            {"text": f"{q} under $30,000", "type": "price", "icon": "fas fa-dollar-sign"},
            {"text": f"{q} sedan", "type": "category", "icon": "fas fa-car"},
            {"text": f"{q} SUV", "type": "category", "icon": "fas fa-truck"}
        ]
    }

@app.post("/api/enhanced-search")
async def enhanced_search_api():
    return {
        "success": True,
        "vehicles": demo_vehicles,
        "total_count": len(demo_vehicles),
        "insights": {
            "price": {"min": 25000, "max": 45000, "avg": 35000},
            "year": {"min": 2020, "max": 2021}
        }
    }

# Add missing endpoints
@app.post("/ingest")
async def ingest(query: str = "", request: Request = None):
    """Handle search/ingest requests"""
    return {
        "success": True,
        "message": "Search processed",
        "query": query,
        "results": demo_vehicles
    }

@app.get("/vehicle/{vehicle_id}", response_class=HTMLResponse)
async def vehicle_detail(vehicle_id: int, request: Request):
    """Show vehicle detail page"""
    vehicle = next((v for v in demo_vehicles if v["id"] == vehicle_id), None)
    if not vehicle:
        return HTMLResponse("<h1>Vehicle not found</h1>", status_code=404)
    
    return templates.TemplateResponse("vehicle_detail.html", {
        "request": request,
        "vehicle": vehicle
    })

if __name__ == "__main__":
    print("🚀 Starting CarGPT Enhanced Features Demo")
    print("📍 Access the application at: http://localhost:8601")
    print("🛑 Press Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8601)