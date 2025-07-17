import { useState, useCallback } from 'react';
import { Vehicle } from '@/types';

// Basic natural language filtering function
const filterVehiclesByNaturalLanguage = (query: string, vehicles: Vehicle[]): Vehicle[] => {
  // Convert query to lowercase for case-insensitive matching
  const lowerQuery = query.toLowerCase();
  const queryTerms = lowerQuery.split(/\s+/).filter(term => term.length > 1 && term.length < 20); // Define queryTerms here for wider scope
  
  // Keywords that might indicate user preferences
  const affordabilityTerms = ['cheap', 'affordable', 'budget', 'inexpensive', 'low price', 'economical'];
  const luxuryTerms = ['luxury', 'premium', 'high-end', 'expensive', 'top-tier'];
  const familyTerms = ['family', 'spacious', 'kids', 'room', 'safe', 'safety'];
  const efficiencyTerms = ['efficient', 'fuel economy', 'gas mileage', 'hybrid', 'electric', 'eco'];
  const performanceTerms = ['fast', 'quick', 'powerful', 'performance', 'sporty', 'speed'];
  
  // Score each vehicle based on how well it matches the query
  const scoredVehicles = vehicles.map(vehicle => {
    let score = 0;
    
    // Refined Direct make/model matching
    let makeModelScore = 0;
    const vehicleMakeLower = vehicle.make.toLowerCase();
    const vehicleModelLower = vehicle.model.toLowerCase();

    // Priority 1: Full query string interactions with make/model
    if (vehicleMakeLower.includes(lowerQuery) || lowerQuery.includes(vehicleMakeLower)) {
        makeModelScore = Math.max(makeModelScore, 55);
        if (vehicleMakeLower === lowerQuery) makeModelScore = Math.max(makeModelScore, 60); // Exact full query match is best
    }
    if (vehicleModelLower.includes(lowerQuery) || lowerQuery.includes(vehicleModelLower)) {
        makeModelScore = Math.max(makeModelScore, 55);
        if (vehicleModelLower === lowerQuery) makeModelScore = Math.max(makeModelScore, 60);
    }

    // Priority 2: Query terms matching make/model fields
    // queryTerms is now defined at the function start
    if (queryTerms.length > 0) {
        let termMatchedMakeField = false;
        let termMatchedModelField = false;

        // List of iconic car models that deserve special handling for exact matches
    const iconicModels = ['nsx', 'gtr', 'r8', '911', 'corvette', 'mustang', 'camaro', 'miata', 'supra'];
            
    queryTerms.forEach(term => {
            let termScoreMake = 0;
            if (vehicleMakeLower === term) termScoreMake = 50;
            else if (vehicleMakeLower.includes(term)) termScoreMake = 30;
            if (termScoreMake > 0) {
                makeModelScore = Math.max(makeModelScore, termScoreMake);
                termMatchedMakeField = true;
            }

            let termScoreModel = 0;
            // Exact model match gets a much higher score
            if (vehicleModelLower === term) termScoreModel = 80;
            // Special handling for iconic car models
            else if (iconicModels.includes(term.toLowerCase()) && 
                    (vehicleModelLower === term.toLowerCase() || 
                     vehicleModelLower.split(' ').includes(term.toLowerCase()))) {
                termScoreModel = 90; // Give iconic models an even higher score
            }
            else if (vehicleModelLower.includes(term)) termScoreModel = 40;
            
            if (termScoreModel > 0) {
                makeModelScore = Math.max(makeModelScore, termScoreModel);
                termMatchedModelField = true;
            }
        });

        // Bonus for multi-term query where terms hit both make and model fields
        if (queryTerms.length > 1 && termMatchedMakeField && termMatchedModelField) {
            makeModelScore += 20; // Add bonus, don't use Math.max here as it's an additional score
        }
    }
    score += makeModelScore;
    
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
  
  const sortedScoredVehicles = scoredVehicles.sort((a, b) => b.score - a.score);

  if (sortedScoredVehicles.length === 0) {
    return [];
  }

  const topScoredItem = sortedScoredVehicles[0];
  
  // If the top vehicle's score is very low, and the query looked specific, return empty to avoid irrelevant results.
  if (topScoredItem.score <= 5 && queryTerms.length > 0) {
    // Consider a query potentially specific if it's 1 or 2 terms long (e.g., "nsx", "acura nsx").
    const potentiallySpecificQuery = queryTerms.length === 1 || queryTerms.length === 2;
    if (potentiallySpecificQuery && topScoredItem.score < 15) {
      // If the query looked like it was for a specific make/model, but the best score is very low,
      // it's better to return no results than highly irrelevant ones.
      return [];
    }
    // If query wasn't "specific" looking, or if it was but score is between 5 and 15, proceed to general filtering rules below.
  }
  
  if (topScoredItem.score === 0 && sortedScoredVehicles.every(item => item.score === 0)) {
      return []; // All items scored 0, nothing found
  }


  // Special case for single-term specific model searches (like "nsx")
  if (queryTerms.length === 1 && queryTerms[0].length <= 5 && topScoredItem.score >= 70) {
    // For specific model searches with high top score, use a very strict threshold
    // This ensures we only return vehicles that are truly relevant to that model
    const strictThreshold = Math.max(topScoredItem.score * 0.7, 50);
    
    return sortedScoredVehicles
      .filter(item => item.score >= strictThreshold)
      .map(item => item.vehicle);
  }
  // Regular case for high-scoring results
  else if (topScoredItem.score >= 50) { 
    // Filter out items with scores significantly lower than the top score.
    // Increased from 25% to 40% to make filtering stricter
    const scoreThreshold = Math.max(topScoredItem.score * 0.4, 20);
    
    return sortedScoredVehicles
      .filter(item => item.score >= scoreThreshold)
      .map(item => item.vehicle);
  } else {
    // For less specific queries or when no strong match is found, return results with a score > 5
    // This avoids showing vehicles that matched on very minor, possibly irrelevant terms.
    return sortedScoredVehicles
      .filter(item => item.score > 5) 
      .map(item => item.vehicle);
  }
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
      const searchResults = await intelligentVehicleSearch(
        query,
        // Add the required onProgress callback parameter
        (progressMessage: string) => {
          console.log(`[LLMSearch] Progress: ${progressMessage}`);
          // You could also set progress state here if needed
        }
      );
      
      setResults(searchResults);
      
      // If no results from intelligent search, fallback to local filtering
      if (searchResults.length === 0 && vehicles.length > 0) {
        console.log('[LLMSearch] No intelligent results, falling back to local filtering');
        const localResults = filterVehiclesByNaturalLanguage(query, vehicles);
        setResults(localResults);
        setError('No exact matches found with intelligent search. Showing best local results.'); // Inform user about fallback
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
