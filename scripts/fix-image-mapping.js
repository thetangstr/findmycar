/**
 * This script fixes the vehicle image mapping by:
 * 1. Reading all actual files present in the vehicle-images directory
 * 2. Creating a clean mapping.json that matches file paths correctly
 * 3. Ensuring vehicle IDs point to the right images
 */
const fs = require('fs');
const path = require('path');

const carImagesDir = path.join(__dirname, '../public/vehicle-images');
const mappingPath = path.join(carImagesDir, 'mapping.json');

// Function to ensure each array has unique entries
function uniqueArray(arr) {
  return [...new Set(arr)];
}

function main() {
  console.log('⚙️ Starting image mapping fix...');
  
  // Load existing mapping for reference
  let oldMapping = {};
  try {
    const oldMappingData = fs.readFileSync(mappingPath, 'utf8');
    oldMapping = JSON.parse(oldMappingData);
    console.log('✅ Loaded existing mapping');
  } catch (error) {
    console.error('⚠️ Error loading existing mapping:', error.message);
  }
  
  // Read all files in the directory
  const files = fs.readdirSync(carImagesDir)
    .filter(file => file.endsWith('.jpg') || file.endsWith('.svg'));
    
  console.log(`🔍 Found ${files.length} image files`);
  
  // Create a fresh mapping object
  const newMapping = {};
  
  // Group files by vehicle model
  const vehicleGroups = {};
  
  files.forEach(file => {
    // Skip the mapping.json file itself
    if (file === 'mapping.json') return;
    
    // Get base name without extension
    const baseName = file.replace(/\.\w+$/, '');
    
    // Get vehicle make/model from filename (remove trailing -1, -2, -3)
    const vehicleKey = baseName.replace(/-\d+$/, '');
    
    if (!vehicleGroups[vehicleKey]) {
      vehicleGroups[vehicleKey] = [];
    }
    
    // Only add jpg files to the mapping (not SVG)
    if (file.endsWith('.jpg')) {
      vehicleGroups[vehicleKey].push(`/vehicle-images/${file}`);
    }
  });
  
  // Add all grouped files to the mapping
  Object.keys(vehicleGroups).forEach(key => {
    if (vehicleGroups[key].length > 0) {
      newMapping[key] = uniqueArray(vehicleGroups[key]);
    }
  });
  
  // Special handling for vehicle IDs like bat-1, bat-2, etc.
  // Keep the existing vehicle ID mappings from the old mapping file
  Object.keys(oldMapping).forEach(key => {
    // If it's a vehicle ID (starts with bat- or autodev-)
    if (key.startsWith('bat-') || key.startsWith('autodev-')) {
      const filesList = [];
      
      // Verify each file in the old mapping actually exists
      if (Array.isArray(oldMapping[key])) {
        oldMapping[key].forEach(filePath => {
          const fileName = filePath.split('/').pop();
          const fullPath = path.join(carImagesDir, fileName);
          
          if (fs.existsSync(fullPath)) {
            filesList.push(filePath);
          } else {
            console.log(`⚠️ File not found for ${key}: ${filePath}`);
          }
        });
      }
      
      // Only add to mapping if we have files
      if (filesList.length > 0) {
        newMapping[key] = uniqueArray(filesList);
      } else {
        // If there are no valid files, use default images
        newMapping[key] = [
          '/vehicle-images/default-car-1.jpg',
          '/vehicle-images/default-car-2.jpg',
          '/vehicle-images/default-car-3.jpg'
        ];
        console.log(`⚠️ Using default images for ${key}`);
      }
    }
  });
  
  // Special handling for the default fallback
  newMapping['default'] = [
    '/vehicle-images/default-car-1.jpg',
    '/vehicle-images/default-car-2.jpg',
    '/vehicle-images/default-car-3.jpg'
  ];
  
  // Special case: Ensure the 1963 Corvette specific ID (bat-8) has the correct images
  if (vehicleGroups['chevrolet-corvette-1963']) {
    newMapping['bat-8'] = uniqueArray(vehicleGroups['chevrolet-corvette-1963']);
    newMapping['chevrolet corvette 1963'] = uniqueArray(vehicleGroups['chevrolet-corvette-1963']);
  }
  
  // Ensure Porsche 911 has proper images
  if (vehicleGroups['porsche-911-1995'] || vehicleGroups['porsche 911 1995']) {
    const porscheImages = [
      ...(vehicleGroups['porsche-911-1995'] || []),
      ...(vehicleGroups['porsche 911 1995'] || [])
    ];
    
    if (porscheImages.length > 0) {
      newMapping['porsche-911-1995'] = uniqueArray(porscheImages);
      newMapping['porsche 911 1995'] = uniqueArray(porscheImages);
      newMapping['bat-1'] = uniqueArray(porscheImages);
    }
  }
  
  // Write the new mapping file
  fs.writeFileSync(mappingPath, JSON.stringify(newMapping, null, 2));
  console.log(`✅ Fixed mapping saved to ${mappingPath}`);
  
  console.log('\n===== NEXT STEPS =====');
  console.log('1. Vehicle image mapping is now fixed');
  console.log('2. Run "npm run build" to include these in your build');
  console.log('3. Deploy with "firebase deploy --only hosting"');
  console.log('=====================\n');
}

main();
