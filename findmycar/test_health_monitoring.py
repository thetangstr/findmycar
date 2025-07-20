#!/usr/bin/env python3
"""
Test script for comprehensive health monitoring
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_health_endpoints():
    """Test all health monitoring endpoints"""
    base_url = "http://localhost:8603"
    
    print("Testing Health Monitoring Endpoints")
    print("=" * 50)
    
    # Test basic health endpoint
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test detailed health endpoint
    print("\n2. Testing /health/detailed endpoint...")
    try:
        response = requests.get(f"{base_url}/health/detailed")
        print(f"   Status Code: {response.status_code}")
        data = response.json()
        print(f"   Overall Status: {data.get('status')}")
        print(f"   Uptime: {data.get('uptime_human')}")
        print(f"   Components:")
        for component in data.get('components', []):
            print(f"      - {component['name']}: {component['status']} - {component['message']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test metrics endpoint
    print("\n3. Testing /metrics endpoint...")
    try:
        response = requests.get(f"{base_url}/metrics")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content Type: {response.headers.get('Content-Type')}")
        print(f"   Sample metrics:")
        lines = response.text.split('\n')[:10]  # First 10 lines
        for line in lines:
            print(f"      {line}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test health dashboard endpoint (JSON)
    print("\n4. Testing /health/dashboard endpoint (JSON)...")
    try:
        headers = {'Accept': 'application/json'}
        response = requests.get(f"{base_url}/health/dashboard", headers=headers)
        print(f"   Status Code: {response.status_code}")
        data = response.json()
        print(f"   Dashboard Status: {data.get('status')}")
        print(f"   Metrics Summary:")
        metrics = data.get('metrics', {})
        print(f"      - Response Times: {metrics.get('response_times', {})}")
        print(f"      - Error Rate: {metrics.get('error_rate')}")
        print(f"      - Cache Hit Rate: {metrics.get('cache_hit_rate')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test health dashboard endpoint (HTML)
    print("\n5. Testing /health/dashboard endpoint (HTML)...")
    try:
        response = requests.get(f"{base_url}/health/dashboard")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content Type: {response.headers.get('Content-Type')}")
        print(f"   HTML Response Length: {len(response.text)} bytes")
        print(f"   Contains dashboard elements: {'health-dashboard' in response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("Health monitoring test complete!")

if __name__ == "__main__":
    # Make sure the Flask app is running
    print("Make sure the Flask app is running on http://localhost:8603")
    print("Press Enter to continue with tests...")
    input()
    
    test_health_endpoints()