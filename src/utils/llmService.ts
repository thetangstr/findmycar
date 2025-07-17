import { OpenAI } from 'openai';
import { Vehicle, SearchFilters } from '@/types';

// This would be stored in environment variables in a real application
// For security, we're not providing a real API key here
const OPENAI_API_KEY = process.env.NEXT_PUBLIC_OPENAI_API_KEY || '';

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: OPENAI_API_KEY,
  dangerouslyAllowBrowser: true // Only for demo purposes
});

/**
 * Convert natural language query to structured search filters
 */
export const queryToFilters = async (query: string): Promise<SearchFilters> => {
  try {
    if (!OPENAI_API_KEY) {
      console.warn('OpenAI API key not provided. Using fallback method.');
      return fallbackQueryToFilters(query);
    }

    const prompt = `
      Convert the following car search query into structured search parameters.
      Query: "${query}"
      
      Return a JSON object with these possible fields (only include fields that are relevant to the query):
      - make: car manufacturer
      - model: car model
      - yearMin: minimum year
      - yearMax: maximum year
      - priceMin: minimum price in dollars
      - priceMax: maximum price in dollars
      - mileageMin: minimum mileage
      - mileageMax: maximum mileage
      - fuelType: one of [Gasoline, Diesel, Hybrid, Electric, Plug-in Hybrid]
      - transmission: one of [Automatic, Manual, CVT, Semi-Automatic]
      
      Example response format:
      {
        "make": "Toyota",
        "yearMin": 2018,
        "priceMax": 30000
      }
    `;

    const response = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [
        { role: "system", content: "You are a helpful assistant that converts natural language car search queries into structured search parameters." },
        { role: "user", content: prompt }
      ],
      temperature: 0.3,
    });

    const content = response.choices[0]?.message?.content;
    if (!content) throw new Error('No response from OpenAI');

    try {
      // Extract JSON from the response
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (!jsonMatch) throw new Error('No JSON found in response');
      
      const filters = JSON.parse(jsonMatch[0]) as SearchFilters;
      return filters;
    } catch (parseError) {
      console.error('Error parsing OpenAI response:', parseError);
      return fallbackQueryToFilters(query);
    }
  } catch (error) {
    console.error('Error in OpenAI query:', error);
    return fallbackQueryToFilters(query);
  }
};

/**
 * Fallback method for converting queries to filters when API is unavailable
 */
const fallbackQueryToFilters = (query: string): SearchFilters => {
  const filters: SearchFilters = {};
  const lowerQuery = query.toLowerCase();

  // Extract make
  const makes = ['toyota', 'honda', 'ford', 'chevrolet', 'bmw', 'audi', 'tesla', 'hyundai'];
  for (const make of makes) {
    if (lowerQuery.includes(make)) {
      filters.make = make.charAt(0).toUpperCase() + make.slice(1);
      break;
    }
  }

  // Extract price range
  const priceMaxMatch = lowerQuery.match(/under\s+\$?(\d{1,3}(?:,\d{3})*|\d+)k?/i) || 
                        lowerQuery.match(/less than\s+\$?(\d{1,3}(?:,\d{3})*|\d+)k?/i) ||
                        lowerQuery.match(/below\s+\$?(\d{1,3}(?:,\d{3})*|\d+)k?/i);
  
  if (priceMaxMatch) {
    let priceMax = parseInt(priceMaxMatch[1].replace(/,/g, ''));
    if (lowerQuery.includes('k') && priceMax < 1000) priceMax *= 1000;
    filters.priceMax = priceMax;
  }

  // Extract year range
  const yearMinMatch = lowerQuery.match(/after\s+(\d{4})/i) || 
                       lowerQuery.match(/newer than\s+(\d{4})/i);
  if (yearMinMatch) {
    filters.yearMin = parseInt(yearMinMatch[1]);
  }

  const yearMaxMatch = lowerQuery.match(/before\s+(\d{4})/i) || 
                       lowerQuery.match(/older than\s+(\d{4})/i);
  if (yearMaxMatch) {
    filters.yearMax = parseInt(yearMaxMatch[1]);
  }

  // Extract fuel type
  if (lowerQuery.includes('electric')) {
    filters.fuelType = 'Electric';
  } else if (lowerQuery.includes('hybrid')) {
    filters.fuelType = 'Hybrid';
  } else if (lowerQuery.includes('diesel')) {
    filters.fuelType = 'Diesel';
  } else if (lowerQuery.includes('gas') || lowerQuery.includes('gasoline')) {
    filters.fuelType = 'Gasoline';
  }

  // Extract transmission
  if (lowerQuery.includes('manual')) {
    filters.transmission = 'Manual';
  } else if (lowerQuery.includes('automatic')) {
    filters.transmission = 'Automatic';
  }

  // Add the original query for full-text search
  filters.query = query;

  return filters;
};

/**
 * Rank vehicles based on natural language query
 */
export const rankVehiclesByQuery = async (query: string, vehicles: Vehicle[]): Promise<Vehicle[]> => {
  try {
    if (!OPENAI_API_KEY) {
      console.warn('OpenAI API key not provided. Using fallback ranking method.');
      return fallbackRankVehicles(query, vehicles);
    }

    // Convert vehicles to a simplified format for the prompt
    const simplifiedVehicles = vehicles.map((v, index) => ({
      id: v.id,
      index,
      make: v.make,
      model: v.model,
      year: v.year,
      price: v.price,
      mileage: v.mileage,
      fuelType: v.fuelType,
      transmission: v.transmission,
      features: v.features.join(', '),
      description: v.description
    }));

    const prompt = `
      Rank these vehicles based on how well they match the user's query: "${query}"
      
      Vehicles:
      ${JSON.stringify(simplifiedVehicles, null, 2)}
      
      Return a JSON array of vehicle IDs in order of relevance, most relevant first.
      Example response format:
      ["3", "1", "5", "2", "4"]
    `;

    const response = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [
        { role: "system", content: "You are a helpful assistant that ranks vehicles based on user preferences." },
        { role: "user", content: prompt }
      ],
      temperature: 0.3,
    });

    const content = response.choices[0]?.message?.content;
    if (!content) throw new Error('No response from OpenAI');

    try {
      // Extract JSON array from the response
      const jsonMatch = content.match(/\[[\s\S]*\]/);
      if (!jsonMatch) throw new Error('No JSON array found in response');
      
      const rankedIds = JSON.parse(jsonMatch[0]) as string[];
      
      // Map the ranked IDs back to the original vehicles
      const vehicleMap = new Map(vehicles.map(v => [v.id, v]));
      const rankedVehicles = rankedIds
        .map(id => vehicleMap.get(id))
        .filter(v => v !== undefined) as Vehicle[];
      
      // Add any vehicles that weren't ranked at the end
      const rankedIds_set = new Set(rankedIds);
      const unrankedVehicles = vehicles.filter(v => !rankedIds_set.has(v.id));
      
      return [...rankedVehicles, ...unrankedVehicles];
    } catch (parseError) {
      console.error('Error parsing OpenAI response:', parseError);
      return fallbackRankVehicles(query, vehicles);
    }
  } catch (error) {
    console.error('Error in OpenAI ranking:', error);
    return fallbackRankVehicles(query, vehicles);
  }
};

/**
 * Fallback method for ranking vehicles when API is unavailable
 */
const fallbackRankVehicles = (query: string, vehicles: Vehicle[]): Vehicle[] => {
  const lowerQuery = query.toLowerCase();
  
  // Score each vehicle based on the query
  const scoredVehicles = vehicles.map(vehicle => {
    let score = 0;
    
    // Direct make/model matching
    if (vehicle.make.toLowerCase().includes(lowerQuery)) score += 10;
    if (vehicle.model.toLowerCase().includes(lowerQuery)) score += 10;
    
    // Description matching
    if (vehicle.description.toLowerCase().includes(lowerQuery)) score += 5;
    
    // Feature matching
    vehicle.features.forEach(feature => {
      if (feature.toLowerCase().includes(lowerQuery)) score += 3;
    });
    
    // Semantic matching based on keywords
    const vehicleDetails = `${vehicle.make} ${vehicle.model} ${vehicle.description} ${vehicle.features.join(' ')} ${vehicle.fuelType} ${vehicle.transmission}`.toLowerCase();
    
    // Check for affordability preferences
    const affordabilityTerms = ['cheap', 'affordable', 'budget', 'inexpensive', 'low price', 'economical'];
    if (affordabilityTerms.some(term => lowerQuery.includes(term))) {
      // Lower price gets higher score
      score += Math.max(0, 50000 - vehicle.price) / 5000;
    }
    
    // Check for luxury preferences
    const luxuryTerms = ['luxury', 'premium', 'high-end', 'expensive', 'top-tier'];
    if (luxuryTerms.some(term => lowerQuery.includes(term))) {
      // Higher price and premium brands get higher score
      const premiumBrands = ['bmw', 'audi', 'mercedes', 'lexus', 'tesla'];
      if (premiumBrands.includes(vehicle.make.toLowerCase())) score += 10;
      score += vehicle.price / 10000;
    }
    
    // Check for family-friendly preferences
    const familyTerms = ['family', 'spacious', 'kids', 'room', 'safe', 'safety'];
    if (familyTerms.some(term => lowerQuery.includes(term))) {
      // SUVs and vehicles with safety features get higher score
      const familyModels = ['suv', 'minivan', 'crossover', 'equinox', 'tucson', 'q5'];
      if (familyModels.some(model => vehicle.model.toLowerCase().includes(model))) score += 10;
      if (vehicleDetails.includes('safety')) score += 5;
      if (vehicleDetails.includes('spacious')) score += 5;
    }
    
    // Check for efficiency preferences
    const efficiencyTerms = ['efficient', 'fuel economy', 'gas mileage', 'hybrid', 'electric', 'eco'];
    if (efficiencyTerms.some(term => lowerQuery.includes(term))) {
      // Hybrid/electric vehicles get higher score
      if (vehicle.fuelType.toLowerCase() === 'hybrid' || vehicle.fuelType.toLowerCase() === 'electric') score += 15;
      // Lower mileage gets higher score for efficiency
      score += Math.max(0, 50000 - vehicle.mileage) / 5000;
    }
    
    // Check for performance preferences
    const performanceTerms = ['fast', 'quick', 'powerful', 'performance', 'sporty', 'speed'];
    if (performanceTerms.some(term => lowerQuery.includes(term))) {
      // Sports cars and performance-oriented vehicles get higher score
      const performanceModels = ['3 series', 'model 3', 'mustang', 'corvette', 'camaro'];
      if (performanceModels.includes(vehicle.model.toLowerCase())) score += 10;
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
