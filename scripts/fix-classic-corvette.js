const fs = require('fs');
const path = require('path');
const axios = require('axios');

// Create vehicle images directory if it doesn't exist
const carImagesDir = path.join(__dirname, '../public/vehicle-images');
if (!fs.existsSync(carImagesDir)) {
  console.log('Creating vehicle images directory');
  fs.mkdirSync(carImagesDir, { recursive: true });
}

// Specific reliable URLs for classic Corvette images
const CORVETTE_IMAGES = [
  // More reliable classic Corvette images from different sources
  'https://images.pexels.com/photos/9252762/pexels-photo-9252762.jpeg',  // Classic Corvette - Red
  'https://images.pexels.com/photos/7641493/pexels-photo-7641493.jpeg',  // Classic Corvette side view 
  'https://images.pexels.com/photos/12119318/pexels-photo-12119318.jpeg' // Classic Corvette front view
];

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
 * Fix the Corvette images specifically
 */
async function fixCorvetteImages() {
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
  
  // Process Corvette images
  const carKey = 'chevrolet-corvette-1963';
  console.log(`\nUpdating images for ${carKey}...`);
  
  const carImages = [];
  
  // Download images with variant numbers
  for (let i = 0; i < CORVETTE_IMAGES.length; i++) {
    const url = CORVETTE_IMAGES[i];
    const imagePath = `/vehicle-images/${carKey}-${i + 1}.jpg`;
    const fullPath = path.join(__dirname, '../public', imagePath);
    
    const success = await downloadImage(url, fullPath);
    if (success) {
      carImages.push(imagePath);
    }
  }
  
  // Add to mapping if successful
  if (carImages.length > 0) {
    // Map to the key format used in our system
    imageMapping[carKey] = carImages;
    console.log(`Updated ${carImages.length} images for ${carKey}`);
    
    // Also update any vehicle IDs that should represent a 1963 Corvette
    // Look through existing vehicle IDs for anything that might be a Corvette 1963
    Object.keys(imageMapping).forEach(key => {
      if (key.startsWith('bat-') || key.startsWith('autodev-')) {
        // For this specific fix, we'll manually set vehicle ID bat-8 to be the 1963 Corvette
        // This assumes bat-8 is the ID of the 1963 Corvette in the system
        if (key === 'bat-8') {
          console.log(`Setting vehicle ID ${key} to use correct Corvette images`);
          imageMapping[key] = carImages;
        }
      }
    });
  }
  
  // Also add specific entry for "chevrolet corvette 1963" (with spaces)
  if (carImages.length > 0) {
    imageMapping["chevrolet corvette 1963"] = carImages;
  }
  
  // Save the updated mapping file
  fs.writeFileSync(mappingPath, JSON.stringify(imageMapping, null, 2));
  console.log(`\nSaved updated image mapping to ${mappingPath}`);
}

async function main() {
  try {
    console.log('Starting Corvette image fix...');
    
    if (!fs.existsSync(path.join(__dirname, 'node_modules/axios'))) {
      console.log('Installing required dependency: axios...');
      require('child_process').execSync('npm install axios', { stdio: 'inherit' });
    }
    
    await fixCorvetteImages();
    
    console.log('\n===== NEXT STEPS =====');
    console.log('1. Corvette images updated');
    console.log('2. Run "npm run build" to include these in your build');
    console.log('3. Deploy with "firebase deploy --only hosting"');
    console.log('=====================\n');
  } catch (error) {
    console.error('Error in main process:', error);
  }
}

main();
