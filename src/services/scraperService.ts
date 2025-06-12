/**
 * scraperService.ts
 * 
 * Service for retrieving vehicle data from Firestore.
 * This file has been cleaned up to contain only the essential Hemmings functionality.
 * All unused scraper functions have been moved to src/services/archived/unused_scrapers.ts
 */

import { Vehicle } from '@/types';
import { app } from '@/utils/firebase';
import { getFirestore, collection, getDocs, query } from 'firebase/firestore';

/**
 * Collection name for Hemmings car listings scraped by the Python scraper component
 */
const HEMMINGS_COLLECTION = 'cars_collection';

/**
 * Fetches car listings scraped from Hemmings.com from the Firestore database.
 * This function is used by both the search page and the featured listings component.
 * 
 * @returns A Promise that resolves to an array of Vehicle objects
 */
/**
 * Returns mock vehicle listings for demo purposes.
 * This replaces the original Hemmings data fetching to avoid image load errors
 * and provide a consistent, reliable demo experience with high-quality listings.
 * 
 * @returns A Promise that resolves to an array of Vehicle objects
 */
export const getHemmingsListings = async (): Promise<Vehicle[]> => {
  try {
    console.log('Using mock demo listings instead of fetching from Firestore');
    
    // Import mock vehicles (specifically the first 3 which are our new demo vehicles)
    const { mockVehicles } = await import('../data/mockVehicles');
    
    // Use only the first 3 mock vehicles (our custom demo listings)
    const demoListings = mockVehicles.slice(0, 3);
    
    console.log(`Returning ${demoListings.length} mock demo listings`);
    return demoListings;
  } catch (error) {
    console.error('Error loading mock demo listings:', error);
    return [];
  }
};


/**
 * Provides fallback sample data when Firestore isn't available or empty
 * Includes appreciation data to show classic car value increases over time
 */
/**
 * Provides reliable hosted images for Hemmings vehicle listings based on make/model
 * This replaces the problematic external URLs from dealeraccelerate domains
 * @param make Vehicle make
 * @param model Vehicle model
 * @param year Vehicle year
 * @returns Array of reliable image URLs
 */
const getReliableImagesForHemmings = (make: string, model: string, year: number): string[] => {
  // Convert make and model to lowercase for case-insensitive matching
  const makeLower = (make || '').toLowerCase();
  const modelLower = (model || '').toLowerCase();
  
  // Default images for common classic car types
  if (makeLower.includes('chevrolet') || makeLower.includes('chevy')) {
    if (modelLower.includes('corvette')) {
      return [
        'https://images.unsplash.com/photo-1603386329225-868f9b1ee6c9?q=80&w=2069&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1611859266238-4b96402e0c7c?q=80&w=2069&auto=format&fit=crop'
      ];
    } else if (modelLower.includes('camaro')) {
      return [
        'https://images.unsplash.com/photo-1603553329474-99f95f35394f?q=80&w=2070&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1612544448445-b8232cff3b6a?q=80&w=2070&auto=format&fit=crop'
      ];
    }
  } else if (makeLower.includes('ford')) {
    if (modelLower.includes('mustang')) {
      return [
        'https://images.unsplash.com/photo-1592198084033-aade902d1aae?q=80&w=2070&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1597007029837-20a4190a1853?q=80&w=2069&auto=format&fit=crop'
      ];
    } else if (modelLower.includes('thunderbird')) {
      return [
        'https://images.unsplash.com/photo-1541038079060-3a9e57b16670?q=80&w=2070&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1596750882402-ab9cb897c6f0?q=80&w=2069&auto=format&fit=crop'
      ];
    }
  } else if (makeLower.includes('porsche')) {
    if (modelLower.includes('911')) {
      return [
        'https://images.unsplash.com/photo-1596458397260-255807e979f0?q=80&w=2070&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1600712242805-5f78671b24da?q=80&w=2071&auto=format&fit=crop'
      ];
    } else if (modelLower.includes('356')) {
      return [
        'https://images.unsplash.com/photo-1580274437636-1c384e617d5b?q=80&w=2068&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1621345578124-aff7a77ea0af?q=80&w=2070&auto=format&fit=crop'
      ];
    }
  } else if (makeLower.includes('ferrari')) {
    return [
      'https://images.unsplash.com/photo-1592364395653-83e648b20cc2?q=80&w=2070&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1583121274602-3e2820c69888?q=80&w=2070&auto=format&fit=crop'
    ];
  } else if (makeLower.includes('jaguar')) {
    if (modelLower.includes('e-type') || modelLower.includes('xke')) {
      return [
        'https://images.unsplash.com/photo-1563225409-127c18758bd5?q=80&w=2070&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1553440569-bcc63803a83d?q=80&w=2025&auto=format&fit=crop'
      ];
    }
  } else if (makeLower.includes('mercedes')) {
    return [
      'https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?q=80&w=2070&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1535732820275-9ffd998cac22?q=80&w=2070&auto=format&fit=crop'
    ];
  } else if (makeLower.includes('bmw')) {
    return [
      'https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=2070&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1549399542-7e8f2b0c6781?q=80&w=2073&auto=format&fit=crop'
    ];
  }
  
  // Fallback for pre-1980s classic cars
  if (year < 1980) {
    return [
      'https://images.unsplash.com/photo-1566008885218-90abf9200ddb?q=80&w=2132&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1584346133934-a3f8d4246d4c?q=80&w=2070&auto=format&fit=crop'
    ];
  }
  
  // Generic fallback for any vehicle
  return [
    'https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?q=80&w=2070&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=2083&auto=format&fit=crop'
  ];
};

/**
 * Helper function to validate image URLs for Hemmings listings (no longer used)
 * @param url The image URL to validate
 * @returns boolean indicating if the URL is valid
 */
/*
const isValidImageUrl = (url: string): boolean => {
  if (!url) return false;
  
  // Basic URL format validation
  try {
    new URL(url);
    return true;
  } catch (e) {
    console.error(`Invalid Hemmings image URL format: ${url}`);
    return false;
  }
};
*/

/**
 * Fixes common issues with Hemmings image URLs from dealeraccelerate domains (no longer used)
 * @param url The potentially malformed image URL
 * @returns Fixed URL or the original if no fixes needed/possible
 */
/*
const fixHemmingsImageUrl = (url: string): string => {
  if (!url) return '';
  
  try {
    // Handle partial URLs missing protocol
    if (url.startsWith('//')) {
      return `https:${url}`;
    }
    
    // Handle dealeraccelerate URLs
    if (url.includes('dealeraccelerate.com')) {
      // Fix URLs with improper formatting or missing components
      if (!url.startsWith('http')) {
        return `https://${url.replace(/^\/+/, '')}`;
      }
      
      // Fix double slashes issue (except after protocol)
      return url.replace(/(https?:\/\/)|(\/{2,})/g, (match, protocol) => {
        return protocol || '/';
      });
    }
    
    // Handle other common image URL issues
    if (!url.match(/^https?:\/\//)) {
      return `https://${url.replace(/^\/+/, '')}`;
    }
    
    return url;
  } catch (e) {
    console.error(`Failed to fix Hemmings image URL: ${url}`, e);
    return ''; // Return empty string to be filtered out
  }
};
*/

const getFallbackHemmingsListings = (): Vehicle[] => {
  console.log('Using fallback Hemmings listings');
  
  // Sample classic car listings with appreciation data
  return [
    {
      id: 'hemmings-1',
      make: 'Chevrolet',
      model: 'Corvette',
      year: 1963,
      price: 149995,
      description: 'Split Window Coupe, 327/340HP, 4-Speed, Factory Air, NCRS Top Flight',
      source: 'hemmings',
      url: 'https://www.hemmings.com/classifieds/cars-for-sale/chevrolet/corvette/2624095.html',
      mileage: 56000,
      vin: '30837S109XXX',
      exteriorColor: 'Silver',
      interiorColor: 'Black',
      fuelType: 'Gasoline',
      transmission: 'Manual',
      engine: '327ci V8',
      features: ['Split Window', 'Factory Air', 'NCRS Top Flight'],
      images: [
        'https://images.unsplash.com/photo-1603386329225-868f9b1ee6c9?q=80&w=2069&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1611859266238-4b96402e0c7c?q=80&w=2069&auto=format&fit=crop'
      ],
      location: 'Los Angeles, CA',
      dealer: 'Classic Car Dealer',
      listingDate: new Date().toISOString()
    },
    {
      id: 'hemmings-2',
      make: 'Ford',
      model: 'Mustang',
      year: 1967,
      price: 79900,
      description: 'Shelby GT500, 428ci, 4-Speed, Documented, Restored',
      source: 'hemmings',
      url: 'https://www.hemmings.com/classifieds/cars-for-sale/ford/mustang/2624096.html',
      mileage: 78000,
      vin: '7T02C123456',
      exteriorColor: 'Blue',
      interiorColor: 'Black',
      fuelType: 'Gasoline',
      transmission: 'Manual',
      engine: '428ci V8',
      features: ['Shelby', 'Restored', 'Documented'],
      images: [
        'https://images.unsplash.com/photo-1592198084033-aade902d1aae?q=80&w=2070&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1597007029837-20a4190a1853?q=80&w=2069&auto=format&fit=crop'
      ],
      location: 'Chicago, IL',
      dealer: 'Shelby Specialists',
      listingDate: new Date().toISOString()
    },
    {
      id: 'hemmings-3',
      make: 'Porsche',
      model: '911',
      year: 1973,
      price: 189500,
      description: 'Carrera RS Lightweight, Matching Numbers, Restored, Documented',
      source: 'hemmings',
      url: 'https://www.hemmings.com/classifieds/cars-for-sale/porsche/911/2624097.html',
      mileage: 45000,
      vin: '9113600XXX',
      exteriorColor: 'White',
      interiorColor: 'Black',
      fuelType: 'Gasoline',
      transmission: 'Manual',
      engine: '2.7L Flat-6',
      features: ['Carrera RS', 'Lightweight', 'Matching Numbers'],
      images: [
        'https://images.unsplash.com/photo-1596458397260-255807e979f0?q=80&w=2070&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1600712242805-5f78671b24da?q=80&w=2071&auto=format&fit=crop'
      ],
      location: 'Miami, FL',
      dealer: 'European Classics',
      listingDate: new Date().toISOString()
    }
  ];
};
