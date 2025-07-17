import React, { useState, useEffect } from 'react';
import { useVehicles } from '@/hooks/useVehicles';
import { useRecentlyViewed } from '@/hooks/useRecentlyViewed';
import VehicleCard from '@/components/VehicleCard';
import Link from 'next/link';
import { Vehicle } from '@/types';

export default function RecentlyViewed() {
  const { getVehicleById } = useVehicles();
  const { getRecentlyViewedVehicles, clearRecentlyViewed } = useRecentlyViewed(getVehicleById);
  const [recentlyViewedVehicles, setRecentlyViewedVehicles] = useState<(Vehicle & { viewedAt: string })[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const loadRecentlyViewed = async () => {
      try {
        const vehicles = await getRecentlyViewedVehicles();
        setRecentlyViewedVehicles(vehicles);
      } catch (error) {
        console.error('Error loading recently viewed vehicles:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadRecentlyViewed();
  }, [getRecentlyViewedVehicles]);
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Recently Viewed Vehicles</h1>
        <p className="text-gray-600">
          View your browsing history of vehicles you&apos;ve recently viewed.
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
      ) : recentlyViewedVehicles.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Recently Viewed Vehicles</h2>
          <p className="text-gray-600 mb-6">
            You haven&apos;t viewed any vehicles yet. Browse our inventory to see vehicles here.
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
                {recentlyViewedVehicles.length} {recentlyViewedVehicles.length === 1 ? 'Vehicle' : 'Vehicles'}
              </h2>
              <button
                onClick={clearRecentlyViewed}
                className="text-red-600 hover:text-red-800 font-medium text-sm flex items-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Clear History
              </button>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recentlyViewedVehicles.map(vehicle => (
              <div key={vehicle.id} className="relative">
                <div className="absolute top-2 left-2 z-10 bg-gray-800 bg-opacity-75 text-white text-xs px-2 py-1 rounded-md">
                  Viewed: {new Date(vehicle.viewedAt).toLocaleDateString()}
                </div>
                <VehicleCard vehicle={vehicle} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
