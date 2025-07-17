/**
 * Image Mapping Generator
 * 
 * This utility helps populate and maintain the vehicle-images/mapping.json file
 * which maps vehicle makes, models, and years to specific image URLs.
 * 
 * It can be used to:
 * 1. Auto-generate mappings from existing vehicles
 * 2. Add new mappings from external sources
 * 3. Merge mappings with the existing mapping file
 */

import fs from 'fs';
import path from 'path';
import { Vehicle } from '@/types';

// Type for our image mapping
interface ImageMapping {
  [key: string]: string[];
}

/**
 * Read the existing mapping file if it exists
 */
export const readMappingFile = async (): Promise<ImageMapping> => {
  try {
    const mappingFilePath = path.join(process.cwd(), 'public', 'vehicle-images', 'mapping.json');
    
    if (fs.existsSync(mappingFilePath)) {
      const fileContent = fs.readFileSync(mappingFilePath, 'utf8');
      return JSON.parse(fileContent);
    }
    
    return {};
  } catch (error) {
    console.error('Error reading mapping file:', error);
    return {};
  }
};

/**
 * Write the mapping file to disk
 */
export const writeMappingFile = async (mappingData: ImageMapping): Promise<boolean> => {
  try {
    const mappingDirectory = path.join(process.cwd(), 'public', 'vehicle-images');
    const mappingFilePath = path.join(mappingDirectory, 'mapping.json');
    
    // Ensure directory exists
    if (!fs.existsSync(mappingDirectory)) {
      fs.mkdirSync(mappingDirectory, { recursive: true });
    }
    
    // Write the mapping file with pretty formatting
    fs.writeFileSync(
      mappingFilePath, 
      JSON.stringify(mappingData, null, 2), 
      'utf8'
    );
    
    console.log(`Mapping file updated successfully with ${Object.keys(mappingData).length} entries.`);
    return true;
  } catch (error) {
    console.error('Error writing mapping file:', error);
    return false;
  }
};

/**
 * Extract mapping entries from vehicles with good images
 */
export const extractMappingsFromVehicles = (vehicles: Vehicle[]): ImageMapping => {
  const mappings: ImageMapping = {};
  
  vehicles.forEach(vehicle => {
    const { id, make, model, year, images } = vehicle;
    
    // Skip vehicles without proper images or with placeholder/incomplete images
    if (!images || images.length === 0 || 
        images.some(url => url.includes('placeholder') || url.includes('unsplash.com/photo-'))) {
      return;
    }
    
    // Add mapping by ID
    if (id) {
      mappings[id] = [...images];
    }
    
    // Add mapping by make-model-year
    if (make && model && year) {
      const key = `${make}-${model}-${year}`.toLowerCase().replace(/\s+/g, '-');
      mappings[key] = [...images];
    }
    
    // Add mapping by make-model 
    if (make && model) {
      const key = `${make}-${model}`.toLowerCase().replace(/\s+/g, '-');
      if (!mappings[key]) {
        mappings[key] = [...images];
      }
    }
  });
  
  return mappings;
};

/**
 * Merge new mappings with existing mapping file
 */
export const mergeMappings = (existingMapping: ImageMapping, newMapping: ImageMapping): ImageMapping => {
  const mergedMapping: ImageMapping = { ...existingMapping };
  
  // Add new entries or update existing ones
  Object.entries(newMapping).forEach(([key, imageUrls]) => {
    if (!mergedMapping[key] || mergedMapping[key].length === 0) {
      // New entry
      mergedMapping[key] = imageUrls;
    } else {
      // Existing entry - add any new URLs that don't already exist
      const existingUrls = new Set(mergedMapping[key]);
      imageUrls.forEach(url => existingUrls.add(url));
      mergedMapping[key] = Array.from(existingUrls);
    }
  });
  
  return mergedMapping;
};

/**
 * Add a custom mapping entry
 */
export const addCustomMapping = (
  mapping: ImageMapping, 
  key: string, 
  imageUrls: string[]
): ImageMapping => {
  return {
    ...mapping,
    [key]: imageUrls
  };
};

/**
 * Update the mapping file with new vehicle data
 */
export const updateMappingFromVehicles = async (vehicles: Vehicle[]): Promise<boolean> => {
  try {
    // Read existing mapping
    const existingMapping = await readMappingFile();
    
    // Extract mappings from vehicles
    const newMappings = extractMappingsFromVehicles(vehicles);
    
    // Merge mappings
    const mergedMapping = mergeMappings(existingMapping, newMappings);
    
    // Write back to file
    return await writeMappingFile(mergedMapping);
  } catch (error) {
    console.error('Error updating mapping from vehicles:', error);
    return false;
  }
};

/**
 * Comprehensive mapping update that handles API images,
 * local images, and creates a robust mapping file
 */
export const generateComprehensiveMapping = async (
  vehicles: Vehicle[],
  customMappings: Record<string, string[]> = {}
): Promise<boolean> => {
  try {
    // Start with existing mapping
    const existingMapping = await readMappingFile();
    
    // Extract mappings from vehicles with good images
    const vehicleMappings = extractMappingsFromVehicles(vehicles);
    
    // Merge all mappings
    let mergedMapping = mergeMappings(existingMapping, vehicleMappings);
    
    // Add any custom mappings
    Object.entries(customMappings).forEach(([key, urls]) => {
      mergedMapping = addCustomMapping(mergedMapping, key, urls);
    });
    
    // Write final mapping to file
    return await writeMappingFile(mergedMapping);
  } catch (error) {
    console.error('Error generating comprehensive mapping:', error);
    return false;
  }
};

/**
 * Function to run from a script to update the mapping file
 */
export const runImageMapGenerator = async (vehiclesData: Vehicle[]): Promise<void> => {
  console.log('Starting image map generation...');
  
  try {
    // Custom mappings for specific vehicles or makes/models
    const customMappings: Record<string, string[]> = {
      // Example custom mappings
      'porsche-911': [
        '/vehicle-images/porsche-911-1990-1.jpg',
        '/vehicle-images/porsche-911-1990-2.jpg',
        '/vehicle-images/porsche-911-1990-3.jpg',
      ],
      'acura-nsx': [
        '/vehicle-images/acura-nsx-1996-1.jpg',
        '/vehicle-images/acura-nsx-1996-2.jpg',
        '/vehicle-images/acura-nsx-1996-3.jpg',
      ],
      'chevrolet-corvette': [
        '/vehicle-images/chevrolet-corvette-2023-1.jpg',
        '/vehicle-images/chevrolet-corvette-2023-2.jpg',
        '/vehicle-images/chevrolet-corvette-2023-3.jpg',
      ],
    };
    
    // Generate and save the comprehensive mapping
    const success = await generateComprehensiveMapping(vehiclesData, customMappings);
    
    if (success) {
      console.log('Image map generation completed successfully!');
    } else {
      console.error('Image map generation failed.');
    }
  } catch (error) {
    console.error('Error in image map generation:', error);
  }
};

export default {
  readMappingFile,
  writeMappingFile,
  extractMappingsFromVehicles,
  mergeMappings,
  addCustomMapping,
  updateMappingFromVehicles,
  generateComprehensiveMapping,
  runImageMapGenerator
};
