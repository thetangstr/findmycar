import React, { useState } from 'react';
import { useVehicles } from '@/hooks/useVehicles';
import { useLLMSearch } from '@/hooks/useLLMSearch';
import { useRecentlyViewed } from '@/hooks/useRecentlyViewed';
import VehicleCard from '@/components/VehicleCard';

export default function LLMSearch() {
  const { vehicles, getVehicleById } = useVehicles();
  const { results, isSearching, error, searchWithLLM } = useLLMSearch(vehicles);
  const { addToRecentlyViewed } = useRecentlyViewed(getVehicleById);
  
  const [query, setQuery] = useState('');
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      searchWithLLM(query);
    }
  };
  
  const exampleQueries = [
    "I need a family-friendly SUV with good safety features",
    "Show me affordable electric vehicles",
    "I want a luxury car with leather seats",
    "Find me a vehicle with good fuel economy for commuting"
  ];
  
  const handleExampleClick = (example: string) => {
    setQuery(example);
    searchWithLLM(example);
  };
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI-Powered Search</h1>
        <p className="text-gray-600">
          Describe what you&apos;re looking for in natural language, and our AI will find the best matches for you.
        </p>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., I need a family car with good safety features under $30,000"
              className="input flex-grow text-lg py-3"
              disabled={isSearching}
            />
            <button
              type="submit"
              className="btn btn-primary md:w-auto w-full py-3 px-6"
              disabled={isSearching || !query.trim()}
            >
              {isSearching ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Searching...
                </span>
              ) : (
                'Search'
              )}
            </button>
          </div>
        </form>
        
        {!results.length && !isSearching && !error && (
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-3">Try these example searches:</h3>
            <div className="flex flex-wrap gap-2">
              {exampleQueries.map((example, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleClick(example)}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-800 px-3 py-2 rounded-full text-sm transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {error && (
          <div className="bg-red-50 text-red-800 p-4 rounded-md mb-6">
            <p>{error}</p>
          </div>
        )}
      </div>
      
      {isSearching && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600 mb-4"></div>
          <p className="text-gray-600">Our AI is analyzing your request...</p>
        </div>
      )}
      
      {results.length > 0 && !isSearching && (
        <div>
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              {results.length} {results.length === 1 ? 'Vehicle' : 'Vehicles'} Found
            </h2>
            <p className="text-gray-600 mt-1">
              Based on your search: &quot;{query}&quot;
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.map(vehicle => (
              <VehicleCard 
                key={vehicle.id} 
                vehicle={vehicle} 
                onView={() => addToRecentlyViewed(vehicle.id)}
              />
            ))}
          </div>
        </div>
      )}
      
      {results.length === 0 && query && !isSearching && !error && (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-xl font-medium text-gray-900 mb-2">No vehicles found</h3>
          <p className="text-gray-600 mb-4">
            Try a different search query or browse our inventory.
          </p>
          <button 
            onClick={() => setQuery('')} 
            className="btn btn-primary"
          >
            Clear Search
          </button>
        </div>
      )}
    </div>
  );
}
