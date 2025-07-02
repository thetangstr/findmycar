#!/usr/bin/env python3
"""
AutoNavigator Startup Script
"""

import uvicorn
from main import app
from database import engine, Base

def main():
    print("🚀 Starting AutoNavigator...")
    
    # Initialize database
    print("📁 Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database ready")
    
    # Start server
    print("🌐 Starting web server on http://127.0.0.1:9000")
    print("📝 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=9000, 
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()