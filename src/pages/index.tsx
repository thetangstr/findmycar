import Head from 'next/head';
import Link from 'next/link';
import { Vehicle } from '@/types';
import { getFeaturedVehicles as getCuratedFeaturedVehicles } from '@/services/featuredVehiclesService';
import VehicleCard from '@/components/VehicleCard';
import Hero from '@/components/home/Hero';
import HowItWorks from '@/components/home/HowItWorks';
import WhyChooseUs from '@/components/home/WhyChooseUs';
import { GetStaticProps } from 'next';

interface HomeProps {
  featuredVehicles: Vehicle[];
}

export default function Home({ featuredVehicles }: HomeProps) {

  return (
    <>
      <Head>
        <title>FindMyCar - AI-Powered Car Search</title>
        <meta name="description" content="Find your next car with our intelligent, AI-powered search engine." />
      </Head>

      <Hero />
      
      <div className="bg-gray-50">
        <div className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-extrabold text-gray-900">Featured Listings</h2>
            <Link href="/search" className="text-primary-600 hover:text-primary-800 font-medium">
              View All &rarr;
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredVehicles.map((vehicle) => (
              <VehicleCard key={vehicle.id} vehicle={vehicle} />
            ))}
          </div>
        </div>
      </div>
      
      <HowItWorks />
      <WhyChooseUs />
    </>
  );
}

export const getStaticProps: GetStaticProps<HomeProps> = async () => {
  const featuredVehicles = getCuratedFeaturedVehicles().slice(0, 3);
  
  return {
    props: {
      featuredVehicles,
    },
  };
};
