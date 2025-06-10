import { useState, useEffect, useCallback } from 'react';
import { ComparisonItem, Vehicle } from '@/types';

export const useComparison = (getVehicleById: (id: string) => Promise<Vehicle | null>) => {
  const [comparisonItems, setComparisonItems] = useState<ComparisonItem[]>([]);
  
  // Load comparison items from localStorage on initial render
  useEffect(() => {
    const storedItems = localStorage.getItem('comparisonItems');
    if (storedItems) {
      try {
        setComparisonItems(JSON.parse(storedItems));
      } catch (error) {
        console.error('Failed to parse comparison items', error);
        localStorage.removeItem('comparisonItems');
      }
    }
  }, []);
  
  // Save comparison items to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('comparisonItems', JSON.stringify(comparisonItems));
  }, [comparisonItems]);
  
  // Add a vehicle to comparison
  const addToComparison = useCallback((vehicleId: string) => {
    // Check if already in comparison
    if (comparisonItems.some(item => item.vehicleId === vehicleId)) {
      return false;
    }
    
    // Limit to 4 vehicles for comparison
    if (comparisonItems.length >= 4) {
      return false;
    }
    
    const newItem: ComparisonItem = {
      vehicleId,
      addedAt: new Date().toISOString()
    };
    
    setComparisonItems(prev => [...prev, newItem]);
    return true;
  }, [comparisonItems]);
  
  // Remove a vehicle from comparison
  const removeFromComparison = useCallback((vehicleId: string) => {
    setComparisonItems(prev => 
      prev.filter(item => item.vehicleId !== vehicleId)
    );
  }, []);
  
  // Clear all vehicles from comparison
  const clearComparison = useCallback(() => {
    setComparisonItems([]);
  }, []);
  
  // Check if a vehicle is in comparison
  const isInComparison = useCallback((vehicleId: string) => {
    return comparisonItems.some(item => item.vehicleId === vehicleId);
  }, [comparisonItems]);
  
  // Get full vehicle objects for comparison
  const getComparisonVehicles = useCallback(async () => {
    const vehicles = await Promise.all(
      comparisonItems.map(async (item) => {
        const vehicle = await getVehicleById(item.vehicleId);
        return vehicle ? { ...vehicle, addedAt: item.addedAt } : null;
      })
    );
    return vehicles.filter(Boolean) as (Vehicle & { addedAt: string })[];
  }, [comparisonItems, getVehicleById]);
  
  return {
    comparisonItems,
    comparisonCount: comparisonItems.length,
    addToComparison,
    removeFromComparison,
    clearComparison,
    isInComparison,
    getComparisonVehicles
  };
};

export default useComparison;
