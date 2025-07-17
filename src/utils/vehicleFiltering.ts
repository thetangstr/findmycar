import { Vehicle } from '@/types';

/**
 * A mapping of common model nicknames or abbreviations to their official make and model names
 */
const MODEL_ALIASES: {[key: string]: {make: string, model: string}} = {
  'nsx': {make: 'Acura', model: 'NSX'},
  'gtr': {make: 'Nissan', model: 'GT-R'},
  'skyline': {make: 'Nissan', model: 'GT-R'},
  'supra': {make: 'Toyota', model: 'Supra'},
  'z06': {make: 'Chevrolet', model: 'Corvette'},
  'zr1': {make: 'Chevrolet', model: 'Corvette'},
  'vette': {make: 'Chevrolet', model: 'Corvette'},
  'miata': {make: 'Mazda', model: 'MX-5'},
  'stingray': {make: 'Chevrolet', model: 'Corvette'},
  'rx7': {make: 'Mazda', model: 'RX-7'},
  'rx8': {make: 'Mazda', model: 'RX-8'},
};

/**
 * Filters an array of vehicles based on a simple query string.
 * Enhanced to handle model-specific aliases and better matching.
 * @param vehicles - The array of vehicles to filter.
 * @param query - The search query string.
 * @returns A new array of vehicles that match the query.
 */
export const filterVehiclesByQuery = (vehicles: Vehicle[], query: string): Vehicle[] => {
  if (!query.trim()) {
    return vehicles; // Return all if query is empty
  }

  const lowerCaseQuery = query.toLowerCase();
  const queryWords = lowerCaseQuery.split(' ').filter(word => word.length > 0);
  
  // Check for model aliases in the query
  for (const [alias, info] of Object.entries(MODEL_ALIASES)) {
    if (queryWords.includes(alias)) {
      // If an alias like "nsx" is found, use strict matching to ensure we only get exact model matches
      // This is especially important for iconic models like NSX that should not match other vehicles
      const exactMatches = vehicles.filter(vehicle => 
        vehicle.make.toLowerCase() === info.make.toLowerCase() && 
        vehicle.model.toLowerCase() === info.model.toLowerCase()
      );
      
      // If we found exact matches, return those
      if (exactMatches.length > 0) {
        return exactMatches;
      }
      
      // Otherwise, use more flexible but still strict matching
      return vehicles.filter(vehicle => 
        vehicle.make.toLowerCase() === info.make.toLowerCase() && 
        (vehicle.model.toLowerCase() === info.model.toLowerCase() ||
         vehicle.model.toLowerCase().startsWith(info.model.toLowerCase() + ' ') ||
         vehicle.model.toLowerCase() === info.model.toLowerCase().replace('-', '') ||
         vehicle.model.toLowerCase().includes(info.model.toLowerCase()))
      );
    }
  }

  return vehicles.filter(vehicle => {
    const searchableText = [
      vehicle.make,
      vehicle.model,
      vehicle.year.toString(),
      vehicle.description,
      vehicle.vin,
      vehicle.exteriorColor,
      vehicle.interiorColor,
      vehicle.engine,
      vehicle.transmission,
      vehicle.dealer,
      vehicle.source,
      ...(vehicle.features || [])
    ].join(' ').toLowerCase();

    // More flexible matching - match if any significant query word is found
    // Only require all words to match if there are more than 3 words (likely a specific search)
    if (queryWords.length <= 3) {
      return queryWords.some(word => {
        // Skip very short words unless they're model codes
        if (word.length < 3 && !Object.keys(MODEL_ALIASES).includes(word)) {
          return true; // Skip checking this word (treated as matched)
        }
        return searchableText.includes(word);
      });
    } else {
      // For longer queries, use stricter matching
      return queryWords.every(word => searchableText.includes(word));
    }
  });
};
