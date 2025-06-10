import { useState, useEffect, useCallback } from 'react';
import { FavoriteItem, Vehicle } from '@/types';

export const useFavorites = (getVehicleById: (id: string) => Promise<Vehicle | null>) => {
  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  
  // Load favorites from localStorage on initial render
  useEffect(() => {
    const storedItems = localStorage.getItem('favorites');
    if (storedItems) {
      try {
        setFavorites(JSON.parse(storedItems));
      } catch (error) {
        console.error('Failed to parse favorites', error);
        localStorage.removeItem('favorites');
      }
    }
  }, []);
  
  // Save favorites to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('favorites', JSON.stringify(favorites));
  }, [favorites]);
  
  // Add a vehicle to favorites
  const addToFavorites = useCallback((vehicleId: string) => {
    // Check if already in favorites
    if (favorites.some(item => item.vehicleId === vehicleId)) {
      return false;
    }
    
    const newItem: FavoriteItem = {
      vehicleId,
      addedAt: new Date().toISOString()
    };
    
    setFavorites(prev => [...prev, newItem]);
    return true;
  }, [favorites]);
  
  // Remove a vehicle from favorites
  const removeFromFavorites = useCallback((vehicleId: string) => {
    setFavorites(prev => 
      prev.filter(item => item.vehicleId !== vehicleId)
    );
  }, []);
  
  // Check if a vehicle is in favorites
  const isInFavorites = useCallback((vehicleId: string) => {
    return favorites.some(item => item.vehicleId === vehicleId);
  }, [favorites]);
  
  // Get full vehicle objects for favorites
  const getFavoriteVehicles = useCallback(async () => {
    const vehiclePromises = favorites.map(async (item) => {
      const vehicle = await getVehicleById(item.vehicleId);
      return vehicle ? { ...vehicle, addedAt: item.addedAt } : null;
    });
    
    const vehicles = await Promise.all(vehiclePromises);
    return vehicles.filter(Boolean) as (Vehicle & { addedAt: string })[];
  }, [favorites, getVehicleById]);
  
  return {
    favorites,
    favoritesCount: favorites.length,
    addToFavorites,
    removeFromFavorites,
    isInFavorites,
    getFavoriteVehicles
  };
};

export default useFavorites;
