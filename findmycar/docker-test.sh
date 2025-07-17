#!/bin/bash

# CarGPT Docker Build and Test Script

echo "🚀 CarGPT Docker Build and Test"
echo "================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"

# Build the Docker image
echo "🔨 Building CarGPT Docker image..."
docker build -t cargpt:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Docker build failed"
    exit 1
fi

# Test the Docker image
echo "🧪 Testing Docker image..."
docker run --rm -d --name cargpt-test -p 8000:8000 cargpt:latest

# Wait for the container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Test health endpoint
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
fi

# Test homepage
if curl -f http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Homepage accessible"
else
    echo "❌ Homepage not accessible"
fi

# Cleanup
echo "🧹 Cleaning up test container..."
docker stop cargpt-test

echo "🎉 Docker test completed!"

# Show image details
echo "📊 Image details:"
docker images cargpt:latest