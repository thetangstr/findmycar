const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true 
  });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  console.log('=== TESTING VEHICLE DETAIL LINKS ===\n');
  
  try {
    // Navigate to homepage
    await page.goto('http://localhost:3000', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    console.log('🔍 Finding vehicle detail links...');
    
    // Wait a bit for content to load
    await page.waitForTimeout(2000);
    
    // Look for actual clickable elements
    const clickableElements = await page.$$('button, a, [role="button"]');
    console.log(`Found ${clickableElements.length} total clickable elements`);
    
    // Filter for vehicle-related links
    const vehicleLinks = [];
    for (const element of clickableElements) {
      const text = await element.textContent();
      const href = await element.getAttribute('href');
      const onclick = await element.getAttribute('onclick');
      
      if ((text && (text.includes('View Details') || text.includes('Details'))) ||
          (href && href.includes('/vehicles/')) ||
          (onclick && onclick.includes('vehicle'))) {
        vehicleLinks.push({
          element,
          text: text?.trim(),
          href,
          onclick,
          tagName: await element.evaluate(el => el.tagName)
        });
      }
    }
    
    console.log(`Found ${vehicleLinks.length} potential vehicle links:`);
    vehicleLinks.forEach((link, i) => {
      console.log(`  ${i + 1}. ${link.tagName}: "${link.text}" href="${link.href}" onclick="${link.onclick}"`);
    });
    
    if (vehicleLinks.length > 0) {
      console.log('\n🖱️ Testing the first vehicle link...');
      const firstLink = vehicleLinks[0];
      
      try {
        // Click and wait for navigation
        const [response] = await Promise.all([
          page.waitForNavigation({ waitUntil: 'networkidle' }).catch(() => null),
          firstLink.element.click()
        ]);
        
        await page.waitForTimeout(2000);
        
        const currentUrl = page.url();
        const statusCode = response ? response.status() : 'No navigation';
        
        console.log(`  Result: ${statusCode} - ${currentUrl}`);
        
        if (currentUrl.includes('404') || statusCode === 404) {
          console.log('  ❌ 404 ERROR CONFIRMED!');
          await page.screenshot({ 
            path: 'confirmed-404-error.png',
            fullPage: true 
          });
          
          // Check if it's a Next.js 404 page
          const pageContent = await page.textContent('body');
          if (pageContent.includes('This page could not be found') || 
              pageContent.includes('404') ||
              currentUrl.includes('404')) {
            console.log('  📄 This appears to be a Next.js 404 page');
            
            // Check the URL structure
            console.log(`  🔗 Attempted URL: ${currentUrl}`);
            if (currentUrl.includes('/vehicles/')) {
              const vehicleId = currentUrl.split('/vehicles/')[1].replace('/', '');
              console.log(`  🆔 Vehicle ID from URL: ${vehicleId}`);
            }
          }
        } else {
          console.log('  ✅ Link works correctly!');
          await page.screenshot({ 
            path: 'working-vehicle-page.png',
            fullPage: true 
          });
        }
        
      } catch (error) {
        console.log(`  ❌ Error clicking link: ${error.message}`);
      }
    } else {
      console.log('❌ No vehicle links found to test');
      
      // Let's check for any links at all
      const allLinks = await page.$$('a');
      console.log(`\nFound ${allLinks.length} total <a> tags:`);
      
      for (let i = 0; i < Math.min(10, allLinks.length); i++) {
        const href = await allLinks[i].getAttribute('href');
        const text = await allLinks[i].textContent();
        console.log(`  ${i + 1}. href="${href}" text="${text?.trim().substring(0, 50)}"`);
      }
    }
    
    // Also check the page source to see how vehicles are structured
    console.log('\n📄 Checking page structure...');
    const content = await page.content();
    
    // Look for vehicle data in the HTML
    if (content.includes('ebay-porsche-1')) {
      console.log('✅ Found ebay-porsche-1 vehicle ID in page');
    }
    if (content.includes('bat-corvette-1')) {
      console.log('✅ Found bat-corvette-1 vehicle ID in page');
    }
    if (content.includes('autotrader-nsx-1')) {
      console.log('✅ Found autotrader-nsx-1 vehicle ID in page');
    }
    
    // Check if there are any React components with vehicle data
    if (content.includes('vehicle') || content.includes('Vehicle')) {
      console.log('✅ Page contains vehicle-related content');
    }
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
  } finally {
    await browser.close();
  }
})();