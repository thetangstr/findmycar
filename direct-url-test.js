const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true 
  });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  console.log('=== TESTING DIRECT URLS FOR 404 ISSUES ===\n');
  
  // URLs to test based on the log errors
  const urlsToTest = [
    'http://localhost:3000/vehicles/ebay-porsche-1/',
    'http://localhost:3000/vehicles/ebay-porsche-1',
    'http://localhost:3000/vehicles/bat-corvette-1/',
    'http://localhost:3000/vehicles/bat-corvette-1',
    'http://localhost:3000/vehicles/autotrader-nsx-1/',
    'http://localhost:3000/vehicles/autotrader-nsx-1',
    'http://localhost:3000/vehicles/bat-2',  // This was in the log as 404
    'http://localhost:3000/vehicles/bat-2/', // This was in the log as 404
  ];
  
  for (const url of urlsToTest) {
    console.log(`🔗 Testing: ${url}`);
    
    try {
      const response = await page.goto(url, { 
        waitUntil: 'networkidle',
        timeout: 10000 
      });
      
      const status = response?.status();
      const finalUrl = page.url();
      
      console.log(`   Status: ${status}`);
      console.log(`   Final URL: ${finalUrl}`);
      
      if (status === 404 || finalUrl.includes('404')) {
        console.log('   ❌ 404 ERROR CONFIRMED!');
        
        // Check page content
        const pageText = await page.textContent('body');
        console.log(`   Page contains "404": ${pageText.includes('404')}`);
        console.log(`   Page contains "not found": ${pageText.toLowerCase().includes('not found')}`);
        
        await page.screenshot({ 
          path: `404-${url.split('/').pop().replace('/', '')}.png`,
          fullPage: true 
        });
      } else if (status === 200) {
        console.log('   ✅ Page loads successfully');
        
        // Check if it's actually a vehicle page
        const pageText = await page.textContent('body');
        if (pageText.includes('Vehicle Details') || pageText.includes('Make') || pageText.includes('Model')) {
          console.log('   ✅ Contains vehicle content');
        } else {
          console.log('   ⚠️ No vehicle content detected');
        }
      } else {
        console.log(`   ⚠️ Unexpected status: ${status}`);
      }
      
    } catch (error) {
      console.log(`   ❌ Error: ${error.message}`);
    }
    
    console.log('');
  }
  
  // Now test a search that might generate the problematic URLs
  console.log('🔍 Testing search functionality to see if it generates bad URLs...');
  
  try {
    await page.goto('http://localhost:3000/search', { 
      waitUntil: 'networkidle',
      timeout: 10000 
    });
    
    await page.screenshot({ 
      path: 'search-page.png',
      fullPage: true 
    });
    
    console.log('   ✅ Search page accessible');
    
    // Look for vehicle cards on search page
    const vehicleLinks = await page.$$('a[href*="/vehicles/"]');
    console.log(`   Found ${vehicleLinks.length} vehicle links on search page`);
    
    if (vehicleLinks.length > 0) {
      // Test a few links from search results
      for (let i = 0; i < Math.min(3, vehicleLinks.length); i++) {
        const href = await vehicleLinks[i].getAttribute('href');
        console.log(`   Testing search result link: ${href}`);
        
        try {
          await vehicleLinks[i].click();
          await page.waitForTimeout(2000);
          
          const currentUrl = page.url();
          const pageText = await page.textContent('body');
          
          if (currentUrl.includes('404') || pageText.includes('404')) {
            console.log(`     ❌ Link leads to 404: ${currentUrl}`);
          } else {
            console.log(`     ✅ Link works: ${currentUrl}`);
          }
          
          await page.goBack();
          await page.waitForTimeout(1000);
          
        } catch (error) {
          console.log(`     ❌ Error testing link: ${error.message}`);
        }
      }
    }
    
  } catch (error) {
    console.log(`   ❌ Error accessing search page: ${error.message}`);
  }
  
  await browser.close();
})();