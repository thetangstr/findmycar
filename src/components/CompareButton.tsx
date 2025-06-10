import React, { useState, useEffect } from 'react';
import { useComparison } from '@/hooks/useComparison';
import { useVehicles } from '@/hooks/useVehicles';

interface CompareButtonProps {
  vehicleId: string;
}

const CompareButton: React.FC<CompareButtonProps> = ({ vehicleId }) => {
  const { getVehicleById } = useVehicles();
  const { addToComparison, removeFromComparison, isInComparison, comparisonCount } = useComparison(getVehicleById);
  const [isComparing, setIsComparing] = useState(false);
  const [isDisabled, setIsDisabled] = useState(false);
  
  useEffect(() => {
    setIsComparing(isInComparison(vehicleId));
    setIsDisabled(!isInComparison(vehicleId) && comparisonCount >= 4);
  }, [vehicleId, isInComparison, comparisonCount]);
  
  const handleToggleCompare = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isComparing) {
      removeFromComparison(vehicleId);
    } else if (!isDisabled) {
      addToComparison(vehicleId);
    }
  };
  
  return (
    <button
      onClick={handleToggleCompare}
      disabled={isDisabled && !isComparing}
      className={`p-2 rounded-full focus:outline-none transition-colors ${
        isComparing 
          ? 'bg-primary-600 text-white hover:bg-primary-700' 
          : isDisabled 
            ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
            : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-300'
      }`}
      title={
        isComparing 
          ? 'Remove from comparison' 
          : isDisabled 
            ? 'Maximum 4 vehicles for comparison' 
            : 'Add to comparison'
      }
    >
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M5 4a1 1 0 00-2 0v7.268a2 2 0 000 3.464V16a1 1 0 102 0v-1.268a2 2 0 000-3.464V4zM11 4a1 1 0 10-2 0v1.268a2 2 0 000 3.464V16a1 1 0 102 0V8.732a2 2 0 000-3.464V4zM16 3a1 1 0 011 1v7.268a2 2 0 010 3.464V16a1 1 0 11-2 0v-1.268a2 2 0 010-3.464V4a1 1 0 011-1z" clipRule="evenodd" />
      </svg>
    </button>
  );
};

export default CompareButton;
