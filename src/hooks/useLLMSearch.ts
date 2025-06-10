import { useState, useCallback } from 'react';
import { Vehicle } from '@/types';
import axios from 'axios';

// Transform auto.dev API response to our Vehicle type
const transformAutoDevToVehicle = (listing: any): Vehicle => {
  // Extract all possible image URLs from various API response formats
  const extractImageUrls = (item: any): string[] => {
    const urls: string[] = [];
    
    // Log the structure for debugging
    console.log('[DEBUG] Extracting images from listing with keys:', Object.keys(item));
    
    // Pre-filter function to immediately filter out problematic domains
    const isValidImageUrl = (url: string): boolean => {
      if (!url) return false;
      
      // Skip ALL bringatrailer.com domains and subdomains
      if (url.includes('bringatrailer.com')) {
        console.log(`[DEBUG] Filtering out bringatrailer.com URL: ${url}`);
        return false;
      }
      
      // Skip placeholder.com URLs which can also fail
      if (url.includes('placeholder.com')) {
        console.log(`[DEBUG] Filtering out placeholder.com URL: ${url}`);
        return false;
      }
      
      // Skip any other known problematic domains
      const problematicDomains = ['invalid-cdn.com', 'broken-images.net'];
      for (const domain of problematicDomains) {
        if (url.includes(domain)) {
          console.log(`[DEBUG] Filtering out problematic domain: ${url}`);
          return false;
        }
      }
      
      // Validate URL format
      try {
        new URL(url);
        return true;
      } catch (e) {
        console.error(`[DEBUG] Invalid URL format: ${url}`);
        return false;
      }
    };
    
    // Check all possible image URL locations in order of preference
    if (Array.isArray(item.photoUrls) && item.photoUrls.length > 0) {
      console.log('[DEBUG] Found photoUrls array with length:', item.photoUrls.length);
      const validPhotoUrls = item.photoUrls.filter(isValidImageUrl);
      urls.push(...validPhotoUrls);
    }
    
    if (item.primaryPhotoUrl && isValidImageUrl(item.primaryPhotoUrl)) {
      console.log('[DEBUG] Found valid primaryPhotoUrl:', item.primaryPhotoUrl);
      urls.push(item.primaryPhotoUrl);
    }
    
    if (item.thumbnailUrl && isValidImageUrl(item.thumbnailUrl)) {
      console.log('[DEBUG] Found valid thumbnailUrl:', item.thumbnailUrl);
      urls.push(item.thumbnailUrl);
    }
    
    if (item.thumbnailUrlLarge && isValidImageUrl(item.thumbnailUrlLarge)) {
      console.log('[DEBUG] Found valid thumbnailUrlLarge:', item.thumbnailUrlLarge);
      urls.push(item.thumbnailUrlLarge);
    }
    
    if (item.media && Array.isArray(item.media.photo_links)) {
      console.log('[DEBUG] Found media.photo_links array with length:', item.media.photo_links.length);
      const validPhotoLinks = item.media.photo_links.filter(isValidImageUrl);
      urls.push(...validPhotoLinks);
    }
    
    if (Array.isArray(item.photos)) {
      console.log('[DEBUG] Found photos array with length:', item.photos.length);
      const photoUrls = item.photos.map((p: any) => p.url).filter(isValidImageUrl);
      urls.push(...photoUrls);
    }
    
    // Filter out duplicates
    const uniqueUrls = [...new Set(urls)];
    console.log('[DEBUG] Extracted unique valid image URLs:', uniqueUrls);
    
    // Don't provide external fallback URLs - our VehicleCard component will handle
    // the fallback with a text-based display if no images are available
    return uniqueUrls;
  };
  
  // Try to parse numeric values safely
  const parseNumeric = (value: any, defaultValue: number = 0): number => {
    if (typeof value === 'number') return value;
    if (typeof value === 'string') {
      // Remove currency symbols, commas, etc.
      const cleaned = value.replace(/[^0-9.]/g, '');
      const parsed = parseFloat(cleaned);
      return isNaN(parsed) ? defaultValue : parsed;
    }
    return defaultValue;
  };
  
  return {
    id: listing.id || `autodev-${Math.random().toString(36).substring(2, 10)}`,
    make: listing.make || 'Unknown',
    model: listing.model || 'Unknown',
    year: parseNumeric(listing.year, new Date().getFullYear()),
    price: parseNumeric(listing.priceUnformatted || listing.price, 0),
    mileage: parseNumeric(listing.mileageUnformatted || listing.mileage, 0),
    exteriorColor: listing.exterior_color || listing.displayColor || 'Unknown',
    interiorColor: listing.interior_color || 'Unknown',
    fuelType: listing.fuel_type || 'Unknown',
    transmission: listing.transmission || 'Unknown',
    engine: listing.engine_description || 'Unknown',
    vin: listing.vin || 'Unknown',
    description: listing.description || `${listing.year || ''} ${listing.make || ''} ${listing.model || ''}`,
    features: listing.features || [],
    images: extractImageUrls(listing),
    location: listing.city && listing.state ? `${listing.city}, ${listing.state}` : 
             (listing.dealer && listing.dealer.city ? `${listing.dealer.city}, ${listing.dealer.state}` : 'Unknown'),
    dealer: listing.dealerName || (listing.dealer && listing.dealer.name ? listing.dealer.name : 'Unknown'),
    listingDate: listing.createdAt || listing.listed_date || new Date().toISOString(),
    source: 'auto.dev',
    url: listing.vdpUrl || listing.clickoffUrl || '',
  };
};

// LLM-based search function using direct calls to auto.dev API
const searchWithAutoDevAPI = async (query: string): Promise<Vehicle[]> => {
  try {
    console.log('[DEBUG] Starting auto.dev API search with query:', query);
    
    // Get the API key from environment variable
    const apiKey = process.env.NEXT_PUBLIC_AUTO_DEV_API_KEY;
    
    if (!apiKey) {
      console.error('[DEBUG] Auto.dev API key is missing');
      throw new Error('Auto.dev API key is not configured');
    }
    
    // Direct API call to auto.dev without using our proxy
    const response = await axios.get('https://auto.dev/api/listings', {
      params: {
        // You can add auto.dev filter parameters here based on the query
        // For now, we'll just get a batch of vehicles
        limit: 50,
      },
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('[DEBUG] Auto.dev API response received:', {
      status: response.status,
      hasData: !!response.data,
      hasListings: !!(response.data && response.data.listings),
      listingsCount: response.data?.listings?.length || 0,
      firstListing: response.data?.listings?.[0] ? {
        id: response.data.listings[0].id,
        make: response.data.listings[0].make,
        model: response.data.listings[0].model,
        hasImages: !!(response.data.listings[0].photoUrls || response.data.listings[0].primaryPhotoUrl),
        imageUrlSample: response.data.listings[0].photoUrls?.[0] || response.data.listings[0].primaryPhotoUrl
      } : 'No listings'
    });
    
    if (!response.data || !response.data.listings) {
      console.error('[DEBUG] Unexpected auto.dev API response format:', response.data);
      return [];
    }
    
    // Transform the auto.dev listings to our Vehicle format
    const vehicles = response.data.listings.map((listing: any) => {
      const vehicle = transformAutoDevToVehicle(listing);
      console.log('[DEBUG] Transformed vehicle image URLs:', vehicle.images);
      return vehicle;
    });
    
    console.log('[DEBUG] Total vehicles after transformation:', vehicles.length);
    
    // Apply local filtering based on the natural language query
    const filteredVehicles = filterVehiclesByNaturalLanguage(query, vehicles);
    console.log('[DEBUG] Vehicles after filtering:', filteredVehicles.length);
    
    return filteredVehicles;
  } catch (error) {
    console.error('[DEBUG] Error fetching from auto.dev API:', error);
    throw error;
  }
};

// Basic natural language filtering function
const filterVehiclesByNaturalLanguage = (query: string, vehicles: Vehicle[]): Vehicle[] => {
  // Convert query to lowercase for case-insensitive matching
  const lowerQuery = query.toLowerCase();
  
  // Keywords that might indicate user preferences
  const affordabilityTerms = ['cheap', 'affordable', 'budget', 'inexpensive', 'low price', 'economical'];
  const luxuryTerms = ['luxury', 'premium', 'high-end', 'expensive', 'top-tier'];
  const familyTerms = ['family', 'spacious', 'kids', 'room', 'safe', 'safety'];
  const efficiencyTerms = ['efficient', 'fuel economy', 'gas mileage', 'hybrid', 'electric', 'eco'];
  const performanceTerms = ['fast', 'quick', 'powerful', 'performance', 'sporty', 'speed'];
  
  // Score each vehicle based on how well it matches the query
  const scoredVehicles = vehicles.map(vehicle => {
    let score = 0;
    
    // Direct make/model matching
    if (vehicle.make.toLowerCase().includes(lowerQuery)) score += 10;
    if (vehicle.model.toLowerCase().includes(lowerQuery)) score += 10;
    
    // Description matching
    if (vehicle.description && vehicle.description.toLowerCase().includes(lowerQuery)) score += 5;
    
    // Feature matching
    if (vehicle.features && vehicle.features.length) {
      vehicle.features.forEach(feature => {
        if (feature.toLowerCase().includes(lowerQuery)) score += 3;
      });
    }
    
    // Semantic matching based on keywords
    const vehicleDetails = `${vehicle.make} ${vehicle.model} ${vehicle.description} ${vehicle.features ? vehicle.features.join(' ') : ''} ${vehicle.fuelType} ${vehicle.transmission}`.toLowerCase();
    
    // Check for affordability preferences
    if (affordabilityTerms.some(term => lowerQuery.includes(term))) {
      // Lower price gets higher score
      score += Math.max(0, 50000 - vehicle.price) / 5000;
    }
    
    // Check for luxury preferences
    if (luxuryTerms.some(term => lowerQuery.includes(term))) {
      // Higher price and premium brands get higher score
      const premiumBrands = ['bmw', 'audi', 'mercedes', 'lexus', 'tesla'];
      if (premiumBrands.includes(vehicle.make.toLowerCase())) score += 10;
      score += vehicle.price / 10000;
    }
    
    // Check for family-friendly preferences
    if (familyTerms.some(term => lowerQuery.includes(term))) {
      // SUVs and vehicles with safety features get higher score
      const familyModels = ['suv', 'minivan', 'crossover', 'equinox', 'tucson', 'q5'];
      if (familyModels.some(model => vehicle.model.toLowerCase().includes(model))) score += 10;
      if (vehicleDetails.includes('safety')) score += 5;
      if (vehicleDetails.includes('spacious')) score += 5;
    }
    
    // Check for efficiency preferences
    if (efficiencyTerms.some(term => lowerQuery.includes(term))) {
      // Hybrid/electric vehicles get higher score
      if (vehicle.fuelType && (vehicle.fuelType.toLowerCase() === 'hybrid' || vehicle.fuelType.toLowerCase() === 'electric')) score += 15;
      // Lower mileage gets higher score for efficiency
      score += Math.max(0, 50000 - vehicle.mileage) / 5000;
    }
    
    // Check for performance preferences
    if (performanceTerms.some(term => lowerQuery.includes(term))) {
      // Sports cars and performance-oriented vehicles get higher score
      const performanceModels = ['3 series', 'model 3', 'mustang', 'corvette', 'camaro'];
      if (performanceModels.some(model => vehicle.model.toLowerCase().includes(model))) score += 10;
      if (vehicleDetails.includes('turbo')) score += 5;
      if (vehicleDetails.includes('v8') || vehicleDetails.includes('v6')) score += 5;
    }
    
    return { vehicle, score };
  });
  
  // Sort by score (highest first) and return just the vehicles
  return scoredVehicles
    .sort((a, b) => b.score - a.score)
    .map(item => item.vehicle);
};

export const useLLMSearch = (vehicles: Vehicle[]) => {
  const [results, setResults] = useState<Vehicle[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const searchWithLLM = useCallback(async (query: string) => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    
    setIsSearching(true);
    setError(null);
    
    try {
      // Use the new intelligent search service
      const { intelligentVehicleSearch } = await import('../services/intelligentSearchService');
      const searchResults = await intelligentVehicleSearch(query);
      
      setResults(searchResults);
      
      // If no results from intelligent search, fallback to local filtering
      if (searchResults.length === 0 && vehicles.length > 0) {
        console.log('[LLMSearch] No intelligent results, falling back to local filtering');
        const localResults = filterVehiclesByNaturalLanguage(query, vehicles);
        setResults(localResults);
      }
    } catch (err) {
      console.error('LLM search error:', err);
      setError('Failed to perform search. Please try again.');
      
      // On error, fallback to local filtering
      if (vehicles.length > 0) {
        try {
          const localResults = filterVehiclesByNaturalLanguage(query, vehicles);
          setResults(localResults);
          setError('Using local results due to search error.');
        } catch (localErr) {
          console.error('Local filtering error:', localErr);
        }
      }
    } finally {
      setIsSearching(false);
    }
  }, [vehicles]);
  
  return {
    results,
    isSearching,
    error,
    searchWithLLM
  };
};

export default useLLMSearch;
