const fs = require('fs');
const path = require('path');
const https = require('https');
const { execSync } = require('child_process');

// Read BaT vehicle data to get makes, models, and years
const realListingsPath = path.join(__dirname, '../src/data/real_listings.json');
const batVehicles = JSON.parse(fs.readFileSync(realListingsPath, 'utf8'));

// Create vehicle images directory
const carImagesDir = path.join(__dirname, '../public/vehicle-images');
if (!fs.existsSync(carImagesDir)) {
  console.log('Creating vehicle images directory');
  fs.mkdirSync(carImagesDir, { recursive: true });
}

// Map to track which images have been downloaded
const downloadedImages = {};

/**
 * Downloads an image from a URL to a local file path
 */
const downloadImage = (url, filepath) => {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(filepath);
    https.get(url, response => {
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download image, status code: ${response.statusCode}`));
        return;
      }
      
      response.pipe(file);
      
      file.on('finish', () => {
        file.close();
        resolve();
      });
      
      file.on('error', err => {
        fs.unlinkSync(filepath); // Delete the file on error
        reject(err);
      });
    }).on('error', err => {
      fs.unlinkSync(filepath); // Delete the file on error
      reject(err);
    });
  });
};

/**
 * Process the batch of vehicle data to download images
 */
const processVehicles = async () => {
  // Create a mapping file for vehicle IDs to image files
  const imageMapping = {};
  
  // Process each vehicle
  for (const vehicle of batVehicles) {
    const { id, make, model, year } = vehicle;
    if (!make || !model || !year) continue;
    
    const searchTerm = `${year} ${make} ${model}`;
    const searchTermSlug = searchTerm.toLowerCase().replace(/\s+/g, '-');
    const imageFolderPath = path.join(carImagesDir, searchTermSlug);
    
    if (!fs.existsSync(imageFolderPath)) {
      fs.mkdirSync(imageFolderPath, { recursive: true });
    }
    
    try {
      console.log(`Searching for images of: ${searchTerm}`);
      
      // Search for public domain images using the Unsplash API
      const command = `curl -s "https://api.unsplash.com/search/photos?query=${encodeURIComponent(searchTerm)}&per_page=3&client_id=YOUR_UNSPLASH_API_KEY"`;
      
      console.log("⚠️ NOTE: You need to replace 'YOUR_UNSPLASH_API_KEY' in the script with a valid Unsplash API key.");
      console.log("Get a free API key from https://unsplash.com/developers");
      
      // For testing/demo purposes without the API key:
      const demoImagePaths = [];
      for (let i = 1; i <= 3; i++) {
        const imagePath = path.join(imageFolderPath, `${i}.jpg`);
        
        // Create a placeholder to indicate where a real image would be downloaded
        fs.writeFileSync(imagePath, `This would be image ${i} for ${searchTerm} downloaded from Unsplash`);
        demoImagePaths.push(`/vehicle-images/${searchTermSlug}/${i}.jpg`);
      }
      
      // Store the image paths in our mapping
      imageMapping[id] = demoImagePaths;
      console.log(`Added demo image placeholders for ${searchTerm}`);
      
      // In a real implementation with API key, you would:
      // 1. Parse the API response to get image URLs
      // 2. Download each image to the imageFolderPath
      // 3. Store the local paths in imageMapping
      
    } catch (error) {
      console.error(`Error processing ${searchTerm}:`, error);
    }
  }
  
  // Save the mapping file
  const mappingPath = path.join(__dirname, '../public/vehicle-images/mapping.json');
  fs.writeFileSync(mappingPath, JSON.stringify(imageMapping, null, 2));
  console.log(`Saved image mapping to ${mappingPath}`);
};

const main = async () => {
  console.log('Starting vehicle image download process...');
  await processVehicles();
  console.log('Finished processing vehicles');
  
  console.log('\n===== IMPORTANT =====');
  console.log('This script created placeholder files to demonstrate the structure.');
  console.log('To download actual images, please:');
  console.log('1. Get an Unsplash API key from https://unsplash.com/developers');
  console.log('2. Replace YOUR_UNSPLASH_API_KEY in this script with your actual key');
  console.log('3. Run the script again');
  console.log('===================\n');
};

main().catch(error => {
  console.error('Error in main process:', error);
});
