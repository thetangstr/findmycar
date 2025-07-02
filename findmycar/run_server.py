#!/usr/bin/env python3
"""
Simple server runner with better error handling
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        print("🚀 Starting AutoNavigator Server...")
        print("📍 Current directory:", os.getcwd())
        print("🔍 Python path:", sys.path[0])
        
        # Test imports one by one
        print("\n📦 Loading dependencies...")
        
        try:
            import fastapi
            print("  ✓ FastAPI loaded")
        except ImportError as e:
            print(f"  ❌ FastAPI import failed: {e}")
            return
            
        try:
            import uvicorn
            print("  ✓ Uvicorn loaded")
        except ImportError as e:
            print(f"  ❌ Uvicorn import failed: {e}")
            return
            
        # Import the app
        print("\n🔧 Loading application...")
        try:
            from main import app
            print("  ✓ Application loaded successfully")
        except Exception as e:
            print(f"  ❌ Application load failed: {e}")
            import traceback
            traceback.print_exc()
            return
            
        # Run server
        print("\n🌐 Starting web server...")
        print("📱 Open your browser to: http://localhost:8080")
        print("🛑 Press Ctrl+C to stop\n")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8080,
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()