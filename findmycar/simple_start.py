#!/usr/bin/env python3
"""
Simple startup script for testing - bypasses complex configuration
"""

import os
import sys
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Set basic environment variables
os.environ["ENVIRONMENT"] = "development"
os.environ["DEBUG"] = "true"
os.environ["EBAY_CLIENT_ID"] = "test_client_id"
os.environ["EBAY_CLIENT_SECRET"] = "test_client_secret"
os.environ["OPENAI_API_KEY"] = "test_openai_key"
os.environ["SECRET_KEY"] = "test_secret_key_for_development"
os.environ["DATABASE_URL"] = "sqlite:///./findmycar.db"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000,http://localhost:8000"

# Create simple FastAPI app
app = FastAPI(title="CarGPT", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Basic routes
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cargpt"}

@app.get("/")
async def read_root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CarGPT - AI-Powered Vehicle Discovery</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container">
            <h1>CarGPT - AI-Powered Vehicle Discovery</h1>
            <p>Application is running successfully!</p>
            <div class="mt-4">
                <h3>Test Search</h3>
                <form action="/search" method="get">
                    <input type="text" name="query" placeholder="Search for vehicles..." class="form-control mb-2">
                    <button type="submit" class="btn btn-primary">Search</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/search")
async def search_vehicles(query: str = ""):
    return {"query": query, "results": [], "message": "Search functionality available"}

@app.get("/enhanced-search")
async def enhanced_search():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enhanced Search - CarGPT</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container">
            <h1>Enhanced Search</h1>
            <p>Enhanced search interface for testing</p>
            <form>
                <input type="text" name="query" placeholder="Enter search query..." class="form-control mb-2">
                <button type="button" class="btn btn-primary">Search</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.get("/comparison")
async def comparison():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vehicle Comparison - CarGPT</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container">
            <h1>Vehicle Comparison</h1>
            <p>Vehicle comparison interface for testing</p>
        </div>
    </body>
    </html>
    """)

@app.get("/favorites")
async def favorites():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Favorites - CarGPT</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container">
            <h1>My Favorites</h1>
            <p>Favorites interface for testing</p>
        </div>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)