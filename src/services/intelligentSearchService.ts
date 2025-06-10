import { Vehicle } from '@/types';
import { GoogleGenerativeAI } from '@google/generative-ai';

// Initialize Gemini AI
const geminiApiKey = process.env.NEXT_PUBLIC_GEMINI_API_KEY;
let genAI: GoogleGenerativeAI | null = null;

if (geminiApiKey && geminiApiKey !== 'your-gemini-api-key-here') {
  genAI = new GoogleGenerativeAI(geminiApiKey);
} else {
  console.warn('Gemini API key not configured, using fallback search');
}

// Car terminology mapping for intelligent search
const CAR_TERMINOLOGY = {
  // BMW specific
  'e46': 'BMW 3 Series E46 (1998-2006)',
  'e92': 'BMW 3 Series E92 (2006-2013)',
  'e90': 'BMW 3 Series E90 (2005-2012)',
  'f30': 'BMW 3 Series F30 (2012-2019)',
  'zhp': 'BMW ZHP Performance Package',
  'm3': 'BMW M3',
  'm5': 'BMW M5',
  'e39': 'BMW 5 Series E39 (1996-2003)',
  'e60': 'BMW 5 Series E60 (2003-2010)',
  
  // Porsche specific
  '911': 'Porsche 911',
  '930': 'Porsche 911 Turbo (930)',
  '964': 'Porsche 911 (964)',
  '993': 'Porsche 911 (993)',
  '996': 'Porsche 911 (996)',
  '997': 'Porsche 911 (997)',
  '991': 'Porsche 911 (991)',
  'turbo s': 'Porsche Turbo S',
  'gt3': 'Porsche GT3',
  'carrera': 'Porsche Carrera',
  
  // Mercedes specific
  'amg': 'Mercedes-AMG',
  'c63': 'Mercedes-Benz C63 AMG',
  'e63': 'Mercedes-Benz E63 AMG',
  's63': 'Mercedes-Benz S63 AMG',
  'sl55': 'Mercedes-Benz SL55 AMG',
  
  // Audi specific
  'rs4': 'Audi RS4',
  'rs6': 'Audi RS6',
  's4': 'Audi S4',
  's6': 'Audi S6',
  'quattro': 'Audi Quattro all-wheel drive',
  
  // Toyota/Lexus specific
  'jza80': 'Toyota Supra JZA80 (1993-2002)',
  'ae86': 'Toyota Corolla AE86 (1983-1987)',
  'mr2': 'Toyota MR2',
  'ls400': 'Lexus LS400',
  'is300': 'Lexus IS300',
  
  // Honda specific
  'integra type r': 'Honda Integra Type R',
  'civic type r': 'Honda Civic Type R',
  's2000': 'Honda S2000',
  'nsx': 'Honda NSX',
  
  // Ford specific
  'gt350': 'Ford Mustang Shelby GT350',
  'gt500': 'Ford Mustang Shelby GT500',
  'focus rs': 'Ford Focus RS',
  
  // Chevrolet specific
  'z06': 'Chevrolet Corvette Z06',
  'zr1': 'Chevrolet Corvette ZR1',
  'ss': 'Chevrolet SS',
  
  // General terms
  'manual': 'manual transmission',
  'stick': 'manual transmission',
  'auto': 'automatic transmission',
  'awd': 'all-wheel drive',
  'rwd': 'rear-wheel drive',
  'fwd': 'front-wheel drive',
  'turbo': 'turbocharged',
  'supercharged': 'supercharged',
  'hybrid': 'hybrid engine',
  'electric': 'electric vehicle',
  'convertible': 'convertible top',
  'hardtop': 'hardtop roof',
  'coupe': 'two-door coupe',
  'sedan': 'four-door sedan',
  'wagon': 'station wagon',
  'suv': 'sport utility vehicle',
  'crossover': 'crossover SUV'
};

/**
 * Translates car slang/terminology to full descriptions using Gemini AI
 */
export const translateCarTerminology = async (query: string): Promise<string> => {
  if (!genAI) {
    // Fallback to local terminology mapping
    let expandedQuery = query.toLowerCase();
    
    for (const [term, meaning] of Object.entries(CAR_TERMINOLOGY)) {
      if (expandedQuery.includes(term.toLowerCase())) {
        expandedQuery = expandedQuery.replace(
          new RegExp(term.toLowerCase(), 'gi'), 
          meaning
        );
      }
    }
    
    return expandedQuery;
  }
  
  try {
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    
    const prompt = `You are an expert automotive assistant. The user is searching for vehicles with this query: "${query}"

Please interpret this query and return a structured search interpretation that includes:
1. The specific car make and model they're looking for
2. Any generation codes (like E46, 964, etc.) expanded to full descriptions
3. Any performance packages or trim levels mentioned
4. The year range if specified or implied
5. Any specific features or characteristics they want

If the query contains automotive slang or abbreviations, expand them. For example:
- "e46 zhp" should become "BMW 3 Series E46 (1998-2006) with ZHP Performance Package"
- "964 turbo" should become "Porsche 911 964 Turbo (1989-1994)"
- "jza80 supra" should become "Toyota Supra JZA80 (1993-2002)"

Return your response as a JSON object with these fields:
{
  "expandedQuery": "The full expanded search description",
  "make": "Specific car manufacturer (if mentioned)",
  "model": "Specific car model (if mentioned)", 
  "yearMin": year number or null,
  "yearMax": year number or null,
  "keywords": ["array", "of", "important", "search", "terms"]
}

User query: "${query}"`;

    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    
    try {
      const parsed = JSON.parse(text);
      return parsed.expandedQuery || query;
    } catch (parseError) {
      console.error('Error parsing Gemini response:', parseError);
      return text || query;
    }
  } catch (error) {
    console.error('Error calling Gemini API:', error);
    // Fallback to local terminology mapping
    let expandedQuery = query.toLowerCase();
    
    for (const [term, meaning] of Object.entries(CAR_TERMINOLOGY)) {
      if (expandedQuery.includes(term.toLowerCase())) {
        expandedQuery = expandedQuery.replace(
          new RegExp(term.toLowerCase(), 'gi'), 
          meaning
        );
      }
    }
    
    return expandedQuery;
  }
};

/**
 * Intelligent search that combines AI interpretation with multiple data sources
 */
export const intelligentVehicleSearch = async (query: string): Promise<Vehicle[]> => {
  console.log('[IntelligentSearch] Starting search for:', query);
  
  // First, interpret the query with AI
  const expandedQuery = await translateCarTerminology(query);
  console.log('[IntelligentSearch] Expanded query:', expandedQuery);
  
  // Initialize results array
  let allResults: Vehicle[] = [];
  
  try {
    // Search BAT listings (our curated data)
    const { searchBatVehicles } = await import('./batVehicleApi');
    const batResults = await searchBatVehicles({ query: expandedQuery });
    console.log('[IntelligentSearch] BAT results:', batResults.length);
    allResults.push(...batResults);
    
    // Search auto.dev API if available
    if (process.env.NEXT_PUBLIC_AUTO_DEV_API_KEY) {
      try {
        const autoDevResults = await searchAutoDevWithIntelligence(expandedQuery);
        console.log('[IntelligentSearch] Auto.dev results:', autoDevResults.length);
        allResults.push(...autoDevResults);
      } catch (error) {
        console.error('[IntelligentSearch] Auto.dev search failed:', error);
      }
    }
    
    // Search local vehicle API as fallback
    const { searchVehicles } = await import('./vehicleApi');
    const localResults = await searchVehicles({ query: expandedQuery });
    console.log('[IntelligentSearch] Local results:', localResults.length);
    allResults.push(...localResults);
    
  } catch (error) {
    console.error('[IntelligentSearch] Error during search:', error);
  }
  
  // Remove duplicates based on VIN or ID
  const uniqueResults = allResults.filter((vehicle, index, self) => {
    return index === self.findIndex(v => v.id === vehicle.id || v.vin === vehicle.vin);
  });
  
  // Score and sort results by relevance
  const scoredResults = scoreVehiclesByRelevance(query, expandedQuery, uniqueResults);
  
  console.log('[IntelligentSearch] Final results:', scoredResults.length);
  return scoredResults;
};

/**
 * Search auto.dev with intelligent query interpretation
 */
const searchAutoDevWithIntelligence = async (expandedQuery: string): Promise<Vehicle[]> => {
  const axios = (await import('axios')).default;
  
  try {
    const apiKey = process.env.NEXT_PUBLIC_AUTO_DEV_API_KEY;
    if (!apiKey) return [];
    
    // Extract search parameters from expanded query
    const searchParams = extractSearchParameters(expandedQuery);
    
    const response = await axios.get('https://auto.dev/api/listings', {
      params: {
        limit: 50,
        ...searchParams
      },
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.data?.listings) {
      return response.data.listings.map(transformAutoDevToVehicle);
    }
    
    return [];
  } catch (error) {
    console.error('[IntelligentSearch] Auto.dev API error:', error);
    return [];
  }
};

/**
 * Extract search parameters from expanded query for API calls
 */
const extractSearchParameters = (expandedQuery: string): any => {
  const params: any = {};
  const query = expandedQuery.toLowerCase();
  
  // Extract make
  const makes = ['bmw', 'porsche', 'audi', 'mercedes', 'toyota', 'honda', 'ford', 'chevrolet', 'lexus'];
  for (const make of makes) {
    if (query.includes(make)) {
      params.make = make;
      break;
    }
  }
  
  // Extract year ranges
  const yearMatch = query.match(/(\d{4})-(\d{4})/);
  if (yearMatch) {
    params.year_min = parseInt(yearMatch[1]);
    params.year_max = parseInt(yearMatch[2]);
  }
  
  return params;
};

/**
 * Transform auto.dev listing to our Vehicle format
 */
const transformAutoDevToVehicle = (listing: any): Vehicle => {
  return {
    id: listing.id || `autodev-${Math.random().toString(36).substring(2, 10)}`,
    make: listing.make || 'Unknown',
    model: listing.model || 'Unknown',
    year: parseInt(listing.year) || new Date().getFullYear(),
    price: parseFloat(listing.price?.toString().replace(/[^0-9.]/g, '')) || 0,
    mileage: parseInt(listing.mileage?.toString().replace(/[^0-9]/g, '')) || 0,
    exteriorColor: listing.exterior_color || 'Unknown',
    interiorColor: listing.interior_color || 'Unknown',
    fuelType: listing.fuel_type || 'Unknown',
    transmission: listing.transmission || 'Unknown',
    engine: listing.engine_description || 'Unknown',
    vin: listing.vin || 'Unknown',
    description: listing.description || `${listing.year} ${listing.make} ${listing.model}`,
    features: listing.features || [],
    images: listing.photoUrls || [],
    location: listing.city && listing.state ? `${listing.city}, ${listing.state}` : 'Unknown',
    dealer: listing.dealerName || 'Unknown',
    listingDate: listing.createdAt || new Date().toISOString(),
    source: 'auto.dev',
    url: listing.vdpUrl || ''
  };
};

/**
 * Score vehicles by relevance to the original and expanded queries
 */
const scoreVehiclesByRelevance = (originalQuery: string, expandedQuery: string, vehicles: Vehicle[]): Vehicle[] => {
  const originalLower = originalQuery.toLowerCase();
  const expandedLower = expandedQuery.toLowerCase();
  
  return vehicles.map(vehicle => {
    let score = 0;
    const vehicleText = `${vehicle.make} ${vehicle.model} ${vehicle.year} ${vehicle.description} ${vehicle.features?.join(' ')}`.toLowerCase();
    
    // Direct matches with original query get highest score
    if (vehicleText.includes(originalLower)) score += 100;
    
    // Matches with expanded query get high score
    if (vehicleText.includes(expandedLower)) score += 80;
    
    // Individual word matches
    const originalWords = originalLower.split(' ');
    const expandedWords = expandedLower.split(' ');
    
    originalWords.forEach(word => {
      if (word.length > 2 && vehicleText.includes(word)) score += 20;
    });
    
    expandedWords.forEach(word => {
      if (word.length > 2 && vehicleText.includes(word)) score += 10;
    });
    
    // Boost score for exact make/model matches
    if (vehicle.make.toLowerCase().includes(originalLower)) score += 50;
    if (vehicle.model.toLowerCase().includes(originalLower)) score += 50;
    
    return { vehicle, score };
  })
  .sort((a, b) => b.score - a.score)
  .map(item => item.vehicle);
};

export default {
  translateCarTerminology,
  intelligentVehicleSearch
}; 