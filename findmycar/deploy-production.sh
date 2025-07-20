#!/bin/bash

# FindMyCar Production Deployment Script
# This script handles the deployment of FindMyCar to production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚗 FindMyCar Production Deployment${NC}"
echo "================================="

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo -e "${RED}❌ Error: .env.prod file not found!${NC}"
    echo "Please copy .env.prod.example to .env.prod and configure it."
    exit 1
fi

# Verify required environment variables
echo -e "${YELLOW}📋 Checking environment configuration...${NC}"
source .env.prod
required_vars=("POSTGRES_PASSWORD" "REDIS_PASSWORD" "SECRET_KEY" "EBAY_CLIENT_ID" "EBAY_CLIENT_SECRET")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Error: $var is not set in .env.prod${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ Environment configuration valid${NC}"

# Build the production images
echo -e "${YELLOW}🔨 Building production Docker images...${NC}"
docker-compose -f docker-compose.prod.yml build

# Stop existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.prod.yml down

# Start the services
echo -e "${YELLOW}🚀 Starting production services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check health status
echo -e "${YELLOW}🏥 Checking health status...${NC}"
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Application is healthy!${NC}"
else
    echo -e "${RED}❌ Health check failed!${NC}"
    echo "Check logs with: docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi

# Display service status
echo -e "${GREEN}📊 Service Status:${NC}"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo "Services available at:"
echo "  - Application: http://localhost"
echo "  - API Docs: http://localhost/docs"
echo "  - Health Check: http://localhost/health"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3000"
echo ""
echo "To view logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "To stop: docker-compose -f docker-compose.prod.yml down"