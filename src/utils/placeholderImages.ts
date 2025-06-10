/**
 * Utility to provide local placeholder image URLs based on vehicle categories
 * This uses static placeholder images stored in the public directory
 * to avoid external placeholder services that may cause DNS resolution errors
 */

// Map of vehicle makes to placeholder image IDs
const makePlaceholders: Record<string, number> = {
  'Porsche': 1,
  'BMW': 2,
  'Mercedes-Benz': 3,
  'Mercedes': 3,
  'Audi': 4,
  'Volkswagen': 5,
  'Toyota': 6,
  'Honda': 7,
  'Ford': 8,
  'Chevrolet': 9,
  'Dodge': 10
};

// Default placeholder IDs for generic vehicle types/categories
const categoryPlaceholders = {
  sedan: 11,
  suv: 12,
  truck: 13,
  sports: 14,
  luxury: 15,
  default: 16
};

/**
 * Gets a placeholder image URL for a specific vehicle make and model
 */
export const getPlaceholderImage = (make?: string, model?: string): string => {
  // Base path for all placeholder images
  const basePath = '/placeholders/car';
  
  // If we have a make that's in our mapping, use the corresponding image
  if (make && makePlaceholders[make]) {
    return `${basePath}${makePlaceholders[make]}.svg`;
  }
  
  // Otherwise use a generic category image based on keywords in model or make
  if (model || make) {
    const searchText = `${make || ''} ${model || ''}`.toLowerCase();
    
    if (searchText.includes('suv') || searchText.includes('crossover')) {
      return `${basePath}${categoryPlaceholders.suv}.svg`;
    }
    
    if (searchText.includes('truck') || searchText.includes('pickup')) {
      return `${basePath}${categoryPlaceholders.truck}.svg`;
    }
    
    if (searchText.includes('sport') || searchText.includes('coupe') || 
        searchText.includes('roadster') || searchText.includes('911')) {
      return `${basePath}${categoryPlaceholders.sports}.svg`;
    }
    
    if (searchText.includes('luxury') || searchText.includes('premium')) {
      return `${basePath}${categoryPlaceholders.luxury}.svg`;
    }
  }
  
  // Default fallback image
  return `${basePath}${categoryPlaceholders.default}.svg`;
};

/**
 * Gets an array of placeholder images for a vehicle
 * Returns multiple variations to provide some variety
 */
export const getPlaceholderImagesArray = (make?: string, model?: string): string[] => {
  // Get the base image
  const baseImage = getPlaceholderImage(make, model);
  
  // Extract the base number
  const match = baseImage.match(/car(\d+)\.svg$/);
  if (!match) {
    return [baseImage]; // Fallback to just the base image
  }
  
  const baseNumber = parseInt(match[1]);
  
  // Create array with multiple variations (using modulo to stay within our image range)
  return [
    baseImage, 
    `/placeholders/car${(baseNumber % 16) + 1}.svg`,
    `/placeholders/car${((baseNumber + 5) % 16) + 1}.svg`
  ];
};
