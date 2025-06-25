import { Vehicle, SearchFilters } from '@/types';
import batVehicleApi from './batVehicleApi';

// Enhanced real vehicle data for fallback
const realVehicleData: Vehicle[] = [
  {
    id: '1',
    make: 'Toyota',
    model: 'RAV4',
    year: 2023,
    price: 32999,
    mileage: 5621,
    exteriorColor: 'Silver',
    interiorColor: 'Black',
    fuelType: 'Hybrid',
    transmission: 'Automatic',
    engine: '2.5L 4-Cylinder',
    vin: 'JTMWRREV4PD123456',
    description: 'Like-new Toyota RAV4 Hybrid with excellent fuel economy and low mileage. Features include Toyota Safety Sense 2.0, Apple CarPlay, Android Auto, and more.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', 'Heated Seats', 'Sunroof'],
    images: ['https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?q=80&w=1000'],
    location: 'San Francisco, CA',
    dealer: 'Bay Area Toyota',
    listingDate: '2025-05-15',
    source: 'Cars.com',
    url: '#',
    bodyStyle: 'SUV'
  },
  {
    id: '2',
    make: 'Honda',
    model: 'CR-V',
    year: 2022,
    price: 29500,
    mileage: 18750,
    exteriorColor: 'Blue',
    interiorColor: 'Gray',
    fuelType: 'Gasoline',
    transmission: 'CVT',
    engine: '1.5L Turbo 4-Cylinder',
    vin: '7FARW2H91NE012345',
    description: 'Well-maintained Honda CR-V with Honda Sensing suite of safety features. Spacious interior, excellent fuel economy, and plenty of cargo space.',
    features: ['Backup Camera', 'Bluetooth', 'Apple CarPlay', 'Android Auto'],
    images: ['https://images.unsplash.com/photo-1619976215249-1fc7c64ea6ac?q=80&w=1000'],
    location: 'Oakland, CA',
    dealer: 'Oakland Honda',
    listingDate: '2025-05-10',
    source: 'AutoTrader',
    url: '#',
    bodyStyle: 'SUV'
  },
  {
    id: '3',
    make: 'Ford',
    model: 'Escape',
    year: 2023,
    price: 27995,
    mileage: 12345,
    exteriorColor: 'White',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '1.5L EcoBoost',
    vin: '1FMCU9G61NUB78901',
    description: 'Ford Escape with SYNC 3, Ford Co-Pilot360, and EcoBoost engine for excellent fuel efficiency. Perfect family SUV with advanced safety features.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', 'Heated Seats'],
    images: ['https://images.unsplash.com/photo-1596816977488-6d3a54be4551?q=80&w=1000'],
    location: 'San Jose, CA',
    dealer: 'Stevens Creek Ford',
    listingDate: '2025-05-20',
    source: 'Facebook Marketplace',
    url: '#',
    bodyStyle: 'SUV'
  },
  {
    id: '4',
    make: 'Chevrolet',
    model: 'Equinox',
    year: 2022,
    price: 25995,
    mileage: 22150,
    exteriorColor: 'Red',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '1.5L Turbo',
    vin: '3GNAXUEV8NL234567',
    description: 'Chevrolet Equinox with Chevy Safety Assist, wireless Apple CarPlay and Android Auto. Spacious interior and excellent fuel economy.',
    features: ['Backup Camera', 'Bluetooth', 'Remote Start'],
    images: ['https://images.unsplash.com/photo-1568605117036-cfb8874a1a5c?q=80&w=1000'],
    location: 'Santa Clara, CA',
    dealer: 'Santa Clara Chevrolet',
    listingDate: '2025-04-28',
    source: 'Dealer Website',
    url: '#',
    bodyStyle: 'SUV'
  },
  {
    id: '5',
    make: 'BMW',
    model: '330i',
    year: 2021,
    price: 38500,
    mileage: 28000,
    exteriorColor: 'Black',
    interiorColor: 'Tan',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '2.0L Turbo 4-Cylinder',
    vin: 'WBA5R1C02M7B12345',
    description: 'Luxury BMW 330i with premium features and excellent performance. Well-maintained with full service history.',
    features: ['Navigation', 'Heated Seats', 'Sunroof', 'Premium Audio'],
    images: ['https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=2070'],
    location: 'Palo Alto, CA',
    dealer: 'BMW of Palo Alto',
    listingDate: '2025-05-01',
    source: 'eBay Motors',
    url: '#',
    bodyStyle: 'Sedan'
  }
];

/**
 * Fetch all vehicles from all available sources
 */
export const fetchVehicles = async (): Promise<Vehicle[]> => {
  try {
    console.log('🚗 Fetching vehicles from all sources...');
    
    // Use our new aggregated search service
    const { searchAllSources } = await import('./aggregatedSearchService');
    const searchResult = await searchAllSources({});
    
    console.log(`✅ Fetched ${searchResult.results.length} vehicles from ${searchResult.enabledSources} sources`);
    return searchResult.results;
    
  } catch (error) {
    console.error('❌ Error fetching vehicles, using fallback:', error);
    
    // Fallback: combine featured vehicles with mock data
    try {
      const { getFeaturedVehicles } = await import('./featuredVehiclesService');
      const featuredVehicles = getFeaturedVehicles();
      return [...featuredVehicles, ...realVehicleData];
    } catch (featuredError) {
      console.error('Failed to load featured vehicles:', featuredError);
      return realVehicleData;
    }
  }
};

/**
 * Fetch a single vehicle by ID from all sources
 */
export const fetchVehicleById = async (id: string): Promise<Vehicle | null> => {
  try {
    console.log(`🔍 Searching for vehicle ID: ${id}`);
    
    // Use our aggregated search service
    const { getVehicleByIdFromAllSources } = await import('./aggregatedSearchService');
    const vehicle = await getVehicleByIdFromAllSources(id);
    
    if (vehicle) {
      console.log(`✅ Found vehicle: ${vehicle.make} ${vehicle.model}`);
      return vehicle;
    }
    
    // Fallback to featured vehicles
    const { getFeaturedVehicles } = await import('./featuredVehiclesService');
    const featuredVehicles = getFeaturedVehicles();
    const featuredVehicle = featuredVehicles.find(v => v.id === id);
    if (featuredVehicle) {
      return featuredVehicle;
    }
    
    // Final fallback to mock data
    return realVehicleData.find(v => v.id === id) || null;
    
  } catch (error) {
    console.error('❌ Error fetching vehicle by ID:', error);
    // Final fallback to mock data
    return realVehicleData.find(v => v.id === id) || null;
  }
};

/**
 * Search vehicles with filters using our aggregated search service
 */
export const searchVehicles = async (filters: SearchFilters): Promise<Vehicle[]> => {
  console.log('🚗 Starting vehicle search with filters:', filters);
  
  try {
    // Use our new aggregated search service that combines multiple sources
    const { searchAllSources } = await import('./aggregatedSearchService');
    const searchResult = await searchAllSources(filters);
    
    console.log(`✅ Search complete: ${searchResult.results.length} vehicles from ${searchResult.enabledSources}/${searchResult.totalSources} sources`);
    console.log('Source breakdown:', searchResult.sourceResults);
    
    return searchResult.results;
  } catch (error) {
    console.error('❌ Error in aggregated search, falling back to mock data:', error);
    
    // Fallback to mock data if aggregated search fails
    return getFallbackSearchResults(filters);
  }
};

/**
 * Fallback search results when all APIs fail
 */
function getFallbackSearchResults(filters: SearchFilters): Vehicle[] {
  console.log('🔄 Using fallback search with mock data');
  
  // Use the static mock data and apply filters
  return realVehicleData.filter(vehicle => {
    // Apply the same filtering logic as the aggregated search
    if (filters.make && vehicle.make.toLowerCase() !== filters.make.toLowerCase()) {
      return false;
    }
    
    if (filters.model && vehicle.model.toLowerCase() !== filters.model.toLowerCase()) {
      return false;
    }
    
    if (filters.yearMin && vehicle.year < filters.yearMin) {
      return false;
    }
    
    if (filters.yearMax && vehicle.year > filters.yearMax) {
      return false;
    }
    
    if (filters.priceMin && vehicle.price < filters.priceMin) {
      return false;
    }
    
    if (filters.priceMax && vehicle.price > filters.priceMax) {
      return false;
    }
    
    if (filters.mileageMax && vehicle.mileage > filters.mileageMax) {
      return false;
    }
    
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

export default {
  fetchVehicles,
  fetchVehicleById,
  searchVehicles
};