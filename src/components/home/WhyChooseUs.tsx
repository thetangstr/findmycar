import React from 'react';
import { Bot, ShieldCheck, TrendingUp, Search } from 'lucide-react';

const features = [
  {
    icon: <Bot className="h-8 w-8 text-primary-600" />,
    name: 'AI-Powered Insights',
    description: 'Get unbiased, data-driven analysis on every vehicle, so you can make smarter decisions.',
  },
  {
    icon: <Search className="h-8 w-8 text-primary-600" />,
    name: 'Comprehensive Search',
    description: 'Our engine searches thousands of listings from multiple sources to find the best cars for you.',
  },
  {
    icon: <ShieldCheck className="h-8 w-8 text-primary-600" />,
    name: 'Trusted & Transparent',
    description: 'We provide clear, honest information, including market analysis and price history.',
  },
  {
    icon: <TrendingUp className="h-8 w-8 text-primary-600" />,
    name: 'Market-Driven Data',
    description: 'Stay ahead with real-time market data, depreciation forecasts, and price alerts.',
  },
]

const WhyChooseUs = () => {
  return (
    <div className="bg-gray-50 py-16 sm:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-base font-semibold text-primary-600 tracking-wide uppercase">Why Choose Us</h2>
          <p className="mt-2 text-3xl font-extrabold text-gray-900 tracking-tight sm:text-4xl">
            The Smartest Way to Buy a Car
          </p>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500">
            We leverage technology to give you confidence and clarity in your car buying journey.
          </p>
        </div>
        <div className="mt-12">
          <div className="grid grid-cols-1 gap-10 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature) => (
              <div key={feature.name} className="pt-6">
                <div className="flow-root bg-white rounded-lg px-6 pb-8 shadow-md h-full">
                  <div className="-mt-6">
                    <div>
                      <span className="inline-flex items-center justify-center p-3 bg-primary-50 rounded-md shadow-lg">
                        {feature.icon}
                      </span>
                    </div>
                    <h3 className="mt-8 text-lg font-medium text-gray-900 tracking-tight">{feature.name}</h3>
                    <p className="mt-5 text-base text-gray-500">{feature.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default WhyChooseUs; 