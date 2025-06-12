import React, { useState, useEffect } from 'react';
import { useVehicles } from '@/hooks/useVehicles';
import { useSearchHistory } from '@/hooks/useSearchHistory';
import { useSavedSearches } from '@/hooks/useSavedSearches';
import { useRecentlyViewed } from '@/hooks/useRecentlyViewed';
import SearchFilters from '@/components/SearchFilters';
import VehicleCard from '@/components/VehicleCard';
import SearchHistoryDropdown from '@/components/SearchHistoryDropdown';
import SaveSearchModal from '@/components/SaveSearchModal';
import SortOptions from '@/components/SortOptions';
import NaturalLanguageSearch from '@/components/NaturalLanguageSearch';
import { SearchFilters as SearchFiltersType } from '@/types';
import { Vehicle } from '@/types';

export default function Search() {
  const { vehicles, filteredVehicles, filters, applyFilters, getVehicleById, loading } = useVehicles();
  const { searchHistory, addToHistory } = useSearchHistory();
  const { saveSearch } = useSavedSearches();
  
  const { addToRecentlyViewed } = useRecentlyViewed(getVehicleById);
  
  // Create a wrapper function for adding to recently viewed
  const handleViewVehicle = (id: string) => {
    addToRecentlyViewed(id);
  };
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [sortedVehicles, setSortedVehicles] = useState<Vehicle[]>([]);
  
  // Apply sorting whenever filtered vehicles or sort options change
  useEffect(() => {
    let sorted = [...filteredVehicles];
    
    if (filters.sortBy) {
      const [field, direction] = filters.sortBy.split('-');
      const isAsc = direction === 'asc';
      
      sorted.sort((a, b) => {
        if (field === 'price') {
          return isAsc ? a.price - b.price : b.price - a.price;
        } else if (field === 'year') {
          return isAsc ? a.year - b.year : b.year - a.year;
        } else if (field === 'mileage') {
          return isAsc ? a.mileage - b.mileage : b.mileage - a.mileage;
        } else if (field === 'listingDate') {
          return isAsc 
            ? new Date(a.listingDate).getTime() - new Date(b.listingDate).getTime() 
            : new Date(b.listingDate).getTime() - new Date(a.listingDate).getTime();
        }
        return 0;
      });
    }
    
    setSortedVehicles(sorted);
  }, [filteredVehicles, filters.sortBy]);
  
  const handleApplyFilters = async (newFilters: SearchFiltersType) => {
    await applyFilters(newFilters);
    addToHistory(newFilters);
    setShowHistory(false);
  };
  
  const handleSaveSearch = (name: string) => {
    saveSearch(name, filters);
  };
  
  const handleHistoryItemClick = async (filters: SearchFiltersType) => {
    await applyFilters(filters);
    setShowHistory(false);
  };
  
  // Handler for natural language search
  const handleNaturalLanguageSearch = async (nlFilters: SearchFiltersType) => {
    await applyFilters(nlFilters);
    addToHistory(nlFilters);
  };
  
  return (
    <div>
      {/* Natural Language Search Component */}
      <NaturalLanguageSearch onSearch={handleNaturalLanguageSearch} className="mb-8" />
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-1">
          <div className="sticky top-24">
            <SearchFilters
              initialFilters={filters}
              onApplyFilters={handleApplyFilters}
              onSaveSearch={() => setIsModalOpen(true)}
            />
            
            {/* Search History Dropdown */}
            {searchHistory.length > 0 && (
              <div className="mt-6 bg-white rounded-lg shadow-md p-4">
                <div 
                  className="flex justify-between items-center cursor-pointer"
                  onClick={() => setShowHistory(!showHistory)}
                >
                  <h3 className="text-lg font-medium text-gray-900">Recent Searches</h3>
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    className={`h-5 w-5 transition-transform ${showHistory ? 'transform rotate-180' : ''}`} 
                    viewBox="0 0 20 20" 
                    fill="currentColor"
                  >
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                
                {showHistory && (
                  <div className="mt-3 space-y-2">
                    {searchHistory.map((item, index) => {
                      // Create a summary of the search
                      const searchSummary = Object.entries(item.filters)
                        .filter(([_, value]) => value !== undefined && value !== '')
                        .map(([key, value]) => `${key.replace(/([A-Z])/g, ' $1').trim()}: ${value}`)
                        .join(', ');
                      
                      return (
                        <div 
                          key={item.id} 
                          className="p-2 hover:bg-gray-50 rounded cursor-pointer text-sm"
                          onClick={() => handleHistoryItemClick(item.filters)}
                        >
                          <p className="text-gray-900 font-medium">Search {index + 1}</p>
                          <p className="text-gray-600 truncate">{searchSummary || 'All vehicles'}</p>
                          <p className="text-gray-400 text-xs mt-1">
                            {new Date(item.timestamp).toLocaleDateString()}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <h2 className="text-xl font-semibold text-gray-900">
                {filteredVehicles.length} {filteredVehicles.length === 1 ? 'Vehicle' : 'Vehicles'} Found
              </h2>
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Sort by:</span>
                  <select 
                    className="border border-gray-300 rounded-md text-sm p-1"
                    value={filters.sortBy || ''}
                    onChange={(e) => {
                      applyFilters({ ...filters, sortBy: e.target.value });
                    }}
                  >
                    <option value="">Default</option>
                    <option value="price-asc">Price: Low to High</option>
                    <option value="price-desc">Price: High to Low</option>
                    <option value="year-desc">Year: Newest</option>
                    <option value="year-asc">Year: Oldest</option>
                    <option value="mileage-asc">Mileage: Low to High</option>
                    <option value="mileage-desc">Mileage: High to Low</option>
                    <option value="listingDate-desc">Newest Listings</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          
          {loading ? (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <h3 className="text-xl font-medium text-gray-900 mb-2">Loading vehicles...</h3>
              <p className="text-gray-600 mb-4">
                Please wait while we find the perfect match for you.
              </p>
            </div>
          ) : filteredVehicles.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-xl font-medium text-gray-900 mb-2">No vehicles found</h3>
              <p className="text-gray-600 mb-4">
                Try adjusting your search filters to find more results.
              </p>
              <button 
                onClick={() => applyFilters({})} 
                className="btn btn-primary"
              >
                Clear All Filters
              </button>
            </div>
          ) : (
            <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 auto-rows-fr">
              {sortedVehicles.map(vehicle => (
                <VehicleCard 
                  key={vehicle.id} 
                  vehicle={vehicle} 
                  onView={() => handleViewVehicle(vehicle.id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Save Search Modal */}
      <SaveSearchModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveSearch}
        filters={filters}
      />
    </div>
  );
}
