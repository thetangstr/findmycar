import React from 'react';
import HomeSearchBox from '../HomeSearchBox';
import { useRouter } from 'next/router';
import { SearchFilters } from '@/types';

const Hero = () => {
  const router = useRouter();

  const handleSearch = (filters: SearchFilters) => {
    // For demo purposes, we'll just navigate to the search page
    // In a real app, you'd pass the filters to the search page
    console.log('Performing search with filters:', filters);
    router.push('/search');
  };

  return (
    <div className="relative bg-white">
      <div className="absolute inset-0">
        <img
          className="w-full h-full object-cover"
          src="https://images.unsplash.com/photo-1553440569-bcc63803a83d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2370&q=80"
          alt="Sports car"
        />
        <div className="absolute inset-0 bg-black/40" style={{ backdropFilter: 'blur(2px)' }}></div>
      </div>
      <div className="relative max-w-7xl mx-auto py-28 px-4 sm:py-36 sm:px-6 lg:px-8 text-center">
        <div className="slide-in slide-delay-1">
          <span className="feature-label">AI-Powered Search</span>
          <h1 className="mt-4 text-5xl font-semibold tracking-tight text-white sm:text-6xl lg:text-7xl font-mono">
            Find Your Next Car
          </h1>
          <p className="mt-6 text-xl text-white/90 max-w-3xl mx-auto font-inter">
            Search thousands of listings with our intelligent, AI-powered search to find the perfect car for you.
          </p>
          <div className="mt-8 flex flex-col justify-center items-center">
            <div className="text-white text-lg font-inter font-medium mb-3">Browse listings from all the major used car sites, including:</div>
            <div className="inline-flex flex-wrap justify-center items-center gap-3 mt-2">
              <div className="text-white bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-all font-medium px-4 py-2 rounded-lg border border-white/20 shadow-md">
                eBay Motors
              </div>
              <div className="text-white bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-all font-medium px-4 py-2 rounded-lg border border-white/20 shadow-md">
                Cars.com
              </div>
              <div className="text-white bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-all font-medium px-4 py-2 rounded-lg border border-white/20 shadow-md">
                FB Marketplace
              </div>
              <div className="text-white bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-all font-medium px-4 py-2 rounded-lg border border-white/20 shadow-md">
                Carvana
              </div>
              <div className="text-white bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-all font-medium px-4 py-2 rounded-lg border border-white/20 shadow-md">
                Cars & Bids
              </div>
              <div className="text-white bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-all font-medium px-4 py-2 rounded-lg border border-white/20 shadow-md">
                Bring a Trailer
              </div>
              <div className="text-white bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-all font-medium px-4 py-2 rounded-lg border border-white/20 shadow-md">
                Reddit
              </div>
            </div>
          </div>
        </div>
        <div className="mt-10 max-w-2xl mx-auto slide-in slide-delay-2">
          <HomeSearchBox onSearch={handleSearch} isSearching={false} />
        </div>
      </div>
    </div>
  );
};

export default Hero;