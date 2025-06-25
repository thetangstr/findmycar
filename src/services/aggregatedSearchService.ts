import { Vehicle, SearchFilters } from '@/types';
import { searchEbayVehicles } from './ebayMotorsApi';
import batVehicleApi from './batVehicleApi';
import { getFeaturedVehicles } from './featuredVehiclesService';
import { getHemmingsListings } from './scraperService';

/**
 * Aggregated Search Service
 * Combines vehicle listings from multiple sources for comprehensive search results
 */

export interface SearchSource {
  name: string;
  enabled: boolean;
  search: (filters: SearchFilters) => Promise<Vehicle[]>;
  priority: number; // Higher priority sources appear first
}

/**
 * Configure all available search sources
 */
const SEARCH_SOURCES: SearchSource[] = [
  {
    name: 'Featured Vehicles',
    enabled: true,
    search: async (filters) => {
      const featured = getFeaturedVehicles();
      return applyFilters(featured, filters);
    },
    priority: 100
  },
  {
    name: 'eBay Motors',
    enabled: true,
    search: searchEbayVehicles,
    priority: 90
  },
  {
    name: 'Bring a Trailer',
    enabled: true,
    search: async (filters) => {
      try {
        return await batVehicleApi.searchBatVehicles(filters);
      } catch (error) {
        console.error('BAT search error:', error);
        return [];
      }
    },
    priority: 80
  },
  {
    name: 'Hemmings',
    enabled: true,
    search: async (filters) => {
      try {
        const hemmings = await getHemmingsListings();
        return applyFilters(hemmings, filters);
      } catch (error) {
        console.error('Hemmings search error:', error);
        return [];
      }
    },
    priority: 70
  },
  // Placeholder for future integrations
  {
    name: 'Cars.com',
    enabled: false, // Will enable when API is implemented
    search: async (filters) => searchCarsComPlaceholder(filters),
    priority: 85
  },
  {
    name: 'AutoTrader',
    enabled: false, // Will enable when API is implemented
    search: async (filters) => searchAutoTraderPlaceholder(filters),
    priority: 85
  }
];

/**
 * Search vehicles across all enabled sources
 */
export const searchAllSources = async (filters: SearchFilters): Promise<{
  results: Vehicle[];
  sourceResults: { source: string; count: number; error?: string }[];
  totalSources: number;
  enabledSources: number;
}> => {
  console.log('🔍 Starting aggregated search across all sources...');
  console.log('Search filters:', filters);
  
  const enabledSources = SEARCH_SOURCES.filter(source => source.enabled);
  const sourceResults: { source: string; count: number; error?: string }[] = [];
  const allResults: Vehicle[] = [];
  
  // Search each source in parallel for better performance
  const searchPromises = enabledSources.map(async (source) => {
    try {
      console.log(`🔍 Searching ${source.name}...`);
      const startTime = Date.now();
      
      const results = await source.search(filters);
      
      const duration = Date.now() - startTime;
      console.log(`✅ ${source.name}: Found ${results.length} results in ${duration}ms`);
      
      sourceResults.push({
        source: source.name,
        count: results.length
      });
      
      // Add source priority to each result for sorting
      const resultsWithPriority = results.map(vehicle => ({
        ...vehicle,
        _sourcePriority: source.priority,
        _sourceSearched: source.name
      }));
      
      return resultsWithPriority;
      
    } catch (error) {
      console.error(`❌ Error searching ${source.name}:`, error);
      sourceResults.push({
        source: source.name,
        count: 0,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      return [];
    }
  });
  
  // Wait for all searches to complete
  const searchResults = await Promise.all(searchPromises);
  
  // Combine and sort results
  for (const results of searchResults) {
    allResults.push(...results);
  }
  
  // Sort by source priority first, then by price
  allResults.sort((a, b) => {
    // First sort by source priority (higher priority first)
    const priorityDiff = (b as any)._sourcePriority - (a as any)._sourcePriority;
    if (priorityDiff !== 0) return priorityDiff;
    
    // Then sort by price (lower price first)
    return a.price - b.price;
  });
  
  // Remove temporary sorting properties
  const cleanResults = allResults.map(vehicle => {
    const { _sourcePriority, _sourceSearched, ...cleanVehicle } = vehicle as any;
    return cleanVehicle;
  });
  
  // Remove duplicates based on VIN or title similarity
  const deduplicatedResults = removeDuplicateVehicles(cleanResults);
  
  console.log(`🎉 Aggregated search complete: ${deduplicatedResults.length} unique results from ${enabledSources.length} sources`);
  
  return {
    results: deduplicatedResults,
    sourceResults,
    totalSources: SEARCH_SOURCES.length,
    enabledSources: enabledSources.length
  };
};

/**
 * Get a single vehicle by ID across all sources
 */
export const getVehicleByIdFromAllSources = async (id: string): Promise<Vehicle | null> => {
  console.log(`🔍 Searching for vehicle ID: ${id} across all sources`);
  
  const enabledSources = SEARCH_SOURCES.filter(source => source.enabled);
  
  for (const source of enabledSources) {
    try {
      // Search with empty filters to get all vehicles, then find by ID
      const allVehicles = await source.search({});
      const vehicle = allVehicles.find(v => v.id === id);
      
      if (vehicle) {
        console.log(`✅ Found vehicle in ${source.name}`);
        return vehicle;
      }
    } catch (error) {
      console.error(`Error searching ${source.name} for vehicle ${id}:`, error);
    }
  }
  
  console.log(`❌ Vehicle ${id} not found in any source`);
  return null;
};

/**
 * Apply search filters to a list of vehicles
 */
function applyFilters(vehicles: Vehicle[], filters: SearchFilters): Vehicle[] {
  return vehicles.filter(vehicle => {
    // Make filter
    if (filters.make && vehicle.make.toLowerCase() !== filters.make.toLowerCase()) {
      return false;
    }
    
    // Model filter
    if (filters.model && vehicle.model.toLowerCase() !== filters.model.toLowerCase()) {
      return false;
    }
    
    // Year filters
    if (filters.yearMin && vehicle.year < filters.yearMin) {
      return false;
    }
    if (filters.yearMax && vehicle.year > filters.yearMax) {
      return false;
    }
    
    // Price filters
    if (filters.priceMin && vehicle.price < filters.priceMin) {
      return false;
    }
    if (filters.priceMax && vehicle.price > filters.priceMax) {
      return false;
    }
    
    // Mileage filters
    if (filters.mileageMax && vehicle.mileage > filters.mileageMax) {
      return false;
    }
    
    // Text search in title and description
    if (filters.query) {
      const query = filters.query.toLowerCase();
      const searchableText = `${vehicle.make} ${vehicle.model} ${vehicle.year} ${vehicle.description}`.toLowerCase();
      if (!searchableText.includes(query)) {
        return false;
      }
    }
    
    return true;
  });
}

/**
 * Remove duplicate vehicles based on VIN or title similarity
 */
function removeDuplicateVehicles(vehicles: Vehicle[]): Vehicle[] {
  const seen = new Set<string>();
  const deduplicated: Vehicle[] = [];
  
  for (const vehicle of vehicles) {
    let uniqueKey: string;
    
    // Use VIN if available, otherwise use a combination of make/model/year/price
    if (vehicle.vin && vehicle.vin.length > 5) {
      uniqueKey = vehicle.vin;
    } else {
      uniqueKey = `${vehicle.make}-${vehicle.model}-${vehicle.year}-${vehicle.price}`;
    }
    
    if (!seen.has(uniqueKey)) {
      seen.add(uniqueKey);
      deduplicated.push(vehicle);
    } else {
      console.log(`🔄 Removed duplicate vehicle: ${vehicle.make} ${vehicle.model} ${vehicle.year}`);
    }
  }
  
  return deduplicated;
}

/**
 * Placeholder for Cars.com integration (to be implemented)
 */
async function searchCarsComPlaceholder(filters: SearchFilters): Promise<Vehicle[]> {
  // This would be replaced with actual Cars.com API integration
  console.log('Cars.com integration not yet implemented');
  return [];
}

/**
 * Placeholder for AutoTrader integration (to be implemented)
 */
async function searchAutoTraderPlaceholder(filters: SearchFilters): Promise<Vehicle[]> {
  // This would be replaced with actual AutoTrader API integration
  console.log('AutoTrader integration not yet implemented');
  return [];
}

/**
 * Get search source status for debugging
 */
export const getSearchSourceStatus = () => {
  return SEARCH_SOURCES.map(source => ({
    name: source.name,
    enabled: source.enabled,
    priority: source.priority
  }));
};

export default {
  searchAllSources,
  getVehicleByIdFromAllSources,
  getSearchSourceStatus
};