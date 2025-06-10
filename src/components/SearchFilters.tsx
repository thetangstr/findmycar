import React, { useState, useEffect } from 'react';
import { SearchFilters as SearchFiltersType } from '@/types';
import { useSearchHistory } from '@/hooks/useSearchHistory';

interface SearchFiltersProps {
  initialFilters?: SearchFiltersType;
  onApplyFilters: (filters: SearchFiltersType) => void;
  onSaveSearch?: () => void;
}

const SearchFilters: React.FC<SearchFiltersProps> = ({ initialFilters = {}, onApplyFilters, onSaveSearch }) => {
  const [filters, setFilters] = useState<SearchFiltersType>(initialFilters);
  const [expandedSections, setExpandedSections] = useState<{[key: string]: boolean}>({
    basic: true,
    price: true,
    vehicle: false,
    features: false,
    location: false
  });
  const { searchHistory } = useSearchHistory();
  
  useEffect(() => {
    setFilters(initialFilters);
  }, [initialFilters]);
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;
    
    let parsedValue: string | number | undefined = value;
    
    // Parse numeric values
    if (type === 'number' && value !== '') {
      parsedValue = parseFloat(value);
    }
    
    // Handle empty values
    if (value === '') {
      parsedValue = undefined;
    }
    
    setFilters(prev => ({
      ...prev,
      [name]: parsedValue
    }));
  };
  
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    const featuresList = filters.features || [];
    
    if (checked) {
      setFilters(prev => ({
        ...prev,
        features: [...featuresList, name]
      }));
    } else {
      setFilters(prev => ({
        ...prev,
        features: featuresList.filter(feature => feature !== name)
      }));
    }
  };
  
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onApplyFilters(filters);
  };
  
  const handleReset = () => {
    setFilters({});
    onApplyFilters({});
  };
  
  // Function to apply a recent search
  const applyRecentSearch = (searchId: string) => {
    const search = searchHistory.find(item => item.id === searchId);
    if (search) {
      setFilters(search.filters);
      onApplyFilters(search.filters);
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Search Filters</h2>
      
      {/* Recent Searches Quick Access */}
      {searchHistory.length > 0 && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Recent Searches
          </label>
          <div className="flex flex-wrap gap-2">
            {searchHistory.slice(0, 3).map(search => (
              <button
                key={search.id}
                type="button"
                onClick={() => applyRecentSearch(search.id)}
                className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700"
              >
                {Object.keys(search.filters).length > 0 ? 
                  `${search.filters.make || ''} ${search.filters.model || ''}`.trim() || 'Search' : 
                  'All Vehicles'}
              </button>
            ))}
          </div>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        {/* Basic Section */}
        <div className="mb-4 border-b border-gray-200 pb-2">
          <button 
            type="button"
            className="flex w-full justify-between items-center text-left"
            onClick={() => toggleSection('basic')}
          >
            <h3 className="text-lg font-medium text-gray-900">Basic Filters</h3>
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className={`h-5 w-5 transition-transform ${expandedSections.basic ? 'transform rotate-180' : ''}`}
              viewBox="0 0 20 20" 
              fill="currentColor"
            >
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
        
        {expandedSections.basic && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {/* Make */}
            <div>
              <label htmlFor="make" className="block text-sm font-medium text-gray-700 mb-1">
                Make
              </label>
              <input
                type="text"
                id="make"
                name="make"
                value={filters.make || ''}
                onChange={handleInputChange}
                className="input"
                placeholder="e.g. Toyota"
              />
            </div>
            
            {/* Model */}
            <div>
              <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-1">
                Model
              </label>
              <input
                type="text"
                id="model"
                name="model"
                value={filters.model || ''}
                onChange={handleInputChange}
                className="input"
                placeholder="e.g. Camry"
              />
            </div>
            
            {/* Year Range */}
            <div>
              <label htmlFor="yearMin" className="block text-sm font-medium text-gray-700 mb-1">
                Year (Min)
              </label>
              <input
                type="number"
                id="yearMin"
                name="yearMin"
                value={filters.yearMin || ''}
                onChange={handleInputChange}
                className="input"
                placeholder="Min Year"
                min={1900}
                max={2030}
              />
            </div>
            
            <div>
              <label htmlFor="yearMax" className="block text-sm font-medium text-gray-700 mb-1">
                Year (Max)
              </label>
              <input
                type="number"
                id="yearMax"
                name="yearMax"
                value={filters.yearMax || ''}
                onChange={handleInputChange}
                className="input"
                placeholder="Max Year"
                min={1900}
                max={2030}
              />
            </div>
          </div>
        )}
        
        {/* Price Section */}
        <div className="mb-4 border-b border-gray-200 pb-2">
          <button 
            type="button"
            className="flex w-full justify-between items-center text-left"
            onClick={() => toggleSection('price')}
          >
            <h3 className="text-lg font-medium text-gray-900">Price & Mileage</h3>
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className={`h-5 w-5 transition-transform ${expandedSections.price ? 'transform rotate-180' : ''}`}
              viewBox="0 0 20 20" 
              fill="currentColor"
            >
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
        
        {expandedSections.price && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {/* Price Range */}
            <div>
              <label htmlFor="priceMin" className="block text-sm font-medium text-gray-700 mb-1">
                Price (Min)
              </label>
              <input
                type="number"
                id="priceMin"
                name="priceMin"
                value={filters.priceMin || ''}
                onChange={handleInputChange}
                className="input"
                placeholder="Min Price"
                min={0}
              />
            </div>
            
            <div>
              <label htmlFor="priceMax" className="block text-sm font-medium text-gray-700 mb-1">
                Price (Max)
              </label>
              <input
                type="number"
                id="priceMax"
                name="priceMax"
                value={filters.priceMax || ''}
                onChange={handleInputChange}
                className="input"
                placeholder="Max Price"
                min={0}
              />
            </div>
            
            {/* Mileage Range */}
            <div>
              <label htmlFor="mileageMin" className="block text-sm font-medium text-gray-700 mb-1">
                Mileage (Min)
              </label>
              <input
                type="number"
                id="mileageMin"
                name="mileageMin"
                value={filters.mileageMin || ''}
                onChange={handleInputChange}
                className="input"
                placeholder="Min Mileage"
                min={0}
              />
            </div>
            
            <div>
              <label htmlFor="mileageMax" className="block text-sm font-medium text-gray-700 mb-1">
                Mileage (Max)
              </label>
              <input
                type="number"
                id="mileageMax"
                name="mileageMax"
                value={filters.mileageMax || ''}
                onChange={handleInputChange}
                className="input"
                placeholder="Max Mileage"
                min={0}
              />
            </div>
          </div>
        )}
        
        {/* Vehicle Details Section */}
        <div className="mb-4 border-b border-gray-200 pb-2">
          <button 
            type="button"
            className="flex w-full justify-between items-center text-left"
            onClick={() => toggleSection('vehicle')}
          >
            <h3 className="text-lg font-medium text-gray-900">Vehicle Details</h3>
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className={`h-5 w-5 transition-transform ${expandedSections.vehicle ? 'transform rotate-180' : ''}`}
              viewBox="0 0 20 20" 
              fill="currentColor"
            >
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
        
        {expandedSections.vehicle && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {/* Fuel Type */}
            <div>
              <label htmlFor="fuelType" className="block text-sm font-medium text-gray-700 mb-1">
                Fuel Type
              </label>
              <select
                id="fuelType"
                name="fuelType"
                value={filters.fuelType || ''}
                onChange={handleInputChange}
                className="input"
              >
                <option value="">Any</option>
                <option value="Gasoline">Gasoline</option>
                <option value="Diesel">Diesel</option>
                <option value="Hybrid">Hybrid</option>
                <option value="Electric">Electric</option>
                <option value="Plug-in Hybrid">Plug-in Hybrid</option>
              </select>
            </div>
            
            {/* Transmission */}
            <div>
              <label htmlFor="transmission" className="block text-sm font-medium text-gray-700 mb-1">
                Transmission
              </label>
              <select
                id="transmission"
                name="transmission"
                value={filters.transmission || ''}
                onChange={handleInputChange}
                className="input"
              >
                <option value="">Any</option>
                <option value="Automatic">Automatic</option>
                <option value="Manual">Manual</option>
                <option value="CVT">CVT</option>
                <option value="Semi-Automatic">Semi-Automatic</option>
              </select>
            </div>
            
            {/* Drivetrain */}
            <div>
              <label htmlFor="drivetrain" className="block text-sm font-medium text-gray-700 mb-1">
                Drivetrain
              </label>
              <select
                id="drivetrain"
                name="drivetrain"
                value={filters.drivetrain || ''}
                onChange={handleInputChange}
                className="input"
              >
                <option value="">Any</option>
                <option value="AWD">All-Wheel Drive (AWD)</option>
                <option value="FWD">Front-Wheel Drive (FWD)</option>
                <option value="RWD">Rear-Wheel Drive (RWD)</option>
                <option value="4WD">Four-Wheel Drive (4WD)</option>
              </select>
            </div>
            
            {/* Body Type */}
            <div>
              <label htmlFor="bodyType" className="block text-sm font-medium text-gray-700 mb-1">
                Body Type
              </label>
              <select
                id="bodyType"
                name="bodyType"
                value={filters.bodyType || ''}
                onChange={handleInputChange}
                className="input"
              >
                <option value="">Any</option>
                <option value="Sedan">Sedan</option>
                <option value="SUV">SUV</option>
                <option value="Truck">Truck</option>
                <option value="Coupe">Coupe</option>
                <option value="Convertible">Convertible</option>
                <option value="Wagon">Wagon</option>
                <option value="Van">Van/Minivan</option>
                <option value="Hatchback">Hatchback</option>
              </select>
            </div>
            
            {/* Exterior Color */}
            <div>
              <label htmlFor="exteriorColor" className="block text-sm font-medium text-gray-700 mb-1">
                Exterior Color
              </label>
              <select
                id="exteriorColor"
                name="exteriorColor"
                value={filters.exteriorColor || ''}
                onChange={handleInputChange}
                className="input"
              >
                <option value="">Any</option>
                <option value="Black">Black</option>
                <option value="White">White</option>
                <option value="Silver">Silver</option>
                <option value="Gray">Gray</option>
                <option value="Red">Red</option>
                <option value="Blue">Blue</option>
                <option value="Green">Green</option>
                <option value="Brown">Brown</option>
                <option value="Yellow">Yellow</option>
                <option value="Orange">Orange</option>
                <option value="Purple">Purple</option>
                <option value="Gold">Gold</option>
              </select>
            </div>
            
            {/* Interior Color */}
            <div>
              <label htmlFor="interiorColor" className="block text-sm font-medium text-gray-700 mb-1">
                Interior Color
              </label>
              <select
                id="interiorColor"
                name="interiorColor"
                value={filters.interiorColor || ''}
                onChange={handleInputChange}
                className="input"
              >
                <option value="">Any</option>
                <option value="Black">Black</option>
                <option value="Gray">Gray</option>
                <option value="Tan">Tan</option>
                <option value="Brown">Brown</option>
                <option value="Beige">Beige</option>
                <option value="White">White</option>
                <option value="Red">Red</option>
              </select>
            </div>
          </div>
        )}
        
        {/* Features Section */}
        <div className="mb-4 border-b border-gray-200 pb-2">
          <button 
            type="button"
            className="flex w-full justify-between items-center text-left"
            onClick={() => toggleSection('features')}
          >
            <h3 className="text-lg font-medium text-gray-900">Features</h3>
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className={`h-5 w-5 transition-transform ${expandedSections.features ? 'transform rotate-180' : ''}`}
              viewBox="0 0 20 20" 
              fill="currentColor"
            >
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
        
        {expandedSections.features && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="feature-navigation"
                name="Navigation"
                checked={filters.features?.includes('Navigation') || false}
                onChange={handleCheckboxChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="feature-navigation" className="ml-2 text-sm text-gray-700">
                Navigation
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="feature-bluetooth"
                name="Bluetooth"
                checked={filters.features?.includes('Bluetooth') || false}
                onChange={handleCheckboxChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="feature-bluetooth" className="ml-2 text-sm text-gray-700">
                Bluetooth
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="feature-leather"
                name="Leather Seats"
                checked={filters.features?.includes('Leather Seats') || false}
                onChange={handleCheckboxChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="feature-leather" className="ml-2 text-sm text-gray-700">
                Leather Seats
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="feature-sunroof"
                name="Sunroof"
                checked={filters.features?.includes('Sunroof') || false}
                onChange={handleCheckboxChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="feature-sunroof" className="ml-2 text-sm text-gray-700">
                Sunroof
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="feature-heated-seats"
                name="Heated Seats"
                checked={filters.features?.includes('Heated Seats') || false}
                onChange={handleCheckboxChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="feature-heated-seats" className="ml-2 text-sm text-gray-700">
                Heated Seats
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="feature-backup-camera"
                name="Backup Camera"
                checked={filters.features?.includes('Backup Camera') || false}
                onChange={handleCheckboxChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="feature-backup-camera" className="ml-2 text-sm text-gray-700">
                Backup Camera
              </label>
            </div>
          </div>
        )}
        
        {/* Location Section */}
        <div className="mb-4 border-b border-gray-200 pb-2">
          <button 
            type="button"
            className="flex w-full justify-between items-center text-left"
            onClick={() => toggleSection('location')}
          >
            <h3 className="text-lg font-medium text-gray-900">Location</h3>
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className={`h-5 w-5 transition-transform ${expandedSections.location ? 'transform rotate-180' : ''}`}
              viewBox="0 0 20 20" 
              fill="currentColor"
            >
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
        
        {expandedSections.location && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label htmlFor="zipCode" className="block text-sm font-medium text-gray-700 mb-1">
                ZIP Code
              </label>
              <input
                type="text"
                id="zipCode"
                name="zipCode"
                value={filters.zipCode || ''}
                onChange={handleInputChange}
                className="input"
                placeholder="Enter ZIP code"
              />
            </div>
            
            <div>
              <label htmlFor="distance" className="block text-sm font-medium text-gray-700 mb-1">
                Distance (miles)
              </label>
              <select
                id="distance"
                name="distance"
                value={filters.distance || ''}
                onChange={handleInputChange}
                className="input"
              >
                <option value="">Any distance</option>
                <option value="10">10 miles</option>
                <option value="25">25 miles</option>
                <option value="50">50 miles</option>
                <option value="100">100 miles</option>
                <option value="250">250 miles</option>
                <option value="500">500 miles</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="sellerType" className="block text-sm font-medium text-gray-700 mb-1">
                Seller Type
              </label>
              <select
                id="sellerType"
                name="sellerType"
                value={filters.sellerType || ''}
                onChange={handleInputChange}
                className="input"
              >
                <option value="">Any</option>
                <option value="Dealer">Dealer</option>
                <option value="Private">Private Seller</option>
              </select>
            </div>
          </div>
        )}
        
        {/* Keyword Search */}
        <div className="mb-6">
          <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-1">
            Keyword Search
          </label>
          <input
            type="text"
            id="query"
            name="query"
            value={filters.query || ''}
            onChange={handleInputChange}
            className="input"
            placeholder="Search by keyword..."
          />
        </div>
        
        {/* Sort Options */}
        <div className="mb-6">
          <label htmlFor="sortBy" className="block text-sm font-medium text-gray-700 mb-1">
            Sort Results By
          </label>
          <select
            id="sortBy"
            name="sortBy"
            value={filters.sortBy || ''}
            onChange={handleInputChange}
            className="input"
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
        
        <div className="flex flex-wrap gap-3 justify-between">
          <div>
            <button type="submit" className="btn btn-primary mr-2">
              Apply Filters
            </button>
            
            <button type="button" onClick={handleReset} className="btn btn-secondary">
              Reset Filters
            </button>
          </div>
          
          {onSaveSearch && (
            <button 
              type="button" 
              onClick={onSaveSearch} 
              className="btn bg-green-600 text-white hover:bg-green-700 flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z" />
              </svg>
              Save Search
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default SearchFilters;
