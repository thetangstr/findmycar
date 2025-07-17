import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useComparison } from '@/hooks/useComparison';
import { useVehicles } from '@/hooks/useVehicles';
import { Vehicle } from '@/types';

const ComparisonIndicator: React.FC = () => {
  const { getVehicleById } = useVehicles();
  const { comparisonCount, getComparisonVehicles } = useComparison(getVehicleById);
  const [comparisonVehicles, setComparisonVehicles] = useState<(Vehicle & { addedAt: string })[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const loadVehicles = async () => {
      if (comparisonCount > 0) {
        setIsLoading(true);
        try {
          const vehicles = await getComparisonVehicles();
          setComparisonVehicles(vehicles);
        } catch (error) {
          console.error('Error loading comparison vehicles:', error);
        } finally {
          setIsLoading(false);
        }
      }
    };
    
    loadVehicles();
  }, [comparisonCount, getComparisonVehicles]);
  
  if (comparisonCount === 0) {
    return null;
  }
  
  if (isLoading) {
    return (
      <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-3 z-50">
        <div className="flex items-center">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600 mr-2"></div>
          <span className="text-sm font-medium">Loading comparison...</span>
        </div>
      </div>
    );
  }
  
  return (
    <div className="relative">
      <Link href="/compare" className="flex items-center p-2 rounded-md bg-primary-100 text-primary-800 hover:bg-primary-200">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M5 4a1 1 0 00-2 0v7.268a2 2 0 000 3.464V16a1 1 0 102 0v-1.268a2 2 0 000-3.464V4zM11 4a1 1 0 10-2 0v1.268a2 2 0 000 3.464V16a1 1 0 102 0V8.732a2 2 0 000-3.464V4zM16 3a1 1 0 011 1v7.268a2 2 0 010 3.464V16a1 1 0 11-2 0v-1.268a2 2 0 010-3.464V4a1 1 0 011-1z" clipRule="evenodd" />
        </svg>
        <span className="text-sm font-medium">Compare ({comparisonCount})</span>
      </Link>
      
      {/* Tooltip showing vehicles in comparison */}
      <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg overflow-hidden z-20 hidden group-hover:block">
        <div className="p-3">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Vehicles in comparison</h3>
          <ul className="space-y-2">
            {comparisonVehicles.map(vehicle => (
              <li key={vehicle.id} className="text-sm text-gray-700 flex items-center">
                <span className="w-2 h-2 bg-primary-500 rounded-full mr-2"></span>
                {vehicle.year} {vehicle.make} {vehicle.model}
              </li>
            ))}
          </ul>
          <div className="mt-3 pt-3 border-t border-gray-200">
            <Link href="/compare" className="text-sm text-primary-600 hover:text-primary-800 font-medium">
              View comparison
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonIndicator;
