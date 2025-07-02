#!/usr/bin/env python3

"""
Quick test to verify the data quality modal functionality
"""

from playwright.sync_api import sync_playwright
import time

def test_data_quality_modal():
    """Test that the data quality modal opens and displays correct information"""
    
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
            
            # Find and click the "Learn more" link
            print("🔍 Looking for data quality notice link...")
            learn_more_link = page.locator("a[href='#dataNotice']")
            
            if learn_more_link.count() > 0:
                print("✅ Found 'Learn more' link")
                learn_more_link.click()
                
                # Wait for modal to appear
                print("⏳ Waiting for modal to appear...")
                page.wait_for_selector("#dataNotice", timeout=5000)
                
                # Check modal content
                modal = page.locator("#dataNotice")
                
                # Verify modal title
                title = modal.locator(".modal-title").text_content()
                print(f"📋 Modal title: {title}")
                
                # Check for key content elements
                content_checks = [
                    ("eBay Motors", "eBay Motors integration mentioned"),
                    ("Coming Soon", "Cars.com status indicated"),
                    ("professional automotive APIs", "API upgrade mentioned"),
                    ("real, current", "Data quality promise"),
                    ("100% real listings", "Current status confirmation")
                ]
                
                for search_text, description in content_checks:
                    if search_text in modal.text_content():
                        print(f"✅ {description}")
                    else:
                        print(f"❌ Missing: {description}")
                
                # Close modal
                print("🔄 Closing modal...")
                modal.locator("button[data-dismiss='modal']").click()
                
                # Wait for modal to close
                time.sleep(1)
                print("✅ Modal test completed successfully")
                
            else:
                print("❌ 'Learn more' link not found")
                
            # Check Cars.com checkbox status
            print("🔍 Checking Cars.com checkbox status...")
            cars_checkbox = page.locator("#sourceCars")
            
            if cars_checkbox.is_disabled():
                print("✅ Cars.com checkbox is properly disabled")
            else:
                print("❌ Cars.com checkbox should be disabled")
                
            # Check for "Coming Soon" badge
            coming_soon_badge = page.locator(".badge-warning:has-text('Coming Soon')")
            if coming_soon_badge.count() > 0:
                print("✅ 'Coming Soon' badge is displayed")
            else:
                print("❌ 'Coming Soon' badge not found")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    print("🧪 Testing Data Quality Modal...")
    test_data_quality_modal()
    print("🏁 Test completed")