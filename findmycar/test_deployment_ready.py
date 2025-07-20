#!/usr/bin/env python3
"""
Test deployment readiness for Firebase CI/CD
"""
import os
import json
from pathlib import Path

def test_deployment_readiness():
    """Test if all deployment files are ready"""
    print("🔍 Testing Deployment Readiness")
    print("=" * 50)
    
    # Check required files
    required_files = [
        '.github/workflows/deploy-firebase.yml',
        'Dockerfile.firebase',
        'firebase.json',
        '.firebaserc',
        'requirements.txt',
        'static/index.html'
    ]
    
    print("1. Checking required files:")
    all_files_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            all_files_exist = False
    
    # Check Firebase configuration
    print("\n2. Checking Firebase configuration:")
    try:
        with open('firebase.json', 'r') as f:
            firebase_config = json.load(f)
        
        if 'hosting' in firebase_config:
            print("   ✅ Firebase hosting configured")
        else:
            print("   ❌ Firebase hosting not configured")
            all_files_exist = False
            
        if firebase_config.get('hosting', {}).get('rewrites'):
            print("   ✅ Cloud Run rewrites configured")
        else:
            print("   ❌ Cloud Run rewrites not configured")
            all_files_exist = False
            
    except Exception as e:
        print(f"   ❌ Firebase config error: {e}")
        all_files_exist = False
    
    # Check .firebaserc
    print("\n3. Checking Firebase project:")
    try:
        with open('.firebaserc', 'r') as f:
            firebaserc = json.load(f)
        
        if firebaserc.get('projects', {}).get('default'):
            print(f"   ✅ Default project: {firebaserc['projects']['default']}")
        else:
            print("   ❌ No default project configured")
            all_files_exist = False
            
    except Exception as e:
        print(f"   ❌ .firebaserc error: {e}")
        all_files_exist = False
    
    # Check GitHub Actions workflow
    print("\n4. Checking GitHub Actions:")
    workflow_path = '.github/workflows/deploy-firebase.yml'
    if Path(workflow_path).exists():
        with open(workflow_path, 'r') as f:
            workflow_content = f.read()
        
        if 'PROJECT_ID:' in workflow_content:
            print("   ✅ PROJECT_ID configured in workflow")
        else:
            print("   ❌ PROJECT_ID not configured in workflow")
        
        if 'FIREBASE_SERVICE_ACCOUNT_KEY' in workflow_content:
            print("   ✅ Service account secret referenced")
        else:
            print("   ❌ Service account secret not referenced")
        
        if 'docker/build-push-action' in workflow_content:
            print("   ✅ Docker build action configured")
        else:
            print("   ❌ Docker build action not configured")
            
        if 'gcloud run deploy' in workflow_content:
            print("   ✅ Cloud Run deployment configured")
        else:
            print("   ❌ Cloud Run deployment not configured")
    
    # Check Dockerfile.firebase
    print("\n5. Checking Dockerfile.firebase:")
    dockerfile_path = 'Dockerfile.firebase'
    if Path(dockerfile_path).exists():
        with open(dockerfile_path, 'r') as f:
            dockerfile_content = f.read()
        
        if 'gunicorn' in dockerfile_content:
            print("   ✅ Gunicorn configured for production")
        else:
            print("   ❌ Gunicorn not configured")
            
        if 'EXPOSE $PORT' in dockerfile_content:
            print("   ✅ Dynamic port configuration")
        else:
            print("   ❌ Static port configuration (should be dynamic)")
            
        if 'USER appuser' in dockerfile_content:
            print("   ✅ Non-root user configured")
        else:
            print("   ❌ Running as root (security risk)")
    
    # Check if main FastAPI app exists
    print("\n6. Checking FastAPI application:")
    if Path('main.py').exists():
        print("   ✅ main.py exists")
        
        # Check if health endpoint exists
        with open('main.py', 'r') as f:
            main_content = f.read()
        
        if '/health' in main_content:
            print("   ✅ Health endpoint configured")
        else:
            print("   ❌ Health endpoint missing")
            all_files_exist = False
    else:
        print("   ❌ main.py not found")
        all_files_exist = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_files_exist:
        print("🎉 DEPLOYMENT READY!")
        print("✅ All required files and configurations present")
        print("✅ Ready for Firebase CI/CD deployment")
        
        print("\n📋 Next Steps:")
        print("1. Update PROJECT_ID in .github/workflows/deploy-firebase.yml")
        print("2. Set up Firebase project and enable APIs")
        print("3. Create secrets in Google Secret Manager")
        print("4. Add FIREBASE_SERVICE_ACCOUNT_KEY to GitHub secrets")
        print("5. Push to GitHub to trigger deployment")
        
    else:
        print("⚠️ DEPLOYMENT NOT READY")
        print("❌ Some required files or configurations are missing")
        print("❌ Fix the issues above before deployment")
    
    return all_files_exist

def main():
    """Run deployment readiness test"""
    print("🚀 Firebase Deployment Readiness Test")
    print("=" * 80)
    
    ready = test_deployment_readiness()
    
    return 0 if ready else 1

if __name__ == "__main__":
    exit(main())