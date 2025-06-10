import React from 'react';
import { Vehicle } from '@/types';
import { LineChart, BarChart, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';

interface MarketAnalysisProps {
  vehicle: Vehicle;
  className?: string;
}

const MarketAnalysis: React.FC<MarketAnalysisProps> = ({ vehicle, className = '' }) => {
  // Mock data for demo purposes
  const marketPrice = vehicle.price * 1.05;
  const greatPrice = vehicle.price * 0.95;
  const priceHistory = [1, 0.98, 0.99, 0.97, 1.01, 0.95].map((factor, i) => ({
    month: i,
    price: vehicle.price * factor,
  }));
  const depreciation = [
    { year: 0, value: vehicle.price },
    { year: 1, value: vehicle.price * 0.85 },
    { year: 2, value: vehicle.price * 0.75 },
    { year: 3, value: vehicle.price * 0.68 },
    { year: 4, value: vehicle.price * 0.60 },
  ];

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="flex items-center mb-6">
        <LineChart className="h-6 w-6 text-primary-600 mr-3" />
        <h2 className="text-xl font-semibold text-gray-900">Market Analysis</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Price Trend Chart */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="font-medium text-gray-800 mb-4">Price History (6 Months)</h3>
          <div className="h-48 w-full bg-gray-50 rounded-md p-2">
             <svg width="100%" height="100%" viewBox="0 0 300 150">
                <line x1="10" y1="140" x2="290" y2="140" stroke="#d1d5db" strokeWidth="1" />
                <line x1="10" y1="10" x2="10" y2="140" stroke="#d1d5db" strokeWidth="1" />
                <polyline
                  fill="none"
                  stroke="#0284c7"
                  strokeWidth="2"
                  points="10,75 60,60 110,80 160,50 210,70 260,40"
                />
             </svg>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>6 months ago</span>
            <span>Today</span>
          </div>
        </div>

        {/* Market Value Comparison */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="font-medium text-gray-800 mb-4">Market Value</h3>
          <div className="space-y-3">
             <PriceBar label="Great Deal" price={greatPrice} color="bg-green-500" vehiclePrice={vehicle.price} />
             <PriceBar label="Listing Price" price={vehicle.price} color="bg-blue-500" vehiclePrice={vehicle.price} isCurrent />
             <PriceBar label="Market Average" price={marketPrice} color="bg-orange-500" vehiclePrice={vehicle.price} />
          </div>
           <p className="text-sm text-gray-600 mt-4">
            This vehicle's price is <span className="font-semibold text-green-600">5% below</span> the market average.
          </p>
        </div>

        {/* Depreciation Forecast */}
        <div className="md:col-span-2 border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium text-gray-800">5-Year Depreciation Forecast</h3>
            <TrendingDown className="h-5 w-5 text-red-500" />
          </div>
          <div className="flex justify-between items-end h-32 px-4">
            {depreciation.map((d) => (
              <div key={d.year} className="flex flex-col items-center">
                <div 
                  className="w-8 bg-primary-300 rounded-t-md"
                  style={{ height: `${(d.value / vehicle.price) * 100}%` }}
                ></div>
                <span className="text-xs text-gray-600 mt-1">{d.year === 0 ? 'Today' : `Yr ${d.year}`}</span>
              </div>
            ))}
          </div>
          <p className="text-sm text-gray-600 mt-4">
            Estimated to retain <span className="font-semibold text-green-600">60%</span> of its value after 5 years.
          </p>
        </div>
      </div>
    </div>
  );
};

const PriceBar = ({ label, price, color, vehiclePrice, isCurrent = false }: any) => {
  const marketPrice = vehiclePrice * 1.05;
  const greatPrice = vehiclePrice * 0.95;
  const range = marketPrice - greatPrice;
  const position = Math.max(0, Math.min(100, ((price - greatPrice) / range) * 100));

  return (
    <div>
        <div className="flex justify-between text-sm mb-1">
            <span className={`font-medium ${isCurrent ? 'text-blue-700' : 'text-gray-600'}`}>{label}</span>
            <span className={`font-semibold ${isCurrent ? 'text-blue-700' : 'text-gray-800'}`}>
              ${price.toLocaleString()}
            </span>
        </div>
      <div className="h-4 w-full bg-gray-200 rounded-full">
        <div className="relative h-full">
          <div className={`h-full rounded-full ${color}`} style={{ width: `${position}%` }}></div>
          {isCurrent && (
            <div className="absolute top-[-4px] h-6 w-1 bg-gray-800" style={{ left: `calc(${position}% - 2px)` }}>
                <div className="absolute top-[-22px] left-1/2 -translate-x-1/2 px-2 py-0.5 bg-gray-800 text-white text-xs rounded-md">
                    Current
                </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MarketAnalysis; 