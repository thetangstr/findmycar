#!/usr/bin/env python3
"""
Test Firebase deployment setup for findmycar-347ec
"""
import os
import json
import subprocess
from pathlib import Path

def run_command(cmd):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_firebase_setup():
    """Test if Firebase deployment is properly configured"""
    print("🔍 Testing Firebase Deployment Setup")
    print("=" * 60)
    
    all_good = True
    
    # Test 1: Check project configuration
    print("\n1️⃣ Checking Firebase project configuration...")
    try:
        with open('.firebaserc', 'r') as f:
            firebaserc = json.load(f)
        project_id = firebaserc.get('projects', {}).get('default', '')
        
        if project_id == 'findmycar-347ec':
            print("   ✅ Firebase project correctly set to: findmycar-347ec")
        else:
            print(f"   ❌ Firebase project is '{project_id}', should be 'findmycar-347ec'")
            all_good = False
    except Exception as e:
        print(f"   ❌ Error reading .firebaserc: {e}")
        all_good = False
    
    # Test 2: Check GitHub Actions workflow
    print("\n2️⃣ Checking GitHub Actions workflow...")
    workflow_file = '.github/workflows/deploy-firebase.yml'
    if Path(workflow_file).exists():
        with open(workflow_file, 'r') as f:
            workflow_content = f.read()
        
        if 'PROJECT_ID: findmycar-347ec' in workflow_content:
            print("   ✅ GitHub Actions workflow has correct project ID")
        else:
            print("   ❌ GitHub Actions workflow has incorrect project ID")
            all_good = False
            
        if 'FIREBASE_SERVICE_ACCOUNT_KEY' in workflow_content:
            print("   ✅ Service account secret configured in workflow")
        else:
            print("   ❌ Service account secret not configured in workflow")
            all_good = False
    else:
        print(f"   ❌ Workflow file not found: {workflow_file}")
        all_good = False
    
    # Test 3: Check Docker files
    print("\n3️⃣ Checking Docker configuration...")
    docker_files = ['Dockerfile.firebase', 'requirements-firebase.txt']
    for file in docker_files:
        if Path(file).exists():
            print(f"   ✅ {file} exists")
        else:
            print(f"   ❌ {file} missing")
            all_good = False
    
    # Test 4: Check static files
    print("\n4️⃣ Checking static files...")
    static_files = ['static/index.html', 'static/firebase-config.js']
    for file in static_files:
        if Path(file).exists():
            print(f"   ✅ {file} exists")
        else:
            print(f"   ❌ {file} missing")
            all_good = False
    
    # Test 5: Check Google Cloud CLI
    print("\n5️⃣ Checking Google Cloud CLI...")
    success, stdout, stderr = run_command("gcloud --version")
    if success:
        print("   ✅ Google Cloud CLI is installed")
        
        # Check current project
        success, stdout, stderr = run_command("gcloud config get-value project")
        current_project = stdout.strip()
        if current_project == 'findmycar-347ec':
            print("   ✅ gcloud project is set to findmycar-347ec")
        else:
            print(f"   ⚠️  gcloud project is '{current_project}', run: gcloud config set project findmycar-347ec")
    else:
        print("   ❌ Google Cloud CLI not installed or not in PATH")
        all_good = False
    
    # Test 6: Check Firebase CLI
    print("\n6️⃣ Checking Firebase CLI...")
    success, stdout, stderr = run_command("firebase --version")
    if success:
        print(f"   ✅ Firebase CLI is installed (version: {stdout.strip()})")
    else:
        print("   ❌ Firebase CLI not installed. Run: npm install -g firebase-tools")
        all_good = False
    
    # Test 7: Check required files for deployment
    print("\n7️⃣ Checking all required files...")
    required_files = [
        'main.py',
        'firebase.json',
        'cloudrun.yaml',
        '.github/workflows/deploy-firebase.yml',
        'GITHUB_FIREBASE_SETUP.md'
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} missing")
            all_good = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 FIREBASE SETUP COMPLETE!")
        print("\n📋 Next Steps:")
        print("1. Run the commands in GITHUB_FIREBASE_SETUP.md")
        print("2. Add FIREBASE_SERVICE_ACCOUNT_KEY to GitHub secrets")
        print("3. Push to GitHub to trigger deployment")
        print("\n🚀 Your app will be deployed to:")
        print("   Web: https://findmycar-347ec.web.app")
        print("   API: https://findmycar-api-xxxxx-uc.a.run.app")
    else:
        print("⚠️  SETUP INCOMPLETE")
        print("Fix the issues above before proceeding with deployment")
        print("\nRefer to GITHUB_FIREBASE_SETUP.md for detailed instructions")
    
    return all_good

def check_github_repo():
    """Check if we're in the right GitHub repository"""
    print("\n8️⃣ Checking GitHub repository...")
    success, stdout, stderr = run_command("git remote get-url origin")
    if success:
        remote_url = stdout.strip()
        if 'thetangstr/findmycar' in remote_url:
            print(f"   ✅ Correct GitHub repository: {remote_url}")
            return True
        else:
            print(f"   ⚠️  Different repository: {remote_url}")
            print("   Make sure to push to https://github.com/thetangstr/findmycar")
            return True
    else:
        print("   ❌ Not a git repository or no origin remote")
        return False

if __name__ == "__main__":
    print("🚀 Firebase Deployment Setup Test")
    print("Project: findmycar-347ec")
    print("GitHub: https://github.com/thetangstr/findmycar")
    print("=" * 80)
    
    setup_ready = test_firebase_setup()
    github_ready = check_github_repo()
    
    if setup_ready and github_ready:
        print("\n✅ Everything is ready for deployment!")
    else:
        print("\n❌ Setup needs attention before deployment")
        exit(1)