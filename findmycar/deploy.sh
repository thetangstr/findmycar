#!/bin/bash

# FindMyCar Deployment Script
# This script helps deploy the application to Firebase/Google Cloud

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-""}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="findmycar-api"

echo -e "${GREEN}FindMyCar Deployment Script${NC}"
echo "================================="

# Check prerequisites
check_prerequisites() {
    echo -e "\n${YELLOW}Checking prerequisites...${NC}"
    
    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI not found. Please install: https://cloud.google.com/sdk/install${NC}"
        exit 1
    fi
    
    # Check firebase
    if ! command -v firebase &> /dev/null; then
        echo -e "${RED}❌ Firebase CLI not found. Please install: npm install -g firebase-tools${NC}"
        exit 1
    fi
    
    # Check docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found. Please install Docker Desktop${NC}"
        exit 1
    fi
    
    # Check project ID
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${YELLOW}Enter your Google Cloud Project ID:${NC}"
        read PROJECT_ID
    fi
    
    echo -e "${GREEN}✅ All prerequisites met${NC}"
}

# Build static files
build_static() {
    echo -e "\n${YELLOW}Building static files...${NC}"
    
    # Create public directory
    rm -rf public
    mkdir -p public/static
    
    # Copy static assets
    cp -r static/* public/static/
    
    # Copy HTML files
    cp templates/modern_landing.html public/index.html
    cp templates/search_results.html public/search.html
    
    # Update paths in HTML files
    sed -i.bak 's|/static/|/static/|g' public/*.html
    rm public/*.html.bak
    
    echo -e "${GREEN}✅ Static files built${NC}"
}

# Deploy API to Cloud Run
deploy_api() {
    echo -e "\n${YELLOW}Deploying API to Cloud Run...${NC}"
    
    # Configure Docker for GCR
    gcloud auth configure-docker
    
    # Build Docker image
    echo "Building Docker image..."
    docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest -f Dockerfile.cloudrun .
    
    # Push to Container Registry
    echo "Pushing to Container Registry..."
    docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
    
    # Deploy to Cloud Run
    echo "Deploying to Cloud Run..."
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 1Gi \
        --cpu 1 \
        --timeout 300 \
        --min-instances 0 \
        --max-instances 10 \
        --project $PROJECT_ID
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)' --project $PROJECT_ID)
    echo -e "${GREEN}✅ API deployed to: $SERVICE_URL${NC}"
}

# Update Firebase config
update_firebase_config() {
    echo -e "\n${YELLOW}Updating Firebase configuration...${NC}"
    
    # Update firebase.json with Cloud Run URL
    if [ ! -z "$SERVICE_URL" ]; then
        # Create temporary firebase.json with updated API URL
        cat > firebase.json.tmp << EOF
{
  "hosting": {
    "public": "public",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "$SERVICE_NAME",
          "region": "$REGION"
        }
      },
      {
        "source": "/search",
        "destination": "/search.html"
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
EOF
        mv firebase.json.tmp firebase.json
    fi
    
    echo -e "${GREEN}✅ Firebase configuration updated${NC}"
}

# Deploy to Firebase Hosting
deploy_hosting() {
    echo -e "\n${YELLOW}Deploying to Firebase Hosting...${NC}"
    
    # Select Firebase project
    firebase use $PROJECT_ID
    
    # Deploy hosting
    firebase deploy --only hosting
    
    echo -e "${GREEN}✅ Firebase Hosting deployed${NC}"
}

# Run deployment
main() {
    check_prerequisites
    
    echo -e "\n${YELLOW}Starting deployment process...${NC}"
    echo "Project ID: $PROJECT_ID"
    echo "Region: $REGION"
    
    # Confirm deployment
    echo -e "\n${YELLOW}Deploy to production? (y/n)${NC}"
    read confirm
    if [ "$confirm" != "y" ]; then
        echo "Deployment cancelled"
        exit 0
    fi
    
    # Run deployment steps
    build_static
    deploy_api
    update_firebase_config
    deploy_hosting
    
    echo -e "\n${GREEN}🎉 Deployment complete!${NC}"
    echo -e "Your app is live at: https://$PROJECT_ID.web.app"
    echo -e "API endpoint: $SERVICE_URL"
    
    # Show next steps
    echo -e "\n${YELLOW}Next steps:${NC}"
    echo "1. Set up environment variables in Cloud Run console"
    echo "2. Configure custom domain (optional)"
    echo "3. Set up monitoring and alerts"
    echo "4. Test the deployment"
}

# Run main function
main