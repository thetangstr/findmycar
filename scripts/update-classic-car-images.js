const fs = require('fs');
const path = require('path');
const axios = require('axios');

// Create vehicle images directory if it doesn't exist
const carImagesDir = path.join(__dirname, '../public/vehicle-images');
if (!fs.existsSync(carImagesDir)) {
  console.log('Creating vehicle images directory');
  fs.mkdirSync(carImagesDir, { recursive: true });
}

// Specific URLs for classic/vintage car images - era appropriate
const CLASSIC_CAR_IMAGE_MAP = {
  // Classic American cars
  'chevrolet corvette 1963': [
    'https://images.unsplash.com/photo-1626665158370-8c71ab379f5a?w=800&q=80', // Real 60s Corvette
    'https://images.unsplash.com/photo-1612293905271-28ff664264a9?w=800&q=80', // Classic Corvette rear
    'https://images.unsplash.com/photo-1582739432144-42adbf2c473e?w=800&q=80'  // Classic Vette side view
  ],
  'ford bronco 1973': [
    'https://images.unsplash.com/photo-1612803751315-d1fe1b453a03?w=800&q=80', // Classic Bronco
    'https://images.unsplash.com/photo-1607603750909-408e193868c7?w=800&q=80', // Vintage Bronco
    'https://images.unsplash.com/photo-1592853625597-7d95150f9b70?w=800&q=80'  // Classic Ford off-road
  ],
  'volkswagen karmann-ghia 1967': [
    'https://images.unsplash.com/photo-1595043233666-2cc0cb0171e4?w=800&q=80', // Real Karmann Ghia
    'https://images.unsplash.com/photo-1541447646807-71c298b8aaf2?w=800&q=80', // Classic VW
    'https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=800&q=80'  // VW classic
  ],
  'jaguar e-type 1969': [
    'https://images.unsplash.com/photo-1529426301869-82f4d98d3d81?w=800&q=80', // Classic Jaguar
    'https://images.unsplash.com/photo-1642850644105-e0d401449b2d?w=800&q=80', // E-Type headlight
    'https://images.unsplash.com/photo-1574950578143-858c6fc58922?w=800&q=80'  // Vintage British car
  ],
  'datsun 240z 1972': [
    'https://images.unsplash.com/photo-1566024349844-1a437ca51a83?w=800&q=80', // Datsun 240Z
    'https://images.unsplash.com/photo-1591124213126-2b5261188d35?w=800&q=80', // Classic Datsun
    'https://images.unsplash.com/photo-1565467850084-8b9a37fd8ba6?w=800&q=80'  // 240Z detail
  ],
  
  // European classics
  'porsche 911 1995': [
    'https://images.unsplash.com/photo-1511919884226-fd3cad34687c?w=800&q=80', // Classic 911
    'https://images.unsplash.com/photo-1503736334956-4c8f8e92946d?w=800&q=80', // Porsche classic
    'https://images.unsplash.com/photo-1600712242805-5f78671b24da?w=800&q=80'  // Vintage Porsche
  ],
  'mercedes-benz 300sl 1989': [
    'https://images.unsplash.com/photo-1507136566006-cfc505b114fc?w=800&q=80', // Classic Mercedes
    'https://images.unsplash.com/photo-1616422285623-13ff0162193c?w=800&q=80', // Mercedes vintage
    'https://images.unsplash.com/photo-1553440569-bcc63803a83d?w=800&q=80'  // Benz classic
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

/**
 * Update images for classic cars
 */
async function updateClassicCarImages() {
  // Load the existing mapping file
  const mappingPath = path.join(__dirname, '../public/vehicle-images/mapping.json');
  let imageMapping = {};
  
  if (fs.existsSync(mappingPath)) {
    try {
      const mappingData = fs.readFileSync(mappingPath, 'utf8');
      imageMapping = JSON.parse(mappingData);
      console.log('Loaded existing image mapping');
    } catch (error) {
      console.error('Error loading mapping file:', error);
    }
  }
  
  // Process each classic car
  for (const [carKey, imageUrls] of Object.entries(CLASSIC_CAR_IMAGE_MAP)) {
    const carIdentifier = carKey.toLowerCase().replace(/\\s+/g, '-');
    console.log(`\nUpdating images for ${carKey}...`);
    
    const carImages = [];
    
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
      console.log(`Updated ${carImages.length} images for ${carKey}`);
    }
    
    // Check if we need to update specific vehicle IDs that use this car type
    // For example, map a specific "bat-8" ID for a 1963 Corvette to these new images
    // This will override the existing mapping for this specific ID
    
    // Example: If this is a 1963 Corvette, find any vehicle IDs with that make/model/year
    const [make, model, year] = carKey.split(' ');
    if (make && model && year) {
      Object.keys(imageMapping).forEach(key => {
        // If the key looks like a vehicle ID (e.g., bat-8) and its images aren't era-appropriate,
        // and the images correspond to a known model, update it
        if (key.startsWith('bat-') || key.startsWith('autodev-')) {
          // Get the first few characters of the first image path to see if it matches our car
          const firstImage = imageMapping[key] && imageMapping[key][0] ? 
            imageMapping[key][0].toLowerCase() : '';
          
          if (firstImage.includes(make.toLowerCase()) && 
              firstImage.includes(model.toLowerCase()) &&
              firstImage.includes(year)) {
            console.log(`Updating vehicle ID ${key} to use correct ${make} ${model} ${year} images`);
            imageMapping[key] = carImages;
          }
        }
      });
    }
  }
  
  // Save the updated mapping file
  fs.writeFileSync(mappingPath, JSON.stringify(imageMapping, null, 2));
  console.log(`\nSaved updated image mapping to ${mappingPath}`);
}

async function main() {
  try {
    console.log('Starting classic car image update...');
    
    if (!fs.existsSync(path.join(__dirname, 'node_modules/axios'))) {
      console.log('Installing required dependency: axios...');
      require('child_process').execSync('npm install axios', { stdio: 'inherit' });
    }
    
    await updateClassicCarImages();
    
    console.log('\n===== NEXT STEPS =====');
    console.log('1. The script has updated classic car images');
    console.log('2. Run "npm run build" to include these in your build');
    console.log('3. Deploy with "firebase deploy --only hosting"');
    console.log('=====================\n');
  } catch (error) {
    console.error('Error in main process:', error);
  }
}

main();
