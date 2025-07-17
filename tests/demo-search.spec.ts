import { test, expect } from '@playwright/test';

test.describe('Demo Search Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the search page
    await page.goto('http://localhost:3000/search');
    await page.waitForLoadState('networkidle');
  });

  test('AC1: Web server is accessible and search page loads', async ({ page }) => {
    // Verify the page loads successfully
    await expect(page).toHaveTitle(/FindMyCar/);
    
    // Verify search page elements are present
    await expect(page.locator('h2').filter({ hasText: 'Intelligent Car Search' })).toBeVisible();
    await expect(page.locator('input[placeholder*="What are you looking for"]')).toBeVisible();
    await expect(page.locator('button').filter({ hasText: 'Search' })).toBeVisible();
  });

  test('AC2: Hardcoded search returns exactly 4 Porsche 911 vehicles', async ({ page }) => {
    // Perform a search that should trigger demo results
    await page.fill('input[placeholder*="What are you looking for"]', 'BMW sedan');
    await page.click('button:has-text("Search")');
    
    // Wait for results to load
    await page.waitForSelector('[data-testid="vehicle-card"], .vehicle-card, [class*="vehicle"]', { timeout: 10000 });
    
    // Count the number of vehicle cards
    const vehicleCards = page.locator('[data-testid="vehicle-card"], .vehicle-card, [class*="grid"] > div:has(img)');
    await expect(vehicleCards).toHaveCount(4);
    
    // Verify all vehicles are Porsche 911s
    const vehicleTitles = vehicleCards.locator('h3, [class*="title"], [class*="make"], [class*="model"]');
    for (let i = 0; i < 4; i++) {
      const title = await vehicleTitles.nth(i).textContent();
      expect(title?.toLowerCase()).toContain('porsche');
      expect(title?.toLowerCase()).toContain('911');
    }
  });

  test('AC3: Vehicle details display correct information', async ({ page }) => {
    // Perform search
    await page.fill('input[placeholder*="What are you looking for"]', 'Honda civic');
    await page.click('button:has-text("Search")');
    
    // Wait for results
    await page.waitForSelector('[data-testid="vehicle-card"], .vehicle-card, [class*="grid"] > div:has(img)', { timeout: 10000 });
    
    const vehicleCards = page.locator('[data-testid="vehicle-card"], .vehicle-card, [class*="grid"] > div:has(img)');
    
    // Check each vehicle card for required information
    for (let i = 0; i < 4; i++) {
      const card = vehicleCards.nth(i);
      
      // Check for Porsche make
      await expect(card).toContainText('Porsche');
      
      // Check for 911 model
      await expect(card).toContainText('911');
      
      // Check year is between 1990-1994
      const cardText = await card.textContent();
      const yearMatch = cardText?.match(/19\d{2}/);
      if (yearMatch) {
        const year = parseInt(yearMatch[0]);
        expect(year).toBeGreaterThanOrEqual(1990);
        expect(year).toBeLessThanOrEqual(1994);
      }
      
      // Check for price (should be present)
      expect(cardText).toMatch(/\$[\d,]+/);
      
      // Check for mileage (should be present)
      expect(cardText).toMatch(/[\d,]+ miles|[\d,]+mi/i);
    }
  });

  test('AC4: Search consistency across different queries', async ({ page }) => {
    const queries = ['Toyota Camry', 'luxury car', 'electric vehicle', 'truck'];
    
    for (const query of queries) {
      // Clear and enter new search
      await page.fill('input[placeholder*="What are you looking for"]', '');
      await page.fill('input[placeholder*="What are you looking for"]', query);
      await page.click('button:has-text("Search")');
      
      // Wait for results
      await page.waitForSelector('[data-testid="vehicle-card"], .vehicle-card, [class*="grid"] > div:has(img)', { timeout: 10000 });
      
      // Verify exactly 4 vehicles returned
      const vehicleCards = page.locator('[data-testid="vehicle-card"], .vehicle-card, [class*="grid"] > div:has(img)');
      await expect(vehicleCards).toHaveCount(4);
      
      // Verify all are Porsche 911s
      for (let i = 0; i < 4; i++) {
        const cardText = await vehicleCards.nth(i).textContent();
        expect(cardText?.toLowerCase()).toContain('porsche');
        expect(cardText?.toLowerCase()).toContain('911');
      }
    }
  });

  test('AC5: Images are displayed correctly', async ({ page }) => {
    // Perform search
    await page.fill('input[placeholder*="What are you looking for"]', 'sports car');
    await page.click('button:has-text("Search")');
    
    // Wait for results and images
    await page.waitForSelector('img', { timeout: 10000 });
    
    const vehicleCards = page.locator('[data-testid="vehicle-card"], .vehicle-card, [class*="grid"] > div:has(img)');
    const images = vehicleCards.locator('img');
    
    // Verify all 4 vehicles have images
    await expect(images).toHaveCount(4);
    
    // Check that images are loaded (not broken)
    for (let i = 0; i < 4; i++) {
      const img = images.nth(i);
      await expect(img).toBeVisible();
      
      // Check if image src is valid (should contain either porsche or other_porsche path)
      const src = await img.getAttribute('src');
      expect(src).toMatch(/\/images\/(porsche|other_porsche)/);
    }
  });

  test('AC6: Search performance and loading states', async ({ page }) => {
    const startTime = Date.now();
    
    // Perform search and measure time
    await page.fill('input[placeholder*="What are you looking for"]', 'classic car');
    await page.click('button:has-text("Search")');
    
    // Wait for results to appear
    await page.waitForSelector('[data-testid="vehicle-card"], .vehicle-card, [class*="grid"] > div:has(img)', { timeout: 10000 });
    
    const endTime = Date.now();
    const searchTime = endTime - startTime;
    
    // Verify search completed within 2 seconds (allowing some buffer for test environment)
    expect(searchTime).toBeLessThan(5000);
    
    // Verify results are displayed
    const vehicleCards = page.locator('[data-testid="vehicle-card"], .vehicle-card, [class*="grid"] > div:has(img)');
    await expect(vehicleCards).toHaveCount(4);
  });

  test('Natural language search returns demo results', async ({ page }) => {
    // Test with natural language search
    await page.fill('input[placeholder*="What are you looking for"]', 'I want a reliable sports car under $80,000');
    
    // Enable "Show AI's thinking" to see demo messages
    const thinkingCheckbox = page.locator('input[type="checkbox"]').filter({ hasText: /thinking/i }).or(
      page.locator('label').filter({ hasText: /thinking/i }).locator('input')
    );
    if (await thinkingCheckbox.isVisible()) {
      await thinkingCheckbox.check();
    }
    
    await page.click('button:has-text("Search")');
    
    // Wait for results
    await page.waitForSelector('[data-testid="vehicle-card"], .vehicle-card, [class*="grid"] > div:has(img)', { timeout: 10000 });
    
    // Verify exactly 4 Porsche 911 vehicles
    const vehicleCards = page.locator('[data-testid="vehicle-card"], .vehicle-card, [class*="grid"] > div:has(img)');
    await expect(vehicleCards).toHaveCount(4);
    
    // Check for demo-specific messages if thinking is shown
    const thinkingSection = page.locator('[class*="thinking"], [class*="progress"]').or(
      page.locator('text=/Demo Mode|demo|Demo search/')
    );
    if (await thinkingSection.isVisible()) {
      await expect(thinkingSection).toContainText(/demo/i);
    }
  });

  test('Filter-based search also returns demo results', async ({ page }) => {
    // Try using filters instead of text search
    // Look for filter controls
    const makeFilter = page.locator('select, input').filter({ hasText: /make/i }).or(
      page.locator('label').filter({ hasText: /make/i }).locator('+ select, + input')
    );
    
    if (await makeFilter.isVisible()) {
      await makeFilter.selectOption('BMW');
    }
    
    // Apply filters or search
    const applyButton = page.locator('button').filter({ hasText: /apply|search/i }).first();
    await applyButton.click();
    
    // Wait for results
    await page.waitForSelector('[data-testid="vehicle-card"], .vehicle-card, [class*="grid"] > div:has(img)', { timeout: 10000 });
    
    // Should still get Porsche 911s despite filtering for BMW
    const vehicleCards = page.locator('[data-testid="vehicle-card"], .vehicle-card, [class*="grid"] > div:has(img)');
    await expect(vehicleCards).toHaveCount(4);
    
    // Verify all are still Porsche 911s (demonstrating hardcoded behavior)
    for (let i = 0; i < 4; i++) {
      const cardText = await vehicleCards.nth(i).textContent();
      expect(cardText?.toLowerCase()).toContain('porsche');
    }
  });
}); 