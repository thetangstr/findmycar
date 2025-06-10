import { Vehicle } from '@/types';

/**
 * Curated featured vehicles with diverse sources and proper images
 */
export const getFeaturedVehicles = (): Vehicle[] => {
  return [
    {
      id: 'featured-porsche-964-ebay',
      make: 'Porsche',
      model: '911 Carrera 2',
      year: 1990,
      price: 89500,
      mileage: 87650,
      exteriorColor: 'Grand Prix White',
      interiorColor: 'Black Leather',
      fuelType: 'Gasoline',
      transmission: '5-Speed Manual',
      engine: '3.6L Naturally Aspirated Flat-6',
      vin: 'WP0AB2963LS450123',
      description: 'Beautiful 1990 Porsche 911 Carrera 2 (964) in classic Grand Prix White over black leather. This is the first year of the legendary 964 generation, featuring the improved 3.6L M64 engine, revised suspension, and timeless G50 5-speed manual transmission. A true driver\'s car with excellent maintenance history and matching numbers.',
      features: [
        'Original M64 3.6L Engine',
        'G50 5-Speed Manual Transmission',
        'Sport Suspension Package',
        'Limited Slip Differential',
        'Air Conditioning',
        'Power Steering',
        'Electric Sunroof',
        'Fuchs Alloy Wheels',
        'Clean Carfax Report'
      ],
      images: [
        'https://images.unsplash.com/photo-1503376780353-7e6692767b70?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80',
        'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80',
        'https://images.unsplash.com/photo-1544829499-33f8f0066a7a?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80',
        'https://images.unsplash.com/photo-1609521263047-f8f205293f24?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80'
      ],
      location: 'Beverly Hills, CA',
      dealer: 'European Classics of California',
      listingDate: '2025-01-15T10:00:00.000Z',
      url: 'https://www.ebay.com/itm/256945356557',
      source: 'eBay Motors'
    },
    {
      id: 'featured-acura-nsx-ebay',
      make: 'Acura',
      model: 'NSX NSX-T',
      year: 1999,
      price: 120000,
      mileage: 28765,
      exteriorColor: 'Kaiser Silver Metallic',
      interiorColor: 'Black Leather',
      fuelType: 'Gasoline',
      transmission: '6-Speed Manual',
      engine: '3.2L VTEC V6',
      vin: 'JH4NA21689T000123',
      description: 'Pristine 1999 Acura NSX NSX-T in sought-after Kaiser Silver Metallic. This is a late-production NSX with the desirable 3.2L VTEC engine and 6-speed manual transmission. The NSX-T features a removable targa top for an enhanced driving experience. Exceptional condition with comprehensive service records.',
      features: [
        '3.2L VTEC V6 Engine',
        '6-Speed Manual Transmission',
        'NSX-T Targa Top Configuration',
        'Mid-Engine Layout',
        'Aluminum Space Frame',
        'Independent Suspension',
        'Brembo Brakes',
        'Power Steering',
        'Premium Sound System'
      ],
      images: [
        'https://images.unsplash.com/photo-1598887142487-c8b6fa67cad9?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80',
        'https://images.unsplash.com/photo-1542362567-b07e54358753?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80',
        'https://images.unsplash.com/photo-1511919884226-fd3cad34687c?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80'
      ],
      location: 'Miami, FL',
      dealer: 'Acura of Miami',
      listingDate: '2025-01-15T10:00:00.000Z',
      url: 'https://www.ebay.com/itm/396690384613',
      source: 'eBay Motors'
    },
    {
      id: 'featured-corvette-z06-bat',
      make: 'Chevrolet',
      model: 'Corvette Z06',
      year: 2012,
      price: 58500,
      mileage: 18500,
      exteriorColor: 'Supersonic Blue Metallic',
      interiorColor: 'Ebony Leather',
      fuelType: 'Gasoline',
      transmission: '6-Speed Manual',
      engine: '7.0L LS7 V8',
      vin: '1G1YY26E925100123',
      description: 'Stunning 2012 Chevrolet Corvette Z06 in rare Supersonic Blue Metallic. Powered by the legendary 7.0L LS7 V8 producing 505 horsepower, paired with a 6-speed manual transmission. This is the last of the great naturally aspirated American supercars. Low mileage with comprehensive maintenance records.',
      features: [
        '7.0L LS7 Naturally Aspirated V8',
        '6-Speed Manual Transmission',
        'Carbon Fiber Hood',
        'Z06 Performance Package',
        'Magnetic Selective Ride Control',
        'Brembo Brake Package',
        'Limited Slip Differential',
        'Track-Tuned Suspension',
        'Performance Exhaust System'
      ],
      images: [
        'https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80',
        'https://images.unsplash.com/photo-1614200187524-dc4b892acf16?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80',
        'https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80'
      ],
      location: 'Austin, TX',
      dealer: 'Bring a Trailer',
      listingDate: '2025-01-15T10:00:00.000Z',
      url: 'https://bringatrailer.com/listing/2012-chevrolet-corvette-z06-8/',
      source: 'Bring a Trailer'
    }
  ];
};

/**
 * Get a featured vehicle by ID
 */
export const getFeaturedVehicleById = (id: string): Vehicle | null => {
  const vehicles = getFeaturedVehicles();
  return vehicles.find(vehicle => vehicle.id === id) || null;
};

export default {
  getFeaturedVehicles,
  getFeaturedVehicleById
}; 