import React from 'react';
import { Vehicle, AppreciationData } from '@/types';
import { LineChart, BarChart, TrendingUp, TrendingDown, DollarSign, ArrowUpRight } from 'lucide-react';

// Helper formatting functions
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(amount);
};

const formatPercentage = (percent: number): string => {
  return Math.round(percent).toString();
};

interface MarketAnalysisProps {
  vehicle: Vehicle;
  className?: string;
}

const MarketAnalysis: React.FC<MarketAnalysisProps> = ({ vehicle, className = '' }) => {
  // Determine if this is a classic/appreciation vehicle
  const isClassicVehicle = !!vehicle.appreciationData;
  
  // Market price is either higher for classic cars or slightly higher for regular cars
  const marketPrice = isClassicVehicle
    ? vehicle.price * 1.08 // Classic cars tend to be undervalued compared to market
    : vehicle.price * 1.05;
  
  const greatPrice = vehicle.price * 0.95;
  
  // Price history - show appreciation for classics, depreciation for modern cars
  const priceHistory = isClassicVehicle
    ? [0.92, 0.95, 0.97, 1.00, 1.03, 1.05].map((factor, i) => ({
        month: i,
        price: vehicle.price * factor,
      }))
    : [1, 0.98, 0.99, 0.97, 1.01, 0.95].map((factor, i) => ({
        month: i,
        price: vehicle.price * factor,
      }));
  
  // Value forecast - either appreciation or depreciation based on vehicle type
  const valueProjection = isClassicVehicle
    ? [
        { year: 0, value: vehicle.price },
        { year: 1, value: vehicle.price * 1.05 },
        { year: 2, value: vehicle.price * 1.12 },
        { year: 3, value: vehicle.price * 1.18 },
        { year: 4, value: vehicle.price * 1.25 },
      ]
    : [
        { year: 0, value: vehicle.price },
        { year: 1, value: vehicle.price * 0.85 },
        { year: 2, value: vehicle.price * 0.75 },
        { year: 3, value: vehicle.price * 0.68 },
        { year: 4, value: vehicle.price * 0.60 },
      ];
      
  // For classic cars with appreciation data, use the actual forecast values
  if (vehicle.appreciationData) {
    const { purchasePrice, fiveYearForecast } = vehicle.appreciationData;
    const yearlyRate = Math.pow(fiveYearForecast / purchasePrice, 1/5);
    
    valueProjection[0] = { year: 0, value: purchasePrice };
    valueProjection[1] = { year: 1, value: purchasePrice * Math.pow(yearlyRate, 1) };
    valueProjection[2] = { year: 2, value: purchasePrice * Math.pow(yearlyRate, 2) };
    valueProjection[3] = { year: 3, value: purchasePrice * Math.pow(yearlyRate, 3) };
    valueProjection[4] = { year: 4, value: purchasePrice * Math.pow(yearlyRate, 4) };
    valueProjection[5] = { year: 5, value: fiveYearForecast };
  }

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
                
                {/* Y-axis price labels */}
                <text x="5" y="140" fontSize="8" textAnchor="end">${(vehicle.price * 0.9).toLocaleString(undefined, {maximumFractionDigits: 0})}</text>
                <text x="5" y="95" fontSize="8" textAnchor="end">${(vehicle.price * 0.95).toLocaleString(undefined, {maximumFractionDigits: 0})}</text>
                <text x="5" y="50" fontSize="8" textAnchor="end">${(vehicle.price * 1.0).toLocaleString(undefined, {maximumFractionDigits: 0})}</text>
                <text x="5" y="10" fontSize="8" textAnchor="end">${(vehicle.price * 1.05).toLocaleString(undefined, {maximumFractionDigits: 0})}</text>
                
                {/* Horizontal grid lines */}
                <line x1="10" y1="95" x2="290" y2="95" stroke="#d1d5db" strokeWidth="0.5" strokeDasharray="2" />
                <line x1="10" y1="50" x2="290" y2="50" stroke="#d1d5db" strokeWidth="0.5" strokeDasharray="2" />
                
                <polyline
                  fill="none"
                  stroke="#0284c7"
                  strokeWidth="2"
                  points="10,75 60,60 110,80 160,50 210,40 260,30"
                />
                
                {/* Price data points with values */}
                <circle cx="10" cy="75" r="3" fill="#0284c7" />
                <circle cx="60" cy="60" r="3" fill="#0284c7" />
                <circle cx="110" cy="80" r="3" fill="#0284c7" />
                <circle cx="160" cy="50" r="3" fill="#0284c7" />
                <circle cx="210" cy="40" r="3" fill="#0284c7" />
                <circle cx="260" cy="30" r="3" fill="#0284c7" />
                
                {/* Current price indicator */}
                <text x="260" y="20" fontSize="8" textAnchor="middle" fill="#0284c7" fontWeight="bold">
                  ${(vehicle.price * 1.04).toLocaleString(undefined, {maximumFractionDigits: 0})}
                </text>
             </svg>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>6 months ago</span>
            <span>Today</span>
          </div>
        </div>

        {/* Value Forecast - Shows either appreciation or depreciation */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="font-medium text-gray-800 mb-4">
            Appreciation Forecast
          </h3>
          <div className="h-48 w-full bg-gray-50 rounded-md p-2">
            <svg width="100%" height="100%" viewBox="0 0 300 150">
              <line x1="10" y1="140" x2="290" y2="140" stroke="#d1d5db" strokeWidth="1" />
              <line x1="10" y1="10" x2="10" y2="140" stroke="#d1d5db" strokeWidth="1" />
              {/* Y-axis labels */}
              <text x="5" y="140" fontSize="8" textAnchor="end">{formatCurrency(0)}</text>
              <text x="5" y="10" fontSize="8" textAnchor="end">
                {formatCurrency(vehicle.appreciationData ? 
                  Math.max(vehicle.price, vehicle.appreciationData.fiveYearForecast) : 
                  vehicle.price)}
              </text>
            
              {/* Always show positive appreciation */}
              <polyline
                fill="none"
                stroke="#16a34a"
                strokeWidth="2"
                points={
                  [
                    { year: 0, value: vehicle.price },
                    { year: 1, value: vehicle.price * 1.05 },
                    { year: 2, value: vehicle.price * 1.12 },
                    { year: 3, value: vehicle.price * 1.20 },
                    { year: 4, value: vehicle.price * 1.28 },
                    { year: 5, value: vehicle.price * 1.35 }
                  ].map((point, i) => {
                    const x = 10 + (i * 56); // Adjust for 5 years (0-5)
                    const maxValue = vehicle.price * 1.4; // Maximum value for scale
                    const normalizedValue = point.value / maxValue;
                    const y = 140 - (normalizedValue * 130);
                    return `${x},${y}`;
                  }).join(' ')
                }
              />
              
              {/* Add price markers */}
              {[
                { year: 0, value: vehicle.price },
                { year: 1, value: vehicle.price * 1.05 },
                { year: 2, value: vehicle.price * 1.12 },
                { year: 3, value: vehicle.price * 1.20 },
                { year: 4, value: vehicle.price * 1.28 },
                { year: 5, value: vehicle.price * 1.35 }
              ].map((point, i) => {
                const x = 10 + (i * 56);
                const maxValue = vehicle.price * 1.4;
                const normalizedValue = point.value / maxValue;
                const y = 140 - (normalizedValue * 130);
                
                return (
                  <g key={i}>
                    <circle cx={x} cy={y} r="3" fill="#16a34a" />
                    {i === 0 || i === 5 ? (
                      <text x={x} y={y-10} fontSize="8" textAnchor="middle" fill="#16a34a">
                        ${point.value.toLocaleString(undefined, {maximumFractionDigits: 0})}
                      </text>
                    ) : null}
                  </g>
                );
              })}
            </svg>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>Now</span>
            <span>1 yr</span>
            <span>2 yrs</span>
            <span>3 yrs</span>
            <span>4 yrs</span>
            <span>5 yrs</span>
          </div>
          <div className="flex items-center mt-4">
            <>
              <TrendingUp className="h-5 w-5 text-green-500 mr-2" />
              <span className="text-sm text-gray-700">
                Est. {formatPercentage(35)}% appreciation over 5 years
                <span className="ml-1 text-green-600 font-medium">(6.2% annually)</span>
              </span>
            </>
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
            This vehicle&apos;s price is <span className="font-semibold text-green-600">5% below</span> the market average.
          </p>
        </div>

        {/* Market Demand */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="font-medium text-gray-800 mb-4">Market Demand Analysis</h3>
          
          {/* Demand Score */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Demand Score</span>
              <span className="text-sm font-bold text-orange-600">87/100</span>
            </div>
            <div className="h-3 w-full bg-gray-200 rounded-full">
              <div className="h-full rounded-full bg-gradient-to-r from-orange-400 to-orange-600" style={{ width: '87%' }}></div>
            </div>
          </div>
          
          {/* Key Market Metrics */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="p-3 bg-orange-50 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-600">Avg. Days Listed</span>
                <ArrowUpRight className="h-4 w-4 text-green-500" />
              </div>
              <div className="mt-1 flex items-end justify-between">
                <span className="text-xl font-bold text-gray-800">12</span>
                <span className="text-xs text-green-600">-45% vs. avg</span>
              </div>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-600">Listing Views</span>
                <ArrowUpRight className="h-4 w-4 text-green-500" />
              </div>
              <div className="mt-1 flex items-end justify-between">
                <span className="text-xl font-bold text-gray-800">46</span>
                <span className="text-xs text-green-600">+32% vs. avg</span>
              </div>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-600">Save Rate</span>
                <ArrowUpRight className="h-4 w-4 text-green-500" />
              </div>
              <div className="mt-1 flex items-end justify-between">
                <span className="text-xl font-bold text-gray-800">4.8%</span>
                <span className="text-xs text-green-600">+1.9% vs. avg</span>
              </div>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-600">Inquiries</span>
                <ArrowUpRight className="h-4 w-4 text-green-500" />
              </div>
              <div className="mt-1 flex items-end justify-between">
                <span className="text-xl font-bold text-gray-800">7</span>
                <span className="text-xs text-green-600">+75% vs. avg</span>
              </div>
            </div>
          </div>
          
          {/* Regional Demand Map */}
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Regional Interest</h4>
            <div className="bg-gray-50 p-3 rounded-lg h-32 flex items-center justify-center overflow-hidden">
              <svg width="280" height="100" viewBox="0 0 280 100">
                {/* Simplified USA map outline */}
                <path d="M10,40 C20,38 30,35 40,40 C50,45 60,35 70,30 C80,25 90,20 100,25 C110,30 120,35 130,30 C140,25 150,20 160,25 C170,30 180,35 190,30 C200,25 210,20 220,25 C230,30 240,35 250,40 C260,45 270,40 280,35" stroke="#d1d5db" fill="none" strokeWidth="1" />
                {/* Hotspots representing high demand regions */}
                <circle cx="50" cy="38" r="8" fill="rgba(249, 115, 22, 0.2)" />
                <circle cx="50" cy="38" r="4" fill="rgba(249, 115, 22, 0.4)" />
                <circle cx="130" cy="30" r="10" fill="rgba(249, 115, 22, 0.2)" />
                <circle cx="130" cy="30" r="5" fill="rgba(249, 115, 22, 0.4)" />
                <circle cx="200" cy="25" r="12" fill="rgba(249, 115, 22, 0.2)" />
                <circle cx="200" cy="25" r="6" fill="rgba(249, 115, 22, 0.4)" />
                
                {/* City labels */}
                <text x="50" y="50" fontSize="6" textAnchor="middle" fill="#4b5563">Chicago</text>
                <text x="130" y="42" fontSize="6" textAnchor="middle" fill="#4b5563">New York</text>
                <text x="200" y="37" fontSize="6" textAnchor="middle" fill="#4b5563">Los Angeles</text>
              </svg>
            </div>
          </div>
          
          {/* Market Insights */}
          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="flex items-start">
              <BarChart className="h-5 w-5 text-orange-500 mr-2 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-800 mb-1">
                  <span className="text-orange-600 font-bold">High demand</span> for this {vehicle.make} {vehicle.model}
                </p>
                <p className="text-xs text-gray-600">
                  This vehicle is receiving {isClassicVehicle ? '86% more interest' : '32% more interest'} than similar listings. 
                  {isClassicVehicle 
                    ? 'Collector interest is driving high engagement from enthusiasts.' 
                    : 'Strong local demand suggests reduced negotiation room.'
                  }
                </p>
                
                <div className="mt-2 flex items-center">
                  <div className="w-3 h-3 rounded-full bg-green-500 mr-1.5"></div>
                  <span className="text-xs text-green-700 font-medium">
                    {isClassicVehicle ? 'Trending among collectors' : 'Higher than average market interest'}
                  </span>
                </div>
              </div>
            </div>
          </div>
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