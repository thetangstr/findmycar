import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { Vehicle } from '@/types';
import { getFallbackImage } from '@/utils/vehicleImageUtils';
import vehicleImageService from '@/services/vehicleImageService';

interface VehicleImageProps {
  vehicle: Vehicle;
  index?: number;
  className?: string;
  width?: number;
  height?: number;
  priority?: boolean;
  objectFit?: 'contain' | 'cover' | 'fill' | 'none' | 'scale-down';
  layout?: 'fill' | 'fixed' | 'intrinsic' | 'responsive';
  onLoad?: () => void;
}

const MAX_RETRIES = 2;

export const VehicleImage: React.FC<VehicleImageProps> = ({
  vehicle,
  index = 0,
  className = '',
  width = 400,
  height = 300,
  priority = false,
  objectFit = 'cover',
  layout,
  onLoad
}) => {
  const [imgSrc, setImgSrc] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [retryCount, setRetryCount] = useState<number>(vehicle._retryCount || 0);
  const [hasError, setHasError] = useState<boolean>(vehicle.hasErrorLoadingImage || false);

  // Make sure we have a valid index
  const safeIndex = index < 0 || index >= vehicle.images.length ? 0 : index;
  
  // Effect to set the image source
  useEffect(() => {
    const setupImage = async () => {
      setIsLoading(true);
      
      // Check if the vehicle has images
      if (!vehicle.images || vehicle.images.length === 0) {
        // Try to get images using the image service
        try {
          const updatedVehicle = await vehicleImageService.enrichVehicleWithImages(vehicle);
          if (updatedVehicle.images && updatedVehicle.images.length > 0) {
            const newImg = updatedVehicle.images[safeIndex];
            setImgSrc(newImg);
            setIsLoading(false);
            return;
          }
        } catch (error) {
          console.error('Error enriching vehicle with images:', error);
        }
        
        // If image service fails, use fallback
        const fallback = getFallbackImage(vehicle);
        setImgSrc(fallback);
        setIsLoading(false);
        return;
      }
      
      // Use the vehicle's existing images
      setImgSrc(vehicle.images[safeIndex]);
      setIsLoading(false);
    };
    
    setupImage();
  }, [vehicle, safeIndex]);

  // Handle image loading error
  const handleError = async () => {
    // Increment retry count
    const newRetryCount = retryCount + 1;
    setRetryCount(newRetryCount);
    
    if (newRetryCount <= MAX_RETRIES) {
      console.log(`Retrying image load (attempt ${newRetryCount}/${MAX_RETRIES}) for vehicle ${vehicle.id}`);
      
      // Try to get a different image for this vehicle
      try {
        const updatedVehicle = await vehicleImageService.enrichVehicleWithImages(vehicle);
        if (updatedVehicle.images && updatedVehicle.images.length > safeIndex) {
          // Use a different image than the one that failed
          const differentIndex = (safeIndex + 1) % updatedVehicle.images.length;
          setImgSrc(updatedVehicle.images[differentIndex]);
          return;
        }
      } catch (error) {
        console.error('Error getting replacement image:', error);
      }
      
      // If all else fails, use the fallback image
      setImgSrc(getFallbackImage(vehicle));
    } else {
      console.log(`Max retries reached for vehicle ${vehicle.id}, using fallback image`);
      setHasError(true);
      setImgSrc(getFallbackImage(vehicle));
    }
  };

  // Loading placeholder
  if (isLoading) {
    return (
      <div 
        className={`animate-pulse bg-gray-300 ${className}`}
        style={{ width: width || '100%', height: height || '100%' }}
      />
    );
  }

  // Common props for the Image component
  const imageProps = {
    src: imgSrc,
    alt: `${vehicle.year} ${vehicle.make} ${vehicle.model}`,
    width: layout ? undefined : width,
    height: layout ? undefined : height,
    layout: layout,
    className: `transition-opacity duration-300 ${className}`,
    objectFit: objectFit,
    priority: priority,
    onLoad: () => {
      // Mark this vehicle as having no error
      vehicle.hasErrorLoadingImage = false;
      onLoad && onLoad();
    },
    onError: () => handleError(),
  };

  return <Image {...imageProps} />;
};

export default VehicleImage;
