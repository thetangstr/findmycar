import Head from 'next/head';
import React from 'react';
import Link from 'next/link';
import { Vehicle } from '@/types';
import { getFeaturedVehicles as getCuratedFeaturedVehicles } from '@/services/featuredVehiclesService';
import VehicleCard from '@/components/VehicleCard';
import Hero from '@/components/home/Hero';
import HowItWorks from '@/components/home/HowItWorks';
import WhyChooseUs from '@/components/home/WhyChooseUs';
import PartnerSection from '@/components/home/PartnerSection';

import { getHemmingsListings } from '@/services/scraperService';
import { GetStaticProps } from 'next';

interface HomeProps {
  featuredVehicles: Vehicle[];
}

export default function Home({ featuredVehicles }: HomeProps) {
  return (
    <div>
      <Head>
        <title>FindMyCar | AI-Powered Car Search</title>
        <meta name="description" content="Find your next car with AI-powered search" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <Hero />
        
        {/* Featured Listings */}
        <section className="bg-white py-16 sm:py-20">
          <div className="container mx-auto px-4">
            <div className="flex flex-col items-center mb-10 slide-in slide-delay-1">
              <span className="feature-label">Discover</span>
              <h2 className="text-4xl font-mono font-semibold text-gray-900 tracking-tight mt-2 text-center">
                Featured Vehicles
              </h2>
              <p className="mt-4 text-lg text-gray-500 max-w-2xl text-center font-inter">
                Explore our handpicked selection of premium vehicles
              </p>
            </div>
            
            {featuredVehicles.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {featuredVehicles.map((vehicle, index) => (
                  <div key={vehicle.id} className={`slide-in slide-delay-${index + 2}`}>
                    <VehicleCard vehicle={vehicle} />
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-600 font-inter">No featured vehicles available at the moment.</p>
              </div>
            )}
            
            <div className="mt-10 text-center slide-in slide-delay-6">
              <Link href="/search" className="inline-flex items-center px-6 py-3 border border-transparent font-medium rounded-full shadow-sm text-white bg-teal-500 hover:bg-teal-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 transition-all duration-300 font-inter">
                View All Vehicles
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </Link>
            </div>
          </div>
        </section>

        {/* How it Works */}
        <HowItWorks />
        
        {/* Why Choose Us */}
        <WhyChooseUs />
        
        {/* Partner Section */}
        <PartnerSection />
        
        {/* FAQ section removed as component doesn't exist */}
      </main>
    </div>
  );
}

export const getStaticProps: GetStaticProps<HomeProps> = async () => {
  const curatedVehicles = getCuratedFeaturedVehicles().slice(0, 3); // Get up to 3 curated
  let hemmingsVehicles: Vehicle[] = [];
  try {
    hemmingsVehicles = (await getHemmingsListings()).slice(0, 3); // Get up to 3 Hemmings
  } catch (error) {
    console.error("Error fetching Hemmings for featured listings:", error);
    // Continue without Hemmings if there's an error
  }

  const allPotentialFeatured = [...hemmingsVehicles, ...curatedVehicles];
  
  const uniqueFeaturedMap = new Map<string, Vehicle>();
  allPotentialFeatured.forEach(vehicle => {
    if (!uniqueFeaturedMap.has(vehicle.id)) {
      uniqueFeaturedMap.set(vehicle.id, vehicle);
    }
  });
  
  const finalFeaturedVehicles = Array.from(uniqueFeaturedMap.values()).slice(0, 3);
  
  return {
    props: {
      featuredVehicles: finalFeaturedVehicles,
    }
    // Removed revalidate property for compatibility with static exports
  };
};
