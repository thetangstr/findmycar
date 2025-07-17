import React, { useState } from 'react';
import { SearchFilters as SearchFiltersType, Vehicle } from '@/types';
import LoadingSpinner from './LoadingSpinner';

interface NaturalLanguageSearchProps {
  onSearch: (filters: SearchFiltersType) => void;
  onVehiclesFound?: (vehicles: Vehicle[]) => void;
  className?: string;
}

const NaturalLanguageSearch: React.FC<NaturalLanguageSearchProps> = ({ onSearch, onVehiclesFound, className = '' }) => {
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [thinkingSteps, setThinkingSteps] = useState<string[]>([]);
  const [useIntelligentSearch, setUseIntelligentSearch] = useState(true);
  const [showThinking, setShowThinking] = useState(false);

  // A simplified parser for when intelligent search is off or fails
  const parseQueryFallback = (text: string): SearchFiltersType => {
    const filters: SearchFiltersType = {};
    const lowerCaseText = text.toLowerCase();
    if (lowerCaseText.includes('sedan')) filters.bodyType = 'Sedan';
    if (lowerCaseText.includes('suv')) filters.bodyType = 'SUV';
    if (lowerCaseText.includes('truck')) filters.bodyType = 'Truck';
    const priceMatch = lowerCaseText.match(/under \$?(\d+)k?/);
    if (priceMatch) {
      filters.priceMax = parseInt(priceMatch[1]) * 1000;
    }
    return filters;
  };

  const handleSearch = async () => {
    if (!query.trim()) return;

    setThinkingSteps([]);
    setIsProcessing(true);

    try {
      if (useIntelligentSearch) {
        const { intelligentVehicleSearch } = await import('../services/intelligentSearchService');
        let searchSource: string | undefined = undefined;
        const lowerQuery = query.toLowerCase();
        if (lowerQuery.includes('from hemmings')) searchSource = 'hemmings';
        else if (lowerQuery.includes('from bat') || lowerQuery.includes('from bring a trailer')) searchSource = 'bat';
        // Add other source detections here, e.g., 'from autodev'

        const vehicles = await intelligentVehicleSearch(query, (message: string) => {
          // Only update steps if the user wants to see them
          if (showThinking) {
            setThinkingSteps((prev) => [...prev, message]);
          }
        }, searchSource);

        if (onVehiclesFound) {
          onVehiclesFound(vehicles);
        }
        // If intelligent search is used, we assume onVehiclesFound handles results or onSearch is implicitly covered by it.
        // If specific filters need to be extracted even after intelligent search, that logic would go here.

      } else {
        // Use the basic fallback parser
        let searchSource: string | undefined = undefined;
        const lowerQuery = query.toLowerCase();
        if (lowerQuery.includes('from hemmings')) searchSource = 'hemmings';
        else if (lowerQuery.includes('from bat') || lowerQuery.includes('from bring a trailer')) searchSource = 'bat';

        const filters = parseQueryFallback(query);
        onSearch({ ...filters, source: searchSource });
      }
    } catch (error) {
      console.error('Error during search, falling back to basic parser:', error);
      // If any error occurs, fall back to the basic parser
      let searchSource: string | undefined = undefined;
      const lowerQuery = query.toLowerCase();
      if (lowerQuery.includes('from hemmings')) searchSource = 'hemmings';
      else if (lowerQuery.includes('from bat') || lowerQuery.includes('from bring a trailer')) searchSource = 'bat';
      const filters = parseQueryFallback(query);
      onSearch({ ...filters, source: searchSource });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 mb-6 ${className}`}>
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Intelligent Car Search</h2>
      <p className="text-gray-600 mb-4">
        Describe your ideal car, e.g., &quot;A reliable BMW sedan under $40k with a manual transmission.&quot;
      </p>

      <div className="flex flex-col md:flex-row gap-3">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="What are you looking for?"
          className="flex-grow p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
          disabled={isProcessing}
        />
        <button
          onClick={handleSearch}
          disabled={isProcessing || !query.trim()}
          className="bg-indigo-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 transition inline-flex items-center"
        >
          {isProcessing ? (
            <>
              <LoadingSpinner size="sm" color="white" className="mr-2" />
              Searching...
            </>
          ) : (
            'Search'
          )}
        </button>
      </div>

      <div className="flex items-center mt-4">
        <div className="flex items-center">
          <input
            id="show-thinking-checkbox"
            type="checkbox"
            checked={showThinking}
            onChange={(e) => setShowThinking(e.target.checked)}
            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
          />
          <label htmlFor="show-thinking-checkbox" className="ml-2 block text-sm text-gray-900">
            Show AI&apos;s thinking
          </label>
        </div>
      </div>

      {showThinking && thinkingSteps.length > 0 && (
        <div className="bg-gray-50 p-4 rounded-lg mt-4 animate-fade-in-up">
          <h3 className="text-lg font-medium text-gray-800 mb-2">Thinking...</h3>
          <ul className="space-y-2">
            {thinkingSteps.map((step, index) => (
              <li key={index} className="text-sm text-gray-600 animate-fade-in-up" style={{ animationDelay: `${index * 100}ms` }}>
                {step}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default NaturalLanguageSearch;

