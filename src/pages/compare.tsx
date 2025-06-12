import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useVehicles } from '@/hooks/useVehicles';
import { useComparison } from '@/hooks/useComparison';
import { Vehicle } from '@/types';

export default function Compare() {
  const { getVehicleById } = useVehicles();
  const { getComparisonVehicles, removeFromComparison, clearComparison, comparisonCount } = useComparison(getVehicleById);
  
  const [comparisonVehicles, setComparisonVehicles] = useState<(Vehicle & { addedAt: string })[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const loadVehicles = async () => {
      setLoading(true);
      try {
        const vehicles = await getComparisonVehicles();
        setComparisonVehicles(vehicles);
      } catch (error) {
        console.error('Error loading comparison vehicles:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadVehicles();
  }, [getComparisonVehicles, comparisonCount]);
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700">Loading comparison...</h2>
        </div>
      </div>
    );
  }
  
  if (comparisonVehicles.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">No Vehicles to Compare</h1>
          <p className="text-gray-600 mb-6">
            You haven't added any vehicles to your comparison list yet. Browse our inventory and add vehicles to compare them side by side.
          </p>
          <Link href="/search" className="btn btn-primary">
            Browse Vehicles
          </Link>
        </div>
      </div>
    );
  }
  
  // Define the properties to compare
  const comparisonProperties = [
    { label: 'Price', key: 'price', format: (value: number) => `$${value.toLocaleString()}` },
    { label: 'Year', key: 'year' },
    { label: 'Mileage', key: 'mileage', format: (value: number) => `${value.toLocaleString()} mi` },
    { label: 'Exterior Color', key: 'exteriorColor' },
    { label: 'Interior Color', key: 'interiorColor' },
    { label: 'Fuel Type', key: 'fuelType' },
    { label: 'Transmission', key: 'transmission' },
    { label: 'Engine', key: 'engine' },
    { label: 'Location', key: 'location' },
    { label: 'Dealer', key: 'dealer' }
  ];
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Compare Vehicles</h1>
        <p className="text-gray-600">
          Compare the specifications of your selected vehicles side by side.
        </p>
      </div>
      
      <div className="bg-white rounded-lg shadow-md overflow-hidden mb-8">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">
              Comparing {comparisonVehicles.length} {comparisonVehicles.length === 1 ? 'Vehicle' : 'Vehicles'}
            </h2>
            <button
              onClick={clearComparison}
              className="text-red-600 hover:text-red-800 font-medium text-sm flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              Clear All
            </button>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50">
                <th className="py-4 px-6 text-left text-sm font-medium text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50 z-10 min-w-[200px]">
                  Vehicle
                </th>
                {comparisonVehicles.map(vehicle => (
                  <th key={vehicle.id} className="py-4 px-6 text-center min-w-[250px]">
                    <div className="relative">
                      <button
                        onClick={() => removeFromComparison(vehicle.id)}
                        className="absolute -top-2 -right-2 bg-white rounded-full p-1 shadow-md text-gray-500 hover:text-red-600"
                        title="Remove from comparison"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            
            <tbody>
              {/* Vehicle Image and Name */}
              <tr>
                <td className="py-4 px-6 text-sm font-medium text-gray-900 sticky left-0 bg-white z-10">
                  Image
                </td>
                {comparisonVehicles.map(vehicle => (
                  <td key={vehicle.id} className="py-4 px-6 text-center">
                    <div className="relative h-40 w-full mb-2">
                      {vehicle.images && vehicle.images.length > 0 ? (
                        <Image
                          src={vehicle.images[0]}
                          alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
                          fill
                          className="object-cover rounded-md"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-gray-100 text-gray-800 rounded-md">
                          <div className="text-center p-4">
                            <p className="font-bold">{vehicle.year} {vehicle.make}</p>
                            <p>{vehicle.model}</p>
                          </div>
                        </div>
                      )}
                    </div>
                    <Link 
                      href={`/vehicles/${vehicle.id}`} 
                      className="text-lg font-semibold text-primary-600 hover:text-primary-800"
                    >
                      {vehicle.year} {vehicle.make} {vehicle.model}
                    </Link>
                  </td>
                ))}
              </tr>
              
              {/* Comparison Properties */}
              {comparisonProperties.map(property => (
                <tr key={property.key} className="border-t border-gray-200">
                  <td className="py-4 px-6 text-sm font-medium text-gray-900 sticky left-0 bg-white z-10">
                    {property.label}
                  </td>
                  {comparisonVehicles.map(vehicle => {
                    // @ts-ignore - Dynamic property access
                    const value = vehicle[property.key];
                    const formattedValue = property.format ? property.format(value) : value;
                    
                    return (
                      <td key={vehicle.id} className="py-4 px-6 text-sm text-gray-700 text-center">
                        {formattedValue}
                      </td>
                    );
                  })}
                </tr>
              ))}
              
              {/* Features */}
              <tr className="border-t border-gray-200">
                <td className="py-4 px-6 text-sm font-medium text-gray-900 sticky left-0 bg-white z-10">
                  Features
                </td>
                {comparisonVehicles.map(vehicle => (
                  <td key={vehicle.id} className="py-4 px-6 text-sm text-gray-700">
                    <ul className="list-disc pl-5 space-y-1">
                      {vehicle.features.map((feature, index) => (
                        <li key={index}>{feature}</li>
                      ))}
                    </ul>
                  </td>
                ))}
              </tr>
              
              {/* Actions */}
              <tr className="border-t border-gray-200">
                <td className="py-4 px-6 text-sm font-medium text-gray-900 sticky left-0 bg-white z-10">
                  Actions
                </td>
                {comparisonVehicles.map(vehicle => (
                  <td key={vehicle.id} className="py-4 px-6 text-center">
                    <Link 
                      href={`/vehicles/${vehicle.id}`} 
                      className="btn btn-primary block mb-2"
                    >
                      View Details
                    </Link>
                    <a 
                      href={vehicle.url} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="btn btn-secondary block mb-2"
                    >
                      View Original Listing
                    </a>
                    <a
                      href={`https://www.progressive.com/auto/car-insurance-quote/?vehicle=${encodeURIComponent(`${vehicle.year} ${vehicle.make} ${vehicle.model}`)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn bg-gradient-to-r from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800 text-white block flex items-center justify-center gap-2"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
                      </svg>
                      Need Insurance?
                    </a>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
