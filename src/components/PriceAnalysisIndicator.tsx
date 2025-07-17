import React, { useState, useEffect } from 'react';
import { Vehicle } from '@/types';
import { PriceAnalysis, DealRating, getPriceAnalysis } from '@/services/kbbService';
import LoadingSpinner from './LoadingSpinner';
import { useToastContext } from '@/contexts/ToastContext';

interface PriceAnalysisIndicatorProps {
  vehicle: Vehicle;
  className?: string;
  compact?: boolean; // For vehicle cards vs detail pages
}

const PriceAnalysisIndicator: React.FC<PriceAnalysisIndicatorProps> = ({ 
  vehicle, 
  className = '',
  compact = false 
}) => {
  const [analysis, setAnalysis] = useState<PriceAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { error: showError } = useToastContext();

  useEffect(() => {
    const fetchPriceAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);
        const priceAnalysis = await getPriceAnalysis(vehicle);
        setAnalysis(priceAnalysis);
      } catch (err) {
        console.error('Error fetching price analysis:', err);
        setError('Unable to load price analysis');
        showError(
          'Price Analysis Unavailable',
          'Unable to load market pricing data for this vehicle.',
          { duration: 5000 }
        );
      } finally {
        setLoading(false);
      }
    };

    fetchPriceAnalysis();
  }, [vehicle, showError]);

  if (loading) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <LoadingSpinner size="sm" />
        <span className="text-sm text-gray-600">Analyzing price...</span>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className={`text-sm text-gray-500 ${className}`}>
        Price analysis unavailable
      </div>
    );
  }

  const { dealRating, marketValue } = analysis;

  const getRatingStyles = (rating: DealRating['rating']) => {
    switch (rating) {
      case 'great_deal':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'good_deal':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'fair_price':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200';
      case 'high_price':
        return 'bg-orange-50 text-orange-700 border-orange-200';
      case 'overpriced':
        return 'bg-red-50 text-red-700 border-red-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  const getRatingText = (rating: DealRating['rating']) => {
    switch (rating) {
      case 'great_deal':
        return 'Great Deal';
      case 'good_deal':
        return 'Good Deal';
      case 'fair_price':
        return 'Fair Price';
      case 'high_price':
        return 'High Price';
      case 'overpriced':
        return 'Overpriced';
      default:
        return 'Unknown';
    }
  };

  const getRatingIcon = (rating: DealRating['rating']) => {
    switch (rating) {
      case 'great_deal':
        return '🔥';
      case 'good_deal':
        return '👍';
      case 'fair_price':
        return '💡';
      case 'high_price':
        return '⚠️';
      case 'overpriced':
        return '❌';
      default:
        return '❓';
    }
  };

  if (compact) {
    return (
      <div className={`inline-flex items-center gap-1 ${className}`}>
        <div 
          className={`px-2 py-1 rounded-full text-xs font-medium border ${getRatingStyles(dealRating.rating)}`}
          title={dealRating.marketComparison}
        >
          <span className="mr-1">{getRatingIcon(dealRating.rating)}</span>
          {getRatingText(dealRating.rating)}
        </div>
        {Math.abs(dealRating.savings) > 1000 && (
          <span className={`text-xs font-medium ${
            dealRating.savings > 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {dealRating.savings > 0 ? '-' : '+'}${Math.abs(dealRating.savings).toLocaleString()}
          </span>
        )}
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border shadow-sm p-4 ${className}`}>
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Price Analysis</h3>
          <p className="text-sm text-gray-600">Based on market data</p>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getRatingStyles(dealRating.rating)}`}>
          <span className="mr-1">{getRatingIcon(dealRating.rating)}</span>
          {getRatingText(dealRating.rating)}
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Listing Price</span>
          <span className="font-semibold text-lg">
            ${analysis.listingPrice.toLocaleString()}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Market Value</span>
          <span className="font-medium">
            ${marketValue.fairMarketValue.toLocaleString()}
          </span>
        </div>

        {Math.abs(dealRating.savings) > 500 && (
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">
              {dealRating.savings > 0 ? 'Savings' : 'Premium'}
            </span>
            <span className={`font-medium ${
              dealRating.savings > 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {dealRating.savings > 0 ? '-' : '+'}${Math.abs(dealRating.savings).toLocaleString()}
            </span>
          </div>
        )}

        <div className="pt-2 border-t">
          <p className="text-sm text-gray-700">{dealRating.marketComparison}</p>
          {marketValue.dataSource === 'mock' && (
            <p className="text-xs text-gray-500 mt-1">
              ⓘ Based on estimated market data
            </p>
          )}
        </div>

        {/* Market value breakdown */}
        <details className="mt-3">
          <summary className="text-sm text-gray-600 cursor-pointer hover:text-gray-800">
            View market value breakdown
          </summary>
          <div className="mt-2 space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Excellent condition</span>
              <span>${marketValue.excellentCondition.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Good condition</span>
              <span>${marketValue.goodCondition.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Fair condition</span>
              <span>${marketValue.fairCondition.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Trade-in value</span>
              <span>${marketValue.tradeInValue.toLocaleString()}</span>
            </div>
          </div>
        </details>
      </div>
    </div>
  );
};

export default PriceAnalysisIndicator;