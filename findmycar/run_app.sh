#!/bin/bash

echo "🚗 Starting AutoNavigator..."
echo "📍 Directory: $(pwd)"
echo ""

# Kill any existing processes on port 8601
lsof -ti:8601 | xargs kill -9 2>/dev/null

# Start the FastAPI app
echo "🌐 Starting server at http://localhost:8601"
echo "🛑 Press Ctrl+C to stop"
echo ""

python3 -m uvicorn main:app --host 0.0.0.0 --port 8601 --reload