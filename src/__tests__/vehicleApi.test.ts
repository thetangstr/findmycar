import { fetchVehicles, fetchVehicleById, searchVehicles } from '../services/vehicleApi';
import '@testing-library/jest-dom';
import { describe, expect, test } from '@jest/globals';

describe('Vehicle API Service', () => {
  // Test fetchVehicles function
  test('fetchVehicles should return an array of vehicles', async () => {
    const vehicles = await fetchVehicles();
    
    // Check that we get an array
    expect(Array.isArray(vehicles)).toBe(true);
    
    // Check that the array is not empty
    expect(vehicles.length).toBeGreaterThan(0);
    
    // Check that each vehicle has the required properties
    vehicles.forEach(vehicle => {
      expect(vehicle).toHaveProperty('id');
      expect(vehicle).toHaveProperty('make');
      expect(vehicle).toHaveProperty('model');
      expect(vehicle).toHaveProperty('year');
      expect(vehicle).toHaveProperty('price');
      expect(vehicle).toHaveProperty('mileage');
    });
  });
  
  // Test fetchVehicleById function
  test('fetchVehicleById should return a single vehicle when given a valid ID', async () => {
    // First get all vehicles to find a valid ID
    const vehicles = await fetchVehicles();
    const testId = vehicles[0].id;
    
    // Fetch the vehicle by ID
    const vehicle = await fetchVehicleById(testId);
    
    // Check that we got a vehicle
    expect(vehicle).not.toBeNull();
    expect(vehicle?.id).toBe(testId);
    expect(vehicle).toHaveProperty('make');
    expect(vehicle).toHaveProperty('model');
    expect(vehicle).toHaveProperty('year');
  });
  
  test('fetchVehicleById should return null for an invalid ID', async () => {
    const vehicle = await fetchVehicleById('invalid-id');
    expect(vehicle).toBeNull();
  });
  
  // Test searchVehicles function
  test('searchVehicles should filter vehicles by make', async () => {
    // Get all vehicles first to find a make to search for
    const allVehicles = await fetchVehicles();
    const testMake = allVehicles[0].make;
    
    // Search for vehicles with that make
    const filteredVehicles = await searchVehicles({ make: testMake });
    
    // Check that all returned vehicles have the correct make
    expect(filteredVehicles.length).toBeGreaterThan(0);
    filteredVehicles.forEach(vehicle => {
      expect(vehicle.make.toLowerCase()).toBe(testMake.toLowerCase());
    });
  });
  
  test('searchVehicles should filter vehicles by price range', async () => {
    const priceMin = 25000;
    const priceMax = 35000;
    
    const filteredVehicles = await searchVehicles({ 
      priceMin,
      priceMax
    });
    
    // Check that all returned vehicles are within the price range
    filteredVehicles.forEach(vehicle => {
      expect(vehicle.price).toBeGreaterThanOrEqual(priceMin);
      expect(vehicle.price).toBeLessThanOrEqual(priceMax);
    });
  });
  
  test('searchVehicles should filter vehicles by multiple criteria', async () => {
    // Get all vehicles first to find values to search for
    const allVehicles = await fetchVehicles();
    const testMake = 'Toyota'; // Using a specific make for consistency
    const testFuelType = 'Hybrid'; // Using a specific fuel type
    
    // Search for vehicles with those criteria
    const filteredVehicles = await searchVehicles({ 
      make: testMake,
      fuelType: testFuelType
    });
    
    // Check that all returned vehicles match both criteria
    if (filteredVehicles.length > 0) {
      filteredVehicles.forEach(vehicle => {
        expect(vehicle.make).toBe(testMake);
        expect(vehicle.fuelType).toBe(testFuelType);
      });
    }
  });
});
