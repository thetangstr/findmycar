import axios from 'axios';
import { Vehicle } from '@/types';
import mockVehicles from '@/data/mockVehicles';

// CarQuery API base URL
const CAR_QUERY_API_BASE_URL = 'https://www.carqueryapi.com/api/0.3/';

/**
 * Fetch makes from the CarQuery API
 */
export const fetchMakes = async (year?: number): Promise<string[]> => {
  try {
    // In a production app, this would make a real API call
    // For now, we'll extract unique makes from our mock data
    const makes = [...new Set(mockVehicles.map(vehicle => vehicle.make))];
    return makes.sort();
  } catch (error) {
    console.error('Error fetching makes:', error);
    return [];
  }
};

/**
 * Fetch models for a specific make from the CarQuery API
 */
export const fetchModels = async (make: string, year?: number): Promise<string[]> => {
  try {
    // In a production app, this would make a real API call
    // For now, we'll filter models from our mock data
    const models = [...new Set(
      mockVehicles
        .filter(vehicle => vehicle.make.toLowerCase() === make.toLowerCase())
        .map(vehicle => vehicle.model)
    )];
    return models.sort();
  } catch (error) {
    console.error(`Error fetching models for ${make}:`, error);
    return [];
  }
};

/**
 * Fetch vehicle listings from multiple sources
 * In a real app, this would aggregate from multiple APIs
 */
export const fetchVehicleListings = async (filters: any = {}): Promise<Vehicle[]> => {
  try {
    // Simulate API latency
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // In a production app, this would make real API calls to multiple sources
    // For now, we'll return our mock data
    return mockVehicles;
  } catch (error) {
    console.error('Error fetching vehicle listings:', error);
    return [];
  }
};

/**
 * Fetch a single vehicle by ID
 */
export const fetchVehicleById = async (id: string): Promise<Vehicle | null> => {
  try {
    // Simulate API latency
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // In a production app, this would make a real API call
    // For now, we'll find the vehicle in our mock data
    const vehicle = mockVehicles.find(v => v.id === id);
    return vehicle || null;
  } catch (error) {
    console.error(`Error fetching vehicle with ID ${id}:`, error);
    return null;
  }
};

/**
 * This would be the integration point for multiple real APIs in a production app
 * For example:
 * - CarGurus API
 * - AutoTrader API
 * - Cars.com API
 * - Edmunds API
 * - etc.
 */
export const aggregateListingsFromMultipleSources = async (filters: any = {}): Promise<Vehicle[]> => {
  // This would make parallel requests to multiple APIs and combine the results
  return fetchVehicleListings(filters);
};
