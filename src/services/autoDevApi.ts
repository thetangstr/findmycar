import axios from 'axios';
import { Vehicle } from '@/types'; // Assuming you'll map the API response to your Vehicle type

const AUTO_DEV_API_BASE_URL = 'https://auto.dev/api';
const API_KEY = process.env.NEXT_PUBLIC_AUTO_DEV_API_KEY;

if (!API_KEY) {
  console.error('ERROR: Auto.dev API key is not defined. Please check your .env.local file.');
}

const autoDevApiClient = axios.create({
  baseURL: AUTO_DEV_API_BASE_URL,
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json',
  },
});

// Interface for the expected listing structure from auto.dev
// You'll need to adjust this based on the actual API response
interface AutoDevListing {
  // Example fields - replace with actual fields from auto.dev API
  id: string;
  vin: string;
  year: number;
  make: string;
  model: string;
  price: number;
  mileage?: number;
  images?: { url: string }[];
  // ... other fields
}

// Interface for the expected VIN details structure from auto.dev
interface AutoDevVinDetails {
  // Example fields - replace with actual fields
  vin: string;
  year: number;
  make: string;
  model: string;
  trim?: string;
  engine?: string;
  // ... other fields
}

/**
 * Transforms an AutoDevListing into your application's Vehicle type.
 * This function will need to be customized based on the actual API response.
 */
const transformListingToVehicle = (listing: AutoDevListing): Vehicle => {
  // Basic transformation, needs refinement based on actual API data
  return {
    id: listing.id || listing.vin, // Use VIN as ID if listing ID isn't present or suitable
    vin: listing.vin,
    make: listing.make,
    model: listing.model,
    year: listing.year,
    price: listing.price,
    mileage: listing.mileage || 0,
    exteriorColor: '', // Placeholder - get from listing if available
    interiorColor: '', // Placeholder
    fuelType: '',      // Placeholder
    transmission: '',  // Placeholder
    engine: '',        // Placeholder
    description: '',   // Placeholder
    features: [],      // Placeholder
    images: listing.images?.map(img => img.url) || [],
    location: '',      // Placeholder
    dealer: '',        // Placeholder
    listingDate: new Date().toISOString(), // Placeholder
    source: 'auto.dev',
    url: '',           // Placeholder - link to the listing if available
  };
};


/**
 * Fetches vehicle listings from auto.dev API.
 * Supports basic filtering if the API allows (e.g., by make, model, year).
 * Refer to auto.dev documentation for available filter parameters.
 * Example: https://auto.dev/api/listings
 */
export const fetchAutoDevListings = async (filters: Record<string, any> = {}): Promise<Vehicle[]> => {
  if (!API_KEY) {
    throw new Error('Auto.dev API key is not configured.');
  }
  try {
    // The auto.dev API might take filters as query parameters.
    // The provided example `https://auto.dev/api/listings?apikey=` suggests apikey in query.
    // However, we're using Bearer token. Check their docs for how to pass filters.
    // For now, assuming filters are passed as query params.
    const response = await autoDevApiClient.get<AutoDevListing[]>('/listings', { params: filters });
    
    // The actual response structure might be { records: [...] } or similar. Adjust accordingly.
    // For example, if data is in response.data.records:
    // const listings = response.data.records || response.data;
    const listings = response.data; 

    if (!Array.isArray(listings)) {
        console.error('Unexpected response format from auto.dev listings API:', listings);
        return [];
    }
    return listings.map(transformListingToVehicle);
  } catch (error) {
    console.error('Error fetching listings from auto.dev:', error);
    // Consider how to handle different error types (e.g., network error, 401, 404)
    if (axios.isAxiosError(error) && error.response) {
      console.error('API Error Data:', error.response.data);
      console.error('API Error Status:', error.response.status);
    }
    return []; // Return empty array or throw error as per your app's error handling strategy
  }
};

/**
 * Fetches detailed vehicle information by VIN from auto.dev API.
 * Example: https://auto.dev/api/vin/YOUR_VIN_HERE
 */
export const fetchAutoDevVinDetails = async (vin: string): Promise<AutoDevVinDetails | null> => {
  if (!API_KEY) {
    throw new Error('Auto.dev API key is not configured.');
  }
  if (!vin) {
    console.error('VIN must be provided to fetch details.');
    return null;
  }
  try {
    const response = await autoDevApiClient.get<AutoDevVinDetails>(`/vin/${vin}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching VIN details for ${vin} from auto.dev:`, error);
    if (axios.isAxiosError(error) && error.response) {
      console.error('API Error Data:', error.response.data);
      console.error('API Error Status:', error.response.status);
    }
    return null;
  }
};

export default {
  fetchAutoDevListings,
  fetchAutoDevVinDetails,
};
