import { Vehicle, SearchFilters } from '@/types';
import { getFirestoreVehicles, getFirestoreVehicleById } from './firebaseService';

// Cache for vehicles to avoid unnecessary Firestore reads
let vehiclesCache: Vehicle[] | null = null;
let lastFetchTime = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

/**
 * Get all vehicles from multiple sources with fallbacks
 * @returns Promise resolving to array of vehicles
 */
export const getVehicles = async (): Promise<Vehicle[]> => {
  const now = Date.now();
  
  // Use cache if available and not expired
  if (vehiclesCache && (now - lastFetchTime < CACHE_DURATION)) {
    return vehiclesCache;
  }
  
  try {
    // Try to fetch vehicles from Firestore first
    let vehicles = await getFirestoreVehicles();
    
    // If Firestore returns empty or insufficient data, try BAT data
    if (!vehicles || vehicles.length === 0) {
      console.log('Firestore empty, trying BAT listings...');
      const { fetchBatVehicles } = await import('./batVehicleApi');
      vehicles = await fetchBatVehicles();
    }
    
    // If still no data, use mock vehicles as final fallback
    if (!vehicles || vehicles.length === 0) {
      console.log('No external data, using mock vehicles...');
      vehicles = getMockVehicles();
    }
    
    // Update cache
    vehiclesCache = vehicles;
    lastFetchTime = now;
    
    return vehicles;
  } catch (error) {
    console.error('Error fetching vehicles:', error);
    
    // Fallback to mock data if all sources fail
    return getMockVehicles();
  }
};

/**
 * Get a vehicle by ID from Firestore
 * @param id Vehicle ID
 * @returns Promise resolving to vehicle or null if not found
 */
export const getVehicleById = async (id: string): Promise<Vehicle | null> => {
  try {
    // Try to find in cache first
    if (vehiclesCache) {
      const cachedVehicle = vehiclesCache.find(v => v.id === id);
      if (cachedVehicle) {
        return cachedVehicle;
      }
    }
    
    // Fetch from Firestore if not in cache
    const vehicle = await getFirestoreVehicleById(id);
    return vehicle;
  } catch (error) {
    console.error(`Error fetching vehicle ${id}:`, error);
    
    // Fallback to mock data if Firestore fetch fails
    if (vehiclesCache) {
      return vehiclesCache.find(v => v.id === id) || null;
    }
    
    const mockVehicles = getMockVehicles();
    return mockVehicles.find(v => v.id === id) || null;
  }
};

/**
 * Search vehicles based on filters
 * @param filters Search filters
 * @returns Promise resolving to filtered vehicles
 */
export const searchVehicles = async (filters: SearchFilters): Promise<Vehicle[]> => {
  try {
    const allVehicles = await getVehicles();
    
    return allVehicles.filter(vehicle => {
      // Apply make filter
      if (filters.make && filters.make !== 'Any' && vehicle.make !== filters.make) {
        return false;
      }
      
      // Apply model filter
      if (filters.model && filters.model !== 'Any' && vehicle.model !== filters.model) {
        return false;
      }
      
      // Apply year range filter
      if (filters.yearMin && vehicle.year < filters.yearMin) {
        return false;
      }
      if (filters.yearMax && vehicle.year > filters.yearMax) {
        return false;
      }
      
      // Apply price range filter
      if (filters.priceMin && vehicle.price < filters.priceMin) {
        return false;
      }
      if (filters.priceMax && vehicle.price > filters.priceMax) {
        return false;
      }
      
      // Apply mileage range filter
      if (filters.mileageMin && vehicle.mileage < filters.mileageMin) {
        return false;
      }
      if (filters.mileageMax && vehicle.mileage > filters.mileageMax) {
        return false;
      }
      
      // Apply exterior color filter
      if (filters.exteriorColor && filters.exteriorColor !== 'Any' && vehicle.exteriorColor !== filters.exteriorColor) {
        return false;
      }
      
      // Apply interior color filter
      if (filters.interiorColor && filters.interiorColor !== 'Any' && vehicle.interiorColor !== filters.interiorColor) {
        return false;
      }
      
      // Apply fuel type filter
      if (filters.fuelType && filters.fuelType !== 'Any' && vehicle.fuelType !== filters.fuelType) {
        return false;
      }
      
      // Apply transmission filter
      if (filters.transmission && filters.transmission !== 'Any' && vehicle.transmission !== filters.transmission) {
        return false;
      }
      
      return true;
    });
  } catch (error) {
    console.error('Error searching vehicles:', error);
    return [];
  }
};

/**
 * Get featured vehicles - using curated collection
 * @param count Number of featured vehicles to return
 * @returns Promise resolving to array of featured vehicles
 */
export const getFeaturedVehicles = async (count: number = 3): Promise<Vehicle[]> => {
  try {
    // Import and use our curated featured vehicles
    const { getFeaturedVehicles: getCuratedFeatured } = await import('./featuredVehiclesService');
    const featuredVehicles = getCuratedFeatured();
    
    // Return the requested number of featured vehicles
    return featuredVehicles.slice(0, count);
  } catch (error) {
    console.error('Error fetching featured vehicles:', error);
    
    // Fallback to regular vehicles if curated ones fail
    try {
      const allVehicles = await getVehicles();
      const sortedVehicles = [...allVehicles].sort((a, b) => b.price - a.price);
      return sortedVehicles.slice(0, count);
    } catch (fallbackError) {
      console.error('Error in fallback featured vehicles:', fallbackError);
      return [];
    }
  }
};

/**
 * Get available makes from the vehicle data
 * @returns Promise resolving to array of unique makes
 */
export const getAvailableMakes = async (): Promise<string[]> => {
  try {
    const allVehicles = await getVehicles();
    const makes = new Set(allVehicles.map(vehicle => vehicle.make));
    return Array.from(makes).sort();
  } catch (error) {
    console.error('Error fetching available makes:', error);
    return [];
  }
};

/**
 * Get available models for a specific make
 * @param make Vehicle make
 * @returns Promise resolving to array of unique models for the make
 */
export const getAvailableModels = async (make: string): Promise<string[]> => {
  try {
    const allVehicles = await getVehicles();
    const models = new Set(
      allVehicles
        .filter(vehicle => make === 'Any' || vehicle.make === make)
        .map(vehicle => vehicle.model)
    );
    return Array.from(models).sort();
  } catch (error) {
    console.error(`Error fetching available models for ${make}:`, error);
    return [];
  }
};

/**
 * Get available exterior colors from the vehicle data
 * @returns Promise resolving to array of unique exterior colors
 */
export const getAvailableExteriorColors = async (): Promise<string[]> => {
  try {
    const allVehicles = await getVehicles();
    const colors = new Set(allVehicles.map(vehicle => vehicle.exteriorColor));
    return Array.from(colors).sort();
  } catch (error) {
    console.error('Error fetching available exterior colors:', error);
    return [];
  }
};

/**
 * Get available interior colors from the vehicle data
 * @returns Promise resolving to array of unique interior colors
 */
export const getAvailableInteriorColors = async (): Promise<string[]> => {
  try {
    const allVehicles = await getVehicles();
    const colors = new Set(allVehicles.map(vehicle => vehicle.interiorColor));
    return Array.from(colors).sort();
  } catch (error) {
    console.error('Error fetching available interior colors:', error);
    return [];
  }
};

/**
 * Get available fuel types from the vehicle data
 * @returns Promise resolving to array of unique fuel types
 */
export const getAvailableFuelTypes = async (): Promise<string[]> => {
  try {
    const allVehicles = await getVehicles();
    const fuelTypes = new Set(allVehicles.map(vehicle => vehicle.fuelType));
    return Array.from(fuelTypes).sort();
  } catch (error) {
    console.error('Error fetching available fuel types:', error);
    return [];
  }
};

/**
 * Get available transmissions from the vehicle data
 * @returns Promise resolving to array of unique transmissions
 */
export const getAvailableTransmissions = async (): Promise<string[]> => {
  try {
    const allVehicles = await getVehicles();
    const transmissions = new Set(allVehicles.map(vehicle => vehicle.transmission));
    return Array.from(transmissions).sort();
  } catch (error) {
    console.error('Error fetching available transmissions:', error);
    return [];
  }
};

/**
 * Fallback mock vehicles data in case Firestore fetch fails
 * @returns Array of mock vehicles
 */
const getMockVehicles = (): Vehicle[] => {
  return [
    {
      id: 'porsche911',
      make: 'Porsche',
      model: '911',
      year: 1975,
      price: 89500,
      mileage: 45000,
      exteriorColor: 'Silver',
      interiorColor: 'Black',
      fuelType: 'Gasoline',
      transmission: 'Manual',
      engine: '3.6L Flat-6',
      vin: 'WP0AA29975S710001',
      description: 'Classic Porsche 911 in excellent condition. Well maintained with service records.',
      features: ['Air Conditioning', 'Power Steering', 'Leather Seats', 'Alloy Wheels', 'Classic Radio'],
      images: [
        'https://images.unsplash.com/photo-1580274455191-1c62238fa333?q=80&w=2000',
        'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?q=80&w=1000',
        'https://images.unsplash.com/photo-1518987048-93e29699e79a?q=80&w=1000'
      ],
      location: 'Los Angeles, CA',
      dealer: 'Classic Car Collection',
      listingDate: '2023-05-15',
      source: 'Classic Car Marketplace',
      url: 'https://example.com/porsche-911-1975'
    },
    {
      id: 'corvette',
      make: 'Chevrolet',
      model: 'Corvette',
      year: 1963,
      price: 150000,
      mileage: 35000,
      exteriorColor: 'Red',
      interiorColor: 'Black',
      fuelType: 'Gasoline',
      transmission: 'Manual',
      engine: '5.7L V8',
      vin: '30837S100001',
      description: 'Iconic American sports car in pristine condition. A true collector\'s item.',
      features: ['Convertible Top', 'AM/FM Radio', 'Power Windows', 'Chrome Wheels', 'Vintage Interior'],
      images: [
        'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?q=80&w=1000',
        'https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?q=80&w=1000',
        'https://images.unsplash.com/photo-1577495508048-b635879837f1?q=80&w=1000'
      ],
      location: 'Miami, FL',
      dealer: 'Vintage Auto Gallery',
      listingDate: '2023-06-20',
      source: 'Collector Car Auctions',
      url: 'https://example.com/corvette-1963'
    },
    // More fallback vehicles would be here...
  ];
};
