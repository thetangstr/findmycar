import { Vehicle } from '@/types';
import batVehicleApi from './batVehicleApi';

// This service connects to real vehicle listings from Bring a Trailer
// We also have fallback mock data in case the listings are unavailable

// Sample data representing real vehicle listings with diverse sources
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
    url: '#'
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
    url: '#'
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
    url: '#'
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
    url: '#'
  },
  {
    id: '5',
    make: 'Hyundai',
    model: 'Tucson',
    year: 2023,
    price: 28750,
    mileage: 8923,
    exteriorColor: 'Gray',
    interiorColor: 'Black',
    fuelType: 'Hybrid',
    transmission: 'Automatic',
    engine: '1.6L Turbo Hybrid',
    vin: 'KM8JBCA19NU345678',
    description: 'Hyundai Tucson Hybrid with excellent fuel economy and Hyundai SmartSense safety features. Includes 10.25" touchscreen with navigation.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', 'Heated Seats', 'Panoramic Sunroof'],
    images: ['/images/vehicles/tucson-1.jpg', '/images/vehicles/tucson-2.jpg'],
    location: 'Fremont, CA',
    dealer: 'Fremont Hyundai',
    listingDate: '2025-05-18',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '6',
    make: 'Mazda',
    model: 'CX-5',
    year: 2023,
    price: 31250,
    mileage: 7650,
    exteriorColor: 'Soul Red Crystal',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '2.5L 4-Cylinder',
    vin: 'JM3KFBDM1P0456789',
    description: 'Mazda CX-5 with premium interior, i-Activsense safety features, and Mazda Connect infotainment. Known for excellent handling and upscale feel.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', 'Heated Seats', 'Sunroof', 'Leather Seats'],
    images: ['/images/vehicles/cx5-1.jpg', '/images/vehicles/cx5-2.jpg'],
    location: 'Palo Alto, CA',
    dealer: 'Palo Alto Mazda',
    listingDate: '2025-05-05',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '7',
    make: 'Subaru',
    model: 'Forester',
    year: 2022,
    price: 29995,
    mileage: 15780,
    exteriorColor: 'Green',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'CVT',
    engine: '2.5L 4-Cylinder',
    vin: 'JF2SKAUC7NH567890',
    description: 'Subaru Forester with standard all-wheel drive, EyeSight Driver Assist Technology, and excellent off-road capability. Perfect for outdoor adventures.',
    features: ['Backup Camera', 'Bluetooth', 'Apple CarPlay', 'Android Auto', 'Heated Seats'],
    images: ['/images/vehicles/forester-1.jpg', '/images/vehicles/forester-2.jpg'],
    location: 'San Rafael, CA',
    dealer: 'Marin Subaru',
    listingDate: '2025-04-22',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '8',
    make: 'Kia',
    model: 'Sportage',
    year: 2023,
    price: 27500,
    mileage: 9876,
    exteriorColor: 'Black',
    interiorColor: 'Gray',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '2.5L 4-Cylinder',
    vin: 'KNDPM3AC8P7678901',
    description: 'Kia Sportage with bold design, advanced driver assistance systems, and excellent warranty. Features include dual panoramic curved display.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', 'Heated Seats'],
    images: ['/images/vehicles/sportage-1.jpg', '/images/vehicles/sportage-2.jpg'],
    location: 'Daly City, CA',
    dealer: 'Daly City Kia',
    listingDate: '2025-05-12',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '9',
    make: 'Nissan',
    model: 'Rogue',
    year: 2022,
    price: 26995,
    mileage: 19250,
    exteriorColor: 'Silver',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'CVT',
    engine: '2.5L 4-Cylinder',
    vin: 'JN8AT3AA7NW789012',
    description: 'Nissan Rogue with Nissan Safety Shield 360, ProPILOT Assist, and excellent cargo space. Comfortable ride with good fuel economy.',
    features: ['Backup Camera', 'Bluetooth', 'Apple CarPlay', 'Android Auto'],
    images: ['/images/vehicles/rogue-1.jpg', '/images/vehicles/rogue-2.jpg'],
    location: 'Redwood City, CA',
    dealer: 'Redwood City Nissan',
    listingDate: '2025-04-30',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '10',
    make: 'Jeep',
    model: 'Cherokee',
    year: 2022,
    price: 32500,
    mileage: 17650,
    exteriorColor: 'Blue',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '3.2L V6',
    vin: '1C4PJMDX8ND890123',
    description: 'Jeep Cherokee with legendary off-road capability, Uconnect 5 infotainment, and advanced safety features. Perfect for adventure seekers.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', '4WD', 'Heated Seats'],
    images: ['https://images.unsplash.com/photo-1606016159991-880d187f6677?q=80&w=1000'],
    location: 'San Francisco, CA',
    dealer: 'SF Jeep',
    listingDate: '2025-05-02',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '11',
    make: 'Volkswagen',
    model: 'Tiguan',
    year: 2023,
    price: 30750,
    mileage: 6543,
    exteriorColor: 'Gray',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '2.0L Turbo 4-Cylinder',
    vin: '3VV2B7AX9PM901234',
    description: 'Volkswagen Tiguan with Digital Cockpit Pro, IQ.DRIVE driver assistance, and optional third-row seating. German engineering with excellent build quality.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', 'Heated Seats', 'Panoramic Sunroof'],
    images: ['/images/vehicles/tiguan-1.jpg', '/images/vehicles/tiguan-2.jpg'],
    location: 'Oakland, CA',
    dealer: 'East Bay VW',
    listingDate: '2025-05-14',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '12',
    make: 'BMW',
    model: 'X3',
    year: 2022,
    price: 45995,
    mileage: 12450,
    exteriorColor: 'Black',
    interiorColor: 'Brown',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '2.0L Turbo 4-Cylinder',
    vin: '5UXTY5C07N9012345',
    description: 'BMW X3 with premium features, excellent handling, and luxurious interior. Includes BMW iDrive 7.0 with 10.25" touchscreen and advanced driver assistance.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', 'Heated Seats', 'Panoramic Sunroof', 'Leather Seats'],
    images: ['/images/vehicles/x3-1.jpg', '/images/vehicles/x3-2.jpg'],
    location: 'San Francisco, CA',
    dealer: 'BMW of San Francisco',
    listingDate: '2025-05-08',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '13',
    make: 'Mercedes-Benz',
    model: 'GLC',
    year: 2022,
    price: 48750,
    mileage: 14320,
    exteriorColor: 'Silver',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '2.0L Turbo 4-Cylinder',
    vin: 'W1N0G8EB7NF123456',
    description: 'Mercedes-Benz GLC with MBUX infotainment system, premium materials, and excellent build quality. Includes advanced safety features and driver assistance.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', 'Heated Seats', 'Panoramic Sunroof', 'Leather Seats'],
    images: ['/images/vehicles/glc-1.jpg', '/images/vehicles/glc-2.jpg'],
    location: 'Palo Alto, CA',
    dealer: 'Palo Alto Mercedes-Benz',
    listingDate: '2025-04-25',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '14',
    make: 'Audi',
    model: 'Q5',
    year: 2022,
    price: 47500,
    mileage: 15670,
    exteriorColor: 'White',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '2.0L Turbo 4-Cylinder',
    vin: 'WA1BNAFY7N2234567',
    description: 'Audi Q5 with quattro all-wheel drive, virtual cockpit, and premium interior. Includes MMI touch display and advanced driver assistance systems.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', 'Heated Seats', 'Panoramic Sunroof', 'Leather Seats'],
    images: ['/images/vehicles/q5-1.jpg', '/images/vehicles/q5-2.jpg'],
    location: 'San Jose, CA',
    dealer: 'Audi San Jose',
    listingDate: '2025-05-01',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '15',
    make: 'Lexus',
    model: 'NX',
    year: 2023,
    price: 43995,
    mileage: 8765,
    exteriorColor: 'Gray',
    interiorColor: 'Black',
    fuelType: 'Hybrid',
    transmission: 'Automatic',
    engine: '2.5L 4-Cylinder Hybrid',
    vin: 'JTJDARDZ1P2345678',
    description: 'Lexus NX Hybrid with Lexus Safety System+ 3.0, premium interior, and excellent fuel economy. Includes 14" touchscreen with new Lexus Interface.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', 'Heated Seats', 'Panoramic Sunroof', 'Leather Seats'],
    images: ['/images/vehicles/nx-1.jpg', '/images/vehicles/nx-2.jpg'],
    location: 'San Rafael, CA',
    dealer: 'Marin Lexus',
    listingDate: '2025-05-17',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '16',
    make: 'Tesla',
    model: 'Model Y',
    year: 2023,
    price: 52990,
    mileage: 5432,
    exteriorColor: 'Red',
    interiorColor: 'White',
    fuelType: 'Electric',
    transmission: 'Automatic',
    engine: 'Electric',
    vin: '7SAYGDEF3PF456789',
    description: 'Tesla Model Y with Autopilot, excellent range, and spacious interior. Includes 15" touchscreen, over-the-air updates, and access to Tesla Supercharger network.',
    features: ['Backup Camera', 'Navigation', 'Heated Seats', 'Panoramic Sunroof'],
    images: ['/images/vehicles/modely-1.jpg', '/images/vehicles/modely-2.jpg'],
    location: 'Fremont, CA',
    dealer: 'Tesla Fremont',
    listingDate: '2025-05-19',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '17',
    make: 'Ford',
    model: 'Bronco Sport',
    year: 2023,
    price: 34750,
    mileage: 7890,
    exteriorColor: 'Blue',
    interiorColor: 'Gray',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '2.0L EcoBoost',
    vin: '3FMCR9B65PRD56789',
    description: 'Ford Bronco Sport with G.O.A.T. Modes (Goes Over Any Type of Terrain), SYNC 3, and excellent off-road capability. Perfect for adventure seekers.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', '4WD', 'Heated Seats'],
    images: ['/images/vehicles/broncosport-1.jpg', '/images/vehicles/broncosport-2.jpg'],
    location: 'Daly City, CA',
    dealer: 'Serramonte Ford',
    listingDate: '2025-05-11',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '18',
    make: 'Volvo',
    model: 'XC60',
    year: 2022,
    price: 46500,
    mileage: 13210,
    exteriorColor: 'Silver',
    interiorColor: 'Black',
    fuelType: 'Hybrid',
    transmission: 'Automatic',
    engine: '2.0L Turbo 4-Cylinder Hybrid',
    vin: 'YV4A22RL8N1678901',
    description: 'Volvo XC60 Recharge with plug-in hybrid technology, Scandinavian design, and advanced safety features. Includes Google built-in with Google Assistant.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', 'Heated Seats', 'Panoramic Sunroof', 'Leather Seats'],
    images: ['/images/vehicles/xc60-1.jpg', '/images/vehicles/xc60-2.jpg'],
    location: 'San Francisco, CA',
    dealer: 'Royal Volvo',
    listingDate: '2025-04-29',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '19',
    make: 'Mazda',
    model: 'CX-9',
    year: 2022,
    price: 38995,
    mileage: 16540,
    exteriorColor: 'Gray',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '2.5L Turbo 4-Cylinder',
    vin: 'JM3TCBDY1N0789012',
    description: 'Mazda CX-9 with three-row seating, premium interior, and excellent handling. Includes i-Activsense safety features and Mazda Connect infotainment.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', 'Heated Seats', 'Sunroof', 'Leather Seats'],
    images: ['/images/vehicles/cx9-1.jpg', '/images/vehicles/cx9-2.jpg'],
    location: 'Oakland, CA',
    dealer: 'Oakland Mazda',
    listingDate: '2025-05-03',
    source: 'Dealer Website',
    url: '#'
  },
  {
    id: '20',
    make: 'Acura',
    model: 'RDX',
    year: 2022,
    price: 42750,
    mileage: 14320,
    exteriorColor: 'White',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '2.0L Turbo 4-Cylinder',
    vin: '5J8TC2H59NL890123',
    description: 'Acura RDX with Super Handling All-Wheel Drive, True Touchpad Interface, and premium audio system. Includes AcuraWatch safety and driver assistance features.',
    features: ['Backup Camera', 'Bluetooth', 'Navigation', 'Heated Seats', 'Panoramic Sunroof', 'Leather Seats'],
    images: ['/images/vehicles/rdx-1.jpg', '/images/vehicles/rdx-2.jpg'],
    location: 'San Jose, CA',
    dealer: 'Acura of San Jose',
    listingDate: '2025-05-07',
    source: 'Dealer Website',
    url: '#'
  }
];

// Function to fetch all vehicles from Bring a Trailer listings
export const fetchVehicles = async (): Promise<Vehicle[]> => {
  try {
    // Get featured vehicles
    const { getFeaturedVehicles } = await import('./featuredVehiclesService');
    const featuredVehicles = getFeaturedVehicles();
    
    // Try to fetch from Bring a Trailer listings
    const batVehicles = await batVehicleApi.fetchBatVehicles();
    
    // Combine featured vehicles with BAT vehicles (featured first)
    return [...featuredVehicles, ...batVehicles];
  } catch (error) {
    console.error('Failed to fetch from BaT listings:', error);
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

// Function to fetch a single vehicle by ID from Bring a Trailer listings
export const fetchVehicleById = async (id: string): Promise<Vehicle | null> => {
  try {
    // First check if it's a featured vehicle
    if (id.startsWith('featured-')) {
      const { getFeaturedVehicles } = await import('./featuredVehiclesService');
      const featuredVehicles = getFeaturedVehicles();
      const featuredVehicle = featuredVehicles.find(v => v.id === id);
      if (featuredVehicle) {
        return featuredVehicle;
      }
    }
    
    // Try to fetch from Bring a Trailer listings
    const vehicle = await batVehicleApi.fetchBatVehicleById(id);
    if (vehicle) {
      return vehicle;
    }
    
    // Fallback to mock data if not found in BaT
    const mockVehicle = realVehicleData.find(v => v.id === id);
    return mockVehicle || null;
  } catch (error) {
    console.error('Failed to fetch vehicle by ID:', error);
    // Fallback to mock data if there's an error
    const mockVehicle = realVehicleData.find(v => v.id === id);
    return mockVehicle || null;
  }
};

// Function to search vehicles with filters using multiple real-world APIs
export const searchVehicles = async (filters: any): Promise<Vehicle[]> => {
  const results: Vehicle[] = [];
  const errors: string[] = [];
  
  // Set up the API keys for various services
  const carMDKey = process.env.NEXT_PUBLIC_CARMD_API_KEY || '';
  const carQueryKey = process.env.NEXT_PUBLIC_CARQUERY_API_KEY || '';
  const marketCheckKey = process.env.NEXT_PUBLIC_MARKETCHECK_API_KEY || '';
  const autoTempestKey = process.env.NEXT_PUBLIC_AUTOTEMPEST_API_KEY || '';
  
  try {
    // 1. Try searching using Bring a Trailer API
    console.log('Searching BaT listings...');
    try {
      const batResults = await batVehicleApi.searchBatVehicles(filters);
      results.push(...batResults);
      console.log(`Found ${batResults.length} results from BaT`);
    } catch (batError) {
      console.error('Error searching BaT:', batError);
      errors.push('BaT search failed');
    }
    
    // 2. Try searching using CarGurus API (if available)
    if (typeof window !== 'undefined') {
      console.log('Searching CarGurus...');
      try {
        const response = await fetch(`https://www.cargurus.com/Cars/searchResults.action?${new URLSearchParams({
          zip: filters.zipCode || '94105',
          inventorySearchWidgetType: 'AUTO',
          sortDir: 'ASC',
          sourceContext: 'carGurusHomePageModel',
          entitySelectingHelper: 'selectedEntity',
          sortType: 'PRICE',
          newUsed: filters.condition || 'used',
          ...(filters.make ? { 'entitySelectingHelper.selectedEntity': filters.make } : {}),
          ...(filters.model ? { 'entitySelectingHelper.selectedEntity2': filters.model } : {}),
          ...(filters.yearMin ? { minYear: filters.yearMin } : {}),
          ...(filters.yearMax ? { maxYear: filters.yearMax } : {}),
          ...(filters.priceMin ? { minPrice: filters.priceMin } : {}),
          ...(filters.priceMax ? { maxPrice: filters.priceMax } : {}),
          ...(filters.mileageMax ? { maxMileage: filters.mileageMax } : {}),
        })}`)
        
        if (response.ok) {
          const data = await response.text();
          // This would need proper HTML parsing in a real app
          const carGurusCount = data.match(/showing ([0-9,]+) matches/);
          console.log(`CarGurus search returned data (matches: ${carGurusCount?.[1] || 'unknown'})`);
        }
      } catch (carGurusError) {
        console.error('Error searching CarGurus:', carGurusError);
        errors.push('CarGurus search failed');
      }
    }
    
    // 3. Try searching using Cars.com API (if available)
    if (typeof window !== 'undefined') {
      console.log('Searching Cars.com...');
      try {
        const response = await fetch(`https://www.cars.com/shopping/results/?${new URLSearchParams({
          stock_type: filters.condition === 'new' ? 'new' : 'used',
          makes: filters.make ? [filters.make].join(',') : '',
          models: filters.model ? [filters.model].join(',') : '',
          list_price_min: filters.priceMin ? String(filters.priceMin) : '',
          list_price_max: filters.priceMax ? String(filters.priceMax) : '',
          maximum_distance: 'all',
          zip: filters.zipCode || '94105',
        })}`)
        
        if (response.ok) {
          const data = await response.text();
          // This would need proper HTML parsing in a real app
          const carsCount = data.match(/([0-9,]+) matches/);
          console.log(`Cars.com search returned data (matches: ${carsCount?.[1] || 'unknown'})`);
        }
      } catch (carsError) {
        console.error('Error searching Cars.com:', carsError);
        errors.push('Cars.com search failed');
      }
    }
    
    // 4. Try searching using AutoTempest API (if we have an API key)
    if (autoTempestKey) {
      console.log('Searching AutoTempest...');
      try {
        const response = await fetch(`https://api.autotempest.com/api/search/autos?${new URLSearchParams({
          apiKey: autoTempestKey,
          make: filters.make || '',
          model: filters.model || '',
          minYear: filters.yearMin ? String(filters.yearMin) : '',
          maxYear: filters.yearMax ? String(filters.yearMax) : '',
          minPrice: filters.priceMin ? String(filters.priceMin) : '',
          maxPrice: filters.priceMax ? String(filters.priceMax) : '',
          maxMileage: filters.mileageMax ? String(filters.mileageMax) : '',
          zip: filters.zipCode || '94105',
        })}`)
        
        if (response.ok) {
          const data = await response.json();
          const autoTempestResults = data.results.map((item: any) => ({
            id: `at-${item.id}`,
            make: item.make,
            model: item.model,
            year: parseInt(item.year, 10),
            price: parseInt(item.price.replace(/[^0-9]/g, ''), 10),
            mileage: parseInt(item.mileage.replace(/[^0-9]/g, ''), 10),
            exteriorColor: item.exteriorColor || 'Unknown',
            interiorColor: item.interiorColor || 'Unknown',
            fuelType: item.fuelType || 'Gasoline',
            transmission: item.transmission || 'Automatic',
            engine: item.engine || '',
            vin: item.vin || '',
            description: item.description || `${item.year} ${item.make} ${item.model}`,
            features: item.features || [],
            images: item.images || [],
            location: item.location || '',
            dealer: item.dealer || 'Private Seller',
            listingDate: item.listingDate || new Date().toISOString().split('T')[0],
            source: 'AutoTempest',
            url: item.url || '#',
          }));
          
          results.push(...autoTempestResults);
          console.log(`Found ${autoTempestResults.length} results from AutoTempest`);
        }
      } catch (autoTempestError) {
        console.error('Error searching AutoTempest:', autoTempestError);
        errors.push('AutoTempest search failed');
      }
    }
    
    // If we got no results from real APIs, fall back to filtering our mock data
    if (results.length === 0) {
      console.warn('No results from real APIs, falling back to mock data');
      const mockResults = realVehicleData.filter(vehicle => {
        // Check make
        if (filters.make && vehicle.make.toLowerCase() !== filters.make.toLowerCase()) {
          return false;
        }
      
        // Check model
        if (filters.model && !vehicle.model.toLowerCase().includes(filters.model.toLowerCase())) {
          return false;
        }
      
        // Check year range
        if (filters.yearMin && vehicle.year < filters.yearMin) {
          return false;
        }
        if (filters.yearMax && vehicle.year > filters.yearMax) {
          return false;
        }
      
        // Check price range
        if (filters.priceMin && vehicle.price < filters.priceMin) {
          return false;
        }
        if (filters.priceMax && vehicle.price > filters.priceMax) {
          return false;
        }
      
        // Check mileage range
        if (filters.mileageMin && vehicle.mileage < filters.mileageMin) {
          return false;
        }
        if (filters.mileageMax && vehicle.mileage > filters.mileageMax) {
          return false;
        }
      
        // Check fuel type
        if (filters.fuelType && vehicle.fuelType !== filters.fuelType) {
          return false;
        }
      
        // Check transmission
        if (filters.transmission && vehicle.transmission !== filters.transmission) {
          return false;
        }
      
        // Check body type (using model as proxy since we don't have bodyType in our data)
        if (filters.bodyType) {
          const suvModels = ['RAV4', 'CR-V', 'Escape', 'Equinox', 'Tucson', 'CX-5', 'Forester', 'Sportage', 'Rogue', 'Cherokee', 'Tiguan', 'X3', 'GLC', 'Q5', 'NX', 'Model Y', 'Bronco Sport', 'XC60', 'CX-9', 'RDX'];
          const sedanModels = ['Camry', 'Accord', 'Civic', 'Corolla', 'Altima', 'Sonata', 'Elantra', 'Mazda3', '3 Series', 'C-Class', 'A4', 'ES', 'Model 3'];
          
          if (filters.bodyType === 'SUV' && !suvModels.includes(vehicle.model)) {
            return false;
          }
          if (filters.bodyType === 'Sedan' && !sedanModels.includes(vehicle.model)) {
            return false;
          }
        }
      
        // Check features
        if (filters.features && filters.features.length > 0) {
          for (const feature of filters.features) {
            if (!vehicle.features.includes(feature)) {
              return false;
            }
          }
        }
      
        // Check exterior color
        if (filters.exteriorColor && vehicle.exteriorColor !== filters.exteriorColor) {
          return false;
        }
      
        // Check interior color
        if (filters.interiorColor && vehicle.interiorColor !== filters.interiorColor) {
          return false;
        }
      
        // Check text query
        if (filters.query) {
          const query = filters.query.toLowerCase();
          const searchableText = `${vehicle.make} ${vehicle.model} ${vehicle.year} ${vehicle.description} ${vehicle.features.join(' ')}`.toLowerCase();
          
          if (!searchableText.includes(query)) {
            return false;
          }
        }
        
        return true;
      });
      
      return mockResults;
    }
    
    // Return real API results
    return results;
  } catch (error) {
    console.error('Unexpected error in vehicle search:', error);
    return realVehicleData; // Last-resort fallback
  }
};

export default {
  fetchVehicles,
  fetchVehicleById,
  searchVehicles
};
