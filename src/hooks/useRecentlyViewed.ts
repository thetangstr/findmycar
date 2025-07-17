import { useState, useEffect, useCallback } from 'react';
import { RecentlyViewedItem, Vehicle } from '@/types';

export const useRecentlyViewed = (getVehicleById: (id: string) => Promise<Vehicle | null>) => {
  const [recentlyViewed, setRecentlyViewed] = useState<RecentlyViewedItem[]>([]);
  const MAX_RECENTLY_VIEWED = 10;
  
  // Load recently viewed items from localStorage on initial render
  useEffect(() => {
    const storedItems = localStorage.getItem('recentlyViewed');
    if (storedItems) {
      try {
        setRecentlyViewed(JSON.parse(storedItems));
      } catch (error) {
        console.error('Failed to parse recently viewed items', error);
        localStorage.removeItem('recentlyViewed');
      }
    }
  }, []);
  
  // Save recently viewed items to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('recentlyViewed', JSON.stringify(recentlyViewed));
  }, [recentlyViewed]);
  
  // Add a vehicle to recently viewed
  const addToRecentlyViewed = useCallback((vehicleId: string) => {
    setRecentlyViewed(prev => {
      // Remove if already exists
      const filtered = prev.filter(item => item.vehicleId !== vehicleId);
      
      // Add to the beginning of the array
      const newItem: RecentlyViewedItem = {
        vehicleId,
        viewedAt: new Date().toISOString()
      };
      
      // Limit to MAX_RECENTLY_VIEWED items
      return [newItem, ...filtered].slice(0, MAX_RECENTLY_VIEWED);
    });
  }, []);
  
  // Clear recently viewed items
  const clearRecentlyViewed = useCallback(() => {
    setRecentlyViewed([]);
  }, []);
  
  // Get full vehicle objects for recently viewed items
  const getRecentlyViewedVehicles = useCallback(async () => {
    const vehicles = await Promise.all(
      recentlyViewed.map(async (item) => {
        const vehicle = await getVehicleById(item.vehicleId);
        return vehicle ? { ...vehicle, viewedAt: item.viewedAt } : null;
      })
    );
    return vehicles.filter(Boolean) as (Vehicle & { viewedAt: string })[];
  }, [recentlyViewed, getVehicleById]);
  
  return {
    recentlyViewed,
    addToRecentlyViewed,
    clearRecentlyViewed,
    getRecentlyViewedVehicles
  };
};

export default useRecentlyViewed;
