import React, { ReactNode, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import ComparisonIndicator from './ComparisonIndicator';
import { useAuth } from '@/utils/auth';
import Footer from './Footer';
import { BellRing, LogIn, User } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  const isActive = (path: string) => {
    return router.pathname === path ? 'bg-primary-700 text-white' : 'text-gray-700 hover:bg-gray-100';
  };
  
  const handleLogout = () => {
    logout();
    router.push('/');
  };
  
  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };
  
  const [showPriceAlertModal, setShowPriceAlertModal] = useState(false);

  const handlePriceAlertClick = () => {
    setShowPriceAlertModal(true);
  };

  const closePriceAlertModal = () => {
    setShowPriceAlertModal(false);
  };

  // Mock user data (as if signed in)
  const mockUser = {
    name: 'Kailor Tang',
    email: 'kailor@example.com',
    avatar: 'https://robohash.org/Kailor.png?set=set4&size=150x150', // Cartoon robot avatar
    alerts: ['2018 Acura NSX', '1967 Chevrolet Corvette']
  };
  
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-3xl font-bold text-primary-600 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 mr-3" viewBox="0 0 20 20" fill="currentColor">
              <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
              <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1v-1h3.05a2.5 2.5 0 014.9 0H19a1 1 0 001-1v-6a1 1 0 00-.293-.707l-3-3A1 1 0 0016 3H3z" />
            </svg>
            Find My Car
          </Link>

          {/* Right side navigation with bell icon and user avatar */}
          <div className="flex items-center space-x-4">
            <button 
              onClick={handlePriceAlertClick} 
              className="text-gray-600 hover:text-primary-600 transition-colors p-2 relative"
              title="Price Alerts"
            >
              <BellRing size={24} />
              <span className="absolute top-1 right-1 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                2
              </span>
            </button>
            
            <div className="flex items-center">
              <div className="mr-2 text-right hidden md:block">
                <p className="text-sm font-medium text-gray-800">{mockUser.name}</p>
                <p className="text-xs text-gray-500">{mockUser.email}</p>
              </div>
              <div className="relative">
                <img 
                  src={mockUser.avatar} 
                  alt="User profile" 
                  className="w-10 h-10 rounded-full border-2 border-primary-500"
                />
                <div className="absolute bottom-0 right-0 bg-green-500 w-3 h-3 rounded-full border-2 border-white"></div>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      {/* No mobile menu in minimalist design */}
      
      {/* Price Alert Modal */}
      {showPriceAlertModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
          <div className="bg-white rounded-xl shadow-lg p-6 m-4 max-w-md w-full">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Price Alerts</h3>
              <button onClick={closePriceAlertModal} className="text-gray-500 hover:text-gray-700">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <div className="mb-6">
              <p className="text-gray-600 mb-4">Get notified when prices change for vehicles you&apos;re interested in.</p>
              
              {mockUser.alerts.length > 0 ? (
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-700">Your Active Alerts:</h4>
                  {mockUser.alerts.map((alert, index) => (
                    <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                      <span className="font-medium text-gray-800">{alert}</span>
                      <button className="text-red-500 hover:text-red-700 text-sm">
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6">
                  <p className="text-gray-500">You don&apos;t have any active price alerts.</p>
                </div>
              )}
            </div>
            
            <div className="flex justify-between border-t pt-4">
              <button 
                onClick={closePriceAlertModal}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Close
              </button>
              <button
                className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                <BellRing size={16} className="mr-2" />
                Create New Alert
              </button>
            </div>
          </div>
        </div>
      )}
      
      <main className="flex-grow container mx-auto px-4 py-8">
        {children}
      </main>
      
      <Footer />
    </div>
  );
};

export default Layout;
