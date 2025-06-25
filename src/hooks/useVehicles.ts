import { useState, useEffect, useCallback } from 'react';
import { Vehicle, SearchFilters } from '@/types';
import vehicleApi from '@/services/vehicleApi';
import { getHemmingsListings } from '@/services/scraperService';
import { filterVehiclesByQuery } from '@/utils/vehicleFiltering';
import vehicleImageService from '@/services/vehicleImageService'; // Import the new image service
import { mockVehicles } from '@/data/mockVehicles'; // Import mock data for demo

export const useVehicles = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [filteredVehicles, setFilteredVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<SearchFilters>({});

  // Load vehicles from our new aggregated search service
  useEffect(() => {
    const loadVehicles = async () => {
      setLoading(true);
      setError(null);
      try {
        console.log('🚗 Loading vehicles from aggregated sources...');
        const allVehicles = await vehicleApi.fetchVehicles();
        console.log(`✅ Loaded ${allVehicles.length} vehicles from aggregated sources`);
        
        setVehicles(allVehicles);
        setFilteredVehicles(allVehicles);
      } catch (err: any) {
        setError(err.message || 'Failed to load vehicles');
        console.error('❌ Error loading vehicles:', err);
        
        // Fallback to mock data if all else fails
        console.log('🔄 Falling back to mock vehicles');
        setVehicles(mockVehicles);
        setFilteredVehicles(mockVehicles);
      } finally {
        setLoading(false);
      }
    };
    loadVehicles();
  }, []);

  // Apply search filters using our aggregated search
  const applyFilters = useCallback(async (newFilters: SearchFilters) => {
    setFilters(newFilters);
    setLoading(true);
    setError(null);

    try {
      console.log('🔍 Applying filters with aggregated search:', newFilters);
      const searchResults = await vehicleApi.searchVehicles(newFilters);
      console.log(`✅ Search complete: ${searchResults.length} vehicles found`);
      
      setFilteredVehicles(searchResults);
    } catch (err: any) {
      console.error('❌ Error applying filters:', err);
      setError(err.message || 'Failed to apply filters');
      
      // Fallback: filter existing vehicles client-side
      if (vehicles.length > 0) {
        const filtered = filterVehiclesByQuery(vehicles, newFilters.query || '');
        setFilteredVehicles(filtered);
      } else {
        setFilteredVehicles([]);
      }
    } finally {
      setLoading(false);
    }
  }, [vehicles]);

  // Get a single vehicle by ID, checking local state first, then API
  const getVehicleById = useCallback(async (id: string): Promise<Vehicle | null> => {
    setLoading(true);
    setError(null);
    try {
      const vehicleFromState = vehicles.find(v => v.id === id);
      if (vehicleFromState) {
        setLoading(false);
        return vehicleFromState;
      }

      const vehicleFromApi = await vehicleApi.fetchVehicleById(id);
      if (vehicleFromApi) {
        setLoading(false);
        return vehicleFromApi;
      }
      
      setError(`Vehicle with ID ${id} not found.`);
      setLoading(false);
      return null;
    } catch (err: any) {
      console.error('Error fetching vehicle by ID:', err);
      setError(err.message || 'Failed to fetch vehicle details.');
      setLoading(false);
      return null;
    }
  }, [vehicles]);

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
