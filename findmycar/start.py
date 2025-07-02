#!/usr/bin/env python3
"""
AutoNavigator Server Launcher
"""

if __name__ == "__main__":
    import uvicorn
    import os
    import sys
    
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 60)
    print("🚗 AutoNavigator - Car Search Platform")
    print("=" * 60)
    print()
    print("🚀 Starting server...")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📝 Press Ctrl+C to stop the server")
    print()
    print("⏳ Please wait while the server starts...")
    print("-" * 60)
    
    try:
        # Run with explicit module path
        uvicorn.run(
            "main:app",
            host="localhost",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that port 8000 is not in use")
        print("3. Verify your .env file has the correct API keys")