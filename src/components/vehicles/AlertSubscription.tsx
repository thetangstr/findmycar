import React, { useState } from 'react';
import { Bell, Mail } from 'lucide-react';

interface AlertSubscriptionProps {
  className?: string;
}

const AlertSubscription: React.FC<AlertSubscriptionProps> = ({ className = '' }) => {
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [email, setEmail] = useState('');

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      setIsSubscribed(true);
      console.log(`Subscribed with email: ${email}`);
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 border border-blue-100 ${className}`}>
      <div className="flex items-center mb-4">
        <Bell className="h-6 w-6 text-blue-500 mr-3" />
        <h3 className="text-lg font-semibold text-gray-900">Get Price Alerts</h3>
      </div>
      
      {isSubscribed ? (
        <div className="text-center bg-green-50 rounded-lg p-4">
          <p className="font-medium text-green-800">
            ✅ You're subscribed!
          </p>
          <p className="text-sm text-green-700 mt-1">
            We'll notify you at <span className="font-semibold">{email}</span> of any price changes.
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubscribe}>
          <p className="text-sm text-gray-600 mb-4">
            Get notified when the price of this vehicle changes.
          </p>
          <div className="flex items-center">
            <div className="relative flex-grow">
              <Mail className="h-4 w-4 text-gray-400 absolute top-1/2 left-3 transform -translate-y-1/2" />
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white font-semibold rounded-r-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              Subscribe
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default AlertSubscription; 