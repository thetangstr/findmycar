import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Vehicle } from '@/types';
import CompareButton from './CompareButton';
import FavoriteButton from './FavoriteButton';
import AIInsightButton from './AIInsightButton';
import PriceAnalysisIndicator from './PriceAnalysisIndicator';

interface VehicleCardProps {
  vehicle: Vehicle;
  onView?: () => void;
  className?: string;
  showRatingButtons?: boolean;
}

const VehicleCard: React.FC<VehicleCardProps> = ({ vehicle, onView, className = '', showRatingButtons = false }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [displayFallback, setDisplayFallback] = useState(false);
  const [userRating, setUserRating] = useState<'up' | 'down' | null>(null);
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

  const handleRating = (rating: 'up' | 'down') => {
    // Toggle rating if the same button is clicked, otherwise set new rating
    setUserRating(userRating === rating ? null : rating);
    
    // Here you could also send the rating to a backend service
    console.log(`User rated vehicle ${vehicle.id} as ${rating}`);
  };

  return (
    <article 
      className={`ios-card slide-in flex flex-col h-full ${className}`}
      role="article"
      aria-labelledby={`vehicle-title-${vehicle.id}`}
      aria-describedby={`vehicle-description-${vehicle.id}`}
    >
      <div className="relative w-full">
        <div className="relative w-full h-40 overflow-hidden rounded-t-xl bg-gray-100">
          <Link 
            href={`/vehicles/${vehicle.id}`} 
            onClick={handleClick}
            aria-label={`View details for ${vehicle.year} ${vehicle.make} ${vehicle.model}`}
            className="block w-full h-full focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-inset rounded-t-xl"
          >
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
                alt={`${vehicle.year} ${vehicle.make} ${vehicle.model} - $${vehicle.price.toLocaleString()}`}
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
        <div className="absolute bottom-2 left-2 bg-black bg-opacity-60 backdrop-blur-sm text-white text-xs font-mono px-2 py-1 rounded-full" aria-label={`Source: ${vehicle.source}`}>
          {vehicle.source}
        </div>
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent h-16" aria-hidden="true"></div>
      </div>
      
      <div className="p-4 flex-grow flex flex-col">
        <Link 
          href={`/vehicles/${vehicle.id}`} 
          onClick={handleClick}
          className="focus:outline-none focus:ring-2 focus:ring-teal-500 rounded-md"
        >
          <h3 
            id={`vehicle-title-${vehicle.id}`}
            className="text-xl font-semibold font-mono tracking-tight text-gray-900 hover:text-teal-600 transition-colors duration-300"
          >
            {vehicle.year} {vehicle.make} {vehicle.model}
          </h3>
        </Link>
        
        <div className="mt-3 flex justify-between items-center">
          <span className="text-2xl font-bold text-teal-500" aria-label={`Price: $${vehicle.price.toLocaleString()}`}>
            ${vehicle.price.toLocaleString()}
          </span>
          <span 
            className="px-3 py-1 bg-teal-50 rounded-full text-xs font-medium text-teal-700 font-inter"
            aria-label={`Mileage: ${vehicle.mileage.toLocaleString()} miles`}
          >
            {vehicle.mileage.toLocaleString()} miles
          </span>
        </div>
        
        {/* Price Analysis Indicator */}
        <div className="mt-3">
          <PriceAnalysisIndicator vehicle={vehicle} compact={true} />
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
        
        <div 
          id={`vehicle-description-${vehicle.id}`}
          className="mt-4 truncate text-sm text-gray-500 font-inter"
        >
          {vehicle.description.substring(0, 80)}...
        </div>
        
        {/* Rating buttons for search results */}
        {showRatingButtons && (
          <div className="mt-4 flex justify-end space-x-2">
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                handleRating('up');
              }}
              className={`flex items-center justify-center w-6 h-6 rounded-full border transition-all duration-200 ${
                userRating === 'up' 
                  ? 'bg-green-500 border-green-500 text-white' 
                  : 'border-gray-300 text-gray-400 hover:border-green-400 hover:text-green-500'
              }`}
              aria-label="Rate positive"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
              </svg>
            </button>
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                handleRating('down');
              }}
              className={`flex items-center justify-center w-6 h-6 rounded-full border transition-all duration-200 ${
                userRating === 'down' 
                  ? 'bg-red-500 border-red-500 text-white' 
                  : 'border-gray-300 text-gray-400 hover:border-red-400 hover:text-red-500'
              }`}
              aria-label="Rate negative"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                <path d="M18 9.5a1.5 1.5 0 11-3 0v-6a1.5 1.5 0 013 0v6zM14 9.667v-5.43a2 2 0 00-1.106-1.79l-.05-.025A4 4 0 0011.057 2H5.64a2 2 0 00-1.962 1.608l-1.2 6A2 2 0 004.44 12H8v4a2 2 0 002 2 1 1 0 001-1v-.667a4 4 0 01.8-2.4l1.4-1.866a4 4 0 00.8-2.4z" />
              </svg>
            </button>
          </div>
        )}
        
        <div className="mt-6 space-y-3 mt-auto">
          {/* AI Insight Button */}
          <AIInsightButton vehicle={vehicle} className="w-full" />
          
          {/* View Details Button */}
          <Link 
            href={`/vehicles/${vehicle.id}`} 
            className="block w-full py-2.5 px-4 bg-teal-500 hover:bg-teal-600 text-white font-medium rounded-full text-center transition-colors duration-300 shadow-sm hover:shadow font-inter focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2"
            onClick={handleClick}
            aria-label={`View full details for ${vehicle.year} ${vehicle.make} ${vehicle.model}`}
          >
            View Details
          </Link>
        </div>
      </div>
    </article>
  );
};

export default VehicleCard;
