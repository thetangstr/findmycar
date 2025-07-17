#!/usr/bin/env python3
"""
Test each data source individually to ensure listings are coming through
Uses both direct client testing and web interface testing with Playwright
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from playwright.async_api import async_playwright
import subprocess
import time
import json
from database import SessionLocal, Vehicle
from ingestion import (
    ingest_data, ingest_carmax_data, ingest_bat_data, 
    ingest_cargurus_data, ingest_autotrader_data
)

class SourceTester:
    def __init__(self):
        self.results = {}
        self.app_process = None
        self.base_url = "http://localhost:8000"
    
    async def start_app(self):
        """Start the FastAPI application"""
        print("🚀 Starting FastAPI application...")
        self.app_process = subprocess.Popen([
            "python", "-m", "uvicorn", "main:app", "--reload", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for app to start
        await asyncio.sleep(5)
        print("✅ Application started")
    
    def stop_app(self):
        """Stop the FastAPI application"""
        if self.app_process:
            self.app_process.terminate()
            self.app_process.wait()
            print("🛑 Application stopped")
    
    def test_direct_ingestion(self, source_name, ingest_function, query="Honda Civic"):
        """Test direct ingestion from a source"""
        print(f"\n🧪 Testing {source_name} direct ingestion...")
        
        try:
            db = SessionLocal()
            
            # Clear any existing data for this source to get fresh results
            db.query(Vehicle).filter(Vehicle.source == source_name.lower()).delete()
            db.commit()
            
            # Test ingestion
            result = ingest_function(db, query, limit=3)
            
            # Check results
            if result.get('success'):
                ingested = result.get('ingested', 0)
                errors = result.get('errors', 0)
                
                # Count vehicles in database
                vehicle_count = db.query(Vehicle).filter(Vehicle.source == source_name.lower()).count()
                
                self.results[source_name] = {
                    'direct_test': 'PASS' if ingested > 0 else 'FAIL',
                    'ingested': ingested,
                    'errors': errors,
                    'db_count': vehicle_count,
                    'error_msg': None
                }
                
                if ingested > 0:
                    # Get sample vehicle
                    sample_vehicle = db.query(Vehicle).filter(Vehicle.source == source_name.lower()).first()
                    if sample_vehicle:
                        self.results[source_name]['sample'] = {
                            'title': sample_vehicle.title,
                            'price': sample_vehicle.price,
                            'make': sample_vehicle.make,
                            'model': sample_vehicle.model,
                            'year': sample_vehicle.year
                        }
                
                print(f"   ✅ {source_name}: {ingested} vehicles ingested, {errors} errors")
                if vehicle_count > 0:
                    sample = db.query(Vehicle).filter(Vehicle.source == source_name.lower()).first()
                    print(f"   📋 Sample: {sample.title} - ${sample.price:,.0f}" if sample and sample.price else f"   📋 Sample: {sample.title}")
            else:
                self.results[source_name] = {
                    'direct_test': 'FAIL',
                    'ingested': 0,
                    'errors': 1,
                    'error_msg': result.get('error', 'Unknown error')
                }
                print(f"   ❌ {source_name}: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            self.results[source_name] = {
                'direct_test': 'FAIL',
                'ingested': 0,
                'errors': 1,
                'error_msg': str(e)
            }
            print(f"   ❌ {source_name}: Exception - {e}")
        finally:
            db.close()
    
    async def test_web_interface(self, browser):
        """Test the web interface for each source"""
        print(f"\n🌐 Testing web interface...")
        
        try:
            page = await browser.new_page()
            
            # Navigate to the main page
            await page.goto(self.base_url)
            await page.wait_for_load_state('networkidle')
            
            # Test each source via the web interface
            sources_to_test = ['ebay', 'carmax', 'bringatrailer', 'cargurus', 'autotrader']
            
            for source in sources_to_test:
                print(f"   🔍 Testing {source} via web interface...")
                
                try:
                    # Uncheck all sources first
                    for s in sources_to_test:
                        checkbox = page.locator(f"input[value='{s}']")
                        if await checkbox.is_checked():
                            await checkbox.uncheck()
                    
                    # Check only the current source
                    source_checkbox = page.locator(f"input[value='{source}']")
                    await source_checkbox.check()
                    
                    # Enter search query
                    search_input = page.locator("input[name='query']")
                    await search_input.fill(f"Honda Civic source:{source}")
                    
                    # Submit search
                    search_button = page.locator("button[type='submit']")
                    await search_button.click()
                    
                    # Wait for results or error
                    await page.wait_for_timeout(10000)  # Wait 10 seconds for ingestion
                    
                    # Check if vehicles were found
                    vehicle_cards = page.locator(".vehicle-card")
                    vehicle_count = await vehicle_cards.count()
                    
                    if source not in self.results:
                        self.results[source] = {}
                    
                    self.results[source]['web_test'] = 'PASS' if vehicle_count > 0 else 'FAIL'
                    self.results[source]['web_vehicle_count'] = vehicle_count
                    
                    print(f"      {'✅' if vehicle_count > 0 else '❌'} Found {vehicle_count} vehicles via web interface")
                    
                    # If vehicles found, get sample data
                    if vehicle_count > 0:
                        first_vehicle = vehicle_cards.first
                        title = await first_vehicle.locator(".vehicle-title").text_content()
                        price = await first_vehicle.locator(".vehicle-price").text_content()
                        print(f"      📋 Sample: {title} - {price}")
                    
                except Exception as e:
                    if source not in self.results:
                        self.results[source] = {}
                    self.results[source]['web_test'] = 'FAIL'
                    self.results[source]['web_error'] = str(e)
                    print(f"      ❌ Web test failed: {e}")
            
            await page.close()
            
        except Exception as e:
            print(f"   ❌ Web interface test failed: {e}")
    
    def print_summary(self):
        """Print a comprehensive summary of all test results"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE SOURCE TEST RESULTS")
        print("="*80)
        
        total_sources = len(self.results)
        passing_direct = sum(1 for r in self.results.values() if r.get('direct_test') == 'PASS')
        passing_web = sum(1 for r in self.results.values() if r.get('web_test') == 'PASS')
        
        print(f"Total Sources Tested: {total_sources}")
        print(f"Direct Ingestion Passing: {passing_direct}/{total_sources}")
        print(f"Web Interface Passing: {passing_web}/{total_sources}")
        print()
        
        for source, results in self.results.items():
            print(f"🔷 {source.upper()}")
            print(f"   Direct Test: {results.get('direct_test', 'NOT_TESTED')}")
            print(f"   Web Test: {results.get('web_test', 'NOT_TESTED')}")
            print(f"   Vehicles Ingested: {results.get('ingested', 0)}")
            
            if results.get('sample'):
                sample = results['sample']
                price_str = f"${sample['price']:,.0f}" if sample.get('price') else "No price"
                print(f"   Sample Vehicle: {sample.get('year', '?')} {sample.get('make', '?')} {sample.get('model', '?')} - {price_str}")
            
            if results.get('error_msg'):
                print(f"   Error: {results['error_msg']}")
            
            print()
        
        # Overall assessment
        if passing_direct == total_sources and passing_web == total_sources:
            print("🎉 ALL TESTS PASSED! All sources are working correctly.")
        elif passing_direct == total_sources:
            print("✅ All direct ingestion tests passed. Some web interface issues detected.")
        else:
            print("⚠️  Some sources have issues. Check individual results above.")

async def main():
    tester = SourceTester()
    
    try:
        # Start the application
        await tester.start_app()
        
        # Test direct ingestion for each source
        print("🧪 TESTING DIRECT INGESTION")
        print("="*50)
        
        tester.test_direct_ingestion('ebay', ingest_data)
        tester.test_direct_ingestion('carmax', ingest_carmax_data)
        tester.test_direct_ingestion('bringatrailer', ingest_bat_data)
        tester.test_direct_ingestion('cargurus', ingest_cargurus_data)
        tester.test_direct_ingestion('autotrader', ingest_autotrader_data)
        
        # Test web interface with Playwright
        print("\n🌐 TESTING WEB INTERFACE")
        print("="*50)
        
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            await tester.test_web_interface(browser)
            await browser.close()
        
        # Print comprehensive summary
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        tester.stop_app()

if __name__ == "__main__":
    asyncio.run(main())