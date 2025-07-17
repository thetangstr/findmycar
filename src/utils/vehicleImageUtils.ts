/**
 * Utility functions for vehicle image handling
 * Provides access to real car photos based on make/model/year
 */

import { Vehicle } from '@/types';

// Define a type for our image mapping
interface ImageMapping {
  [key: string]: string[];
}

/**
 * Get real vehicle images from our mapping file if available,
 * otherwise construct a path based on make/model/year.
 * All images are now real photos, not silhouettes.
 */
export const getRealVehicleImages = async (vehicle: Vehicle): Promise<string[]> => {
  try {
    // Try to load the mapping file
    let imageMapping: ImageMapping = {};
    try {
      const response = await fetch('/vehicle-images/mapping.json');
      if (response.ok) {
        imageMapping = await response.json();
      }
    } catch (error) {
      console.error('Error loading vehicle image mapping:', error);
    }

    // First check if we have images for this specific vehicle ID
    if (imageMapping[vehicle.id] && imageMapping[vehicle.id].length > 0) {
      console.debug(`Found ${imageMapping[vehicle.id].length} real images for vehicle ID ${vehicle.id}`);
      return imageMapping[vehicle.id];
    }

    // Next try by make/model/year combination
    const { make, model, year } = vehicle;
    if (make && model && year) {
      const carIdentifier = `${make}-${model}-${year}`.toLowerCase().replace(/\s+/g, '-');
      if (imageMapping[carIdentifier] && imageMapping[carIdentifier].length > 0) {
        console.debug(`Found ${imageMapping[carIdentifier].length} real images for ${carIdentifier}`);
        return imageMapping[carIdentifier];
      }
      
      // Try just the make-model (without year)
      const makeModelKey = `${make}-${model}`.toLowerCase().replace(/\s+/g, '-');
      if (imageMapping[makeModelKey] && imageMapping[makeModelKey].length > 0) {
        console.debug(`Found ${imageMapping[makeModelKey].length} real images for ${makeModelKey}`);
        return imageMapping[makeModelKey];
      }

      // Try just the make
      const makeKey = make.toLowerCase().replace(/\s+/g, '-');
      if (imageMapping[makeKey] && imageMapping[makeKey].length > 0) {
        console.debug(`Found ${imageMapping[makeKey].length} real images for make: ${makeKey}`);
        return imageMapping[makeKey];
      }
    }

    // If all else fails, use default images
    if (imageMapping.default && imageMapping.default.length > 0) {
      console.debug('Using default car images');
      return imageMapping.default;
    }

    // Absolute last resort
    return [
      '/vehicle-images/default-car-1.jpg',
      '/vehicle-images/default-car-2.jpg',
      '/vehicle-images/default-car-3.jpg'
    ];
  } catch (error) {
    console.error('Error in getRealVehicleImages:', error);
    return [
      '/vehicle-images/default-car-1.jpg',
      '/vehicle-images/default-car-2.jpg',
      '/vehicle-images/default-car-3.jpg'
    ];
  }
};

/**
 * Generate a fallback image for a vehicle based on its make/model/year
 * This is a utility function used when real images are not available
 * This will return a real photo instead of an SVG silhouette.
 */
export const getFallbackImage = (vehicle: Vehicle): string => {
  if (!vehicle || !vehicle.make) return '/vehicle-images/default-car-1.jpg';
  
  // Determine the right image based on vehicle make and model
  const searchText = `${vehicle.make} ${vehicle.model || ''}`.toLowerCase();
  
  if (searchText.includes('porsche') || searchText.includes('911')) {
    return '/vehicle-images/porsche-911-1995-2.jpg';
  }
  
  if (searchText.includes('bmw')) {
    return '/vehicle-images/bmw-m3-2003-1.jpg';
  }
  
  if (searchText.includes('mercedes')) {
    return '/vehicle-images/mercedes-benz-300sl-1989-1.jpg';
  }
  
  if (searchText.includes('corvette') || searchText.includes('chevrolet')) {
    return '/vehicle-images/chevrolet-corvette-1963-1.jpg';
  }
  
  if (searchText.includes('toyota')) {
    return '/vehicle-images/toyota-land-cruiser-1987-2.jpg';
  }
  
  if (searchText.includes('audi')) {
    return '/vehicle-images/audi-rs4-2007-1.jpg';
  }
  
  if (searchText.includes('volkswagen')) {
    return '/vehicle-images/volkswagen-karmann-ghia-1967-1.jpg';
  }
  
  if (searchText.includes('ford')) {
    return '/vehicle-images/ford-bronco-1973-1.jpg';
  }
  
  if (searchText.includes('datsun') || searchText.includes('nissan')) {
    return '/vehicle-images/datsun-240z-1972-1.jpg';
  }
  
  if (searchText.includes('jaguar')) {
    return '/vehicle-images/jaguar-e-type-1969-2.jpg';
  }
  
  // Default fallback for any other make
  return '/vehicle-images/default-car-1.jpg';
};

// Maintain backwards compatibility
export const getFallbackSilhouette = getFallbackImage;
