import React, { useState } from 'react';
import { SearchFilters as SearchFiltersType, Vehicle } from '@/types';

interface NaturalLanguageSearchProps {
  onSearch: (filters: SearchFiltersType) => void;
  onVehiclesFound?: (vehicles: Vehicle[]) => void;
}

const NaturalLanguageSearch: React.FC<NaturalLanguageSearchProps> = ({ onSearch, onVehiclesFound }) => {
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [useIntelligentSearch, setUseIntelligentSearch] = useState(true);

  // Function to parse natural language query into search filters
  const parseQuery = (text: string): SearchFiltersType => {
    const filters: SearchFiltersType = {};
    
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

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsProcessing(true);
    
    try {
      if (useIntelligentSearch) {
        // Use the intelligent search service for better results
        const { intelligentVehicleSearch } = await import('../services/intelligentSearchService');
        const vehicles = await intelligentVehicleSearch(query);
        
        if (onVehiclesFound && vehicles.length > 0) {
          onVehiclesFound(vehicles);
        } else {
          // Fallback to traditional filter parsing if no vehicles found
          const filters = parseQuery(query);
          onSearch(filters);
        }
      } else {
        // Use traditional filter parsing
        const filters = parseQuery(query);
        onSearch(filters);
      }
    } catch (error) {
      console.error('Error in intelligent search, falling back to traditional search:', error);
      // Fallback to traditional filter parsing
      const filters = parseQuery(query);
      onSearch(filters);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Natural Language Search</h2>
      <p className="text-gray-600 mb-4">
        Describe what you're looking for in plain English, e.g., "SUV under $40k with leather seats"
      </p>
      
      <div className="flex flex-col md:flex-row gap-3">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What kind of vehicle are you looking for?"
          className="input flex-grow"
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        
        <button
          onClick={handleSearch}
          disabled={isProcessing || !query.trim()}
          className="btn btn-primary whitespace-nowrap"
        >
          {isProcessing ? 'Processing...' : 'Search'}
        </button>
      </div>
      
      {/* Search mode toggle */}
      <div className="mt-4 flex items-center gap-4">
        <label className="flex items-center gap-2 text-sm text-gray-600">
          <input
            type="checkbox"
            checked={useIntelligentSearch}
            onChange={(e) => setUseIntelligentSearch(e.target.checked)}
            className="rounded border-gray-300"
          />
          Use AI-powered search (understands car terminology like "e46 zhp")
        </label>
      </div>
      
      {/* Example queries */}
      <div className="mt-4">
        <p className="text-sm text-gray-500 mb-2">
          {useIntelligentSearch ? 'Try these AI search examples:' : 'Try these basic examples:'}
        </p>
        <div className="flex flex-wrap gap-2">
          {(useIntelligentSearch ? [
            'e46 zhp',
            '964 turbo',
            'jza80 supra',
            'rs4 avant',
            'm3 e92',
            'porsche gt3',
            'bmw with zhp package'
          ] : [
            'SUV under $40k',
            'Toyota with leather seats',
            '2020 or newer sedan',
            'Electric vehicle with AWD',
            'Truck with backup camera'
          ]).map((example, index) => (
            <button
              key={index}
              onClick={() => {
                setQuery(example);
                setTimeout(handleSearch, 100);
              }}
              className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default NaturalLanguageSearch;
