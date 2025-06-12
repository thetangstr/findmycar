import { Vehicle } from '@/types';
import { mockVehicles } from '@/data/mockVehicles';

/**
 * Curated featured vehicles with diverse sources and proper images
 * Now using our 3 reliable mock listings for a consistent demo experience
 */
export const getFeaturedVehicles = (): Vehicle[] => {
  // Get only our 3 custom mock vehicle listings (the first 3 in the array)
  return mockVehicles.slice(0, 3);
};

/**
 * Get a featured vehicle by ID
 */
export const getFeaturedVehicleById = (id: string): Vehicle | null => {
  const vehicles = getFeaturedVehicles();
  return vehicles.find(vehicle => vehicle.id === id) || null;
};

export default {
  getFeaturedVehicles,
  getFeaturedVehicleById
};