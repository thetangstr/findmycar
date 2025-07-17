import { Vehicle } from '@/types';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { getHemmingsListings } from '@/services/scraperService';
import { filterVehiclesByQuery } from '@/utils/vehicleFiltering';
import { searchBatVehicles } from './batVehicleApi'; // Assuming this is the correct path
import { mockVehicles } from '@/data/mockVehicles'; // Import mock data for demo

// Demo function to get hardcoded Porsche 911 results (1990-1994, under 100k miles)
const getDemoResults = (): Vehicle[] => {
  return mockVehicles.filter(vehicle => 
    vehicle.make === 'Porsche' && 
    vehicle.model?.includes('911') &&
    vehicle.year >= 1990 && 
    vehicle.year <= 1994 &&
    vehicle.mileage < 100000
  );
};

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
  // For demo: Always return hardcoded Porsche 911 results regardless of query
  onProgress(`Demo Mode: Searching for Porsche 911s (1990-1994, under 100k miles)...`);
  
  // Simulate processing time for demo
  await new Promise(resolve => setTimeout(resolve, 500));
  
  const demoResults = getDemoResults();
  onProgress(`Found ${demoResults.length} matching Porsche 911 vehicles for demo.`);
  
  // Simulate some additional processing time
  await new Promise(resolve => setTimeout(resolve, 300));
  
  onProgress(`Demo search complete. Showing curated Porsche 911 collection.`);
  return demoResults;
};

export default {
  translateCarTerminology,
  intelligentVehicleSearch,
};