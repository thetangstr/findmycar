/**
 * Vehicle Image Service
 * 
 * This service provides a robust solution for fetching and generating accurate car photos
 * that match vehicle descriptions. It implements multiple fallback mechanisms:
 * 
 * 1. External car image APIs (Unsplash, Bing Image Search)
 * 2. Local image mapping
 * 3. Default fallback images
 * 
 * It also preserves the hardcoded images for the 3 featured listings.
 */

import { Vehicle } from '@/types';
import { getFallbackImage } from '@/utils/vehicleImageUtils';
import aiImageGenerationService from '@/services/aiImageGenerationService';

// IDs of the featured listings with hardcoded images (to be excluded from image fetching)
const FEATURED_LISTING_IDS = [
  'ebay-porsche-1',   // 1990 Porsche 911 Carrera 2 Cabriolet
  'bat-corvette-1',   // 2023 Chevrolet Corvette Z06 Convertible
  'autotrader-nsx-1', // 1996 Acura NSX T
];

/**
 * API key for Unsplash (should be set in environment variables)
 */
const UNSPLASH_ACCESS_KEY = process.env.NEXT_PUBLIC_UNSPLASH_ACCESS_KEY || '';

/**
 * API key for Bing Image Search (should be set in environment variables)
 */
const BING_SEARCH_API_KEY = process.env.NEXT_PUBLIC_BING_SEARCH_API_KEY || '';

/**
 * Cache for storing image URLs to avoid redundant API calls
 * Key format: make-model-year or make-model
 */
const imageCache: { [key: string]: string[] } = {};

/**
 * Searches Unsplash for car images based on vehicle details
 */
const searchUnsplashImages = async (vehicle: Vehicle): Promise<string[]> => {
  if (!UNSPLASH_ACCESS_KEY) {
    console.warn('Unsplash API key not configured, skipping Unsplash image search');
    return [];
  }

  try {
    const { make, model, year } = vehicle;
    const query = `${make} ${model} ${year || ''}`.trim();
    
    // Build search parameters
    const params = new URLSearchParams({
      query: query,
      per_page: '3',
      orientation: 'landscape',
      client_id: UNSPLASH_ACCESS_KEY
    });

    // Make the API call
    const response = await fetch(`https://api.unsplash.com/search/photos?${params}`);
    
    if (!response.ok) {
      throw new Error(`Unsplash API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Map results to image URLs
    const images = data.results.map((result: any) => result.urls.regular);
    
    if (images.length > 0) {
      console.log(`Found ${images.length} Unsplash images for ${query}`);
      // Cache the results
      const cacheKey = `${make}-${model}${year ? '-' + year : ''}`.toLowerCase().replace(/\s+/g, '-');
      imageCache[cacheKey] = images;
    }
    
    return images;
  } catch (error) {
    console.error('Error searching Unsplash:', error);
    return [];
  }
};

/**
 * Searches Bing Image Search for car images based on vehicle details
 */
const searchBingImages = async (vehicle: Vehicle): Promise<string[]> => {
  if (!BING_SEARCH_API_KEY) {
    console.warn('Bing Search API key not configured, skipping Bing image search');
    return [];
  }
  
  try {
    const { make, model, year, exteriorColor } = vehicle;
    const colorInfo = exteriorColor && !exteriorColor.toLowerCase().includes('unknown') ? exteriorColor : '';
    const query = `${year || ''} ${make} ${model} ${colorInfo}`.trim();
    
    // Make the API call
    const response = await fetch(
      'https://api.bing.microsoft.com/v7.0/images/search?' + new URLSearchParams({
        q: query,
        count: '5',
        aspect: 'Wide',
        mkt: 'en-US'
      }), 
      {
        headers: {
          'Ocp-Apim-Subscription-Key': BING_SEARCH_API_KEY
        }
      }
    );
    
    if (!response.ok) {
      throw new Error(`Bing API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Map results to image URLs, filtering out potentially problematic URLs
    const images = data.value
      .filter((item: any) => {
        // Filter out suspicious or problematic domains
        const url = item.contentUrl.toLowerCase();
        return !url.includes('placeholder') && 
               !url.includes('blocked') &&
               !url.includes('transparent') &&
               !url.includes('svg');
      })
      .map((item: any) => item.contentUrl)
      .slice(0, 3); // Limit to 3 images
    
    if (images.length > 0) {
      console.log(`Found ${images.length} Bing images for ${query}`);
      // Cache the results
      const cacheKey = `${make}-${model}${year ? '-' + year : ''}`.toLowerCase().replace(/\s+/g, '-');
      imageCache[cacheKey] = images;
    }
    
    return images;
  } catch (error) {
    console.error('Error searching Bing:', error);
    return [];
  }
};

/**
 * Gets images from the local mapping file
 */
const getImagesFromMapping = async (vehicle: Vehicle): Promise<string[]> => {
  try {
    // Try to load the mapping file
    let imageMapping: { [key: string]: string[] } = {};
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
      return imageMapping[vehicle.id];
    }

    // Next try by make/model/year combination
    const { make, model, year } = vehicle;
    if (make && model && year) {
      const carIdentifier = `${make}-${model}-${year}`.toLowerCase().replace(/\s+/g, '-');
      if (imageMapping[carIdentifier] && imageMapping[carIdentifier].length > 0) {
        return imageMapping[carIdentifier];
      }
      
      // Try just the make-model (without year)
      const makeModelKey = `${make}-${model}`.toLowerCase().replace(/\s+/g, '-');
      if (imageMapping[makeModelKey] && imageMapping[makeModelKey].length > 0) {
        return imageMapping[makeModelKey];
      }

      // Try just the make
      const makeKey = make.toLowerCase().replace(/\s+/g, '-');
      if (imageMapping[makeKey] && imageMapping[makeKey].length > 0) {
        return imageMapping[makeKey];
      }
    }

    return [];
  } catch (error) {
    console.error('Error fetching images from mapping:', error);
    return [];
  }
};

/**
 * Gets the default fallback images for a vehicle
 */
const getDefaultImages = (vehicle: Vehicle): string[] => {
  const baseImage = getFallbackImage(vehicle);
  const imageBase = baseImage.replace(/\d+\.jpg$/, '');
    
  // Add three variations of real car photos for this vehicle
  const images = [
    `${imageBase}1.jpg`,
    `${imageBase}2.jpg`,
    `${imageBase}3.jpg`
  ];
  
  // Make sure the fallbacks exist, otherwise use the default
  if (baseImage.includes('default')) {
    return [
      '/vehicle-images/default-car-1.jpg',
      '/vehicle-images/default-car-2.jpg',
      '/vehicle-images/default-car-3.jpg'
    ];
  }
  
  return images;
};

/**
 * Main function to get vehicle images
 * Implements the fallback logic: External APIs → Mapping → AI Generation → Default Images
 */
export const getVehicleImages = async (vehicle: Vehicle): Promise<string[]> => {
  // If this is one of our featured listings, preserve its hardcoded images
  if (FEATURED_LISTING_IDS.includes(vehicle.id)) {
    console.log(`Preserving hardcoded images for featured vehicle ${vehicle.id}`);
    return vehicle.images;
  }

  // Skip if vehicle has valid images already
  if (vehicle.images && vehicle.images.length > 0 && 
      vehicle.images.every(url => !url.includes('placeholder'))) {
    return vehicle.images;
  }

  // Check the cache first
  const { make, model, year } = vehicle;
  const cacheKey = `${make}-${model}${year ? '-' + year : ''}`.toLowerCase().replace(/\s+/g, '-');
  
  if (imageCache[cacheKey] && imageCache[cacheKey].length > 0) {
    console.log(`Using cached images for ${cacheKey}`);
    return imageCache[cacheKey];
  }

  // Step 1: Try Unsplash API
  const unsplashImages = await searchUnsplashImages(vehicle);
  if (unsplashImages.length > 0) {
    return unsplashImages;
  }
  
  // Step 2: Try Bing Image Search
  const bingImages = await searchBingImages(vehicle);
  if (bingImages.length > 0) {
    return bingImages;
  }
  
  // Step 3: Try local image mapping
  const mappingImages = await getImagesFromMapping(vehicle);
  if (mappingImages.length > 0) {
    return mappingImages;
  }
  
  // Step 4: Try AI image generation if available
  if (aiImageGenerationService.isAiImageGenerationAvailable()) {
    console.log(`Attempting AI image generation for ${vehicle.make} ${vehicle.model}`);
    const aiImages = await aiImageGenerationService.generateVehicleImages(vehicle, 3);
    if (aiImages.length > 0) {
      return aiImages;
    }
  }
  
  // Step 5: Use default images as final fallback
  return getDefaultImages(vehicle);
};

/**
 * Utility function to update a vehicle with accurate images
 */
export const enrichVehicleWithImages = async (vehicle: Vehicle): Promise<Vehicle> => {
  // Skip if this is one of our featured listings
  if (FEATURED_LISTING_IDS.includes(vehicle.id)) {
    return vehicle;
  }
  
  try {
    const images = await getVehicleImages(vehicle);
    return {
      ...vehicle,
      images,
      hasErrorLoadingImage: false,
      _retryCount: 0
    };
  } catch (error) {
    console.error(`Error enriching vehicle ${vehicle.id} with images:`, error);
    return vehicle;
  }
};

/**
 * Utility function to update multiple vehicles with accurate images
 */
export const enrichVehiclesWithImages = async (vehicles: Vehicle[]): Promise<Vehicle[]> => {
  // Process vehicles in batches to avoid overwhelming APIs
  const batchSize = 5;
  const results: Vehicle[] = [];
  
  for (let i = 0; i < vehicles.length; i += batchSize) {
    const batch = vehicles.slice(i, i + batchSize);
    const enrichedBatch = await Promise.all(batch.map(enrichVehicleWithImages));
    results.push(...enrichedBatch);
    
    // Add a small delay between batches to avoid rate limiting
    if (i + batchSize < vehicles.length) {
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }
  
  return results;
};

// Export the service
export default {
  getVehicleImages,
  enrichVehicleWithImages,
  enrichVehiclesWithImages
};
