import React, { useState, useEffect } from 'react';
import { Vehicle } from '@/types';
import { generateBuyerAnalysis, BuyerAnalysis, isGeminiAvailable } from '@/services/geminiService';

interface AIInsightButtonProps {
  vehicle: Vehicle;
  className?: string;
}

const AIInsightButton: React.FC<AIInsightButtonProps> = ({ vehicle, className = '' }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<BuyerAnalysis | null>(null);
  const [showModal, setShowModal] = useState(false);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const result = await generateBuyerAnalysis(vehicle);
      setAnalysis(result);
      setShowModal(true);
    } catch (error) {
      console.error('Error generating analysis:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const closeModal = () => {
    setShowModal(false);
  };

  // Handle escape key press and focus management
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && showModal) {
        closeModal();
      }
    };

    if (showModal) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
      
      // Focus the modal for screen readers
      const modalElement = document.querySelector('[role="dialog"]') as HTMLElement;
      if (modalElement) {
        modalElement.focus();
      }
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      // Restore body scroll
      document.body.style.overflow = 'unset';
    };
  }, [showModal]);

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'buy': return 'text-green-600 bg-green-50 border-green-200';
      case 'consider': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'avoid': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    if (score >= 4) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <>
      <button
        onClick={handleAnalyze}
        disabled={isAnalyzing}
        className={`inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      >
        {isAnalyzing ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Analyzing...
          </>
        ) : (
          <>
            <svg className="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            {isGeminiAvailable() ? 'AI Insights' : 'Vehicle Analysis'}
          </>
        )}
      </button>

      {/* Analysis Modal */}
      {showModal && analysis && (
        <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black bg-opacity-50">
          <div 
            className="relative w-full max-w-2xl p-6 mx-4 bg-white rounded-lg shadow-xl" 
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-headline"
          >
            {!isGeminiAvailable() && (
              <div className="mb-4 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
                <p className="text-sm text-yellow-700">Note: AI insights powered by Google Gemini are not available. Displaying pre-analyzed vehicle recommendations.</p>
              </div>
            )}
            <div className="p-6">
              {/* Header */}
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 id="modal-headline" className="text-2xl font-bold text-gray-900 mb-2">
                    🤖 AI Buyer's Analysis
                  </h2>
                  <p className="text-gray-600">
                    {vehicle.year} {vehicle.make} {vehicle.model}
                  </p>
                </div>
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  aria-label="Close modal"
                  title="Close (ESC)"
                >
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Recommendation Badge and Score */}
              <div className="flex items-center gap-4 mb-6">
                <div className={`px-4 py-2 rounded-lg border-2 font-semibold uppercase tracking-wider ${getRecommendationColor(analysis.recommendation)}`}>
                  {analysis.recommendation}
                </div>
                <div className="flex items-center">
                  <span className="text-gray-600 mr-2">Score:</span>
                  <span className={`text-xl font-bold ${getScoreColor(analysis.score)}`}>
                    {analysis.score}/10
                  </span>
                </div>
              </div>

              {/* One-Liner Summary */}
              <div className="mb-6 italic text-center text-gray-700 border-l-4 border-primary-500 pl-4 py-2 bg-gray-50 rounded-r-lg">
                <p>"{analysis.oneLiner}"</p>
              </div>

              {/* Summary */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Summary</h3>
                <p className="text-gray-700 bg-gray-50 p-4 rounded-lg">
                  {analysis.summary}
                </p>
              </div>

              {/* Pros and Cons */}
              <div className="grid md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-green-700 mb-3 flex items-center">
                    <svg className="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Pros
                  </h3>
                  <ul className="space-y-2">
                    {analysis.pros.map((pro, index) => (
                      <li key={index} className="flex items-start text-gray-700">
                        <span className="text-green-500 mr-2 mt-1">•</span>
                        {pro}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-red-700 mb-3 flex items-center">
                    <svg className="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Cons
                  </h3>
                  <ul className="space-y-2">
                    {analysis.cons.map((con, index) => (
                      <li key={index} className="flex items-start text-gray-700">
                        <span className="text-red-500 mr-2 mt-1">•</span>
                        {con}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Price Analysis */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">💰 Price Analysis</h3>
                <p className="text-gray-700 bg-blue-50 p-4 rounded-lg border border-blue-200">
                  {analysis.priceAnalysis}
                </p>
              </div>

              {/* Market Position */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">📊 Market Position</h3>
                <p className="text-gray-700 bg-purple-50 p-4 rounded-lg border border-purple-200">
                  {analysis.marketPosition}
                </p>
              </div>

              {/* Footer */}
              <div className="border-t pt-4">
                <p className="text-sm text-gray-500 text-center">
                  ⚠️ This analysis is AI-generated for informational purposes only. 
                  Always consult with automotive professionals and conduct thorough inspections before purchasing.
                </p>
                <div className="flex justify-center gap-3 mt-4">
                  <button
                    onClick={closeModal}
                    className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    Close Analysis
                  </button>
                  <p className="text-xs text-gray-400 flex items-center">
                    Press <kbd className="px-2 py-1 text-xs bg-gray-100 rounded border">ESC</kbd> to close
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default AIInsightButton; 