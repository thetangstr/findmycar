const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true 
  });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  console.log('=== FINDMYCAR DETAILED INVESTIGATION ===\n');
  
  // Track all network activity
  const requests = [];
  const responses = [];
  
  page.on('request', request => {
    requests.push({
      url: request.url(),
      method: request.method(),
      resourceType: request.resourceType()
    });
  });
  
  page.on('response', response => {
    responses.push({
      url: response.url(),
      status: response.status(),
      statusText: response.statusText()
    });
  });
  
  // Track console messages
  const consoleMessages = [];
  page.on('console', msg => {
    consoleMessages.push({
      type: msg.type(),
      text: msg.text()
    });
  });
  
  try {
    // Navigate to homepage
    console.log('🏠 Navigating to homepage...');
    await page.goto('http://localhost:3000', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    // Take homepage screenshot
    await page.screenshot({ 
      path: 'detailed-homepage.png',
      fullPage: true 
    });
    console.log('✅ Homepage screenshot saved\n');
    
    // Check what vehicle cards are actually present
    console.log('🔍 Analyzing vehicle cards on homepage...');
    
    // Try multiple selectors to find vehicle cards
    const possibleSelectors = [
      '[data-testid="vehicle-card"]',
      '.vehicle-card',
      '.car-card', 
      '.listing-card',
      'a[href*="/vehicles/"]',
      '[class*="vehicle"]',
      '[class*="card"]'
    ];
    
    let vehicleCards = [];
    for (const selector of possibleSelectors) {
      const cards = await page.$$(selector);
      if (cards.length > 0) {
        console.log(`   Found ${cards.length} elements with selector: ${selector}`);
        vehicleCards = cards;
        break;
      }
    }
    
    if (vehicleCards.length === 0) {
      console.log('   ❌ No vehicle cards found with any selector');
      
      // Let's examine the page content more thoroughly
      const bodyText = await page.textContent('body');
      console.log('   Page contains "Featured Vehicles":', bodyText.includes('Featured Vehicles'));
      console.log('   Page contains "View All Vehicles":', bodyText.includes('View All Vehicles'));
      
      // Look for any links that might be vehicle detail links
      const allLinks = await page.$$('a');
      console.log(`   Total links on page: ${allLinks.length}`);
      
      for (let i = 0; i < Math.min(5, allLinks.length); i++) {
        const href = await allLinks[i].getAttribute('href');
        const text = await allLinks[i].textContent();
        if (href && (href.includes('vehicle') || href.includes('car'))) {
          console.log(`   Vehicle-related link: ${href} (${text?.trim()})`);
        }
      }
    } else {
      console.log(`   ✅ Found ${vehicleCards.length} vehicle cards\n`);
      
      // Extract details from each card
      for (let i = 0; i < Math.min(3, vehicleCards.length); i++) {
        const card = vehicleCards[i];
        console.log(`   Vehicle Card ${i + 1}:`);
        
        // Try to get the link href
        const link = await card.$('a');
        if (link) {
          const href = await link.getAttribute('href');
          console.log(`     Link: ${href}`);
          
          // Try to click this link to test for 404
          console.log(`     Testing link...`);
          try {
            const [response] = await Promise.all([
              page.waitForNavigation({ timeout: 5000 }),
              link.click()
            ]);
            
            const status = response?.status();
            const url = page.url();
            console.log(`     Response: ${status} - ${url}`);
            
            if (status === 404 || url.includes('404')) {
              console.log('     ❌ 404 ERROR CONFIRMED!');
              await page.screenshot({ 
                path: `404-error-card-${i + 1}.png`,
                fullPage: true 
              });
            } else {
              console.log('     ✅ Link works correctly');
              // Go back to test the next one
              await page.goBack({ waitUntil: 'networkidle' });
            }
          } catch (error) {
            console.log(`     ⚠️ Error testing link: ${error.message}`);
          }
        } else {
          console.log(`     No link found in this card`);
        }
        
        // Try to get text content
        const text = await card.textContent();
        console.log(`     Text: ${text?.trim()?.substring(0, 100)}...`);
        console.log('');
      }
    }
    
    // Check for eBay-related content and errors
    console.log('🏪 Checking eBay integration...');
    const ebayErrors = consoleMessages.filter(msg => 
      msg.text.toLowerCase().includes('ebay') && msg.type === 'error'
    );
    
    if (ebayErrors.length > 0) {
      console.log(`   ❌ Found ${ebayErrors.length} eBay-related errors:`);
      ebayErrors.forEach(error => {
        console.log(`     ${error.text}`);
      });
    } else {
      console.log('   ✅ No eBay-specific errors found');
    }
    
    // Check CORS errors specifically
    const corsErrors = consoleMessages.filter(msg => 
      msg.text.toLowerCase().includes('cors') && msg.type === 'error'
    );
    
    if (corsErrors.length > 0) {
      console.log(`   ❌ Found ${corsErrors.length} CORS errors:`);
      corsErrors.forEach(error => {
        console.log(`     ${error.text.substring(0, 200)}...`);
      });
    }
    
    // Check failed network requests
    console.log('\n🌐 Network Analysis:');
    const failedResponses = responses.filter(r => r.status >= 400);
    
    if (failedResponses.length > 0) {
      console.log(`   ❌ Found ${failedResponses.length} failed requests:`);
      failedResponses.forEach(resp => {
        console.log(`     ${resp.status} ${resp.statusText}: ${resp.url}`);
      });
    } else {
      console.log('   ✅ No failed HTTP requests');
    }
    
    // Check for eBay API calls
    const ebayRequests = requests.filter(r => r.url.includes('ebay'));
    if (ebayRequests.length > 0) {
      console.log(`   🔍 Found ${ebayRequests.length} eBay API attempts:`);
      ebayRequests.forEach(req => {
        console.log(`     ${req.method} ${req.url.substring(0, 100)}...`);
      });
    } else {
      console.log('   ⚠️ No eBay API requests detected');
    }
    
    // Test search functionality
    console.log('\n🔍 Testing search functionality...');
    const searchInput = await page.$('input[type="search"], input[placeholder*="search"], #search, .search-input, input[name="search"]');
    
    if (searchInput) {
      console.log('   ✅ Search input found');
      await searchInput.fill('Toyota');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(3000);
      
      const currentUrl = page.url();
      console.log(`   Navigated to: ${currentUrl}`);
      
      if (currentUrl.includes('search')) {
        console.log('   ✅ Search navigation works');
        
        // Check search results
        const searchCards = await page.$$('[data-testid="vehicle-card"], .vehicle-card, .car-card, .listing-card');
        console.log(`   Found ${searchCards.length} search results`);
        
        await page.screenshot({ 
          path: 'search-results.png',
          fullPage: true 
        });
      } else {
        console.log('   ❌ Search did not navigate to search page');
      }
    } else {
      console.log('   ❌ No search input found');
    }
    
    // Final analysis
    console.log('\n=== SUMMARY ===');
    console.log(`Total console messages: ${consoleMessages.length}`);
    console.log(`Total network requests: ${requests.length}`);
    console.log(`Failed responses: ${failedResponses.length}`);
    console.log(`CORS errors: ${corsErrors.length}`);
    console.log(`eBay API attempts: ${ebayRequests.length}`);
    console.log(`eBay-related errors: ${ebayErrors.length}`);
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
  } finally {
    await browser.close();
  }
})();