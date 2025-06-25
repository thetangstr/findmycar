import Head from 'next/head';
import { Vehicle } from '@/types';

interface SEOHeadProps {
  title?: string;
  description?: string;
  keywords?: string[];
  canonicalUrl?: string;
  ogImage?: string;
  ogType?: 'website' | 'article' | 'product';
  vehicle?: Vehicle;
  structuredData?: any;
}

const SEOHead: React.FC<SEOHeadProps> = ({
  title = 'FindMyCar - Find Your Perfect Vehicle',
  description = 'FindMyCar helps you find, compare, and save your favorite vehicles from multiple sources with AI-powered insights.',
  keywords = ['cars', 'vehicles', 'auto search', 'car finder', 'vehicle comparison'],
  canonicalUrl,
  ogImage = '/images/og-default.jpg',
  ogType = 'website',
  vehicle,
  structuredData
}) => {
  const siteName = 'FindMyCar';
  const domain = 'https://findmycar.app'; // Replace with actual domain
  
  // Generate vehicle-specific SEO data
  const vehicleTitle = vehicle 
    ? `${vehicle.year} ${vehicle.make} ${vehicle.model} - ${vehicle.price.toLocaleString()} | ${siteName}`
    : title;
    
  const vehicleDescription = vehicle
    ? `${vehicle.year} ${vehicle.make} ${vehicle.model} for $${vehicle.price.toLocaleString()} with ${vehicle.mileage.toLocaleString()} miles. ${vehicle.description.substring(0, 120)}...`
    : description;
    
  const vehicleKeywords = vehicle
    ? [
        vehicle.make.toLowerCase(),
        vehicle.model.toLowerCase(),
        vehicle.year.toString(),
        vehicle.fuelType.toLowerCase(),
        vehicle.transmission.toLowerCase(),
        ...keywords
      ]
    : keywords;

  // Generate structured data for vehicle
  const vehicleStructuredData = vehicle ? {
    "@context": "https://schema.org",
    "@type": "Car",
    "name": `${vehicle.year} ${vehicle.make} ${vehicle.model}`,
    "brand": {
      "@type": "Brand",
      "name": vehicle.make
    },
    "model": vehicle.model,
    "vehicleModelDate": vehicle.year.toString(),
    "mileageFromOdometer": {
      "@type": "QuantitativeValue",
      "value": vehicle.mileage,
      "unitCode": "SMI"
    },
    "fuelType": vehicle.fuelType,
    "vehicleTransmission": vehicle.transmission,
    "color": vehicle.exteriorColor,
    "interiorColor": vehicle.interiorColor,
    "offers": {
      "@type": "Offer",
      "price": vehicle.price,
      "priceCurrency": "USD",
      "availability": "https://schema.org/InStock",
      "seller": {
        "@type": "Organization",
        "name": vehicle.dealer
      }
    },
    "description": vehicle.description,
    "url": `${domain}/vehicles/${vehicle.id}`,
    "image": vehicle.images?.[0] || ogImage,
    "vehicleEngine": {
      "@type": "EngineSpecification",
      "name": vehicle.engine
    }
  } : null;

  // Website structured data
  const websiteStructuredData = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": siteName,
    "description": description,
    "url": domain,
    "potentialAction": {
      "@type": "SearchAction",
      "target": {
        "@type": "EntryPoint",
        "urlTemplate": `${domain}/search?q={search_term_string}`
      },
      "query-input": "required name=search_term_string"
    }
  };

  // Organization structured data
  const organizationStructuredData = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": siteName,
    "description": "AI-powered vehicle search and comparison platform",
    "url": domain,
    "logo": `${domain}/logo.png`,
    "contactPoint": {
      "@type": "ContactPoint",
      "contactType": "customer service",
      "availableLanguage": "English"
    },
    "sameAs": [
      // Add social media URLs when available
    ]
  };

  const finalStructuredData = structuredData || vehicleStructuredData || [
    websiteStructuredData,
    organizationStructuredData
  ];

  return (
    <Head>
      {/* Basic Meta Tags */}
      <title>{vehicleTitle}</title>
      <meta name="description" content={vehicleDescription} />
      <meta name="keywords" content={vehicleKeywords.join(', ')} />
      <meta name="author" content={siteName} />
      
      {/* Canonical URL */}
      {canonicalUrl && <link rel="canonical" href={canonicalUrl} />}
      
      {/* Open Graph / Facebook */}
      <meta property="og:type" content={ogType} />
      <meta property="og:title" content={vehicleTitle} />
      <meta property="og:description" content={vehicleDescription} />
      <meta property="og:site_name" content={siteName} />
      {canonicalUrl && <meta property="og:url" content={canonicalUrl} />}
      <meta property="og:image" content={vehicle?.images?.[0] || ogImage} />
      <meta property="og:image:alt" content={vehicle ? `${vehicle.year} ${vehicle.make} ${vehicle.model}` : 'FindMyCar'} />
      <meta property="og:locale" content="en_US" />
      
      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={vehicleTitle} />
      <meta name="twitter:description" content={vehicleDescription} />
      <meta name="twitter:image" content={vehicle?.images?.[0] || ogImage} />
      
      {/* Additional Meta Tags */}
      <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
      <meta name="googlebot" content="index, follow" />
      
      {/* Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(finalStructuredData)
        }}
      />
      
      {/* Additional vehicle-specific meta tags */}
      {vehicle && (
        <>
          <meta property="product:price:amount" content={vehicle.price.toString()} />
          <meta property="product:price:currency" content="USD" />
          <meta property="auto:make" content={vehicle.make} />
          <meta property="auto:model" content={vehicle.model} />
          <meta property="auto:year" content={vehicle.year.toString()} />
          <meta property="auto:mileage" content={vehicle.mileage.toString()} />
          <meta property="auto:fuel_type" content={vehicle.fuelType} />
          <meta property="auto:transmission" content={vehicle.transmission} />
        </>
      )}
    </Head>
  );
};

export default SEOHead;