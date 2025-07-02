#!/usr/bin/env python3

"""
Test Auto.dev UI integration
"""

from playwright.sync_api import sync_playwright
import time

def test_autodev_ui():
    """Test that Auto.dev integration works in the UI"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        try:
            # Navigate to the application
            print("🌐 Opening AutoNavigator application...")
            page.goto("http://localhost:8000")
            
            # Wait for page to load
            page.wait_for_selector("h1", timeout=10000)
            print("✅ Page loaded successfully")
            
            # Expand advanced filters first
            print("🔧 Expanding advanced filters...")
            toggle_button = page.locator("button:has-text('Show Advanced Filters')")
            if toggle_button.count() > 0:
                toggle_button.click()
                time.sleep(1)
                print("✅ Advanced filters expanded")
            
            # Check if Auto.dev checkbox is available
            autodev_checkbox = page.locator("#sourceAutoDev")
            if autodev_checkbox.count() > 0:
                print("✅ Auto.dev checkbox found")
                
                # Check that it's enabled
                if not autodev_checkbox.is_disabled():
                    print("✅ Auto.dev checkbox is enabled")
                else:
                    print("❌ Auto.dev checkbox is disabled")
                    
                # Check for "New!" badge
                new_badge = page.locator(".badge-success:has-text('New!')")
                if new_badge.count() > 0:
                    print("✅ 'New!' badge is displayed for Auto.dev")
                else:
                    print("❌ 'New!' badge not found")
                    
                # Test search with Auto.dev source
                print("🔍 Testing search with Auto.dev...")
                
                # Fill in search query
                page.fill("#query", "Honda Civic 2020")
                
                # Check Auto.dev checkbox
                autodev_checkbox.check()
                
                # Submit search
                page.click("button[type='submit']")
                
                # Wait for results or redirect
                print("⏳ Waiting for search results...")
                page.wait_for_url("*", timeout=30000)
                
                # Check if we have vehicles
                time.sleep(2)  # Give time for page to fully load
                
                # Look for Auto.dev vehicles
                autodev_buttons = page.locator("a:has-text('View on Auto.dev')")
                if autodev_buttons.count() > 0:
                    print(f"✅ Found {autodev_buttons.count()} Auto.dev listings")
                    
                    # Click on first Auto.dev listing to test link
                    first_button = autodev_buttons.first
                    href = first_button.get_attribute("href")
                    print(f"📄 First Auto.dev listing URL: {href}")
                    
                    if href and "auto.dev" in href.lower():
                        print("✅ Auto.dev listing has correct URL format")
                    else:
                        print("❌ Auto.dev listing URL format issue")
                        
                else:
                    print("❌ No Auto.dev listings found")
                    
                    # Check if any vehicles at all
                    all_vehicles = page.locator(".vehicle-card")
                    print(f"🔍 Total vehicles found: {all_vehicles.count()}")
                    
            else:
                print("❌ Auto.dev checkbox not found")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    print("🧪 Testing Auto.dev UI Integration...")
    test_autodev_ui()
    print("🏁 Test completed")