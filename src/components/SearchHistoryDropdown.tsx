import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { SearchFilters } from '@/types';

interface SearchHistoryDropdownProps {
  searchHistory: {
    id: string;
    filters: SearchFilters;
    timestamp: string;
  }[];
  onSelectHistory: (filters: SearchFilters) => void;
}

const SearchHistoryDropdown: React.FC<SearchHistoryDropdownProps> = ({
  searchHistory,
  onSelectHistory,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  
  // Format the timestamp to a readable format
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };
  
  // Format filter values for display
  const formatFilterValue = (key: string, value: any) => {
    if (key === 'price' || key.includes('price')) {
      return `$${value.toLocaleString()}`;
    }
    if (key === 'mileage' || key.includes('mileage')) {
      return `${value.toLocaleString()} miles`;
    }
    return value;
  };
  
  // Create a summary of the filters
  const getFilterSummary = (filters: SearchFilters) => {
    const filterEntries = Object.entries(filters);
    if (filterEntries.length === 0) return 'All vehicles';
    
    const summaryParts = filterEntries
      .slice(0, 2) // Only show first 2 filters in the summary
      .map(([key, value]) => {
        const formattedKey = key.replace(/([A-Z])/g, ' $1').toLowerCase();
        return `${formattedKey}: ${formatFilterValue(key, value)}`;
      });
    
    if (filterEntries.length > 2) {
      summaryParts.push(`+${filterEntries.length - 2} more`);
    }
    
    return summaryParts.join(', ');
  };
  
  return (
    <div className="relative">
      <button
        className="flex items-center text-sm text-gray-600 hover:text-gray-800"
        onClick={() => setIsOpen(!isOpen)}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5 mr-1"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        Recent Searches
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className={`h-4 w-4 ml-1 transition-transform ${isOpen ? 'transform rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {isOpen && (
        <div className="absolute z-10 mt-2 w-72 bg-white rounded-md shadow-lg py-1 right-0">
          {searchHistory.length === 0 ? (
            <div className="px-4 py-2 text-sm text-gray-500">No recent searches</div>
          ) : (
            <ul className="max-h-60 overflow-y-auto">
              {searchHistory.map((item) => (
                <li key={item.id}>
                  <button
                    className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                    onClick={() => {
                      onSelectHistory(item.filters);
                      setIsOpen(false);
                    }}
                  >
                    <div className="font-medium">{getFilterSummary(item.filters)}</div>
                    <div className="text-xs text-gray-500">{formatTimestamp(item.timestamp)}</div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchHistoryDropdown;
