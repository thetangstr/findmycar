import React, { useState } from 'react';
import { SearchFilters } from '@/types';

interface HomeSearchBoxProps {
  onSearch: (filters: SearchFilters) => void;
  isSearching: boolean;
}

const HomeSearchBox: React.FC<HomeSearchBoxProps> = ({ onSearch, isSearching }) => {
  const [query, setQuery] = useState('');

  // Function to parse natural language query into search filters
  const parseQuery = (text: string): SearchFilters => {
    const filters: SearchFilters = {};
    
    // Parse for vehicle type/body style
    const bodyTypePatterns = [
      { regex: /\b(suv|suvs|crossover|crossovers)\b/i, value: 'SUV' },
      { regex: /\b(sedan|sedans)\b/i, value: 'Sedan' },
      { regex: /\b(truck|trucks|pickup|pickups)\b/i, value: 'Truck' },
      { regex: /\b(coupe|coupes)\b/i, value: 'Coupe' },
      { regex: /\b(convertible|convertibles)\b/i, value: 'Convertible' },
      { regex: /\b(hatchback|hatchbacks)\b/i, value: 'Hatchback' },
      { regex: /\b(wagon|wagons)\b/i, value: 'Wagon' },
      { regex: /\b(van|vans|minivan|minivans)\b/i, value: 'Van' }
    ];
    
    for (const pattern of bodyTypePatterns) {
      if (pattern.regex.test(text)) {
        filters.bodyType = pattern.value;
        break;
      }
    }
    
    // Parse for makes
    const commonMakes = [
      'Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'BMW', 'Mercedes', 
      'Audi', 'Lexus', 'Hyundai', 'Kia', 'Subaru', 'Mazda', 'Volkswagen',
      'Jeep', 'Tesla', 'Volvo', 'Porsche', 'Acura', 'Infiniti', 'Cadillac'
    ];
    
    for (const make of commonMakes) {
      if (new RegExp(`\\b${make}\\b`, 'i').test(text)) {
        filters.make = make;
        break;
      }
    }
    
    // Parse for price ranges
    const underPriceMatch = text.match(/\bunder\s+\$?(\d+)[k]?\b/i);
    const maxPriceMatch = text.match(/\bless than\s+\$?(\d+)[k]?\b/i);
    const priceRangeMatch = text.match(/\bbetween\s+\$?(\d+)[k]?\s+and\s+\$?(\d+)[k]?\b/i);
    
    if (underPriceMatch || maxPriceMatch) {
      const match = underPriceMatch || maxPriceMatch;
      let price = parseInt(match![1], 10);
      if (match![0].toLowerCase().includes('k')) {
        price *= 1000;
      }
      filters.priceMax = price;
    } else if (priceRangeMatch) {
      let min = parseInt(priceRangeMatch[1], 10);
      let max = parseInt(priceRangeMatch[2], 10);
      
      if (priceRangeMatch[0].toLowerCase().includes('k')) {
        min *= 1000;
        max *= 1000;
      }
      
      filters.priceMin = min;
      filters.priceMax = max;
    }
    
    // Parse for year ranges
    const yearMatch = text.match(/\b(20\d{2}|19\d{2})\b/g);
    if (yearMatch && yearMatch.length === 1) {
      const year = parseInt(yearMatch[0], 10);
      // If it's likely a newer car, set as min year
      if (year > 2010) {
        filters.yearMin = year;
      } else {
        filters.yearMax = year;
      }
    } else if (yearMatch && yearMatch.length >= 2) {
      const years = yearMatch.map(y => parseInt(y, 10)).sort((a, b) => a - b);
      filters.yearMin = years[0];
      filters.yearMax = years[years.length - 1];
    }
    
    // Parse for features
    const featurePatterns = [
      { regex: /\b(leather|leather seats)\b/i, value: 'Leather Seats' },
      { regex: /\b(sunroof|moonroof)\b/i, value: 'Sunroof' },
      { regex: /\b(navigation|nav|gps)\b/i, value: 'Navigation' },
      { regex: /\b(bluetooth)\b/i, value: 'Bluetooth' },
      { regex: /\b(heated seats)\b/i, value: 'Heated Seats' },
      { regex: /\b(backup camera|rear camera|reverse camera)\b/i, value: 'Backup Camera' }
    ];
    
    const features: string[] = [];
    for (const pattern of featurePatterns) {
      if (pattern.regex.test(text)) {
        features.push(pattern.value);
      }
    }
    
    if (features.length > 0) {
      filters.features = features;
    }
    
    // Parse for fuel type
    const fuelTypePatterns = [
      { regex: /\b(electric|ev)\b/i, value: 'Electric' },
      { regex: /\b(hybrid)\b/i, value: 'Hybrid' },
      { regex: /\b(plug-in hybrid|phev)\b/i, value: 'Plug-in Hybrid' },
      { regex: /\b(gas|gasoline)\b/i, value: 'Gasoline' },
      { regex: /\b(diesel)\b/i, value: 'Diesel' }
    ];
    
    for (const pattern of fuelTypePatterns) {
      if (pattern.regex.test(text)) {
        filters.fuelType = pattern.value;
        break;
      }
    }
    
    // Parse for transmission
    const transmissionPatterns = [
      { regex: /\b(automatic|auto)\b/i, value: 'Automatic' },
      { regex: /\b(manual|stick shift)\b/i, value: 'Manual' },
      { regex: /\b(cvt)\b/i, value: 'CVT' }
    ];
    
    for (const pattern of transmissionPatterns) {
      if (pattern.regex.test(text)) {
        filters.transmission = pattern.value;
        break;
      }
    }
    
    // Parse for drivetrain
    const drivetrainPatterns = [
      { regex: /\b(awd|all wheel drive|all-wheel drive)\b/i, value: 'AWD' },
      { regex: /\b(4wd|4 wheel drive|four wheel drive|4x4)\b/i, value: '4WD' },
      { regex: /\b(fwd|front wheel drive|front-wheel drive)\b/i, value: 'FWD' },
      { regex: /\b(rwd|rear wheel drive|rear-wheel drive)\b/i, value: 'RWD' }
    ];
    
    for (const pattern of drivetrainPatterns) {
      if (pattern.regex.test(text)) {
        filters.drivetrain = pattern.value;
        break;
      }
    }
    
    return filters;
  };

  const handleSearch = () => {
    if (!query.trim()) return;
    
    // Parse the query to extract search parameters
    const filters = parseQuery(query);
    
    // Apply the filters
    onSearch(filters);
  };

  return (
    <div className="relative w-full">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe your dream car..."
          className="w-full px-6 py-5 text-lg rounded-full border-0 shadow-lg focus:ring-2 focus:ring-primary-500 transition-all duration-300 pr-16"
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button
          onClick={handleSearch}
          disabled={isSearching || !query.trim()}
          className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-primary-600 hover:bg-primary-700 text-white rounded-full p-3 transition-all duration-300 shadow-md"
          aria-label="Search"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>
      </div>
      
      {isSearching && (
        <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-80 rounded-full">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      )}
    </div>
  );
};

export default HomeSearchBox;
