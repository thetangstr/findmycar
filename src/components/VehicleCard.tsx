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
  className?: string;
}

const VehicleCard: React.FC<VehicleCardProps> = ({ vehicle, onView, className = '' }) => {
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
    <div className={`ios-card slide-in flex flex-col h-full ${className}`}>
      <div className="relative w-full">
        <div className="relative w-full h-40 overflow-hidden rounded-t-xl bg-gray-100">
          <Link href={`/vehicles/${vehicle.id}`} onClick={handleClick}>
            {displayFallback || !imageUrl ? (
              // Render a built-in fallback div with vehicle info
              <div className="w-full h-full flex items-center justify-center bg-gray-50 text-gray-800 cursor-pointer hover:bg-gray-100 transition-colors">
                <div className="text-center p-4">
                  <p className="font-mono font-semibold">{vehicle.year} {vehicle.make}</p>
                  <p className="font-inter">{vehicle.model}</p>
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
        <div className="absolute bottom-2 left-2 bg-black bg-opacity-60 backdrop-blur-sm text-white text-xs font-mono px-2 py-1 rounded-full">
          {vehicle.source}
        </div>
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent h-16"></div>
      </div>
      
      <div className="p-4 flex-grow flex flex-col">
        <Link href={`/vehicles/${vehicle.id}`} onClick={handleClick}>
          <h3 className="text-xl font-semibold font-mono tracking-tight text-gray-900 hover:text-teal-600 transition-colors duration-300">
            {vehicle.year} {vehicle.make} {vehicle.model}
          </h3>
        </Link>
        
        <div className="mt-3 flex justify-between items-center">
          <span className="text-2xl font-bold text-teal-500">${vehicle.price.toLocaleString()}</span>
          <span className="px-3 py-1 bg-teal-50 rounded-full text-xs font-medium text-teal-700 font-inter">{vehicle.mileage.toLocaleString()} miles</span>
        </div>
        
        <div className="mt-4 flex flex-wrap gap-2">
          {vehicle.exteriorColor && (
            <div className="px-3 py-1 bg-gray-50 rounded-full text-xs font-medium text-gray-700 flex items-center">
              {vehicle.exteriorColor}
            </div>
          )}
          {vehicle.fuelType && (
            <div className="px-3 py-1 bg-gray-50 rounded-full text-xs font-medium text-gray-700 flex items-center">
              {vehicle.fuelType}
            </div>
          )}
          {vehicle.transmission && (
            <div className="px-3 py-1 bg-gray-50 rounded-full text-xs font-medium text-gray-700 flex items-center">
              {vehicle.transmission}
            </div>
          )}
        </div>
        
        <div className="mt-4 truncate text-sm text-gray-500 font-inter">
          {vehicle.description.substring(0, 80)}...
        </div>
        
        <div className="mt-6 space-y-3 mt-auto">
          {/* AI Insight Button */}
          <AIInsightButton vehicle={vehicle} className="w-full" />
          
          {/* View Details Button */}
          <Link 
            href={`/vehicles/${vehicle.id}`} 
            className="block w-full py-2.5 px-4 bg-teal-500 hover:bg-teal-600 text-white font-medium rounded-full text-center transition-colors duration-300 shadow-sm hover:shadow font-inter"
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
