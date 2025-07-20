# 🚀 GitHub Actions Firebase Deployment Setup

This guide will help you set up automatic deployment from **https://github.com/thetangstr/findmycar** to Firebase project **findmycar-347ec**.

## 📋 Prerequisites

- GitHub repository: https://github.com/thetangstr/findmycar
- Firebase project: findmycar-347ec
- Google Cloud CLI installed locally
- Firebase CLI installed locally

## Step 1: Enable Required APIs in Google Cloud

Go to [Google Cloud Console](https://console.cloud.google.com) and select project **findmycar-347ec**, then run:

```bash
# Set your project
gcloud config set project findmycar-347ec

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## Step 2: Create Service Account for GitHub Actions

```bash
# Create service account
gcloud iam service-accounts create github-actions \
    --description="Service account for GitHub Actions deployment" \
    --display-name="GitHub Actions"

# Grant necessary permissions
gcloud projects add-iam-policy-binding findmycar-347ec \
    --member="serviceAccount:github-actions@findmycar-347ec.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding findmycar-347ec \
    --member="serviceAccount:github-actions@findmycar-347ec.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding findmycar-347ec \
    --member="serviceAccount:github-actions@findmycar-347ec.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding findmycar-347ec \
    --member="serviceAccount:github-actions@findmycar-347ec.iam.gserviceaccount.com" \
    --role="roles/firebase.admin"

# Create and download service account key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@findmycar-347ec.iam.gserviceaccount.com
```

## Step 3: Create Secrets in Google Secret Manager

```bash
# Create secrets for eBay API (use your actual credentials)
echo -n "KailorTa-fmc-PRD-a8e70e47c-c916c494" | gcloud secrets create ebay-client-id --data-file=-
echo -n "PRD-8e70e47c45e6-8603-4564-9283-bd68" | gcloud secrets create ebay-client-secret --data-file=-

# Create app secret key (generate a secure one)
echo -n "your-secure-256-bit-secret-key-here" | gcloud secrets create app-secret-key --data-file=-

# Grant service account access to secrets
gcloud secrets add-iam-policy-binding ebay-client-id \
    --member="serviceAccount:github-actions@findmycar-347ec.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding ebay-client-secret \
    --member="serviceAccount:github-actions@findmycar-347ec.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding app-secret-key \
    --member="serviceAccount:github-actions@findmycar-347ec.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## Step 4: Set Up GitHub Repository Secret

1. Go to https://github.com/thetangstr/findmycar/settings/secrets/actions
2. Click "New repository secret"
3. Name: `FIREBASE_SERVICE_ACCOUNT_KEY`
4. Value: Copy the entire contents of `github-actions-key.json` file
5. Click "Add secret"

**Important**: After adding the secret, delete the local `github-actions-key.json` file for security:
```bash
rm github-actions-key.json
```

## Step 5: Initialize Firebase Hosting

```bash
# Login to Firebase
firebase login

# Initialize hosting (in your project directory)
firebase init hosting

# When prompted:
# - Select "Use an existing project"
# - Choose "findmycar-347ec"
# - Public directory: "static"
# - Single-page app: No
# - Set up automatic builds: No
# - Overwrite index.html: No
```

## Step 6: Push to GitHub

```bash
# Add all files
git add .

# Commit
git commit -m "Add Firebase deployment configuration for findmycar-347ec"

# Push to GitHub (this will trigger the deployment)
git push origin main
```

## Step 7: Monitor Deployment

1. Go to https://github.com/thetangstr/findmycar/actions
2. You should see a workflow running called "Deploy to Firebase"
3. Click on it to see real-time logs
4. The deployment takes about 5-10 minutes

## Step 8: Verify Deployment

Once the workflow completes successfully:

1. **Firebase Hosting**: https://findmycar-347ec.web.app
2. **Cloud Run API**: Check the GitHub Actions logs for the URL (will be something like `https://findmycar-api-xxxxx-uc.a.run.app`)
3. **Health Check**: Visit `https://findmycar-api-xxxxx-uc.a.run.app/health`

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Permission Denied Errors
```bash
# Ensure the service account has all required permissions
gcloud projects get-iam-policy findmycar-347ec \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:github-actions@findmycar-347ec.iam.gserviceaccount.com" \
    --format="table(bindings.role)"
```

#### 2. Secret Not Found
```bash
# Verify secrets exist
gcloud secrets list

# Check secret permissions
gcloud secrets get-iam-policy ebay-client-id
```

#### 3. Container Registry Issues
```bash
# Enable Container Registry API if not enabled
gcloud services enable containerregistry.googleapis.com

# Check if images are being pushed
gcloud container images list
```

#### 4. Cloud Run Deployment Fails
```bash
# Check Cloud Run services
gcloud run services list --region us-central1

# View deployment logs
gcloud run services logs read findmycar-api --region us-central1
```

## 📊 What Happens on Each Push

When you push to the `main` branch:

1. **Tests Run** - Basic health checks and configuration validation
2. **Docker Build** - Creates optimized container image
3. **Push to GCR** - Uploads image to Google Container Registry
4. **Deploy to Cloud Run** - Updates the service with new image
5. **Health Check** - Verifies deployment is working
6. **Update Summary** - Creates deployment report in GitHub

## 🔐 Security Notes

- Never commit the `github-actions-key.json` file
- Rotate service account keys periodically
- Use Secret Manager for all sensitive data
- Review IAM permissions regularly

## 📈 Monitoring Your Deployment

### Cloud Run Console
Visit: https://console.cloud.google.com/run?project=findmycar-347ec

### Firebase Console
Visit: https://console.firebase.google.com/project/findmycar-347ec

### GitHub Actions
Visit: https://github.com/thetangstr/findmycar/actions

## 🎉 Success!

Once everything is set up, every push to `main` will automatically:
- Build your Docker container
- Deploy to Cloud Run
- Update Firebase Hosting
- Run health checks
- Notify you of the deployment status

Your FindMyCar app will be live at:
- **Web**: https://findmycar-347ec.web.app
- **API**: https://findmycar-api-xxxxx-uc.a.run.app

## Need Help?

If you encounter issues:
1. Check GitHub Actions logs first
2. Review Cloud Run logs in Google Cloud Console
3. Ensure all secrets are properly configured
4. Verify service account permissions