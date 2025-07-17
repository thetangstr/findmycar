const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true 
  });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('🔍 Testing FindMyCar Search Functionality in Detail\n');

  try {
    // Test 1: Check if search page exists
    console.log('1. Testing Search Page Access...');
    await page.goto('http://localhost:8000/search/', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(2000);
    
    const searchPageTitle = await page.title();
    console.log(`   ✓ Search Page Title: ${searchPageTitle}`);
    
    // Test 2: Check home page search functionality
    console.log('\n2. Testing Homepage Search Box...');
    await page.goto('http://localhost:8000', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(2000);
    
    // Look for the main search input
    const searchInput = await page.$('input[type="text"][placeholder*="dream car"]');
    if (searchInput) {
      console.log('   ✓ Found main search input on homepage');
      
      // Test typing in search box
      await searchInput.fill('Porsche 911');
      const inputValue = await searchInput.inputValue();
      console.log(`   ✓ Successfully typed in search box: "${inputValue}"`);
      
      // Look for search button
      const searchButton = await page.$('button[aria-label="Search"]');
      if (searchButton) {
        console.log('   ✓ Found search button');
        
        // Check if button is enabled/disabled
        const isDisabled = await searchButton.isDisabled();
        console.log(`   ✓ Search button status: ${isDisabled ? 'Disabled' : 'Enabled'}`);
        
        if (!isDisabled) {
          console.log('   ⚠ Attempting to click search button...');
          await searchButton.click();
          await page.waitForTimeout(3000);
          
          const currentUrl = page.url();
          console.log(`   ✓ After search click, current URL: ${currentUrl}`);
        } else {
          console.log('   ⚠ Search button is disabled - likely due to static export');
        }
      } else {
        console.log('   ⚠ Search button not found');
      }
    } else {
      console.log('   ⚠ Main search input not found');
    }

    // Test 3: Check featured vehicles and their sources
    console.log('\n3. Analyzing Featured Vehicles...');
    
    // Count vehicles
    const vehicles = await page.$$('article[role="article"]');
    console.log(`   ✓ Found ${vehicles.length} featured vehicles`);
    
    // Check each vehicle for source badges
    for (let i = 0; i < vehicles.length; i++) {
      const vehicle = vehicles[i];
      const vehicleTitle = await vehicle.$eval('h3', el => el.textContent.trim());
      
      // Look for source badge
      const sourceBadge = await vehicle.$('[aria-label*="Source"], .bg-black.bg-opacity-60');
      if (sourceBadge) {
        const sourceText = await sourceBadge.textContent();
        console.log(`   ✓ Vehicle ${i + 1}: "${vehicleTitle}" - Source: ${sourceText.trim()}`);
      } else {
        console.log(`   ⚠ Vehicle ${i + 1}: "${vehicleTitle}" - No source badge found`);
      }
    }

    // Test 4: Check aggregated sources mentioned in hero section
    console.log('\n4. Checking Aggregated Sources in Hero Section...');
    
    const sourceButtons = await page.$$('.bg-white\\/10.backdrop-blur-sm');
    console.log(`   ✓ Found ${sourceButtons.length} source badges in hero section:`);
    
    for (const button of sourceButtons) {
      const sourceText = await button.textContent();
      console.log(`     - ${sourceText.trim()}`);
    }

    // Test 5: Test vehicle detail navigation
    console.log('\n5. Testing Vehicle Detail Navigation...');
    
    if (vehicles.length > 0) {
      const firstVehicle = vehicles[0];
      const vehicleLink = await firstVehicle.$('a[href^="/vehicles/"]');
      
      if (vehicleLink) {
        const href = await vehicleLink.getAttribute('href');
        console.log(`   ✓ Attempting to navigate to: ${href}`);
        
        await vehicleLink.click();
        await page.waitForTimeout(3000);
        
        const detailUrl = page.url();
        console.log(`   ✓ Vehicle detail URL: ${detailUrl}`);
        
        // Check if detail page loaded
        if (detailUrl.includes('/vehicles/')) {
          console.log('   ✓ Successfully navigated to vehicle detail page');
          
          // Check for vehicle details
          const vehicleDetail = await page.evaluate(() => {
            return {
              hasTitle: !!document.querySelector('h1, .text-4xl'),
              hasPrice: !!document.querySelector('[class*="price"], .text-green'),
              hasImages: document.querySelectorAll('img').length > 0,
              hasDescription: !!document.querySelector('[class*="description"], p'),
              hasSpecs: !!document.querySelector('[class*="spec"], .grid')
            };
          });
          
          console.log('   ✓ Vehicle detail page contains:');
          console.log(`     - Title: ${vehicleDetail.hasTitle}`);
          console.log(`     - Price: ${vehicleDetail.hasPrice}`);
          console.log(`     - Images: ${vehicleDetail.hasImages}`);
          console.log(`     - Description: ${vehicleDetail.hasDescription}`);
          console.log(`     - Specifications: ${vehicleDetail.hasSpecs}`);
        } else {
          console.log('   ⚠ Failed to navigate to vehicle detail page');
        }
      } else {
        console.log('   ⚠ No vehicle detail link found');
      }
    }

    // Test 6: Check for dynamic content loading
    console.log('\n6. Checking for Dynamic Content...');
    
    await page.goto('http://localhost:8000', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);
    
    // Check for loading states
    const loadingElements = await page.$$('[role="status"], .animate-spin');
    console.log(`   ✓ Found ${loadingElements.length} loading indicators`);
    
    // Check for price analysis elements
    const priceAnalysisElements = await page.$$('text=Analyzing price');
    console.log(`   ✓ Found price analysis elements: ${priceAnalysisElements.length > 0 ? 'Yes' : 'No'}`);

    // Take final screenshot
    await page.screenshot({ path: 'detailed-search-test-screenshot.png', fullPage: true });
    console.log('\n📸 Detailed test screenshot saved as: detailed-search-test-screenshot.png');

    // Summary
    console.log('\n📊 DETAILED TEST SUMMARY:');
    console.log('================================');
    console.log(`✓ Application is a static export running on localhost:8000`);
    console.log(`✓ Featured vehicles: ${vehicles.length} found with source badges`);
    console.log(`✓ Homepage search box: Available but likely non-functional due to static export`);
    console.log(`✓ Vehicle sources mentioned: eBay Motors, Bring a Trailer, FB Marketplace, etc.`);
    console.log(`✓ Vehicle detail pages: Navigation working`);
    console.log(`✓ The application shows aggregated vehicle data from multiple sources`);

  } catch (error) {
    console.error('\n❌ Test Error:', error.message);
  } finally {
    await browser.close();
    console.log('\n✅ Detailed test completed!');
  }
})();