/**
 * Script to scrape vehicle listings and store them in Firebase
 * 
 * Usage:
 * node scripts/scrape-listings.js --source=autotrader --location=90210 --pages=2
 */

const { initializeApp } = require('firebase/app');
const { getFirestore } = require('firebase/firestore');
const { getStorage } = require('firebase/storage');
const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');

// Parse command line arguments
const args = process.argv.slice(2).reduce((acc, arg) => {
  const [key, value] = arg.split('=');
  acc[key.replace('--', '')] = value;
  return acc;
}, {});

// Default values
const source = args.source || 'autotrader';
const location = args.location || '90210';
const pages = parseInt(args.pages || '1', 10);

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDJEX-fLWA-XxxxxxxxxxxxxxxxxxxX",
  authDomain: "findmycar-347ec.firebaseapp.com",
  projectId: "findmycar-347ec",
  storageBucket: "findmycar-347ec.appspot.com",
  messagingSenderId: "1031395498953",
  appId: "1:1031395498953:web:xxxxxxxxxxxxxxxx"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const firestore = getFirestore(app);
const storage = getStorage(app);

// Collection names
const VEHICLES_COLLECTION = 'vehicles';
const SCRAPE_LOGS_COLLECTION = 'scrape_logs';

/**
 * Main function to scrape vehicle listings
 */
async function scrapeListings() {
  console.log(`Starting scraping from ${source} for location ${location} (${pages} pages)...`);
  
  try {
    // Log the start of scraping
    await logScrapeActivity(source, 'start', location);
    
    // Scrape listings based on source
    const vehicles = await (source === 'autotrader' 
      ? scrapeAutoTraderListings(location, pages)
      : scrapeCarsComListings(location, pages));
    
    console.log(`Scraped ${vehicles.length} vehicles from ${source}`);
    
    // Store vehicles in Firestore
    await storeVehicles(vehicles);
    
    // Log the completion of scraping
    await logScrapeActivity(source, 'complete', location, vehicles.length);
    
    console.log('Scraping completed successfully!');
  } catch (error) {
    console.error('Error during scraping:', error);
    
    // Log the error
    await logScrapeActivity(source, 'error', location, 0, error);
  }
}

/**
 * Scrape vehicle listings from AutoTrader
 */
async function scrapeAutoTraderListings(location, maxPages) {
  const vehicles = [];
  const baseUrl = 'https://www.autotrader.com/cars-for-sale';
  
  for (let page = 1; page <= maxPages; page++) {
    const url = `${baseUrl}/all-cars?searchRadius=0&zip=${location}&page=${page}`;
    
    // Implement delay to avoid rate limiting
    await delay(2000);
    
    console.log(`Scraping page ${page} from ${url}...`);
    
    try {
      const response = await axios.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Referer': 'https://www.autotrader.com/',
          'Connection': 'keep-alive',
          'Upgrade-Insecure-Requests': '1',
          'Cache-Control': 'max-age=0'
        }
      });
      
      const $ = cheerio.load(response.data);
      
      // Extract vehicle listings
      $('.vehicle-card').each((index, element) => {
        try {
          const title = $(element).find('.vehicle-card-header h2').text().trim();
          const [year, make, model] = parseVehicleTitle(title);
          
          const price = parsePrice($(element).find('.first-price').text().trim());
          const mileage = parseMileage($(element).find('.mileage').text().trim());
          const description = $(element).find('.vehicle-card-description').text().trim();
          
          // Extract image URLs
          const imageUrls = [];
          $(element).find('.vehicle-image img').each((i, img) => {
            const src = $(img).attr('src') || $(img).attr('data-src');
            if (src) imageUrls.push(src);
          });
          
          // Generate a unique ID
          const id = generateVehicleId(make, model, year);
          
          // Extract additional details
          const exteriorColor = extractDetail($, element, 'Exterior Color');
          const interiorColor = extractDetail($, element, 'Interior Color');
          const fuelType = extractDetail($, element, 'Fuel Type');
          const transmission = extractDetail($, element, 'Transmission');
          const engine = extractDetail($, element, 'Engine');
          const vin = extractDetail($, element, 'VIN');
          const dealer = $(element).find('.dealer-name').text().trim();
          const listingUrl = $(element).find('.vehicle-card-link').attr('href') || '';
          
          // Create vehicle object
          const vehicle = {
            id,
            make,
            model,
            year,
            price,
            mileage,
            exteriorColor: exteriorColor || 'Unknown',
            interiorColor: interiorColor || 'Unknown',
            fuelType: fuelType || 'Unknown',
            transmission: transmission || 'Unknown',
            engine: engine || 'Unknown',
            vin: vin || 'Unknown',
            description: description || `${year} ${make} ${model}`,
            features: [],
            images: imageUrls,
            imageUrl: imageUrls[0] || '',
            location: location,
            dealer: dealer || 'Unknown',
            listingDate: new Date().toISOString(),
            source: 'autotrader',
            url: `https://www.autotrader.com${listingUrl}`
          };
          
          vehicles.push(vehicle);
          console.log(`Found vehicle: ${year} ${make} ${model}`);
        } catch (error) {
          console.error('Error parsing vehicle listing:', error);
        }
      });
    } catch (error) {
      console.error(`Error scraping page ${page}:`, error);
    }
  }
  
  return vehicles;
}

/**
 * Scrape vehicle listings from Cars.com
 */
async function scrapeCarsComListings(location, maxPages) {
  const vehicles = [];
  const baseUrl = 'https://www.cars.com/shopping/results/';
  
  for (let page = 1; page <= maxPages; page++) {
    const url = `${baseUrl}?page=${page}&zip=${location}`;
    
    // Implement delay to avoid rate limiting
    await delay(2000);
    
    console.log(`Scraping page ${page} from ${url}...`);
    
    try {
      const response = await axios.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Referer': 'https://www.cars.com/',
          'Connection': 'keep-alive',
          'Upgrade-Insecure-Requests': '1',
          'Cache-Control': 'max-age=0'
        }
      });
      
      const $ = cheerio.load(response.data);
      
      // Extract vehicle listings
      $('.vehicle-card').each((index, element) => {
        try {
          const title = $(element).find('.title').text().trim();
          const [year, make, model] = parseVehicleTitle(title);
          
          const price = parsePrice($(element).find('.primary-price').text().trim());
          const mileage = parseMileage($(element).find('.mileage').text().trim());
          const description = $(element).find('.vehicle-description').text().trim();
          
          // Extract image URLs
          const imageUrls = [];
          $(element).find('.vehicle-image img').each((i, img) => {
            const src = $(img).attr('src') || $(img).attr('data-src');
            if (src) imageUrls.push(src);
          });
          
          // Generate a unique ID
          const id = generateVehicleId(make, model, year);
          
          // Extract additional details
          const exteriorColor = extractDetail($, element, 'Exterior Color');
          const interiorColor = extractDetail($, element, 'Interior Color');
          const fuelType = extractDetail($, element, 'Fuel Type');
          const transmission = extractDetail($, element, 'Transmission');
          const engine = extractDetail($, element, 'Engine');
          const vin = extractDetail($, element, 'VIN');
          const dealer = $(element).find('.dealer-name').text().trim();
          const listingUrl = $(element).find('.vehicle-card-link').attr('href') || '';
          
          // Create vehicle object
          const vehicle = {
            id,
            make,
            model,
            year,
            price,
            mileage,
            exteriorColor: exteriorColor || 'Unknown',
            interiorColor: interiorColor || 'Unknown',
            fuelType: fuelType || 'Unknown',
            transmission: transmission || 'Unknown',
            engine: engine || 'Unknown',
            vin: vin || 'Unknown',
            description: description || `${year} ${make} ${model}`,
            features: [],
            images: imageUrls,
            imageUrl: imageUrls[0] || '',
            location: location,
            dealer: dealer || 'Unknown',
            listingDate: new Date().toISOString(),
            source: 'cars.com',
            url: `https://www.cars.com${listingUrl}`
          };
          
          vehicles.push(vehicle);
          console.log(`Found vehicle: ${year} ${make} ${model}`);
        } catch (error) {
          console.error('Error parsing vehicle listing:', error);
        }
      });
    } catch (error) {
      console.error(`Error scraping page ${page}:`, error);
    }
  }
  
  return vehicles;
}

/**
 * Store vehicles in Firestore
 */
async function storeVehicles(vehicles) {
  console.log(`Storing ${vehicles.length} vehicles in Firestore...`);
  
  // For demo purposes, we'll just write to a JSON file
  const outputFile = path.join(__dirname, 'scraped-vehicles.json');
  fs.writeFileSync(outputFile, JSON.stringify(vehicles, null, 2));
  
  console.log(`Vehicles stored in ${outputFile}`);
  
  // In a real implementation, you would store in Firestore
  // and download/upload images to Firebase Storage
}

/**
 * Log scraping activity
 */
async function logScrapeActivity(source, status, location, count = 0, error = null) {
  console.log(`Logging scrape activity: ${source} - ${status}`);
  
  // For demo purposes, we'll just log to console
  // In a real implementation, you would store in Firestore
}

/**
 * Helper function to parse vehicle title into year, make, and model
 */
function parseVehicleTitle(title) {
  // Default values
  let year = new Date().getFullYear();
  let make = 'Unknown';
  let model = 'Unknown';
  
  // Try to extract year, make, and model from title
  const yearMatch = title.match(/\b(19|20)\d{2}\b/);
  if (yearMatch) {
    year = parseInt(yearMatch[0]);
    
    // Remove year from title to make parsing easier
    const titleWithoutYear = title.replace(yearMatch[0], '').trim();
    
    // Common car makes
    const commonMakes = [
      'Acura', 'Alfa Romeo', 'Aston Martin', 'Audi', 'Bentley', 'BMW', 'Buick',
      'Cadillac', 'Chevrolet', 'Chrysler', 'Dodge', 'Ferrari', 'Fiat', 'Ford',
      'Genesis', 'GMC', 'Honda', 'Hyundai', 'Infiniti', 'Jaguar', 'Jeep', 'Kia',
      'Lamborghini', 'Land Rover', 'Lexus', 'Lincoln', 'Lotus', 'Maserati',
      'Mazda', 'McLaren', 'Mercedes-Benz', 'Mini', 'Mitsubishi', 'Nissan',
      'Porsche', 'Ram', 'Rolls-Royce', 'Subaru', 'Tesla', 'Toyota', 'Volkswagen', 'Volvo'
    ];
    
    // Find make in title
    for (const commonMake of commonMakes) {
      if (titleWithoutYear.includes(commonMake)) {
        make = commonMake;
        
        // Extract model (everything after make)
        const makeIndex = titleWithoutYear.indexOf(commonMake);
        model = titleWithoutYear.substring(makeIndex + commonMake.length).trim();
        break;
      }
    }
  }
  
  return [year, make, model];
}

/**
 * Helper function to parse price string to number
 */
function parsePrice(priceStr) {
  const matches = priceStr.match(/[\d,]+/);
  if (matches) {
    return parseInt(matches[0].replace(/,/g, ''));
  }
  return 0;
}

/**
 * Helper function to parse mileage string to number
 */
function parseMileage(mileageStr) {
  const matches = mileageStr.match(/[\d,]+/);
  if (matches) {
    return parseInt(matches[0].replace(/,/g, ''));
  }
  return 0;
}

/**
 * Helper function to extract detail from vehicle listing
 */
function extractDetail($, element, label) {
  const detailElement = $(element).find(`.detail-label:contains("${label}")`).next('.detail-value');
  return detailElement.length ? detailElement.text().trim() : null;
}

/**
 * Generate a unique ID for a vehicle
 */
function generateVehicleId(make, model, year) {
  const timestamp = Date.now();
  const randomStr = Math.random().toString(36).substring(2, 8);
  return `${make.toLowerCase()}-${model.toLowerCase()}-${year}-${randomStr}-${timestamp}`.replace(/\s+/g, '-');
}

/**
 * Helper function to delay execution
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Run the scraper
scrapeListings();
