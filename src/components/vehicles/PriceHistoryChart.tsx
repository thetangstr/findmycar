import React, { useEffect, useState } from 'react';
import { PriceHistoryEntry, PriceHistoryService } from '@/utils/priceHistory';
import { Vehicle } from '@/types';

interface PriceHistoryChartProps {
  vehicle: Vehicle;
}

/**
 * Component for displaying vehicle price history
 * 
 * Features:
 * - Line chart showing price changes over time
 * - Price trend indicators
 * - Min/max price highlighting
 */
const PriceHistoryChart: React.FC<PriceHistoryChartProps> = ({ vehicle }) => {
  const [priceHistory, setPriceHistory] = useState<PriceHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get price history for this vehicle
    let history = PriceHistoryService.getVehiclePriceHistory(vehicle.id);
    
    // If no history exists, generate mock data for demo purposes
    if (history.length === 0) {
      history = PriceHistoryService.generateMockPriceHistory(vehicle.id, vehicle.price);
      
      // Save the generated history
      const mockHistory = {
        vehicleId: vehicle.id,
        history
      };
      
      const storedHistories = localStorage.getItem('price_histories');
      const histories = storedHistories ? JSON.parse(storedHistories) : [];
      histories.push(mockHistory);
      localStorage.setItem('price_histories', JSON.stringify(histories));
    }
    
    // Update price history with current price
    PriceHistoryService.updatePriceHistory(vehicle);
    
    // Get updated history
    history = PriceHistoryService.getVehiclePriceHistory(vehicle.id);
    setPriceHistory(history);
    setLoading(false);
  }, [vehicle]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-40">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (priceHistory.length === 0) {
    return (
      <div className="text-center p-4 bg-gray-50 rounded-md">
        <p className="text-gray-600">No price history available for this vehicle.</p>
      </div>
    );
  }

  // Calculate min and max prices
  const prices = priceHistory.map(entry => entry.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  
  // Calculate price change
  const firstPrice = priceHistory[0].price;
  const lastPrice = priceHistory[priceHistory.length - 1].price;
  const priceChange = lastPrice - firstPrice;
  const priceChangePercent = (priceChange / firstPrice) * 100;
  
  // Determine if price is trending up, down, or stable
  const priceTrend = priceChange > 0 ? 'up' : priceChange < 0 ? 'down' : 'stable';

  // Calculate chart dimensions
  const chartHeight = 120;
  const chartWidth = 100; // percentage width
  
  // Calculate y-axis scale
  const yMin = Math.floor(minPrice * 0.95); // Add 5% padding
  const yMax = Math.ceil(maxPrice * 1.05);
  const yRange = yMax - yMin;
  
  // Generate chart points
  const points = priceHistory.map((entry, index) => {
    const x = (index / (priceHistory.length - 1)) * chartWidth;
    const y = chartHeight - ((entry.price - yMin) / yRange) * chartHeight;
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">Price History</h3>
      
      <div className="flex justify-between items-center mb-4">
        <div>
          <span className="text-sm text-gray-500">Starting Price:</span>
          <span className="ml-1 font-medium">${firstPrice.toLocaleString()}</span>
        </div>
        <div>
          <span className="text-sm text-gray-500">Current Price:</span>
          <span className="ml-1 font-medium">${lastPrice.toLocaleString()}</span>
        </div>
        <div>
          <span className="text-sm text-gray-500">Change:</span>
          <span className={`ml-1 font-medium ${
            priceTrend === 'up' ? 'text-red-600' : 
            priceTrend === 'down' ? 'text-green-600' : 
            'text-gray-600'
          }`}>
            {priceChange > 0 ? '+' : ''}{priceChange.toLocaleString()} 
            ({priceChangePercent > 0 ? '+' : ''}{priceChangePercent.toFixed(1)}%)
            {priceTrend === 'up' && (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 inline-block ml-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            )}
            {priceTrend === 'down' && (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 inline-block ml-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            )}
          </span>
        </div>
      </div>
      
      <div className="relative h-32 w-full">
        {/* Chart */}
        <svg className="w-full h-full" viewBox={`0 0 ${chartWidth} ${chartHeight}`} preserveAspectRatio="none">
          {/* Price line */}
          <polyline
            points={points}
            fill="none"
            stroke={priceTrend === 'up' ? '#ef4444' : priceTrend === 'down' ? '#10b981' : '#6b7280'}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          
          {/* Fill area under the line */}
          <polyline
            points={`0,${chartHeight} ${points} ${chartWidth},${chartHeight}`}
            fill={priceTrend === 'up' ? 'rgba(239, 68, 68, 0.1)' : priceTrend === 'down' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(107, 114, 128, 0.1)'}
            stroke="none"
          />
          
          {/* Highlight min and max points */}
          {priceHistory.map((entry, index) => {
            if (entry.price === minPrice || entry.price === maxPrice) {
              const x = (index / (priceHistory.length - 1)) * chartWidth;
              const y = chartHeight - ((entry.price - yMin) / yRange) * chartHeight;
              return (
                <circle
                  key={index}
                  cx={x}
                  cy={y}
                  r="3"
                  fill={entry.price === minPrice ? '#10b981' : '#ef4444'}
                  stroke="#ffffff"
                  strokeWidth="1"
                />
              );
            }
            return null;
          })}
        </svg>
        
        {/* Y-axis labels */}
        <div className="absolute top-0 left-0 h-full flex flex-col justify-between text-xs text-gray-500">
          <span>${yMax.toLocaleString()}</span>
          <span>${yMin.toLocaleString()}</span>
        </div>
      </div>
      
      {/* X-axis labels */}
      <div className="flex justify-between text-xs text-gray-500 mt-1">
        <span>{new Date(priceHistory[0].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
        {priceHistory.length > 2 && (
          <span>{new Date(priceHistory[Math.floor(priceHistory.length / 2)].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
        )}
        <span>{new Date(priceHistory[priceHistory.length - 1].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
      </div>
      
      <div className="mt-4 text-sm text-gray-500">
        <p>
          {priceTrend === 'up' && 'This vehicle has increased in price over time.'}
          {priceTrend === 'down' && 'This vehicle has decreased in price over time.'}
          {priceTrend === 'stable' && 'This vehicle has maintained a stable price.'}
          {' '}
          {minPrice !== lastPrice && maxPrice !== lastPrice && `The price has ranged from $${minPrice.toLocaleString()} to $${maxPrice.toLocaleString()}.`}
        </p>
      </div>
    </div>
  );
};

export default PriceHistoryChart;
