import React, { useState, useEffect } from 'react';
import { useVehicles } from '@/hooks/useVehicles';
import { useFavorites } from '@/hooks/useFavorites';
import { useRecentlyViewed } from '@/hooks/useRecentlyViewed';
import VehicleCard from '@/components/VehicleCard';
import Link from 'next/link';
import { Vehicle } from '@/types';

export default function Favorites() {
  const { getVehicleById } = useVehicles();
  const { getFavoriteVehicles, removeFromFavorites } = useFavorites(getVehicleById);
  const { addToRecentlyViewed } = useRecentlyViewed(getVehicleById);
  const [favoriteVehicles, setFavoriteVehicles] = useState<(Vehicle & { addedAt: string })[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const loadFavorites = async () => {
      try {
        const vehicles = await getFavoriteVehicles();
        setFavoriteVehicles(vehicles);
      } catch (error) {
        console.error('Error loading favorites:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadFavorites();
  }, [getFavoriteVehicles]);
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Favorite Vehicles</h1>
        <p className="text-gray-600">
          View and manage your saved favorite vehicles.
        </p>
      </div>
      
      {loading ? (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <div className="animate-pulse flex flex-col items-center">
            <div className="rounded-full bg-gray-200 h-16 w-16 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2 mb-6"></div>
            <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          </div>
        </div>
      ) : favoriteVehicles.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Favorites Yet</h2>
          <p className="text-gray-600 mb-6">
            You haven&apos;t added any vehicles to your favorites yet. Browse our inventory and add vehicles you like to your favorites.
          </p>
          <Link href="/search" className="btn btn-primary">
            Browse Vehicles
          </Link>
        </div>
      ) : (
        <div>
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">
                {favoriteVehicles.length} {favoriteVehicles.length === 1 ? 'Vehicle' : 'Vehicles'}
              </h2>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Sort by:</span>
                <select className="border border-gray-300 rounded-md text-sm p-1">
                  <option>Date Added: Newest</option>
                  <option>Date Added: Oldest</option>
                  <option>Price: Low to High</option>
                  <option>Price: High to Low</option>
                </select>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {favoriteVehicles.map(vehicle => (
              <div key={vehicle.id} className="relative">
                <button
                  onClick={() => removeFromFavorites(vehicle.id)}
                  className="absolute top-2 right-2 z-10 bg-white rounded-full p-2 shadow-md text-red-500 hover:text-red-700"
                  title="Remove from favorites"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
                <VehicleCard 
                  vehicle={vehicle} 
                  onView={() => addToRecentlyViewed(vehicle.id)}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
