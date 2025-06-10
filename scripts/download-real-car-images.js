const fs = require('fs');
const path = require('path');
const https = require('https');
const axios = require('axios');

// Read BaT vehicle data to get makes, models, and years
const realListingsPath = path.join(__dirname, '../src/data/real_listings.json');
const batVehicles = JSON.parse(fs.readFileSync(realListingsPath, 'utf8'));

// Create vehicle images directory if it doesn't exist
const carImagesDir = path.join(__dirname, '../public/vehicle-images');
if (!fs.existsSync(carImagesDir)) {
  console.log('Creating vehicle images directory');
  fs.mkdirSync(carImagesDir, { recursive: true });
}

// API endpoints for free car images
const CAR_IMAGE_APIS = [
  // Car API collections - these are public, no API key required
  'https://raw.githubusercontent.com/filippofilip95/car-logos-dataset/master/images/compiled/original',
  'https://raw.githubusercontent.com/filippofilip95/car-logos-dataset/master/images/optimized',
  'https://www.carlogos.org/car-logos',
  'https://car-images-api.herokuapp.com/images',
  'https://www.carlogos.org/logo-models',
];

// Image URLs for specific makes and models
const MAKE_MODEL_IMAGE_MAP = {
  // Porsche models
  'porsche 911': [
    'https://images.unsplash.com/photo-1584060622420-feeeda1c6fd4?w=1080&q=80',
    'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=1080&q=80',
    'https://images.unsplash.com/photo-1611859266238-4b98091d9d9b?w=1080&q=80'
  ],
  'porsche': [
    'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&q=80',
    'https://images.unsplash.com/photo-1580274455191-1c62238fa333?w=1080&q=80'
  ],
  // BMW models
  'bmw m3': [
    'https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=1080&q=80',
    'https://images.unsplash.com/photo-1556800572-1b8aeef2c54f?w=1080&q=80'
  ],
  'bmw': [
    'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=1080&q=80',
    'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=1080&q=80'
  ],
  // Mercedes models
  'mercedes': [
    'https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=1080&q=80',
    'https://images.unsplash.com/photo-1595580142244-678a4ffc98e9?w=1080&q=80'
  ],
  'mercedes-benz': [
    'https://images.unsplash.com/photo-1605515230419-20966bd8f482?w=1080&q=80',
    'https://images.unsplash.com/photo-1617654112368-307921291f42?w=1080&q=80'
  ],
  // Toyota models
  'toyota land cruiser': [
    'https://images.unsplash.com/photo-1564934304050-e9bb87a26813?w=1080&q=80',
    'https://images.unsplash.com/photo-1567425928496-1ab66c650131?w=1080&q=80'
  ],
  'toyota': [
    'https://images.unsplash.com/photo-1559416523-140ddc3d238c?w=1080&q=80',
    'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=1080&q=80'
  ],
  // Audi models
  'audi rs4': [
    'https://images.unsplash.com/photo-1606152421802-db97b9c7a11b?w=1080&q=80',
    'https://images.unsplash.com/photo-1603386329225-868f9b1ee6c9?w=1080&q=80'
  ],
  'audi': [
    'https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?w=1080&q=80',
    'https://images.unsplash.com/photo-1541348263662-e068662d82af?w=1080&q=80'
  ],
  // Ford models
  'ford bronco': [
    'https://images.unsplash.com/photo-1625583117867-645b8ad51bba?w=1080&q=80',
    'https://images.unsplash.com/photo-1630127112426-ce178e2eaecd?w=1080&q=80'
  ],
  'ford': [
    'https://images.unsplash.com/photo-1551830820-330a71b99659?w=1080&q=80',
    'https://images.unsplash.com/photo-1612544448445-b8232cff3b6c?w=1080&q=80'
  ],
  // Volkswagen models
  'volkswagen': [
    'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?w=1080&q=80',
    'https://images.unsplash.com/photo-1542282088-fe8426682b8f?w=1080&q=80'
  ],
  // Chevrolet models
  'chevrolet corvette': [
    'https://images.unsplash.com/photo-1580414057403-c5f451f30e1c?w=1080&q=80',
    'https://images.unsplash.com/photo-1554744512-d6c603f27c54?w=1080&q=80'
  ],
  'chevrolet': [
    'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1080&q=80',
    'https://images.unsplash.com/photo-1612544448445-b8232cff3b6c?w=1080&q=80'
  ],
  // Jaguar models
  'jaguar': [
    'https://images.unsplash.com/photo-1605515298946-d0573716e008?w=1080&q=80',
    'https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=1080&q=80'
  ],
  // Ferrari models
  'ferrari': [
    'https://images.unsplash.com/photo-1632441032234-66b5ada1a5ee?w=1080&q=80',
    'https://images.unsplash.com/photo-1592198084033-aade902d1aae?w=1080&q=80',
    'https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=1080&q=80'
  ],
  // Lamborghini models
  'lamborghini': [
    'https://images.unsplash.com/photo-1573950940509-d924ee3fd345?w=1080&q=80',
    'https://images.unsplash.com/photo-1600712242805-5f78671b24da?w=1080&q=80',
    'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=1080&q=80'
  ],
  // Default car image
  'default': [
    'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1080&q=80',
    'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&q=80',
    'https://images.unsplash.com/photo-1518987048-93e29699e79a?w=1080&q=80'
  ]
};

// Download an image from a URL to a local file
async function downloadImage(url, imagePath) {
  // If the file already exists, don't download again
  if (fs.existsSync(imagePath)) {
    console.log(`File already exists: ${imagePath}`);
    return true;
  }
  
  try {
    const response = await axios.get(url, { responseType: 'arraybuffer' });
    fs.writeFileSync(imagePath, response.data);
    console.log(`Downloaded: ${imagePath}`);
    return true;
  } catch (error) {
    console.error(`Error downloading ${url}:`, error.message);
    return false;
  }
}

// Get image URLs for a vehicle based on its make and model
function getImageUrlsForVehicle(vehicle) {
  const { make, model } = vehicle;
  if (!make) return MAKE_MODEL_IMAGE_MAP.default;
  
  const fullName = `${make} ${model || ''}`.toLowerCase().trim();
  
  // Check for exact make-model match
  for (const [namePattern, urls] of Object.entries(MAKE_MODEL_IMAGE_MAP)) {
    if (fullName.includes(namePattern)) {
      return urls;
    }
  }
  
  // Check for make-only match
  for (const [namePattern, urls] of Object.entries(MAKE_MODEL_IMAGE_MAP)) {
    if (namePattern.toLowerCase() === make.toLowerCase()) {
      return urls;
    }
  }
  
  // Use default if no match
  return MAKE_MODEL_IMAGE_MAP.default;
}

/**
 * Process the batch of vehicle data and download images
 */
async function processVehicles() {
  // Create a mapping file for vehicle IDs to image files
  const imageMapping = {};
  const processedCars = new Set(); // Track processed make/model/year combinations
  
  console.log('Starting to process vehicles...');
  
  // Process vehicles by make/model/year first
  for (const vehicle of batVehicles) {
    const { id, make, model, year } = vehicle;
    if (!make || !model) continue;
    
    const carIdentifier = `${make}-${model}-${year || 'unknown'}`.toLowerCase().replace(/\s+/g, '-');
    
    // Only process each unique car once
    if (!processedCars.has(carIdentifier)) {
      processedCars.add(carIdentifier);
      const carImages = [];
      
      // Get image URLs for this vehicle
      const imageUrls = getImageUrlsForVehicle(vehicle);
      
      // Download images with variant numbers
      for (let i = 0; i < imageUrls.length; i++) {
        const url = imageUrls[i];
        const imagePath = `/vehicle-images/${carIdentifier}-${i + 1}.jpg`;
        const fullPath = path.join(__dirname, '../public', imagePath);
        
        const success = await downloadImage(url, fullPath);
        if (success) {
          carImages.push(imagePath);
        }
      }
      
      // Add to mapping if successful
      if (carImages.length > 0) {
        imageMapping[carIdentifier] = carImages;
      }
    }
  }
  
  // Now map vehicle IDs to image paths
  for (const vehicle of batVehicles) {
    const { id, make, model, year } = vehicle;
    if (!make) continue;
    
    const carIdentifier = `${make}-${model}-${year || 'unknown'}`.toLowerCase().replace(/\s+/g, '-');
    
    // Check if we have images for this make/model/year
    if (imageMapping[carIdentifier]) {
      imageMapping[id] = imageMapping[carIdentifier];
    } else {
      // Try to find a close match
      const makePattern = make.toLowerCase();
      const possibleMatch = Object.keys(imageMapping).find(key => key.startsWith(makePattern));
      
      if (possibleMatch) {
        imageMapping[id] = imageMapping[possibleMatch];
      } else {
        // No match found, use default images
        const defaultId = 'default';
        
        if (!imageMapping[defaultId]) {
          // Create default car images
          imageMapping[defaultId] = [];
          for (let i = 0; i < MAKE_MODEL_IMAGE_MAP.default.length; i++) {
            const url = MAKE_MODEL_IMAGE_MAP.default[i];
            const imagePath = `/vehicle-images/default-car-${i + 1}.jpg`;
            const fullPath = path.join(__dirname, '../public', imagePath);
            
            const success = await downloadImage(url, fullPath);
            if (success) {
              imageMapping[defaultId].push(imagePath);
            }
          }
        }
        
        imageMapping[id] = imageMapping[defaultId] || [];
      }
    }
  }
  
  // Save the mapping file
  const mappingPath = path.join(__dirname, '../public/vehicle-images/mapping.json');
  fs.writeFileSync(mappingPath, JSON.stringify(imageMapping, null, 2));
  console.log(`\nSaved image mapping to ${mappingPath}`);
  
  // Count total images downloaded
  const totalImages = Object.values(imageMapping)
    .reduce((count, images) => count + (Array.isArray(images) ? images.length : 0), 0);
  
  console.log(`\nDownloaded ${totalImages} real car images for ${Object.keys(imageMapping).length} vehicles/categories`);
}

async function main() {
  try {
    console.log('Starting real car images download...');
    
    if (!fs.existsSync(path.join(__dirname, 'node_modules/axios'))) {
      console.log('Installing required dependency: axios...');
      require('child_process').execSync('npm install axios', { stdio: 'inherit' });
    }
    
    await processVehicles();
    
    console.log('\n===== NEXT STEPS =====');
    console.log('1. The script has downloaded real car images for all vehicles');
    console.log('2. Run "npm run build" to include these in your build');
    console.log('3. Deploy with "firebase deploy --only hosting"');
    console.log('=====================\n');
  } catch (error) {
    console.error('Error in main process:', error);
  }
}

main();
