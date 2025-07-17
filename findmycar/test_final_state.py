#!/usr/bin/env python3
"""Test the final state after search redirect."""

import asyncio
from playwright.async_api import async_playwright

async def test_final_state():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Capture console logs
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        try:
            # Go directly to a URL that simulates post-search redirect
            print("🌐 Loading page with search message (simulating redirect)...")
            test_url = "http://localhost:8601/?message=Successfully%20ingested%200%20vehicles%20from%205%20sources"
            await page.goto(test_url, wait_until="networkidle")
            
            # Wait for JS to execute
            await page.wait_for_timeout(2000)
            
            # Print console logs
            print("\n📋 Console logs:")
            for log in console_logs:
                print(f"  {log}")
            
            # Check loading overlay state
            overlay_info = await page.evaluate("""
                () => {
                    const overlay = document.getElementById('loadingOverlay');
                    if (!overlay) return { found: false };
                    
                    // Get all possible display states
                    const computedStyle = window.getComputedStyle(overlay);
                    const rect = overlay.getBoundingClientRect();
                    
                    return {
                        found: true,
                        inlineDisplay: overlay.style.display,
                        computedDisplay: computedStyle.display,
                        visibility: computedStyle.visibility,
                        opacity: computedStyle.opacity,
                        isVisible: rect.width > 0 && rect.height > 0 && computedStyle.display !== 'none',
                        className: overlay.className,
                        hasSpinner: overlay.querySelector('.spinner-border') !== null
                    };
                }
            """)
            
            print("\n📊 Loading Overlay Analysis:")
            for key, value in overlay_info.items():
                print(f"  - {key}: {value}")
            
            # Check for stuck UI elements
            stuck_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    
                    // Check for any visible spinners
                    document.querySelectorAll('.spinner-border, .fa-spinner').forEach(el => {
                        const style = window.getComputedStyle(el);
                        if (style.display !== 'none' && style.visibility !== 'hidden') {
                            elements.push({
                                type: 'spinner',
                                class: el.className,
                                parent: el.parentElement?.className
                            });
                        }
                    });
                    
                    // Check for "Searching..." text
                    document.querySelectorAll('*').forEach(el => {
                        if (el.textContent && el.textContent.includes('Searching...') && el.children.length === 0) {
                            elements.push({
                                type: 'searching_text',
                                tag: el.tagName,
                                class: el.className
                            });
                        }
                    });
                    
                    return elements;
                }
            """)
            
            if stuck_elements:
                print("\n⚠️  Stuck UI elements found:")
                for elem in stuck_elements:
                    print(f"  - {elem}")
            else:
                print("\n✅ No stuck UI elements found")
            
            # Check success message
            success_alert = await page.query_selector(".alert-success")
            if success_alert:
                text = await success_alert.text_content()
                print(f"\n✅ Success message: {text.strip()}")
            
            # Take screenshot
            await page.screenshot(path="/tmp/final_state.png", full_page=True)
            print("\n📸 Screenshot: /tmp/final_state.png")
            
            # Final verdict
            if overlay_info.get('found') and not overlay_info.get('isVisible'):
                print("\n✅ SUCCESS: Loading overlay is properly hidden after redirect!")
            elif overlay_info.get('found') and overlay_info.get('isVisible'):
                print("\n❌ BUG: Loading overlay is still visible after redirect!")
            else:
                print("\n⚠️  Loading overlay not found in DOM")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            
        finally:
            print("\n🎬 Test complete! Browser will close in 5 seconds...")
            await page.wait_for_timeout(5000)
            await browser.close()

print("🚗 Testing final state after search redirect\n")
asyncio.run(test_final_state())