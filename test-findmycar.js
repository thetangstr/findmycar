const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true 
  });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  console.log('Starting FindMyCar application test...\n');
  
  // Enable console logging
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`Console Error: ${msg.text()}`);
    }
  });
  
  // Monitor network requests
  const failedRequests = [];
  const apiRequests = [];
  
  page.on('requestfailed', request => {
    failedRequests.push({
      url: request.url(),
      failure: request.failure()
    });
  });
  
  page.on('request', request => {
    if (request.url().includes('api') || request.url().includes('ebay')) {
      apiRequests.push({
        url: request.url(),
        method: request.method()
      });
    }
  });
  
  page.on('response', response => {
    if (response.url().includes('api') || response.url().includes('ebay')) {
      console.log(`API Response: ${response.url()} - Status: ${response.status()}`);
    }
  });
  
  try {
    // Step 1: Navigate to homepage
    console.log('1. Navigating to http://localhost:3000...');
    await page.goto('http://localhost:3000', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    // Take screenshot of homepage
    await page.screenshot({ 
      path: 'homepage-screenshot.png',
      fullPage: true 
    });
    console.log('   ✓ Homepage screenshot saved');
    
    // Step 2: Check for vehicle listings
    console.log('\n2. Checking for vehicle listings...');
    const vehicleCards = await page.$$('[data-testid="vehicle-card"], .vehicle-card, .car-card, .listing-card, [class*="vehicle"], [class*="listing"]');
    console.log(`   Found ${vehicleCards.length} vehicle cards`);
    
    // Get vehicle information
    if (vehicleCards.length > 0) {
      console.log('\n   Vehicle details:');
      for (let i = 0; i < Math.min(3, vehicleCards.length); i++) {
        const card = vehicleCards[i];
        const title = await card.$eval('h2, h3, .title, [class*="title"]', el => el.textContent).catch(() => 'No title');
        const price = await card.$eval('[class*="price"], .price', el => el.textContent).catch(() => 'No price');
        const source = await card.$eval('[class*="source"], .source', el => el.textContent).catch(() => 'Unknown source');
        console.log(`   - Vehicle ${i + 1}: ${title} | ${price} | Source: ${source}`);
      }
    }
    
    // Step 3: Check for eBay-specific elements
    console.log('\n3. Checking for eBay listings...');
    const ebayListings = await page.$$('[class*="ebay"], [data-source="ebay"], [src*="ebay"]');
    console.log(`   Found ${ebayListings.length} eBay-related elements`);
    
    // Step 4: Test search functionality
    console.log('\n4. Testing search functionality...');
    const searchInput = await page.$('input[type="search"], input[placeholder*="search"], #search, .search-input');
    if (searchInput) {
      await searchInput.fill('Toyota Camry');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(3000);
      
      const searchResults = await page.$$('[data-testid="vehicle-card"], .vehicle-card, .car-card, .listing-card');
      console.log(`   Search returned ${searchResults.length} results`);
      
      await page.screenshot({ 
        path: 'search-results-screenshot.png',
        fullPage: true 
      });
    }
    
    // Step 5: Test clicking on vehicle details
    console.log('\n5. Testing vehicle detail links...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    
    const detailLinks = await page.$$('a[href*="vehicle"], a[href*="car"], a[href*="detail"], button:has-text("View Details"), a:has-text("View Details")');
    console.log(`   Found ${detailLinks.length} detail links`);
    
    if (detailLinks.length > 0) {
      const firstLink = detailLinks[0];
      const href = await firstLink.getAttribute('href');
      console.log(`   First link URL: ${href}`);
      
      // Click and wait for navigation
      const [response] = await Promise.all([
        page.waitForNavigation({ waitUntil: 'networkidle' }).catch(() => null),
        firstLink.click()
      ]);
      
      await page.waitForTimeout(2000);
      
      const currentUrl = page.url();
      const statusCode = response ? response.status() : 'No response';
      console.log(`   Navigated to: ${currentUrl}`);
      console.log(`   Response status: ${statusCode}`);
      
      if (currentUrl.includes('404') || statusCode === 404) {
        console.log('   ⚠️  404 ERROR DETECTED!');
        await page.screenshot({ 
          path: '404-error-screenshot.png',
          fullPage: true 
        });
      }
    }
    
    // Step 6: Check page source for data
    console.log('\n6. Checking page source for vehicle data...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    
    const pageContent = await page.content();
    const hasEbayContent = pageContent.toLowerCase().includes('ebay');
    const hasApiCalls = apiRequests.filter(req => req.url.includes('ebay')).length > 0;
    
    console.log(`   Page contains eBay references: ${hasEbayContent}`);
    console.log(`   eBay API calls made: ${hasApiCalls}`);
    
    // Report findings
    console.log('\n=== TEST SUMMARY ===');
    console.log(`Failed network requests: ${failedRequests.length}`);
    if (failedRequests.length > 0) {
      failedRequests.forEach(req => {
        console.log(`  - ${req.url}: ${req.failure}`);
      });
    }
    
    console.log(`\nAPI requests made: ${apiRequests.length}`);
    apiRequests.forEach(req => {
      console.log(`  - ${req.method} ${req.url}`);
    });
    
  } catch (error) {
    console.error('Test error:', error);
  } finally {
    await browser.close();
  }
})();