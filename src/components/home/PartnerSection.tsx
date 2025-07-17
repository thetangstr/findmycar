import React from 'react';

const PartnerSection = () => {
  return (
    <div className="bg-white border-t border-gray-200 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-base font-semibold text-primary-600 tracking-wide uppercase">Our Partners</h2>
          <p className="mt-2 text-3xl font-extrabold text-gray-900 tracking-tight sm:text-4xl">
            Trusted by Top Automotive Sites
          </p>
        </div>
        <div className="mt-10">
          <div className="flex flex-wrap justify-center items-center gap-x-12 gap-y-8">
            <img src="/logo/ebay-logo.svg" alt="eBay Motors" className="h-10 opacity-70 hover:opacity-100 transition-opacity" />
            <img src="/logo/carscom-logo.svg" alt="Cars.com" className="h-9 opacity-70 hover:opacity-100 transition-opacity" />
            <img src="/logo/truecar-logo.svg" alt="TrueCar" className="h-9 opacity-70 hover:opacity-100 transition-opacity" />
            <img src="/logo/carvana-logo.svg" alt="Carvana" className="h-9 opacity-70 hover:opacity-100 transition-opacity" />
            <img src="/logo/carsbids-logo.svg" alt="Cars & Bids" className="h-9 opacity-70 hover:opacity-100 transition-opacity" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default PartnerSection;
