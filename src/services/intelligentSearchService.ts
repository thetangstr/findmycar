import { Vehicle } from '@/types';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { getHemmingsListings } from '@/services/scraperService';
import { filterVehiclesByQuery } from '@/utils/vehicleFiltering';
import { searchBatVehicles } from './batVehicleApi'; // Assuming this is the correct path

// Initialize Gemini AI
const geminiApiKey = process.env.NEXT_PUBLIC_GEMINI_API_KEY;
let genAI: GoogleGenerativeAI | null = null;

if (geminiApiKey && geminiApiKey !== 'your-gemini-api-key-here') {
  genAI = new GoogleGenerativeAI(geminiApiKey);
} else {
  console.warn('Gemini API key not configured, intelligent search features may be limited.');
}

// Car terminology mapping (can be expanded)
const CAR_TERMINOLOGY = {
  'e46': 'BMW 3 Series E46 (1998-2006)',
  'zhp': 'BMW ZHP Performance Package',
  '911': 'Porsche 911',
  // Add more terms as needed
};

export const translateCarTerminology = async (query: string): Promise<string> => {
  if (!genAI) {
    let expandedQuery = query.toLowerCase();
    for (const [term, meaning] of Object.entries(CAR_TERMINOLOGY)) {
      if (expandedQuery.includes(term.toLowerCase())) {
        expandedQuery = expandedQuery.replace(new RegExp(term.toLowerCase(), 'gi'), meaning);
      }
    }
    return expandedQuery;
  }
  try {
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    const prompt = `Interpret the following car search query and expand any automotive slang or abbreviations. Return only the expanded query as a single string. Query: "${query}"`;
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    return text.trim() || query;
  } catch (error) {
    console.error('Error calling Gemini API for terminology translation:', error);
    let expandedQuery = query.toLowerCase(); // Fallback to local if API fails
    for (const [term, meaning] of Object.entries(CAR_TERMINOLOGY)) {
      if (expandedQuery.includes(term.toLowerCase())) {
        expandedQuery = expandedQuery.replace(new RegExp(term.toLowerCase(), 'gi'), meaning);
      }
    }
    return expandedQuery;
  }
};

export const intelligentVehicleSearch = async (
  initialQuery: string,
  onProgress: (message: string) => void,
  source?: string
): Promise<Vehicle[]> => {
  const cleanedQuery = initialQuery.toLowerCase().replace(/from (hemmings|bat|bring a trailer)/g, '').trim();
  onProgress(`Interpreting your search: "${cleanedQuery}"${source ? ` from ${source}` : ''}`);

  const expandedQuery = await translateCarTerminology(cleanedQuery);
  onProgress(`Understood as: "${expandedQuery}"`);

  let results: Vehicle[] = [];

  if (source === 'hemmings') {
    onProgress('Fetching listings from Hemmings...');
    const hemmingsVehicles = await getHemmingsListings();
    onProgress(`Found ${hemmingsVehicles.length} total listings on Hemmings. Filtering for "${expandedQuery}"...`);
    results = filterVehiclesByQuery(hemmingsVehicles, expandedQuery);
    onProgress(`Found ${results.length} matching vehicles on Hemmings.`);
    return results;
  }

  // Search across all data sources
  if (!source || source === 'bat') {
    try {
      onProgress('Searching Bring a Trailer...');
      const batResults = await searchBatVehicles({ query: expandedQuery });
      onProgress(`Found ${batResults.length} matching vehicles on Bring a Trailer.`);
      results = [...results, ...batResults];
    } catch (error) {
      console.error('Error searching Bring a Trailer:', error);
      onProgress('Error searching Bring a Trailer.');
    }
  }
  
  // Search AutoTrader-like listings
  try {
    onProgress('Searching AutoTrader listings...');
    const { searchVehicles } = await import('./vehicleApi');
    const autotraderResults = await searchVehicles({ query: expandedQuery, source: 'autotrader' });
    onProgress(`Found ${autotraderResults.length} matching vehicles on AutoTrader.`);
    results = [...results, ...autotraderResults];
  } catch (error) {
    console.error('Error searching AutoTrader:', error);
    onProgress('Error searching AutoTrader.');
  }
  
  // Search eBay listings
  try {
    onProgress('Searching eBay Motors listings...');
    const { searchVehicles } = await import('./vehicleApi');
    const ebayResults = await searchVehicles({ query: expandedQuery, source: 'ebay' });
    onProgress(`Found ${ebayResults.length} matching vehicles on eBay.`);
    results = [...results, ...ebayResults];
  } catch (error) {
    console.error('Error searching eBay:', error);
    onProgress('Error searching eBay Motors.');
  }
  
  // Previous Auto.dev Search has been removed
  
  // Fallback to local vehicle API if no source specified or if other searches yield no results and it's a general query
  if (!source && results.length === 0) {
     try {
        const { searchVehicles } = await import('./vehicleApi'); // Local API
        onProgress('No results from specialized sources, trying general vehicle search...');
        const localApiResults = await searchVehicles({ query: expandedQuery });
        onProgress(`Found ${localApiResults.length} vehicles from general search.`);
        results = [...results, ...localApiResults];
     } catch (error) {
        console.error('Error searching local Vehicle API:', error);
        onProgress('Error searching general vehicle listings.');
     }
  }

  // Remove duplicates (simple implementation, can be improved)
  const uniqueResults = results.filter((vehicle, index, self) =>
    index === self.findIndex(v => (v.vin && v.vin === vehicle.vin && v.vin !== 'Unknown') || (v.make === vehicle.make && v.model === vehicle.model && v.year === vehicle.year && v.price === vehicle.price))
  );
  
  onProgress(`Search complete. Found ${uniqueResults.length} relevant vehicles.`);
  return uniqueResults;
};

export default {
  translateCarTerminology,
  intelligentVehicleSearch,
};