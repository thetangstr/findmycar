import { Vehicle, SearchFilters } from '@/types';
import { getFallbackImage } from '@/utils/vehicleImageUtils';

// Import the static real listings data directly
import realListingsData from '../data/real_listings.json';

// Type assertion to ensure the imported data is treated as an array of Vehicle objects
const batListingsInput = realListingsData as Vehicle[];

console.log('[DEBUG batVehicleApi] Initializing batVehicleApi.ts...');
if (batListingsInput && batListingsInput.length > 0) {
  console.log('[DEBUG batVehicleApi] Raw images for first vehicle (batListingsInput[0].id: ' + batListingsInput[0].id + '):', JSON.stringify(batListingsInput[0].images));
} else {
  console.log('[DEBUG batVehicleApi] batListingsInput is empty or undefined.');
}

/**
 * Helper function to validate and filter image URLs.
 */
const isValidImageUrl = (url: string): boolean => {
  if (!url) return false;

  // Skip ALL bringatrailer.com domains and subdomains
  if (url.includes('bringatrailer.com')) {
    // console.log(`[DEBUG batVehicleApi] Filtering out bringatrailer.com URL: ${url}`);
    return false;
  }

  // Skip placeholder.com URLs which can also fail
  if (url.includes('placeholder.com')) {
    // console.log(`[DEBUG batVehicleApi] Filtering out placeholder.com URL: ${url}`);
    return false;
  }

  // Validate URL format (basic check)
  try {
    new URL(url);
    return true;
  } catch (e) {
    // console.error(`[DEBUG batVehicleApi] Invalid URL format: ${url}`);
    return false;
  }
};

/**
 * Helper function to simulate a real API call with a small delay
 * This makes the application feel more realistic
 */
const simulateApiDelay = async (): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, 300));
};

// Process all vehicles to filter their images
const batListings: Vehicle[] = batListingsInput.map(vehicle => {
  // Apply image URL filtering to each vehicle
  const filteredImages = vehicle.images ? vehicle.images.filter(url => isValidImageUrl(url)) : [];
  
  // If no valid images remain after filtering, use vehicle-specific silhouette images
  let finalImages = filteredImages;
  
  // If no images, add real car photos specific to the vehicle's make/model
  if (finalImages.length === 0) {
    // Get the base fallback image path
    const baseImage = getFallbackImage(vehicle);
    const imageBase = baseImage.replace(/\d+\.jpg$/, '');
    
    // Add three variations of real car photos for this vehicle
    finalImages = [
      `${imageBase}1.jpg`,
      `${imageBase}2.jpg`,
      `${imageBase}3.jpg`
    ];
    
    // Make sure the fallbacks exist, otherwise use the default
    if (baseImage.includes('default')) {
      finalImages = [
        '/vehicle-images/default-car-1.jpg',
        '/vehicle-images/default-car-2.jpg',
        '/vehicle-images/default-car-3.jpg'
      ];
    }
  }
  
  return {
    ...vehicle,
    images: finalImages
  };
});

if (batListings && batListings.length > 0) {
  console.log('[DEBUG batVehicleApi] Processed images for first vehicle (batListings[0].id: ' + batListings[0].id + '):', JSON.stringify(batListings[0].images));
} else {
  console.log('[DEBUG batVehicleApi] Processed batListings is empty or undefined.');
}

/**
 * Fetches all vehicles from Bring a Trailer listings (with filtered images)
 */
export const fetchBatVehicles = async (): Promise<Vehicle[]> => {
  try {
    await simulateApiDelay();
    // Data is already processed with filtered images
    return batListings;
  } catch (error) {
    console.error('Error fetching BaT vehicles:', error);
    return [];
  }
};

/**
 * Fetches a single vehicle by ID from Bring a Trailer listings (with filtered images)
 */
export const fetchBatVehicleById = async (id: string): Promise<Vehicle | null> => {
  try {
    await simulateApiDelay();
    // Find vehicle by ID in the already processed static data
    const vehicle = batListings.find(v => v.id === id) || null;
    return vehicle; // Images are already filtered
  } catch (error) {
    console.error('Error fetching BaT vehicle by ID:', error);
    return null;
  }
};

/**
 * Searches vehicles with filters from Bring a Trailer listings (with filtered images)
 */
export const searchBatVehicles = async (filters: SearchFilters): Promise<Vehicle[]> => {
  try {
    await simulateApiDelay();
    
    // Apply search filters to the already image-filtered data
    const searchResults = batListings.filter((vehicle: Vehicle) => {
      if (filters.make && vehicle.make.toLowerCase() !== filters.make.toLowerCase()) return false;
      if (filters.model && !vehicle.model.toLowerCase().includes(filters.model.toLowerCase())) return false;
      if (filters.yearMin && vehicle.year < filters.yearMin) return false;
      if (filters.yearMax && vehicle.year > filters.yearMax) return false;
      if (filters.priceMin && vehicle.price < filters.priceMin) return false;
      if (filters.priceMax && vehicle.price > filters.priceMax) return false;
      if (filters.mileageMin && vehicle.mileage < filters.mileageMin) return false;
      if (filters.mileageMax && vehicle.mileage > filters.mileageMax) return false;
      if (filters.fuelType && vehicle.fuelType !== filters.fuelType) return false;
      if (filters.transmission && vehicle.transmission !== filters.transmission) return false;
      if (filters.query) {
        const query = filters.query.toLowerCase();
        const searchableText = `${vehicle.make} ${vehicle.model} ${vehicle.year} ${vehicle.description} ${Array.isArray(vehicle.features) ? vehicle.features.join(' ') : ''}`.toLowerCase();
        if (!searchableText.includes(query)) return false;
      }
      return true;
    });
    // Images in searchResults are already filtered because they come from batListings
    return searchResults;
  } catch (error) {
    console.error('Error searching BaT vehicles:', error);
    return [];
  }
};

export default {
  fetchBatVehicles,
  fetchBatVehicleById,
  searchBatVehicles
};
