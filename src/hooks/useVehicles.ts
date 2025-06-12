import { useState, useEffect, useCallback } from 'react';
import { Vehicle, SearchFilters } from '@/types';
import vehicleApi from '@/services/vehicleApi';
import { getHemmingsListings } from '@/services/scraperService';
import { filterVehiclesByQuery } from '@/utils/vehicleFiltering';
import vehicleImageService from '@/services/vehicleImageService'; // Import the new image service

export const useVehicles = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [filteredVehicles, setFilteredVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<SearchFilters>({});

  // Fetch vehicles from API and Hemmings, then enrich with accurate images
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch vehicles from different sources
        const [apiVehicles, hemmingsVehicles] = await Promise.all([
          vehicleApi.fetchVehicles(),
          getHemmingsListings()
        ]);
        const combinedVehicles = [...apiVehicles, ...hemmingsVehicles];
        
        // Enrich vehicles with accurate images (preserves the 3 featured listings)
        console.log('Enriching vehicles with accurate images...');
        const enrichedVehicles = await vehicleImageService.enrichVehiclesWithImages(combinedVehicles);
        console.log(`Enriched ${enrichedVehicles.length} vehicles with images`);
        
        setVehicles(enrichedVehicles);
        setFilteredVehicles(enrichedVehicles);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch vehicles');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Apply filters locally to the combined list of vehicles
  const applyFilters = useCallback(async (newFilters: SearchFilters) => {
    setFilters(newFilters);
    setLoading(true);
    setError(null);

    try {
      let results = vehicles; // Start with all combined vehicles

      // Apply text query filter using the utility function
      if (newFilters.query && newFilters.query.trim() !== '') {
        results = filterVehiclesByQuery(results, newFilters.query);
      }

      // Apply structured filters
      results = results.filter(vehicle => {
        if (newFilters.make && vehicle.make?.toLowerCase() !== newFilters.make.toLowerCase()) return false;
        if (newFilters.model && !vehicle.model?.toLowerCase().includes(newFilters.model.toLowerCase())) return false;
        if (newFilters.yearMin && vehicle.year && vehicle.year < newFilters.yearMin) return false;
        if (newFilters.yearMax && vehicle.year && vehicle.year > newFilters.yearMax) return false;
        if (newFilters.priceMin && vehicle.price && vehicle.price < newFilters.priceMin) return false;
        if (newFilters.priceMax && vehicle.price && vehicle.price > newFilters.priceMax) return false;
        if (newFilters.mileageMin && typeof vehicle.mileage === 'number' && vehicle.mileage < newFilters.mileageMin) return false;
        if (newFilters.mileageMax && typeof vehicle.mileage === 'number' && vehicle.mileage > newFilters.mileageMax) return false;
        if (newFilters.fuelType && vehicle.fuelType?.toLowerCase() !== newFilters.fuelType.toLowerCase()) return false;
        if (newFilters.transmission && vehicle.transmission?.toLowerCase() !== newFilters.transmission.toLowerCase()) return false;
        if (newFilters.source && vehicle.source?.toLowerCase() !== newFilters.source.toLowerCase()) return false;
        return true;
      });

      setFilteredVehicles(results);
    } catch (err: any) {
      console.error('Error applying filters locally:', err);
      setError(err.message || 'Failed to apply filters');
      setFilteredVehicles(vehicles); // Fallback to all vehicles on error
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
