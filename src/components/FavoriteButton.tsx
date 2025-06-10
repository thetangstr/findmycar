import React, { useState, useEffect } from 'react';
import { useFavorites } from '@/hooks/useFavorites';
import { useVehicles } from '@/hooks/useVehicles';

interface FavoriteButtonProps {
  vehicleId: string;
}

const FavoriteButton: React.FC<FavoriteButtonProps> = ({ vehicleId }) => {
  const { getVehicleById } = useVehicles();
  const { addToFavorites, removeFromFavorites, isInFavorites } = useFavorites(getVehicleById);
  const [isFavorite, setIsFavorite] = useState(false);
  
  useEffect(() => {
    // Check if the vehicle is in favorites
    setIsFavorite(isInFavorites(vehicleId));
  }, [vehicleId, isInFavorites]);
  
  const handleToggleFavorite = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isFavorite) {
      removeFromFavorites(vehicleId);
      setIsFavorite(false);
    } else {
      addToFavorites(vehicleId);
      setIsFavorite(true);
    }
  };
  
  return (
    <button
      onClick={handleToggleFavorite}
      className={`p-2 rounded-full focus:outline-none transition-colors ${
        isFavorite 
          ? 'bg-red-500 text-white hover:bg-red-600' 
          : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-300'
      }`}
      title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
    >
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path 
          fillRule="evenodd" 
          d={isFavorite 
            ? "M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" 
            : "M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z"
          } 
          clipRule="evenodd" 
        />
      </svg>
    </button>
  );
};

export default FavoriteButton;
