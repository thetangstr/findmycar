import React, { useState, useEffect } from 'react';
import { Vehicle } from '@/types';

interface MarketInsightsProps {
  vehicle: Vehicle;
  similarVehicles?: Vehicle[];
}

interface MarketData {
  averagePrice: number;
  priceRange: { min: number; max: number };
  daysOnMarket: number;
  priceCompetitiveness: 'excellent' | 'good' | 'fair' | 'high';
  marketTrend: 'rising' | 'falling' | 'stable';
  popularFeatures: string[];
  similarCount: number;
}

/**
 * Market Insights Component
 * 
 * Provides valuable market data and insights for a specific vehicle:
 * - Average market price for similar vehicles
 * - Price competitiveness rating
 * - Days on market comparison
 * - Market trend indicators
 * - Popular features in similar vehicles
 */
const MarketInsights: React.FC<MarketInsightsProps> = ({ vehicle, similarVehicles = [] }) => {
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real application, this would be an API call to get market data
    // For now, we'll generate mock data based on the vehicle and similar vehicles
    const generateMarketInsights = () => {
      setLoading(true);
      
      // Simulate API delay
      setTimeout(() => {
        // Generate mock market data
        const mockMarketData: MarketData = {
          // Calculate average price from similar vehicles or estimate based on current vehicle
          averagePrice: similarVehicles.length > 0
            ? Math.round(similarVehicles.reduce((sum, v) => sum + v.price, 0) / similarVehicles.length)
            : Math.round(vehicle.price * (0.9 + Math.random() * 0.2)), // ±10% of current price
          
          // Price range
          priceRange: {
            min: similarVehicles.length > 0
              ? Math.min(...similarVehicles.map(v => v.price))
              : Math.round(vehicle.price * 0.85),
            max: similarVehicles.length > 0
              ? Math.max(...similarVehicles.map(v => v.price))
              : Math.round(vehicle.price * 1.15)
          },
          
          // Random days on market between 10-60 days
          daysOnMarket: Math.floor(10 + Math.random() * 50),
          
          // Determine price competitiveness
          priceCompetitiveness: determinePriceCompetitiveness(vehicle.price, similarVehicles),
          
          // Random market trend
          marketTrend: ['rising', 'falling', 'stable'][Math.floor(Math.random() * 3)] as 'rising' | 'falling' | 'stable',
          
          // Popular features
          popularFeatures: generatePopularFeatures(vehicle),
          
          // Count of similar vehicles
          similarCount: similarVehicles.length > 0 ? similarVehicles.length : Math.floor(5 + Math.random() * 20)
        };
        
        setMarketData(mockMarketData);
        setLoading(false);
      }, 1000);
    };
    
    generateMarketInsights();
  }, [vehicle, similarVehicles]);

  // Helper function to determine price competitiveness
  const determinePriceCompetitiveness = (price: number, similarVehicles: Vehicle[]): 'excellent' | 'good' | 'fair' | 'high' => {
    if (similarVehicles.length === 0) {
      // Random competitiveness if no similar vehicles
      return ['excellent', 'good', 'fair', 'high'][Math.floor(Math.random() * 4)] as 'excellent' | 'good' | 'fair' | 'high';
    }
    
    const avgPrice = similarVehicles.reduce((sum, v) => sum + v.price, 0) / similarVehicles.length;
    const ratio = price / avgPrice;
    
    if (ratio < 0.9) return 'excellent';
    if (ratio < 1.0) return 'good';
    if (ratio < 1.1) return 'fair';
    return 'high';
  };
  
  // Helper function to generate popular features
  const generatePopularFeatures = (vehicle: Vehicle): string[] => {
    const allFeatures = [
      'Bluetooth', 'Navigation', 'Backup Camera', 'Leather Seats', 'Sunroof',
      'Heated Seats', 'Apple CarPlay', 'Android Auto', 'Keyless Entry',
      'Blind Spot Monitoring', 'Lane Departure Warning', 'Adaptive Cruise Control'
    ];
    
    // Get 3-5 random features
    const count = 3 + Math.floor(Math.random() * 3);
    const shuffled = [...allFeatures].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Insights</h3>
        <div className="flex justify-center items-center h-40">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  if (!marketData) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Market Insights</h3>
        <p className="text-gray-600">No market data available for this vehicle.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Insights</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div className="bg-gray-50 p-3 rounded-md">
          <h4 className="text-sm font-medium text-gray-500">Average Market Price</h4>
          <p className="text-xl font-bold text-gray-900">${marketData.averagePrice.toLocaleString()}</p>
          <p className="text-sm text-gray-600">
            Range: ${marketData.priceRange.min.toLocaleString()} - ${marketData.priceRange.max.toLocaleString()}
          </p>
        </div>
        
        <div className="bg-gray-50 p-3 rounded-md">
          <h4 className="text-sm font-medium text-gray-500">Price Competitiveness</h4>
          <p className={`text-xl font-bold ${
            marketData.priceCompetitiveness === 'excellent' ? 'text-green-600' :
            marketData.priceCompetitiveness === 'good' ? 'text-blue-600' :
            marketData.priceCompetitiveness === 'fair' ? 'text-yellow-600' :
            'text-red-600'
          }`}>
            {marketData.priceCompetitiveness.charAt(0).toUpperCase() + marketData.priceCompetitiveness.slice(1)}
          </p>
          <p className="text-sm text-gray-600">
            {marketData.priceCompetitiveness === 'excellent' && 'Great deal compared to similar vehicles'}
            {marketData.priceCompetitiveness === 'good' && 'Good price for this vehicle'}
            {marketData.priceCompetitiveness === 'fair' && 'Average price for this vehicle'}
            {marketData.priceCompetitiveness === 'high' && 'Higher than average for similar vehicles'}
          </p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div className="bg-gray-50 p-3 rounded-md">
          <h4 className="text-sm font-medium text-gray-500">Days on Market</h4>
          <p className="text-xl font-bold text-gray-900">{marketData.daysOnMarket} days</p>
          <p className="text-sm text-gray-600">
            {marketData.daysOnMarket < 20 
              ? 'Selling faster than average' 
              : marketData.daysOnMarket > 40 
                ? 'Selling slower than average' 
                : 'Average time on market'}
          </p>
        </div>
        
        <div className="bg-gray-50 p-3 rounded-md">
          <h4 className="text-sm font-medium text-gray-500">Market Trend</h4>
          <p className={`text-xl font-bold flex items-center ${
            marketData.marketTrend === 'rising' ? 'text-red-600' :
            marketData.marketTrend === 'falling' ? 'text-green-600' :
            'text-gray-600'
          }`}>
            {marketData.marketTrend.charAt(0).toUpperCase() + marketData.marketTrend.slice(1)}
            {marketData.marketTrend === 'rising' && (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clipRule="evenodd" />
              </svg>
            )}
            {marketData.marketTrend === 'falling' && (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M12 13a1 1 0 100 2h5a1 1 0 001-1v-5a1 1 0 10-2 0v2.586l-4.293-4.293a1 1 0 00-1.414 0L8 9.586l-4.293-4.293a1 1 0 00-1.414 1.414l5 5a1 1 0 001.414 0L11 9.414 14.586 13H12z" clipRule="evenodd" />
              </svg>
            )}
            {marketData.marketTrend === 'stable' && (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a1 1 0 01-1 1H3a1 1 0 110-2h14a1 1 0 011 1z" clipRule="evenodd" />
              </svg>
            )}
          </p>
          <p className="text-sm text-gray-600">
            {marketData.marketTrend === 'rising' && 'Prices are trending upward'}
            {marketData.marketTrend === 'falling' && 'Prices are trending downward'}
            {marketData.marketTrend === 'stable' && 'Prices are relatively stable'}
          </p>
        </div>
      </div>
      
      <div className="bg-gray-50 p-3 rounded-md mb-4">
        <h4 className="text-sm font-medium text-gray-500">Popular Features in Similar Vehicles</h4>
        <div className="flex flex-wrap gap-2 mt-2">
          {marketData.popularFeatures.map((feature, index) => (
            <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {feature}
            </span>
          ))}
        </div>
      </div>
      
      <div className="text-sm text-gray-600">
        <p>Based on {marketData.similarCount} similar {vehicle.make} {vehicle.model} vehicles in your area.</p>
        <p className="mt-1 text-xs text-gray-500">
          *Market insights are estimates and may vary based on location, vehicle condition, and other factors.
        </p>
      </div>
    </div>
  );
};

export default MarketInsights;
