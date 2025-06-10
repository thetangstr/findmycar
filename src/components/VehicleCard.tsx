import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Vehicle } from '@/types';
import CompareButton from './CompareButton';
import FavoriteButton from './FavoriteButton';
import AIInsightButton from './AIInsightButton';

interface VehicleCardProps {
  vehicle: Vehicle;
  onView?: () => void;
}

const VehicleCard: React.FC<VehicleCardProps> = ({ vehicle, onView }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [displayFallback, setDisplayFallback] = useState(false);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    setCurrentImageIndex(0); // Reset index when vehicle prop changes
    if (!vehicle.images || vehicle.images.length === 0) {
      setDisplayFallback(true);
    } else {
      setDisplayFallback(false); // Has images, attempt to load
    }
  }, [vehicle.images]);

  const handleImageError = () => {
    // Check if vehicle.images is defined and not empty before accessing length
    if (vehicle.images && vehicle.images.length > 0 && currentImageIndex < vehicle.images.length - 1) {
      setCurrentImageIndex(prevIndex => prevIndex + 1);
    } else {
      setDisplayFallback(true);
    }
  };

  // Determine the imageUrl to attempt loading
  const imageUrl = hasError || !vehicle.images || vehicle.images.length === 0 
    ? '/placeholder-image.png' 
    : vehicle.images[currentImageIndex];

  const handleClick = () => {
    if (onView) {
      onView();
    }
  };

  return (
    <div className="bg-white rounded-xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
      <div className="relative h-56 w-full">
        <div className="relative w-full h-40 overflow-hidden rounded-t-lg bg-gray-200">
          <Link href={`/vehicles/${vehicle.id}`} onClick={handleClick}>
            {displayFallback || !imageUrl ? (
              // Render a built-in fallback div with vehicle info
              <div className="w-full h-full flex items-center justify-center bg-gray-100 text-gray-800 cursor-pointer hover:bg-gray-200 transition-colors">
                <div className="text-center p-4">
                  <p className="font-bold">{vehicle.year} {vehicle.make}</p>
                  <p>{vehicle.model}</p>
                </div>
              </div>
            ) : (
              <img
                src={imageUrl} // Use the state-derived imageUrl
                alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
                className="w-full h-full object-cover cursor-pointer hover:scale-105 transition-transform duration-300"
                loading="eager"
                onError={() => {
                  console.error(`[DEBUG VehicleCard] Image load error for: ${imageUrl}`);
                  handleImageError();
                }}
              />
            )}
          </Link>
        </div>
        <div className="absolute top-3 right-3 flex space-x-2">
          <FavoriteButton vehicleId={vehicle.id} />
          <CompareButton vehicleId={vehicle.id} />
        </div>
        <div className="absolute bottom-2 left-2 bg-black bg-opacity-60 text-white text-xs font-semibold px-2 py-1 rounded-md">
          Source: {vehicle.source}
        </div>
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent h-20"></div>
      </div>
      
      <div className="p-5">
        <Link href={`/vehicles/${vehicle.id}`} onClick={handleClick}>
          <h3 className="text-xl font-semibold text-gray-900 hover:text-primary-600 transition-colors duration-300">
            {vehicle.year} {vehicle.make} {vehicle.model}
          </h3>
        </Link>
        
        <div className="mt-3 flex justify-between items-center">
          <span className="text-2xl font-bold text-primary-600">${vehicle.price.toLocaleString()}</span>
          <span className="px-3 py-1 bg-gray-100 rounded-full text-sm font-medium text-gray-700">{vehicle.mileage.toLocaleString()} miles</span>
        </div>
        
        <div className="mt-4 flex flex-wrap gap-3">
          <div className="px-3 py-1.5 bg-gray-50 rounded-lg text-sm font-medium text-gray-700 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1.5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            {vehicle.exteriorColor}
          </div>
          <div className="px-3 py-1.5 bg-gray-50 rounded-lg text-sm font-medium text-gray-700 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1.5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            {vehicle.fuelType}
          </div>
          <div className="px-3 py-1.5 bg-gray-50 rounded-lg text-sm font-medium text-gray-700 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1.5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
            {vehicle.transmission}
          </div>
        </div>
        
        <div className="mt-5 truncate text-sm text-gray-500 italic">
          {vehicle.description.substring(0, 80)}...
        </div>
        
        <div className="mt-6 space-y-3">
          {/* AI Insight Button */}
          <AIInsightButton vehicle={vehicle} className="w-full" />
          
          {/* View Details Button */}
          <Link 
            href={`/vehicles/${vehicle.id}`} 
            className="block w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg text-center transition-colors duration-300 shadow-sm hover:shadow"
            onClick={handleClick}
          >
            View Details
          </Link>
        </div>
      </div>
    </div>
  );
};

export default VehicleCard;
