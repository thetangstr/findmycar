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
    <div className="relative bg-gray-800">
      <div className="absolute inset-0">
        <img
          className="w-full h-full object-cover"
          src="https://images.unsplash.com/photo-1553440569-bcc63803a83d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2370&q=80"
          alt="Sports car"
        />
        <div className="absolute inset-0 bg-gray-800" style={{ mixBlendMode: 'multiply' }}></div>
      </div>
      <div className="relative max-w-7xl mx-auto py-24 px-4 sm:py-32 sm:px-6 lg:px-8 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl">
          Find Your Next Car with AI
        </h1>
        <p className="mt-6 text-xl text-indigo-100 max-w-3xl mx-auto">
          Search thousands of listings with our intelligent, AI-powered search to find the perfect car for you.
        </p>
        <div className="mt-10 max-w-2xl mx-auto">
          <HomeSearchBox onSearch={handleSearch} isSearching={false} />
        </div>
      </div>
    </div>
  );
};

export default Hero; 