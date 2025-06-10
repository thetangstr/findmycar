const fs = require('fs');
const path = require('path');

// Read BaT vehicle data to get makes, models, and years
const realListingsPath = path.join(__dirname, '../src/data/real_listings.json');
const batVehicles = JSON.parse(fs.readFileSync(realListingsPath, 'utf8'));

// Create vehicle images directory
const carImagesDir = path.join(__dirname, '../public/vehicle-images');
if (!fs.existsSync(carImagesDir)) {
  console.log('Creating vehicle images directory');
  fs.mkdirSync(carImagesDir, { recursive: true });
}

// Base colors for different makes
const makeColors = {
  'Porsche': '#c8102e',     // Porsche Red
  'BMW': '#0066b1',         // BMW Blue
  'Mercedes': '#00263a',    // Mercedes-Benz Blue
  'Mercedes-Benz': '#00263a',
  'Audi': '#bb0a30',        // Audi Red
  'Volkswagen': '#1d1f2a',  // VW Dark Blue
  'Toyota': '#eb0a1e',      // Toyota Red
  'Honda': '#cc0000',       // Honda Red
  'Ford': '#00274c',        // Ford Blue
  'Chevrolet': '#cfb87c',   // Chevrolet Gold
  'Dodge': '#be0a30',       // Dodge Red
  'Ferrari': '#ff0000',     // Ferrari Red
  'Lamborghini': '#ddb321', // Lamborghini Yellow
  'Bugatti': '#001e62',     // Bugatti Blue
  'Jaguar': '#1a1a1a',      // Jaguar Black
  'Maserati': '#003057',    // Maserati Blue
  'Alfa Romeo': '#a41d33',  // Alfa Red
  'Subaru': '#00309f',      // Subaru Blue
  'Mazda': '#910a2a',       // Mazda Red
  'Lexus': '#1a1a1a',       // Lexus Black
};

// Default color if make is not in the above list
const defaultColor = '#555555';

// Vehicle body styles with their silhouettes
const bodyStyles = {
  // Body types with their corresponding SVG paths
  'sedan': {
    viewBox: '0 0 800 400',
    path: 'M150,300 C150,300 160,220 240,220 L560,220 C640,220 650,300 650,300 L650,320 C650,320 640,350 560,350 L240,350 C160,350 150,320 150,320 L150,300 Z M200,220 L240,150 L560,150 L600,220 M180,300 A20,20 0 1,0 180,340 A20,20 0 1,0 180,300 Z M620,300 A20,20 0 1,0 620,340 A20,20 0 1,0 620,300 Z M240,150 L280,180 L520,180 L560,150 Z'
  },
  'coupe': {
    viewBox: '0 0 800 400',
    path: 'M150,300 C150,300 200,220 280,220 L520,220 C600,220 650,300 650,300 L650,320 C650,320 640,350 560,350 L240,350 C160,350 150,320 150,320 L150,300 Z M220,220 L280,140 L520,140 L580,220 M180,300 A20,20 0 1,0 180,340 A20,20 0 1,0 180,300 Z M620,300 A20,20 0 1,0 620,340 A20,20 0 1,0 620,300 Z M280,140 L300,170 L500,170 L520,140 Z'
  },
  'suv': {
    viewBox: '0 0 800 400',
    path: 'M150,300 C150,300 160,220 240,220 L560,220 C640,220 650,300 650,300 L650,320 C650,320 640,350 560,350 L240,350 C160,350 150,320 150,320 L150,300 Z M220,220 L240,150 L560,150 L580,220 M180,300 A20,20 0 1,0 180,340 A20,20 0 1,0 180,300 Z M620,300 A20,20 0 1,0 620,340 A20,20 0 1,0 620,300 Z M240,150 L240,220 L560,220 L560,150 Z'
  },
  'truck': {
    viewBox: '0 0 800 400',
    path: 'M150,300 C150,300 160,220 250,220 L380,220 L380,170 L560,170 L560,220 L650,220 L650,300 L650,320 C650,320 640,350 560,350 L240,350 C160,350 150,320 150,320 L150,300 Z M180,300 A20,20 0 1,0 180,340 A20,20 0 1,0 180,300 Z M620,300 A20,20 0 1,0 620,340 A20,20 0 1,0 620,300 Z'
  },
  'convertible': {
    viewBox: '0 0 800 400',
    path: 'M150,300 C150,300 160,220 240,220 L560,220 C640,220 650,300 650,300 L650,320 C650,320 640,350 560,350 L240,350 C160,350 150,320 150,320 L150,300 Z M240,220 C240,220 280,180 380,180 L440,180 C540,180 560,220 560,220 M180,300 A20,20 0 1,0 180,340 A20,20 0 1,0 180,300 Z M620,300 A20,20 0 1,0 620,340 A20,20 0 1,0 620,300 Z'
  },
  'sports': {
    viewBox: '0 0 800 400',
    path: 'M150,300 C150,300 190,220 280,220 L520,220 C610,220 650,300 650,300 L650,320 C650,320 640,350 560,350 L240,350 C160,350 150,320 150,320 L150,300 Z M220,220 L270,170 L530,170 L580,220 M180,300 A20,20 0 1,0 180,340 A20,20 0 1,0 180,300 Z M620,300 A20,20 0 1,0 620,340 A20,20 0 1,0 620,300 Z M270,170 L300,190 L500,190 L530,170 Z'
  },
  'vintage': {
    viewBox: '0 0 800 400',
    path: 'M180,300 C180,300 200,250 200,220 L600,220 C600,250 620,300 620,300 L620,320 C620,320 600,350 560,350 L240,350 C200,350 180,320 180,320 L180,300 Z M200,220 L200,170 L600,170 L600,220 M200,300 A20,20 0 1,0 200,340 A20,20 0 1,0 200,300 Z M600,300 A20,20 0 1,0 600,340 A20,20 0 1,0 600,300 Z M220,170 L220,140 L580,140 L580,170 Z'
  },
  'default': {
    viewBox: '0 0 800 400',
    path: 'M150,300 C150,300 160,220 240,220 L560,220 C640,220 650,300 650,300 L650,320 C650,320 640,350 560,350 L240,350 C160,350 150,320 150,320 L150,300 Z M200,220 L240,150 L560,150 L600,220 M180,300 A20,20 0 1,0 180,340 A20,20 0 1,0 180,300 Z M620,300 A20,20 0 1,0 620,340 A20,20 0 1,0 620,300 Z M240,150 L280,180 L520,180 L560,150 Z'
  }
};

// Determine body style from make, model and year
const getBodyStyle = (make, model, year) => {
  const nameAndModel = `${make} ${model}`.toLowerCase();
  
  // Sports cars
  if (nameAndModel.includes('911') || 
      nameAndModel.includes('corvette') || 
      nameAndModel.includes('ferrari') || 
      nameAndModel.includes('lambo') ||
      nameAndModel.includes('viper') ||
      nameAndModel.includes('mustang') ||
      nameAndModel.includes('camaro') ||
      nameAndModel.includes('miata') ||
      nameAndModel.includes('supra')) {
    return 'sports';
  }
  
  // SUVs
  if (nameAndModel.includes('suv') || 
      nameAndModel.includes('crossover') || 
      nameAndModel.includes('explorer') || 
      nameAndModel.includes('tahoe') ||
      nameAndModel.includes('suburban') ||
      nameAndModel.includes('range rover') ||
      nameAndModel.includes('cherokee') ||
      nameAndModel.includes('4runner') ||
      nameAndModel.includes('escalade')) {
    return 'suv';
  }
  
  // Trucks
  if (nameAndModel.includes('truck') || 
      nameAndModel.includes('pickup') || 
      nameAndModel.includes('f-150') || 
      nameAndModel.includes('silverado') ||
      nameAndModel.includes('tacoma') ||
      nameAndModel.includes('tundra') ||
      nameAndModel.includes('ranger')) {
    return 'truck';
  }
  
  // Convertibles
  if (nameAndModel.includes('convertible') || 
      nameAndModel.includes('cabrio') || 
      nameAndModel.includes('spyder') ||
      nameAndModel.includes('roadster')) {
    return 'convertible';
  }
  
  // Vintage cars (pre-1980)
  if (year < 1980) {
    return 'vintage';
  }
  
  // Coupes
  if (nameAndModel.includes('coupe') || 
      nameAndModel.includes('two-door') ||
      nameAndModel.includes('2-door')) {
    return 'coupe';
  }
  
  // Default to sedan
  return 'sedan';
};

// Generate an SVG image for a vehicle
const generateVehicleSVG = (make, model, year) => {
  const bodyStyle = getBodyStyle(make, model, year);
  const { viewBox, path } = bodyStyles[bodyStyle] || bodyStyles.default;
  const baseColor = makeColors[make] || defaultColor;
  
  // Generate a slightly different color based on the year to add variety
  const yearOffset = parseInt(year.toString().slice(-2)) / 100;
  const color = adjustColor(baseColor, yearOffset);
  
  // Generate SVG with car silhouette
  const svg = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="800" height="400" viewBox="${viewBox}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .car-body { fill: ${color}; stroke: #000000; stroke-width: 2; }
    .car-details { fill: none; stroke: #000000; stroke-width: 1.5; }
    .car-info { font-family: Arial, sans-serif; font-size: 24px; text-anchor: middle; }
    .make { font-weight: bold; }
    .gradient { opacity: 0.2; }
  </style>
  
  <!-- Background gradient -->
  <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#ffffff" />
    <stop offset="100%" stop-color="#dddddd" />
  </linearGradient>
  <rect width="100%" height="100%" fill="url(#bg-gradient)" />
  
  <!-- Light reflection gradient -->
  <linearGradient id="reflection" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="rgba(255, 255, 255, 0.1)" />
    <stop offset="50%" stop-color="rgba(255, 255, 255, 0.3)" />
    <stop offset="100%" stop-color="rgba(255, 255, 255, 0.1)" />
  </linearGradient>
  
  <!-- Car body -->
  <path d="${path}" class="car-body" />
  
  <!-- Light reflection -->
  <path d="${path}" fill="url(#reflection)" class="gradient" />
  
  <!-- Car information -->
  <text x="400" y="80" class="car-info make">${make}</text>
  <text x="400" y="110" class="car-info">${model}</text>
  <text x="400" y="140" class="car-info">${year}</text>
</svg>`;

  return svg;
};

// Helper function to adjust color based on year
function adjustColor(hexColor, offset) {
  // Parse the hex color
  const r = parseInt(hexColor.slice(1, 3), 16);
  const g = parseInt(hexColor.slice(3, 5), 16);
  const b = parseInt(hexColor.slice(5, 7), 16);
  
  // Adjust the color (brighten or darken slightly based on year)
  const factor = 1.0 + (offset - 0.5) * 0.4; // Creates a range from 0.8 to 1.2
  
  // Apply the factor and ensure values stay within 0-255
  const newR = Math.min(255, Math.max(0, Math.round(r * factor)));
  const newG = Math.min(255, Math.max(0, Math.round(g * factor)));
  const newB = Math.min(255, Math.max(0, Math.round(b * factor)));
  
  // Convert back to hex
  return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
}

/**
 * Process the batch of vehicle data to generate images
 */
const processVehicles = async () => {
  // Create a mapping file for vehicle IDs to image files
  const imageMapping = {};
  const processedCars = new Set(); // Track processed make/model/year combinations
  
  // Process each vehicle
  for (const vehicle of batVehicles) {
    const { id, make, model, year } = vehicle;
    if (!make || !model || !year) continue;
    
    const carIdentifier = `${make}-${model}-${year}`.toLowerCase().replace(/\s+/g, '-');
    
    // Only process each unique car once
    if (!processedCars.has(carIdentifier)) {
      processedCars.add(carIdentifier);
      
      // Generate 3 variants of the car (different angles/details)
      const carImages = [];
      
      for (let variant = 1; variant <= 3; variant++) {
        const imagePath = `/vehicle-images/${carIdentifier}-${variant}.svg`;
        const fullPath = path.join(__dirname, '../public', imagePath);
        
        // Generate the SVG
        const svgContent = generateVehicleSVG(make, model, year);
        
        // Make sure the directory exists
        fs.mkdirSync(path.dirname(fullPath), { recursive: true });
        
        // Save the SVG
        fs.writeFileSync(fullPath, svgContent);
        console.log(`Created: ${imagePath}`);
        
        carImages.push(imagePath);
      }
      
      // Add to mapping
      imageMapping[carIdentifier] = carImages;
    }
    
    // Reference the correct images for this vehicle ID
    const lookupId = `${make}-${model}-${year}`.toLowerCase().replace(/\s+/g, '-');
    imageMapping[id] = imageMapping[lookupId] || [];
  }
  
  // Save the mapping file
  const mappingPath = path.join(__dirname, '../public/vehicle-images/mapping.json');
  fs.writeFileSync(mappingPath, JSON.stringify(imageMapping, null, 2));
  console.log(`\nSaved image mapping to ${mappingPath}`);
};

const main = async () => {
  console.log('Starting vehicle image generation process...');
  await processVehicles();
  console.log('\nFinished generating vehicle images');
  
  console.log('\n===== NEXT STEPS =====');
  console.log('1. The script has created SVG silhouettes for all vehicles');
  console.log('2. Run "npm run build" to include these in your build');
  console.log('3. Deploy with "firebase deploy --only hosting"');
  console.log('=====================\n');
};

main().catch(error => {
  console.error('Error in main process:', error);
});
