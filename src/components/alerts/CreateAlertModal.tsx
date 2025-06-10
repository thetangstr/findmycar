import React, { useState } from 'react';
import { SearchFilters } from '@/types';
import { useAlerts } from '@/hooks/useAlerts';

interface CreateAlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  filters: SearchFilters;
}

const CreateAlertModal: React.FC<CreateAlertModalProps> = ({ isOpen, onClose, filters }) => {
  const { createAlert } = useAlerts();
  const [alertName, setAlertName] = useState('');
  const [frequency, setFrequency] = useState<'daily' | 'weekly' | 'instant'>('daily');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  // Format filters for display
  const formatFilterValue = (key: string, value: any) => {
    if (key === 'price' || key.includes('price')) {
      return `$${value.toLocaleString()}`;
    }
    if (key === 'mileage' || key.includes('mileage')) {
      return `${value.toLocaleString()} miles`;
    }
    return value;
  };

  const filterSummary = Object.entries(filters)
    .filter(([_, value]) => value !== undefined && value !== '')
    .map(([key, value]) => {
      // Format the key for display
      const formattedKey = key
        .replace(/([A-Z])/g, ' $1') // Add space before capital letters
        .replace(/^./, str => str.toUpperCase()); // Capitalize first letter
      
      return `${formattedKey}: ${formatFilterValue(key, value)}`;
    })
    .join(', ');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!alertName.trim()) {
      setError('Please provide a name for this alert');
      return;
    }

    setIsSubmitting(true);

    try {
      createAlert(alertName.trim(), filters, frequency);
      setAlertName('');
      setFrequency('daily');
      onClose();
    } catch (err) {
      setError('Failed to create alert. Please try again.');
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Create Email Alert</h2>
        
        {filterSummary && (
          <div className="mb-4 p-3 bg-gray-50 rounded-md text-sm text-gray-700">
            <p className="font-medium mb-1">Alert Criteria:</p>
            <p>{filterSummary || 'All vehicles'}</p>
          </div>
        )}
        
        {error && (
          <div className="mb-4 p-3 bg-red-50 rounded-md text-sm text-red-700">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="alertName" className="block text-sm font-medium text-gray-700 mb-1">
              Alert Name
            </label>
            <input
              type="text"
              id="alertName"
              value={alertName}
              onChange={(e) => setAlertName(e.target.value)}
              className="input"
              placeholder="e.g. Toyota SUVs under $30k"
              disabled={isSubmitting}
              autoFocus
            />
          </div>
          
          <div className="mb-6">
            <label htmlFor="frequency" className="block text-sm font-medium text-gray-700 mb-1">
              Alert Frequency
            </label>
            <select
              id="frequency"
              value={frequency}
              onChange={(e) => setFrequency(e.target.value as any)}
              className="input"
              disabled={isSubmitting}
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="instant">Instant (as soon as new listings appear)</option>
            </select>
            <p className="mt-1 text-xs text-gray-500">
              How often would you like to receive alerts about new listings?
            </p>
          </div>
          
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating...
                </span>
              ) : 'Create Alert'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateAlertModal;
