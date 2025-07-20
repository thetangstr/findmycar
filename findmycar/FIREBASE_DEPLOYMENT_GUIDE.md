# 🚀 Firebase Deployment Guide

## Overview

This guide will help you deploy FindMyCar to Firebase using Cloud Run and GitHub Actions for automatic CI/CD.

## Prerequisites

1. **Google Cloud Console Account**
2. **Firebase Project**
3. **GitHub Repository**
4. **eBay API Credentials**

## Step 1: Firebase Project Setup

### 1.1 Create Firebase Project

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Create new project (or use existing)
firebase projects:create findmycar-prod

# Select the project
firebase use findmycar-prod
```

### 1.2 Enable Required APIs

In Google Cloud Console, enable these APIs:
- Cloud Run API
- Container Registry API
- Secret Manager API
- Cloud Build API

```bash
# Enable APIs via CLI
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## Step 2: Secrets Configuration

### 2.1 Create Secrets in Google Secret Manager

```bash
# eBay API credentials
echo -n "your-ebay-client-id" | gcloud secrets create ebay-client-id --data-file=-
echo -n "your-ebay-client-secret" | gcloud secrets create ebay-client-secret --data-file=-

# Application secret key
echo -n "your-256-bit-secret-key" | gcloud secrets create app-secret-key --data-file=-
```

### 2.2 Create Service Account for GitHub Actions

```bash
# Create service account
gcloud iam service-accounts create github-actions \
    --description="Service account for GitHub Actions" \
    --display-name="GitHub Actions"

# Grant necessary permissions
gcloud projects add-iam-policy-binding findmycar-prod \
    --member="serviceAccount:github-actions@findmycar-prod.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding findmycar-prod \
    --member="serviceAccount:github-actions@findmycar-prod.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding findmycar-prod \
    --member="serviceAccount:github-actions@findmycar-prod.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create and download service account key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@findmycar-prod.iam.gserviceaccount.com
```

## Step 3: GitHub Repository Setup

### 3.1 Repository Secrets

In your GitHub repository, go to Settings > Secrets and Variables > Actions and add:

- **`FIREBASE_SERVICE_ACCOUNT_KEY`**: Contents of `github-actions-key.json`

### 3.2 Update Configuration

Edit `.github/workflows/deploy-firebase.yml` and update:

```yaml
env:
  PROJECT_ID: your-actual-project-id  # Replace with your Firebase project ID
  SERVICE_NAME: findmycar-api
  REGION: us-central1  # Or your preferred region
```

## Step 4: Local Testing

### 4.1 Test Docker Build

```bash
# Build the Firebase Docker image
docker build -f Dockerfile.firebase -t findmycar:firebase .

# Test locally
docker run -p 8080:8080 \
  -e EBAY_CLIENT_ID="your-ebay-client-id" \
  -e EBAY_CLIENT_SECRET="your-ebay-client-secret" \
  -e SECRET_KEY="your-secret-key" \
  -e DATABASE_URL="sqlite:///./findmycar.db" \
  findmycar:firebase
```

### 4.2 Test Health Check

```bash
curl http://localhost:8080/health
```

## Step 5: Deployment

### 5.1 Push to GitHub

```bash
git add .
git commit -m "Add Firebase deployment configuration"
git push origin main
```

### 5.2 Monitor Deployment

1. Go to your GitHub repository
2. Click on "Actions" tab
3. Watch the deployment pipeline run
4. Check for any errors in the logs

### 5.3 Verify Deployment

Once deployment completes, test:

```bash
# Health check
curl https://findmycar-api-[hash]-uc.a.run.app/health

# Vehicle search
curl "https://findmycar-api-[hash]-uc.a.run.app/search?query=Honda&year_min=2010"
```

## Success Criteria

Your deployment is successful when:

✅ GitHub Actions pipeline completes without errors  
✅ Cloud Run service is running and healthy  
✅ Health check endpoint returns 200 OK  
✅ Vehicle search returns results from all 3 sources  
✅ Logs show no critical errors  
✅ Response times are under 45 seconds  
EOF < /dev/null
