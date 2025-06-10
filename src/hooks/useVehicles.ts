import { useState, useEffect, useCallback } from 'react';
import { Vehicle, SearchFilters } from '@/types';
import vehicleApi from '@/services/vehicleApi';

export const useVehicles = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [filteredVehicles, setFilteredVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<SearchFilters>({});

  // Fetch vehicles from the API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await vehicleApi.fetchVehicles();
        setVehicles(data);
        setFilteredVehicles(data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch vehicles');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  // Apply filters to vehicles using the API
  const applyFilters = useCallback(async (newFilters: SearchFilters) => {
    setFilters(newFilters);
    setLoading(true);
    
    try {
      // Use the API to search with filters
      const results = await vehicleApi.searchVehicles(newFilters);
      setFilteredVehicles(results);
    } catch (err) {
      console.error('Error applying filters:', err);
      setError('Failed to apply filters');
    } finally {
      setLoading(false);
    }
  }, [vehicles]);

  // Get a single vehicle by ID using the API
  const getVehicleById = useCallback(async (id: string): Promise<Vehicle | null> => {
    try {
      return await vehicleApi.fetchVehicleById(id);
    } catch (err) {
      console.error('Error fetching vehicle by ID:', err);
      return null;
    }
  }, []);

  return {
    vehicles,
    filteredVehicles,
    loading,
    error,
    filters,
    applyFilters,
    getVehicleById
  };
};

export default useVehicles;
