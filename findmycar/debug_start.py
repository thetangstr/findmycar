import sys
import traceback

try:
    print("🔍 Debug Mode: Starting AutoNavigator")
    print("-" * 50)
    
    print("1. Importing modules...")
    from fastapi import FastAPI, Depends, Request, Form
    from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
    from fastapi.templating import Jinja2Templates
    from sqlalchemy.orm import Session
    print("   ✓ FastAPI imports successful")
    
    from database import SessionLocal, engine, Base
    print("   ✓ Database imports successful")
    
    from ingestion import ingest_data
    from nlp_search import parse_natural_language_query, enhance_query_with_use_case
    from communication import communication_assistant
    import crud
    print("   ✓ All module imports successful")
    
    print("\n2. Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("   ✓ Database initialized")
    
    print("\n3. Importing main app...")
    from main import app
    print("   ✓ Main app imported")
    
    print("\n4. Starting server on http://127.0.0.1:8080")
    print("-" * 50)
    
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="debug")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()