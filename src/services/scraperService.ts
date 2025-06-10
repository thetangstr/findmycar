import axios from 'axios';
import cheerio from 'cheerio';
import { Vehicle } from '@/types';
import { firestore, storage } from '@/utils/firebase';
import { collection, addDoc, getDocs, query, where, doc, setDoc } from 'firebase/firestore';
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';

// Collection names
const VEHICLES_COLLECTION = 'vehicles';
const SCRAPE_LOGS_COLLECTION = 'scrape_logs';

/**
 * Scrape vehicle listings from AutoTrader
 * Note: This is for educational purposes only. Always check terms of service
 * and implement proper rate limiting in production.
 */
export const scrapeAutoTraderListings = async (
  location: string = 'all', 
  maxPages: number = 1
): Promise<Vehicle[]> => {
  const vehicles: Vehicle[] = [];
  const baseUrl = 'https://www.autotrader.com/cars-for-sale';
  
  try {
    // Log the start of scraping
    await logScrapeActivity('autotrader', 'start', location);
    
    for (let page = 1; page <= maxPages; page++) {
      const url = `${baseUrl}/all-cars?searchRadius=0&zip=${location}&page=${page}`;
      
      // Implement delay to avoid rate limiting
      await delay(2000);
      
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
          const imageUrls: string[] = [];
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
          const vehicle: Vehicle = {
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
            location: location,
            dealer: dealer || 'Unknown',
            listingDate: new Date().toISOString(),
            source: 'autotrader',
            url: `https://www.autotrader.com${listingUrl}`
          };
          
          vehicles.push(vehicle);
        } catch (error) {
          console.error('Error parsing vehicle listing:', error);
        }
      });
      
      console.log(`Scraped page ${page} of AutoTrader listings for ${location}`);
    }
    
    // Log the completion of scraping
    await logScrapeActivity('autotrader', 'complete', location, vehicles.length);
    
    return vehicles;
  } catch (error) {
    console.error('Error scraping AutoTrader listings:', error);
    
    // Log the error
    await logScrapeActivity('autotrader', 'error', location, 0, error);
    
    return [];
  }
};

/**
 * Scrape vehicle listings from Cars.com
 * Note: This is for educational purposes only. Always check terms of service
 * and implement proper rate limiting in production.
 */
export const scrapeCarsComListings = async (
  location: string = 'all', 
  maxPages: number = 1
): Promise<Vehicle[]> => {
  const vehicles: Vehicle[] = [];
  const baseUrl = 'https://www.cars.com/shopping/results/';
  
  try {
    // Log the start of scraping
    await logScrapeActivity('cars.com', 'start', location);
    
    for (let page = 1; page <= maxPages; page++) {
      const url = `${baseUrl}?page=${page}&zip=${location}`;
      
      // Implement delay to avoid rate limiting
      await delay(2000);
      
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
          const imageUrls: string[] = [];
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
          const vehicle: Vehicle = {
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
            location: location,
            dealer: dealer || 'Unknown',
            listingDate: new Date().toISOString(),
            source: 'cars.com',
            url: `https://www.cars.com${listingUrl}`
          };
          
          vehicles.push(vehicle);
        } catch (error) {
          console.error('Error parsing vehicle listing:', error);
        }
      });
      
      console.log(`Scraped page ${page} of Cars.com listings for ${location}`);
    }
    
    // Log the completion of scraping
    await logScrapeActivity('cars.com', 'complete', location, vehicles.length);
    
    return vehicles;
  } catch (error) {
    console.error('Error scraping Cars.com listings:', error);
    
    // Log the error
    await logScrapeActivity('cars.com', 'error', location, 0, error);
    
    return [];
  }
};

/**
 * Store scraped vehicles in Firestore
 */
export const storeScrapedVehicles = async (vehicles: Vehicle[]): Promise<void> => {
  for (const vehicle of vehicles) {
    try {
      // Check if vehicle already exists
      const vehiclesQuery = query(
        collection(firestore, VEHICLES_COLLECTION),
        where('id', '==', vehicle.id)
      );
      
      const querySnapshot = await getDocs(vehiclesQuery);
      
      if (!querySnapshot.empty) {
        // Update existing vehicle
        const docId = querySnapshot.docs[0].id;
        await setDoc(doc(firestore, VEHICLES_COLLECTION, docId), {
          ...vehicle,
          updatedAt: new Date().toISOString()
        });
        console.log(`Updated vehicle ${vehicle.id} in Firestore`);
      } else {
        // Add new vehicle
        await addDoc(collection(firestore, VEHICLES_COLLECTION), {
          ...vehicle,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        });
        console.log(`Added vehicle ${vehicle.id} to Firestore`);
      }
      
      // Download and store images if available
      if (vehicle.images && vehicle.images.length > 0) {
        await downloadAndStoreImages(vehicle);
      }
    } catch (error) {
      console.error(`Error storing vehicle ${vehicle.id}:`, error);
    }
  }
};

/**
 * Download images from URLs and store in Firebase Storage
 */
const downloadAndStoreImages = async (vehicle: Vehicle): Promise<void> => {
  const updatedImageUrls: string[] = [];
  
  for (let i = 0; i < vehicle.images.length; i++) {
    const imageUrl = vehicle.images[i];
    
    try {
      // Download image
      const response = await axios.get(imageUrl, { responseType: 'arraybuffer' });
      const buffer = Buffer.from(response.data, 'binary');
      
      // Generate filename
      const filename = `${vehicle.id}_${i}.jpg`;
      
      // Upload to Firebase Storage
      const storageRef = ref(storage, `vehicles/${vehicle.id}/${filename}`);
      await uploadBytes(storageRef, buffer);
      
      // Get download URL
      const downloadURL = await getDownloadURL(storageRef);
      updatedImageUrls.push(downloadURL);
      
      console.log(`Uploaded image ${i+1} for ${vehicle.id} to Firebase Storage`);
    } catch (error) {
      console.error(`Error processing image ${i+1} for ${vehicle.id}:`, error);
    }
  }
  
  // Update vehicle with Firebase Storage URLs if any were successfully uploaded
  if (updatedImageUrls.length > 0) {
    try {
      const vehiclesQuery = query(
        collection(firestore, VEHICLES_COLLECTION),
        where('id', '==', vehicle.id)
      );
      
      const querySnapshot = await getDocs(vehiclesQuery);
      
      if (!querySnapshot.empty) {
        const docId = querySnapshot.docs[0].id;
        await setDoc(doc(firestore, VEHICLES_COLLECTION, docId), {
          ...vehicle,
          images: updatedImageUrls,
          updatedAt: new Date().toISOString()
        });
        console.log(`Updated vehicle ${vehicle.id} with Firebase Storage image URLs`);
      }
    } catch (error) {
      console.error(`Error updating vehicle ${vehicle.id} with image URLs:`, error);
    }
  }
};

/**
 * Log scraping activity to Firestore
 */
const logScrapeActivity = async (
  source: string,
  status: 'start' | 'complete' | 'error',
  location: string,
  count: number = 0,
  error?: any
): Promise<void> => {
  try {
    await addDoc(collection(firestore, SCRAPE_LOGS_COLLECTION), {
      source,
      status,
      location,
      count,
      error: error ? error.toString() : null,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error logging scrape activity:', error);
  }
};

/**
 * Helper function to parse vehicle title into year, make, and model
 */
const parseVehicleTitle = (title: string): [number, string, string] => {
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
};

/**
 * Helper function to parse price string to number
 */
const parsePrice = (priceStr: string): number => {
  const matches = priceStr.match(/[\d,]+/);
  if (matches) {
    return parseInt(matches[0].replace(/,/g, ''));
  }
  return 0;
};

/**
 * Helper function to parse mileage string to number
 */
const parseMileage = (mileageStr: string): number => {
  const matches = mileageStr.match(/[\d,]+/);
  if (matches) {
    return parseInt(matches[0].replace(/,/g, ''));
  }
  return 0;
};

/**
 * Helper function to extract detail from vehicle listing
 */
const extractDetail = ($: cheerio.CheerioAPI, element: any, label: string): string | null => {
  const detailElement = $(element).find(`.detail-label:contains("${label}")`).next('.detail-value');
  return detailElement.length ? detailElement.text().trim() : null;
};

/**
 * Generate a unique ID for a vehicle
 */
const generateVehicleId = (make: string, model: string, year: number): string => {
  const timestamp = Date.now();
  const randomStr = Math.random().toString(36).substring(2, 8);
  return `${make.toLowerCase()}-${model.toLowerCase()}-${year}-${randomStr}-${timestamp}`.replace(/\s+/g, '-');
};

/**
 * Helper function to delay execution
 */
const delay = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};
