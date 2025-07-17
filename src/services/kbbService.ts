import { Vehicle } from '@/types';

export interface KBBValuation {
  fairMarketValue: number;
  excellentCondition: number;
  goodCondition: number;
  fairCondition: number;
  poorCondition: number;
  privatePartyValue: number;
  tradeInValue: number;
  retailValue: number;
  dataSource: 'kbb' | 'edmunds' | 'nada' | 'mock';
  lastUpdated: string;
}

export interface DealRating {
  rating: 'great_deal' | 'good_deal' | 'fair_price' | 'high_price' | 'overpriced';
  savings: number; // Positive if below market value, negative if above
  percentageFromMarket: number; // How much above/below market value
  marketComparison: string; // Human readable description
  confidence: number; // 0-100 confidence in the valuation
}

export interface PriceAnalysis {
  listingPrice: number;
  marketValue: KBBValuation;
  dealRating: DealRating;
  priceHistory?: {
    originalPrice?: number;
    priceDrops?: Array<{
      date: string;
      oldPrice: number;
      newPrice: number;
    }>;
  };
}

// KBB API configuration
const KBB_API_KEY = process.env.NEXT_PUBLIC_KBB_API_KEY || '';
const KBB_BASE_URL = 'https://api.kbb.com/v1';

// Alternative APIs for backup
const EDMUNDS_API_KEY = process.env.NEXT_PUBLIC_EDMUNDS_API_KEY || '';
const NADA_API_KEY = process.env.NEXT_PUBLIC_NADA_API_KEY || '';

/**
 * Get vehicle valuation from KBB API
 */
export const getKBBValuation = async (vehicle: Vehicle): Promise<KBBValuation> => {
  // First try KBB API if available
  if (KBB_API_KEY) {
    try {
      const response = await fetch(`${KBB_BASE_URL}/vehicles/valuation`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${KBB_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          year: vehicle.year,
          make: vehicle.make,
          model: vehicle.model,
          trim: extractTrim(vehicle.model, vehicle.description),
          mileage: vehicle.mileage,
          condition: inferCondition(vehicle),
          zipCode: extractZipCode(vehicle.location) || '94105', // Default to SF
        }),
      });

      if (response.ok) {
        const data = await response.json();
        return {
          fairMarketValue: data.fairMarketValue,
          excellentCondition: data.values.excellent,
          goodCondition: data.values.good,
          fairCondition: data.values.fair,
          poorCondition: data.values.poor,
          privatePartyValue: data.privatePartyValue,
          tradeInValue: data.tradeInValue,
          retailValue: data.retailValue,
          dataSource: 'kbb',
          lastUpdated: new Date().toISOString(),
        };
      }
    } catch (error) {
      console.error('KBB API error:', error);
    }
  }

  // Fallback to Edmunds API
  if (EDMUNDS_API_KEY) {
    try {
      const edmundsValue = await getEdmundsValuation(vehicle);
      if (edmundsValue) return edmundsValue;
    } catch (error) {
      console.error('Edmunds API error:', error);
    }
  }

  // Final fallback to mock/estimated values
  return getMockValuation(vehicle);
};

/**
 * Alternative valuation from Edmunds API
 */
const getEdmundsValuation = async (vehicle: Vehicle): Promise<KBBValuation | null> => {
  try {
    const response = await fetch(
      `https://api.edmunds.com/api/vehicle/v2/${vehicle.make}/${vehicle.model}/${vehicle.year}/truepricing?api_key=${EDMUNDS_API_KEY}&zip=${extractZipCode(vehicle.location) || '94105'}`
    );

    if (response.ok) {
      const data = await response.json();
      const tmv = data.tmv;
      
      return {
        fairMarketValue: tmv.nationalBasePrice,
        excellentCondition: tmv.nationalBasePrice * 1.15,
        goodCondition: tmv.nationalBasePrice,
        fairCondition: tmv.nationalBasePrice * 0.85,
        poorCondition: tmv.nationalBasePrice * 0.65,
        privatePartyValue: tmv.nationalBasePrice * 0.9,
        tradeInValue: tmv.nationalBasePrice * 0.75,
        retailValue: tmv.nationalBasePrice * 1.1,
        dataSource: 'edmunds',
        lastUpdated: new Date().toISOString(),
      };
    }
  } catch (error) {
    console.error('Edmunds API error:', error);
  }
  
  return null;
};

/**
 * Generate mock valuation based on vehicle data and market trends
 */
const getMockValuation = (vehicle: Vehicle): KBBValuation => {
  // Basic depreciation model
  const currentYear = new Date().getFullYear();
  const ageDepreciation = Math.pow(0.85, currentYear - vehicle.year); // 15% per year
  const mileageDepreciation = Math.max(0.4, 1 - (vehicle.mileage / 200000)); // Depreciate based on mileage
  
  // Base value estimation
  let baseValue = estimateBaseValue(vehicle);
  baseValue *= ageDepreciation * mileageDepreciation;
  
  // Adjust for make/model desirability
  baseValue *= getDesirabilityMultiplier(vehicle.make, vehicle.model);
  
  // Condition multipliers
  const excellentMultiplier = 1.2;
  const goodMultiplier = 1.0;
  const fairMultiplier = 0.8;
  const poorMultiplier = 0.6;
  
  return {
    fairMarketValue: Math.round(baseValue),
    excellentCondition: Math.round(baseValue * excellentMultiplier),
    goodCondition: Math.round(baseValue * goodMultiplier),
    fairCondition: Math.round(baseValue * fairMultiplier),
    poorCondition: Math.round(baseValue * poorMultiplier),
    privatePartyValue: Math.round(baseValue * 0.92),
    tradeInValue: Math.round(baseValue * 0.78),
    retailValue: Math.round(baseValue * 1.15),
    dataSource: 'mock',
    lastUpdated: new Date().toISOString(),
  };
};

/**
 * Estimate base MSRP for the vehicle
 */
const estimateBaseValue = (vehicle: Vehicle): number => {
  // Vehicle type base values (rough estimates)
  const baseValues: { [key: string]: number } = {
    // Luxury brands
    'BMW': 45000,
    'Mercedes-Benz': 50000,
    'Audi': 42000,
    'Lexus': 45000,
    'Porsche': 75000,
    'Ferrari': 250000,
    'Lamborghini': 200000,
    'Bentley': 180000,
    'Rolls-Royce': 350000,
    
    // Premium brands
    'Acura': 35000,
    'Infiniti': 38000,
    'Cadillac': 45000,
    'Lincoln': 42000,
    'Volvo': 40000,
    'Genesis': 48000,
    
    // Mainstream brands
    'Toyota': 28000,
    'Honda': 26000,
    'Ford': 28000,
    'Chevrolet': 30000,
    'Nissan': 25000,
    'Hyundai': 24000,
    'Kia': 23000,
    'Mazda': 26000,
    'Subaru': 28000,
    'Volkswagen': 30000,
    
    // Trucks/SUVs get premium
    'Ram': 35000,
    'GMC': 38000,
    'Jeep': 32000,
    'Land Rover': 55000,
    
    // Electric vehicles
    'Tesla': 50000,
    'Rivian': 65000,
    'Lucid': 85000,
  };

  let baseValue = baseValues[vehicle.make] || 25000;
  
  // Adjust for model type
  const modelLower = vehicle.model.toLowerCase();
  if (modelLower.includes('suv') || modelLower.includes('truck') || modelLower.includes('pickup')) {
    baseValue *= 1.2;
  } else if (modelLower.includes('coupe') || modelLower.includes('convertible')) {
    baseValue *= 1.1;
  } else if (modelLower.includes('wagon') || modelLower.includes('minivan')) {
    baseValue *= 0.9;
  }
  
  return baseValue;
};

/**
 * Get desirability multiplier for make/model
 */
const getDesirabilityMultiplier = (make: string, model: string): number => {
  const makeMultipliers: { [key: string]: number } = {
    'Porsche': 1.3,
    'Ferrari': 1.5,
    'Lamborghini': 1.4,
    'BMW': 1.1,
    'Mercedes-Benz': 1.1,
    'Audi': 1.05,
    'Lexus': 1.1,
    'Toyota': 1.05, // Reliable brand
    'Honda': 1.05, // Reliable brand
    'Tesla': 1.2,  // High demand
    'Ford': 0.95,
    'Chevrolet': 0.95,
    'Chrysler': 0.85,
    'Mitsubishi': 0.8,
  };

  // Special model adjustments
  const modelLower = model.toLowerCase();
  let modelMultiplier = 1.0;
  
  if (modelLower.includes('m3') || modelLower.includes('m5') || modelLower.includes('amg')) {
    modelMultiplier = 1.3; // High-performance models
  } else if (modelLower.includes('hybrid') || modelLower.includes('electric')) {
    modelMultiplier = 1.1; // Green vehicles premium
  } else if (modelLower.includes('diesel')) {
    modelMultiplier = 0.9; // Diesel penalty in US market
  }
  
  return (makeMultipliers[make] || 1.0) * modelMultiplier;
};

/**
 * Analyze deal quality based on listing price vs market value
 */
export const analyzeDeal = (listingPrice: number, marketValue: KBBValuation): DealRating => {
  const fairValue = marketValue.fairMarketValue;
  const savings = fairValue - listingPrice;
  const percentageFromMarket = ((listingPrice - fairValue) / fairValue) * 100;
  
  let rating: DealRating['rating'];
  let marketComparison: string;
  let confidence = 85; // Base confidence

  if (percentageFromMarket <= -15) {
    rating = 'great_deal';
    marketComparison = `Excellent value - $${Math.abs(savings).toLocaleString()} below market value`;
  } else if (percentageFromMarket <= -8) {
    rating = 'good_deal';
    marketComparison = `Good deal - $${Math.abs(savings).toLocaleString()} below market value`;
  } else if (percentageFromMarket <= 8) {
    rating = 'fair_price';
    marketComparison = 'Fair market price';
  } else if (percentageFromMarket <= 20) {
    rating = 'high_price';
    marketComparison = `Above market - $${savings.toLocaleString()} over typical value`;
  } else {
    rating = 'overpriced';
    marketComparison = `Significantly overpriced - $${savings.toLocaleString()} over market value`;
  }

  // Reduce confidence for mock data
  if (marketValue.dataSource === 'mock') {
    confidence = 65;
  }

  return {
    rating,
    savings,
    percentageFromMarket,
    marketComparison,
    confidence,
  };
};

/**
 * Get comprehensive price analysis for a vehicle
 */
export const getPriceAnalysis = async (vehicle: Vehicle): Promise<PriceAnalysis> => {
  const marketValue = await getKBBValuation(vehicle);
  const dealRating = analyzeDeal(vehicle.price, marketValue);
  
  return {
    listingPrice: vehicle.price,
    marketValue,
    dealRating,
    // Price history would come from tracking price changes over time
    priceHistory: {
      originalPrice: vehicle.price, // Would be stored when first scraped
      priceDrops: [], // Would be populated from historical data
    },
  };
};

// Helper functions
const extractTrim = (model: string, description: string): string => {
  // Extract trim level from model name or description
  const trimPatterns = [
    /\b(LX|EX|EX-L|Touring|Sport|Premium|Base|S|SE|SEL|Limited|Platinum)\b/i,
    /\b(LS|LT|LTZ|SS|RS|Z06|ZR1|GT|Shelby)\b/i,
    /\b(xDrive|quattro|AWD|4WD|FWD|RWD)\b/i,
  ];

  for (const pattern of trimPatterns) {
    const match = description.match(pattern) || model.match(pattern);
    if (match) return match[1];
  }

  return 'Base';
};

const inferCondition = (vehicle: Vehicle): string => {
  // Infer condition from mileage and age
  const currentYear = new Date().getFullYear();
  const age = currentYear - vehicle.year;
  const averageMilesPerYear = vehicle.mileage / Math.max(age, 1);

  if (vehicle.mileage < 30000 && age < 3) return 'Excellent';
  if (vehicle.mileage < 60000 && averageMilesPerYear < 12000) return 'Good';
  if (vehicle.mileage < 100000) return 'Fair';
  return 'Poor';
};

const extractZipCode = (location: string): string | null => {
  const zipMatch = location.match(/\b\d{5}\b/);
  return zipMatch ? zipMatch[0] : null;
};

export default {
  getKBBValuation,
  analyzeDeal,
  getPriceAnalysis,
};