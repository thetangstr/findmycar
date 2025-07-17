import React from 'react';
import Skeleton from './Skeleton';

interface VehicleCardSkeletonProps {
  className?: string;
}

const VehicleCardSkeleton: React.FC<VehicleCardSkeletonProps> = ({ className = '' }) => {
  return (
    <div className={`ios-card slide-in flex flex-col h-full ${className}`}>
      {/* Image skeleton */}
      <div className="relative w-full">
        <div className="relative w-full h-40 overflow-hidden rounded-t-xl bg-gray-100">
          <Skeleton height="100%" />
        </div>
        
        {/* Button skeletons in top right */}
        <div className="absolute top-3 right-3 flex space-x-2">
          <Skeleton variant="circular" width="32px" height="32px" />
          <Skeleton variant="circular" width="32px" height="32px" />
        </div>
        
        {/* Source badge skeleton */}
        <div className="absolute bottom-2 left-2">
          <Skeleton width="60px" height="20px" className="rounded-full" />
        </div>
      </div>
      
      <div className="p-4 flex-grow flex flex-col">
        {/* Title skeleton */}
        <Skeleton variant="text" width="80%" className="mb-3" />
        
        {/* Price and mileage skeleton */}
        <div className="mt-3 flex justify-between items-center">
          <Skeleton width="100px" height="24px" />
          <Skeleton width="80px" height="20px" className="rounded-full" />
        </div>
        
        {/* Feature badges skeleton */}
        <div className="mt-4 flex flex-wrap gap-2">
          <Skeleton width="60px" height="24px" className="rounded-full" />
          <Skeleton width="70px" height="24px" className="rounded-full" />
          <Skeleton width="55px" height="24px" className="rounded-full" />
        </div>
        
        {/* Description skeleton */}
        <div className="mt-4">
          <Skeleton variant="text" lines={2} />
        </div>
        
        {/* Buttons skeleton */}
        <div className="mt-6 space-y-3 mt-auto">
          <Skeleton height="40px" className="rounded-full" />
          <Skeleton height="40px" className="rounded-full" />
        </div>
      </div>
    </div>
  );
};

export default VehicleCardSkeleton;