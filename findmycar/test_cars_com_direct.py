#!/usr/bin/env python3
"""
Test the direct Cars.com implementation
"""
import logging
from datetime import datetime
from cars_com_direct_client import CarsComDirectClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_direct_cars_com():
    """Test direct Cars.com access"""
    print("🔍 Testing Direct Cars.com Implementation")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        client = CarsComDirectClient()
        
        # Test 1: Health check
        print("\n1. Testing health check...")
        health = client.check_health()
        print(f"   Status: {health['status']}")
        print(f"   Response time: {health['response_time']:.2f}s")
        print(f"   Message: {health['message']}")
        
        if health['status'] != 'healthy':
            print("⚠️  Cars.com not accessible, but continuing tests...")
        
        # Test 2: Basic search
        print("\n2. Testing basic search (Honda)...")
        results = client.search_vehicles(
            make="Honda",
            year_min=2018,
            price_max=30000,
            per_page=10
        )
        
        total = results.get('total', 0)
        vehicles = results.get('vehicles', [])
        
        print(f"   Found {total} vehicles")
        print(f"   Returned {len(vehicles)} vehicles")
        
        # Display sample results
        if vehicles:
            print("\n   Sample vehicles:")
            for i, vehicle in enumerate(vehicles[:3], 1):
                print(f"\n   Vehicle {i}:")
                print(f"     Title: {vehicle.get('title', 'N/A')}")
                print(f"     Price: ${vehicle.get('price', 0):,}")
                print(f"     Year: {vehicle.get('year', 'N/A')}")
                print(f"     Make: {vehicle.get('make', 'N/A')}")
                print(f"     Model: {vehicle.get('model', 'N/A')}")
                print(f"     Location: {vehicle.get('location', 'N/A')}")
                print(f"     Link: {vehicle.get('link', 'N/A')}")
        
        # Test 3: Specific model search
        print("\n3. Testing specific model search (Toyota Camry)...")
        results2 = client.search_vehicles(
            make="Toyota",
            model="Camry",
            year_min=2020,
            per_page=5
        )
        
        print(f"   Found {results2.get('total', 0)} Toyota Camrys")
        
        # Test 4: Price range search
        print("\n4. Testing price range search (Under $25k)...")
        results3 = client.search_vehicles(
            price_max=25000,
            year_min=2018,
            per_page=5
        )
        
        print(f"   Found {results3.get('total', 0)} vehicles under $25k")
        
        return total > 0
        
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = test_direct_cars_com()
    
    print("\n" + "=" * 60)
    print("🏆 DIRECT CARS.COM TEST RESULTS")
    print("=" * 60)
    
    if success:
        print("✅ SUCCESS - Direct Cars.com implementation working!")
        print("💡 This can replace the broken Marketcheck integration")
    else:
        print("❌ FAILED - Direct implementation needs work")
        print("💡 May need to adjust parsing or handle anti-bot measures")

if __name__ == "__main__":
    main()