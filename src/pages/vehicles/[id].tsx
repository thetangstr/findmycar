import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import Head from 'next/head';
import { GetStaticProps, GetStaticPaths } from 'next';
import { useVehicles } from '@/hooks/useVehicles';
import { useRecentlyViewed } from '@/hooks/useRecentlyViewed';
import CompareButton from '@/components/CompareButton';
import FavoriteButton from '@/components/FavoriteButton';
import AIInsightButton from '@/components/AIInsightButton';
import { getFallbackAnalysis, generateBuyerAnalysis, isGeminiAvailable, BuyerAnalysis } from '@/services/geminiService';
import ImageGallery from '@/components/vehicles/ImageGallery';
import SocialPostsCarousel from '@/components/SocialPostsCarousel';
import MarketAnalysis from '@/components/vehicles/MarketAnalysis';
import { useAuth } from '@/utils/auth';
import { Vehicle } from '@/types';
import { getFeaturedVehicles } from '@/services/featuredVehiclesService';
import { getHemmingsListings } from '@/services/scraperService';

interface VehicleDetailProps {
  vehicle: Vehicle | null;
  preloadedAnalysis?: BuyerAnalysis;
}

export default function VehicleDetail({ vehicle, preloadedAnalysis }: VehicleDetailProps) {
  const router = useRouter();
  const { getVehicleById } = useVehicles();
  const { addToRecentlyViewed } = useRecentlyViewed(getVehicleById);
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  
  // Find similar vehicles (same make, model, within 3 years of this vehicle's year)
  const [similarVehicles, setSimilarVehicles] = useState<Vehicle[]>([]);

  useEffect(() => {
    if (vehicle) {
      // Mock similar vehicles for demo
      const mockSimilar = [
        { ...vehicle, id: 'similar-1', price: vehicle.price * 1.05 },
        { ...vehicle, id: 'similar-2', price: vehicle.price * 0.98 },
        { ...vehicle, id: 'similar-3', price: vehicle.price * 1.12 },
      ];
      setSimilarVehicles(mockSimilar);
    }
  }, [vehicle]);
  
  // Add to recently viewed when the page loads
  useEffect(() => {
    if (vehicle && !loading) {
      addToRecentlyViewed(vehicle.id);
    }
  }, [vehicle, loading, addToRecentlyViewed]);
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700">Loading vehicle details...</h2>
        </div>
      </div>
    );
  }
  
  if (!vehicle) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Vehicle Not Found</h1>
          <p className="text-gray-600 mb-6">The vehicle you're looking for doesn't exist or has been removed.</p>
          <Link href="/search" className="btn btn-primary">
            Back to Search
          </Link>
        </div>
      </div>
    );
  }
  
  // Analysis state for the banner
  const [bannerAnalysis, setBannerAnalysis] = useState<BuyerAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  const generateAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      let result: BuyerAnalysis;
      
      // Force fallback analysis for the Porsche 911 to use our enhanced enthusiast analysis
      if (vehicle.id === 'ebay-porsche-1') {
        console.log('Using enhanced analysis for Porsche 911 Carrera 2');
        result = getFallbackAnalysis(vehicle as Vehicle);
      }
      // Use Gemini API if available, otherwise fall back to pre-generated analysis
      else if (isGeminiAvailable()) {
        result = await generateBuyerAnalysis(vehicle as Vehicle);
      } else {
        console.warn('Gemini API unavailable, using fallback analysis');
        result = getFallbackAnalysis(vehicle as Vehicle);
      }
      
      setBannerAnalysis(result);
    } catch (error) {
      console.error('Error generating analysis:', error);
      // If API call fails, use fallback analysis as backup
      const fallbackResult = getFallbackAnalysis(vehicle as Vehicle);
      setBannerAnalysis(fallbackResult);
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  // Determine if recommendation is positive when we have an analysis
  const isPositive = bannerAnalysis ? bannerAnalysis.recommendation !== 'avoid' : true;

  return (
    <>
      <Head>
        <title>{vehicle.year} {vehicle.make} {vehicle.model} | FindMyCar</title>
        <meta name="description" content={`${vehicle.year} ${vehicle.make} ${vehicle.model} with ${vehicle.mileage?.toLocaleString() || 'N/A'} miles for $${vehicle.price?.toLocaleString() || 'N/A'}`} />
      </Head>
      
      <div className="container mx-auto p-4">
        <div className="mb-6">
          <Link href="/search" className="text-primary-600 hover:text-primary-800 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            Back to Search
          </Link>
        </div>

        <div className="flex flex-wrap items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            {vehicle.year} {vehicle.make} {vehicle.model}
          </h1>
          <div className="flex space-x-2">
            <AIInsightButton vehicle={vehicle} />
            <FavoriteButton vehicleId={vehicle.id} />
            <CompareButton vehicleId={vehicle.id} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md overflow-hidden mb-8">
          {/* Advanced LLM Analysis Banner */}
          <div className="border-l-4 bg-blue-50 border-blue-500">
            {bannerAnalysis ? (
              // Show analysis results when available
              <>
                <div className={`px-6 py-3 text-center font-bold text-lg ${
                  isPositive ? 'text-green-800' : 'text-yellow-800'
                }`}>
                  {bannerAnalysis.recommendation.toUpperCase()}
                </div>
                <div className={`px-6 pb-4 text-sm leading-relaxed ${
                  isPositive ? 'text-green-700' : 'text-yellow-700'
                }`}>
                  <strong>🤖 Vehicle Analysis:</strong> {bannerAnalysis.oneLiner || bannerAnalysis.summary}
                </div>
              </>
            ) : (
              // Show generate button when no analysis is available
              <div className="px-6 py-4 flex flex-col sm:flex-row items-center justify-between">
                <div className="text-blue-700 mb-3 sm:mb-0">
                  <strong>🤖 Vehicle Analysis:</strong> Get AI-powered enthusiast insights for this vehicle
                </div>
                <button
                  onClick={generateAnalysis}
                  disabled={isAnalyzing}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
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
                    <>Generate Analysis</>
                  )}
                </button>
              </div>
            )}
          </div>
          
          <ImageGallery 
            images={vehicle.images} 
            alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`} 
          />

          <div className="p-6 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Vehicle Details</h2>
                {/* Add prominent price display */}
                <div className="bg-gray-100 p-4 rounded-lg mb-4">
                  <p className="text-sm text-gray-500">Price</p>
                  <p className="text-2xl font-bold text-primary-600">
                    ${vehicle.price?.toLocaleString() || 'Contact for Price'}
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Make</p>
                    <p className="font-medium">{vehicle.make}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Model</p>
                    <p className="font-medium">{vehicle.model}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Year</p>
                    <p className="font-medium">{vehicle.year}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Exterior Color</p>
                    <p className="font-medium">{vehicle.exteriorColor}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Interior Color</p>
                    <p className="font-medium">{vehicle.interiorColor}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Engine</p>
                    <p className="font-medium">{vehicle.engine}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Transmission</p>
                    <p className="font-medium">{vehicle.transmission}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Fuel Type</p>
                    <p className="font-medium">{vehicle.fuelType}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">VIN</p>
                    <p className="font-medium">{vehicle.vin}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Dealer</p>
                    <p className="font-medium">{vehicle.dealer}</p>
                  </div>
                </div>
              </div>

              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Description</h2>
                <p className="text-gray-700 mb-6">{vehicle.description}</p>

                <h2 className="text-xl font-semibold text-gray-900 mb-4">Features</h2>
                <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {vehicle.features.map((feature, index) => (
                    <li key={index} className="flex items-center text-gray-700">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-500 mr-2" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="flex flex-wrap gap-4 mt-8">
              <a 
                href={vehicle.url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="btn btn-primary flex-grow md:flex-grow-0"
              >
                View Original Listing
              </a>
              <a
                href={`https://www.progressive.com/auto/car-insurance-quote/?vehicle=${encodeURIComponent(`${vehicle.year} ${vehicle.make} ${vehicle.model}`)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn bg-gradient-to-r from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800 text-white flex-grow md:flex-grow-0 flex items-center gap-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
                </svg>
                Need Insurance?
              </a>
              <Link href="/search" className="btn btn-secondary flex-grow md:flex-grow-0">
                Back to Search
              </Link>
            </div>
          </div>
        </div>

        {/* Social Posts Section */}
        <SocialPostsCarousel 
          make={vehicle.make}
          model={vehicle.model}
          year={vehicle.year}
          className="mb-8"
        />

        {/* Market Analysis Section */}
        <MarketAnalysis vehicle={vehicle} className="mb-8" />
      </div>
    </>
  );
}

export const getStaticPaths: GetStaticPaths = async () => {
  // Get featured vehicle IDs for pre-generation
  const featuredVehicles = getFeaturedVehicles();
  
  // Also get Hemmings listings for pre-generation
  let hemmingsVehicles: Vehicle[] = [];
  try {
    hemmingsVehicles = await getHemmingsListings();
    console.log(`Got ${hemmingsVehicles.length} Hemmings vehicles for static paths`);
  } catch (error) {
    console.error('Error fetching Hemmings vehicles for static paths:', error);
  }
  
  // Combine all vehicle IDs
  const allVehicles = [...featuredVehicles, ...hemmingsVehicles];
  
  const paths = allVehicles.map((vehicle) => ({
    params: { id: vehicle.id },
  }));

  return {
    paths,
    fallback: false, // Must use false for static export mode
  };
};

export const getStaticProps: GetStaticProps<VehicleDetailProps> = async ({ params }) => {
  const id = params?.id as string;

  // Check if it's a featured vehicle first
  const featuredVehicles = getFeaturedVehicles();
  const featuredVehicle = featuredVehicles.find(v => v.id === id);
  
  // Special handling for our Porsche 964 with enhanced analysis
  if (featuredVehicle && id === 'ebay-porsche-1') {
    // Get the enhanced analysis for this specific vehicle
    const preloadedAnalysis = getFallbackAnalysis(featuredVehicle);
    return {
      props: {
        vehicle: featuredVehicle,
        preloadedAnalysis
      }
      // Removed revalidate property for static export compatibility
    };
  }
  
  // Normal featured vehicle without special analysis
  if (featuredVehicle) {
    return {
      props: {
        vehicle: featuredVehicle,
      },
    };
  }

  // If not a featured vehicle, check if it's a Hemmings vehicle
  try {
    const hemmingsVehicles = await getHemmingsListings();
    const hemmingsVehicle = hemmingsVehicles.find(v => v.id === id);
    
    if (hemmingsVehicle) {
      return {
        props: {
          vehicle: hemmingsVehicle,
        },
      };
    }
  } catch (error) {
    console.error(`Error fetching Hemmings vehicle with ID ${id}:`, error);
  }

  // If not found in either source, return 404
  return {
    notFound: true,
  };
};
