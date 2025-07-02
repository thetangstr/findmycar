#!/usr/bin/env python3

"""
Quick verification of current UI state
"""

import requests
import time

def verify_current_state():
    """Check what's currently being served"""
    
    try:
        print("🔍 Checking localhost:8000...")
        response = requests.get("http://localhost:8000", timeout=10)
        
        if response.status_code == 200:
            html = response.text
            
            print("✅ Server is responding")
            
            # Check for key elements
            checks = [
                ('id="sourceCars" disabled', "Cars.com checkbox disabled"),
                ('Coming Soon', "Coming Soon badge"),
                ('data-toggle="modal"', "Modal trigger link"),
                ('id="dataNotice"', "Data quality modal"),
                ("We're upgrading our data sources", "Upgrade notice text"),
                ('Value="cars.com"', "Cars.com checkbox value")
            ]
            
            print("\n📋 Current UI State:")
            for search_text, description in checks:
                if search_text in html:
                    print(f"✅ {description}")
                else:
                    print(f"❌ Missing: {description}")
            
            # Show Cars.com section specifically
            print("\n🎯 Cars.com Section Preview:")
            lines = html.split('\n')
            for i, line in enumerate(lines):
                if 'sourceCars' in line:
                    for j in range(max(0, i-2), min(len(lines), i+5)):
                        print(f"  {lines[j].strip()}")
                    break
                    
        else:
            print(f"❌ Server error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to localhost:8000")
        print("💡 Try: python start.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_current_state()