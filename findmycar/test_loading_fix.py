#!/usr/bin/env python3
"""Simple test to check if loading overlay is hidden after page load."""

import asyncio
from playwright.async_api import async_playwright

async def test_loading_fix():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Visit page with message parameter (simulates redirect after search)
            print("🌐 Loading page with search message...")
            await page.goto("http://localhost:8601/?message=Search%20completed")
            
            # Wait for DOMContentLoaded
            await page.wait_for_load_state("domcontentloaded")
            print("✅ Page loaded")
            
            # Check loading overlay
            result = await page.evaluate("""
                () => {
                    const overlay = document.getElementById('loadingOverlay');
                    if (!overlay) return { found: false };
                    
                    const style = window.getComputedStyle(overlay);
                    const displayStyle = overlay.style.display;
                    
                    return {
                        found: true,
                        styleDisplay: displayStyle,
                        computedDisplay: style.display,
                        isVisible: style.display !== 'none' && displayStyle !== 'none',
                        classList: overlay.className
                    };
                }
            """)
            
            print(f"\n📊 Loading Overlay Status:")
            print(f"  - Found: {result['found']}")
            if result['found']:
                print(f"  - style.display: '{result['styleDisplay']}'")
                print(f"  - computed display: '{result['computedDisplay']}'")
                print(f"  - Is visible: {result['isVisible']}")
                
                if result['isVisible']:
                    print("\n❌ BUG: Loading overlay is still visible!")
                else:
                    print("\n✅ FIXED: Loading overlay is properly hidden!")
                    
            # Also check for any visible spinners
            spinners = await page.evaluate("""
                () => {
                    const spinners = document.querySelectorAll('.spinner-border:not([style*="display: none"]), .fa-spinner');
                    return spinners.length;
                }
            """)
            
            print(f"\n🔄 Visible spinners found: {spinners}")
            
            # Check if DOMContentLoaded handler exists
            has_handler = await page.evaluate("""
                () => {
                    return typeof window.searchProgressTracker !== 'undefined';
                }
            """)
            
            print(f"📍 Progress tracker initialized: {has_handler}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            await browser.close()

print("Testing loading overlay fix...\n")
asyncio.run(test_loading_fix())