import { Vehicle, SearchFilters } from '@/types';

// Import static real listings data
import realListingsData from '../data/real_listings.json';

// Type assertion to ensure the imported data is treated as an array of Vehicle objects
const realListings = realListingsData as Vehicle[];

/**
 * Fetches all real vehicle listings from our static dataset
 * @returns Promise<Vehicle[]> Array of vehicle objects
 */
export const fetchRealVehicles = async (): Promise<Vehicle[]> => {
  try {
    // Return the static real listings data
    return realListings;
  } catch (error) {
    console.error('Error fetching real vehicles:', error);
    throw error;
  }
};

/**
 * Fetches a single vehicle by ID from our static dataset
 * @param id The vehicle ID to find
 * @returns Promise<Vehicle | null> The vehicle object or null if not found
 */
export const fetchRealVehicleById = async (id: string): Promise<Vehicle | null> => {
  try {
    // Find the vehicle with the matching ID in our static dataset
    return realListings.find(vehicle => vehicle.id === id) || null;
  } catch (error) {
    console.error('Error fetching real vehicle by ID:', error);
    throw error;
  }
};

/**
 * Searches vehicles with filters from our static dataset
 * @param filters The search filters to apply
 * @returns Promise<Vehicle[]> Array of filtered vehicle objects
 */
export const searchRealVehicles = async (filters: SearchFilters): Promise<Vehicle[]> => {
  try {
    // Apply filters to our static dataset
    return realListings.filter(vehicle => {
      // Check make
      if (filters.make && vehicle.make.toLowerCase() !== filters.make.toLowerCase()) {
        return false;
      }
      
      // Check model
      if (filters.model && !vehicle.model.toLowerCase().includes(filters.model.toLowerCase())) {
        return false;
      }
      
      // Check year range
      if (filters.yearMin && vehicle.year < filters.yearMin) {
        return false;
      }
      if (filters.yearMax && vehicle.year > filters.yearMax) {
        return false;
      }
      
      // Check price range
      if (filters.priceMin && vehicle.price < filters.priceMin) {
        return false;
      }
      if (filters.priceMax && vehicle.price > filters.priceMax) {
        return false;
      }
      
      // Check mileage range
      if (filters.mileageMin && vehicle.mileage < filters.mileageMin) {
        return false;
      }
      if (filters.mileageMax && vehicle.mileage > filters.mileageMax) {
        return false;
      }
      
      // Check fuel type
      if (filters.fuelType && vehicle.fuelType !== filters.fuelType) {
        return false;
      }
      
      // Check transmission
      if (filters.transmission && vehicle.transmission !== filters.transmission) {
        return false;
      }
      
      // Check text query
      if (filters.query) {
        const query = filters.query.toLowerCase();
        const searchableText = `${vehicle.make} ${vehicle.model} ${vehicle.year} ${vehicle.description} ${vehicle.features.join(' ')}`.toLowerCase();
        
        if (!searchableText.includes(query)) {
          return false;
        }
      }
      
      return true;
    });
  } catch (error) {
    console.error('Error searching real vehicles:', error);
    throw error;
  }
};

export default {
  fetchRealVehicles,
  fetchRealVehicleById,
  searchRealVehicles
};
