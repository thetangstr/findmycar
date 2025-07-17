import React from 'react';
import { Search, Bot, Car } from 'lucide-react';

const steps = [
  {
    icon: <Search className="h-10 w-10 text-white" />,
    name: 'Search for a Car',
    description: 'Use our simple, natural language search to describe exactly what you\'re looking for in a vehicle.',
  },
  {
    icon: <Bot className="h-10 w-10 text-white" />,
    name: 'Get AI Insights',
    description: 'Our AI analyzes each listing, providing you with detailed insights, pros and cons, and a market price comparison.',
  },
  {
    icon: <Car className="h-10 w-10 text-white" />,
    name: 'Find Your Perfect Car',
    description: 'Compare your options and drive away in the car that\'s truly right for you, backed by data-driven confidence.',
  },
];

const HowItWorks = () => {
  return (
    <div className="bg-white py-16 sm:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-base font-semibold text-primary-600 tracking-wide uppercase">How It Works</h2>
          <p className="mt-2 text-3xl font-extrabold text-gray-900 tracking-tight sm:text-4xl">
            Finding Your Car in 3 Easy Steps
          </p>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500">
            Our process is designed to be simple, transparent, and powerful.
          </p>
        </div>
        <div className="mt-12">
          <div className="grid grid-cols-1 gap-12 sm:grid-cols-2 lg:grid-cols-3">
            {steps.map((step, index) => (
              <div key={step.name} className="text-center">
                <div className="flex items-center justify-center h-20 w-20 rounded-full bg-primary-600 mx-auto">
                  {step.icon}
                </div>
                <div className="mt-5">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">{step.name}</h3>
                  <p className="mt-2 text-base text-gray-500">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HowItWorks; 