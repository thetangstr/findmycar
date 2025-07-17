#!/usr/bin/env python3
"""Debug test for search functionality with console monitoring."""

import asyncio
from playwright.async_api import async_playwright
import time

async def test_search_with_debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Capture console logs
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        # Monitor responses
        responses = []
        def handle_response(response):
            responses.append({
                'url': response.url,
                'status': response.status,
                'method': response.request.method
            })
        page.on("response", handle_response)
        
        try:
            print("🌐 Loading CarGPT homepage...")
            await page.goto("http://localhost:8601", wait_until="networkidle")
            print("✅ Homepage loaded")
            
            # Wait for JS to initialize
            await page.wait_for_timeout(2000)
            
            # Print initial console logs
            print("\n📋 Initial console logs:")
            for log in console_logs:
                print(f"  {log}")
            console_logs.clear()
            
            # Enter search query
            print("\n🔍 Entering search query...")
            await page.fill('input[name="query"]', "honda civic eg6")
            
            # Click search button
            search_button = await page.query_selector('button[type="submit"]')
            if search_button:
                print("🚀 Clicking search button...")
                
                # Start monitoring
                start_time = time.time()
                
                # Click and don't wait for navigation
                await search_button.click()
                
                # Monitor for a few seconds
                print("\n⏳ Monitoring search progress...")
                for i in range(10):  # Monitor for 10 seconds
                    await page.wait_for_timeout(1000)
                    
                    # Check loading overlay
                    is_visible = await page.evaluate("""
                        () => {
                            const overlay = document.getElementById('loadingOverlay');
                            return overlay ? window.getComputedStyle(overlay).display !== 'none' : false;
                        }
                    """)
                    
                    # Check current URL
                    current_url = page.url
                    
                    print(f"\n[{i+1}s] Status check:")
                    print(f"  - URL: {current_url[:80]}...")
                    print(f"  - Loading overlay visible: {is_visible}")
                    print(f"  - Responses: {len(responses)}")
                    
                    # Print new console logs
                    if console_logs:
                        print("  - Console logs:")
                        for log in console_logs[-5:]:  # Last 5 logs
                            print(f"    {log}")
                        console_logs.clear()
                    
                    # Check if search completed
                    if "message=" in current_url:
                        print(f"\n✅ Search completed! Redirected after {time.time() - start_time:.1f}s")
                        break
                
                # Wait for page to stabilize
                await page.wait_for_timeout(2000)
                
                # Final state check
                print("\n📊 Final state:")
                final_url = page.url
                print(f"  - URL: {final_url}")
                
                # Check loading overlay final state
                overlay_state = await page.evaluate("""
                    () => {
                        const overlay = document.getElementById('loadingOverlay');
                        if (!overlay) return "not found";
                        const style = window.getComputedStyle(overlay);
                        return {
                            display: style.display,
                            visibility: style.visibility,
                            inlineStyle: overlay.style.display
                        };
                    }
                """)
                print(f"  - Loading overlay state: {overlay_state}")
                
                # Check for alerts
                alerts = await page.query_selector_all(".alert")
                print(f"  - Alerts found: {len(alerts)}")
                for alert in alerts[:2]:
                    text = await alert.text_content()
                    print(f"    • {text[:100]}...")
                
                # Final console logs
                if console_logs:
                    print("\n📋 Final console logs:")
                    for log in console_logs:
                        print(f"  {log}")
                
                # Screenshot
                await page.screenshot(path="/tmp/search_debug_final.png", full_page=True)
                print("\n📸 Screenshot: /tmp/search_debug_final.png")
                
            else:
                print("❌ Search button not found!")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await page.screenshot(path="/tmp/debug_error.png")
            
        finally:
            print("\n🎬 Test complete! Browser will close in 5 seconds...")
            await page.wait_for_timeout(5000)
            await browser.close()

print("🚗 Starting debug test for search functionality\n")
asyncio.run(test_search_with_debug())