import React, { useState } from 'react';
import Image from 'next/image';
import { Vehicle } from '@/types';

interface ImageGalleryProps {
  images: string[];
  alt: string;
  vehicle?: Vehicle;
}

/**
 * Image Gallery component for displaying vehicle images with navigation
 * 
 * Features:
 * - Main image display with previous/next navigation
 * - Thumbnail navigation
 * - Fullscreen mode
 * - Image counter
 * - Fallback for missing images
 */
const ImageGallery: React.FC<ImageGalleryProps> = ({ images, alt, vehicle }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Use local text-based fallback instead of external placeholder URLs
  const hasImages = images && images.length > 0;
  const displayImages = hasImages ? images : [];

  // For rendering the fallback UI when no images are available
  const renderFallbackUI = () => (
    <div className="w-full h-full flex items-center justify-center bg-gray-100 text-gray-800">
      <div className="text-center p-4">
        <p className="text-xl font-bold">No Image Available</p>
        <p className="text-sm mt-2">{alt || 'Vehicle image not available'}</p>
      </div>
    </div>
  );

  const handlePrevious = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex === 0 ? displayImages.length - 1 : prevIndex - 1
    );
  };

  const handleNext = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex === displayImages.length - 1 ? 0 : prevIndex + 1
    );
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  return (
    <div className="relative" data-testid="image-gallery">
      {/* Main Image */}
      <div 
        className={`relative ${isFullscreen ? 'fixed inset-0 z-50 bg-black' : 'h-96 w-full rounded-lg overflow-hidden'}`}
        onClick={toggleFullscreen}
      >
        {hasImages && displayImages.length > 0 ? (
          <Image
            src={displayImages[currentIndex]}
            alt={`${alt} - Image ${currentIndex + 1}`}
            fill
            className={`object-contain ${isFullscreen ? 'p-4' : 'object-cover'}`}
          />
        ) : renderFallbackUI()}
        
        {/* Navigation Arrows */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            handlePrevious();
          }}
          className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 focus:outline-none"
          aria-label="Previous image"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleNext();
          }}
          className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 focus:outline-none"
          aria-label="Next image"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
        
        {/* Fullscreen Toggle */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            toggleFullscreen();
          }}
          className="absolute top-2 right-2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 focus:outline-none"
          aria-label={isFullscreen ? "Exit fullscreen" : "View fullscreen"}
        >
          {isFullscreen ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M5 10a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1H6a1 1 0 01-1-1v-3zm7-1a1 1 0 00-1 1v3a1 1 0 001 1h3a1 1 0 001-1v-3a1 1 0 00-1-1h-3z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 01-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4zm9 1a1 1 0 010-2h4a1 1 0 011 1v4a1 1 0 01-2 0V6.414l-2.293 2.293a1 1 0 11-1.414-1.414L13.586 5H12zm-9 7a1 1 0 012 0v1.586l2.293-2.293a1 1 0 111.414 1.414L6.414 15H8a1 1 0 010 2H4a1 1 0 01-1-1v-4zm13-1a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 010-2h1.586l-2.293-2.293a1 1 0 111.414-1.414L15 13.586V12a1 1 0 011-1z" clipRule="evenodd" />
            </svg>
          )}
        </button>
        
        {/* Image Counter */}
        <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-50 text-white px-3 py-1 rounded-full text-sm">
          {currentIndex + 1} / {displayImages.length}
        </div>
        
        {/* Source Bubble */}
        {vehicle?.source && (
          <div className="absolute bottom-2 left-2 bg-black bg-opacity-60 backdrop-blur-sm text-white text-xs font-mono px-2 py-1 rounded-full">
            {vehicle.source}
          </div>
        )}
      </div>
      
      {/* Thumbnail Navigation */}
      {hasImages && displayImages.length > 1 && (
        <div className="mt-4 flex space-x-2 overflow-x-auto pb-2">
          {displayImages.map((image, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`relative h-16 w-16 flex-shrink-0 rounded-md overflow-hidden border-2 ${
                index === currentIndex ? 'border-primary-500' : 'border-transparent'
              }`}
              aria-label={`View image ${index + 1}`}
            >
              {image ? (
                <Image
                  src={image}
                  alt={`${alt} - Thumbnail ${index + 1}`}
                  fill
                  className="object-cover"
                  onError={() => {
                    console.error(`[DEBUG ImageGallery] Thumbnail load error for image: ${image}`);
                  }}
                />
              ) : renderFallbackUI()}
            </button>
          ))}
        </div>
      )}
      
      {/* Fullscreen Overlay */}
      {isFullscreen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-90"
          onClick={toggleFullscreen}
        ></div>
      )}
    </div>
  );
};

export default ImageGallery;
