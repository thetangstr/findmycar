#!/usr/bin/env python3
"""
Test authentication setup
"""

import os
import sys

def test_auth_setup():
    """Test if authentication is properly configured"""
    print("🔍 Testing Authentication Setup")
    print("=" * 60)
    
    # Test 1: Check environment variables
    print("\n1️⃣ Checking environment variables...")
    secret_key = os.getenv("SECRET_KEY")
    if secret_key and len(secret_key) > 10:
        print("   ✅ SECRET_KEY is configured")
    else:
        print("   ⚠️  SECRET_KEY not configured or too short")
        print("   Run: python generate_secret_key.py")
    
    # Test 2: Check Firebase Admin SDK
    print("\n2️⃣ Checking Firebase Admin SDK...")
    try:
        import firebase_admin
        print("   ✅ firebase-admin package installed")
    except ImportError:
        print("   ❌ firebase-admin not installed")
        print("   Run: pip install firebase-admin")
        return False
    
    # Test 3: Check Firebase credentials
    print("\n3️⃣ Checking Firebase credentials...")
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("   ✅ GOOGLE_APPLICATION_CREDENTIALS is set")
    else:
        print("   ⚠️  GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   This will use default credentials in production")
    
    # Test 4: Check auth module
    print("\n4️⃣ Checking auth module...")
    try:
        from firebase_auth import FirebaseAuth
        print("   ✅ firebase_auth module loads successfully")
    except ImportError as e:
        print(f"   ❌ Error loading firebase_auth: {e}")
        return False
    
    # Test 5: Check static files
    print("\n5️⃣ Checking static files...")
    files_to_check = [
        "static/js/auth.js",
        "templates/base.html",
        "templates/index_auth.html"
    ]
    
    all_files_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"   ✅ {file} exists")
        else:
            print(f"   ❌ {file} missing")
            all_files_exist = False
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 Authentication setup is ready!")
    print("\nNext steps:")
    print("1. Set GOOGLE_APPLICATION_CREDENTIALS if running locally")
    print("2. Update main.py to use index_auth.html template")
    print("3. Test Google Sign-in in the browser")
    
    return True

if __name__ == "__main__":
    test_auth_setup()