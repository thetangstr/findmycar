import React, { useState } from 'react';
import { useAlerts } from '@/hooks/useAlerts';
import Link from 'next/link';
import { useAuth } from '@/utils/auth';
import LoginForm from '@/components/auth/LoginForm';

export default function Alerts() {
  const { user } = useAuth();
  const { alerts, loading, error, deleteAlert, testAlert } = useAlerts();
  const [testingId, setTestingId] = useState<string | null>(null);
  const [testSuccess, setTestSuccess] = useState<boolean | null>(null);

  // Handle alert deletion
  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this alert?')) {
      deleteAlert(id);
    }
  };

  // Handle test alert
  const handleTest = async (id: string) => {
    setTestingId(id);
    setTestSuccess(null);
    
    const success = await testAlert(id);
    setTestSuccess(success);
    
    setTimeout(() => {
      setTestingId(null);
      setTestSuccess(null);
    }, 3000);
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // If user is not logged in, show login form
  if (!user) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Email Alerts</h1>
          <p className="text-gray-600">
            Please log in to manage your email alerts.
          </p>
        </div>
        
        <div className="flex justify-center">
          <LoginForm onSuccess={() => window.location.reload()} />
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Email Alerts</h1>
        <p className="text-gray-600">
          Manage your email alerts for new vehicle listings.
        </p>
      </div>
      
      {error && (
        <div className="bg-red-50 text-red-800 p-4 rounded-md mb-6">
          {error}
        </div>
      )}
      
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600 mb-4"></div>
          <p className="text-gray-600">Loading your alerts...</p>
        </div>
      ) : alerts.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Alerts Set Up</h2>
          <p className="text-gray-600 mb-6">
            You haven&apos;t set up any email alerts yet. Create alerts to get notified when new vehicles matching your criteria are listed.
          </p>
          <Link href="/search" className="btn btn-primary">
            Search and Create Alert
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {alerts.map(alert => (
            <div key={alert.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-xl font-semibold text-gray-900">{alert.name}</h3>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    alert.frequency === 'instant' 
                      ? 'bg-green-100 text-green-800' 
                      : alert.frequency === 'daily'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-purple-100 text-purple-800'
                  }`}>
                    {alert.frequency.charAt(0).toUpperCase() + alert.frequency.slice(1)}
                  </span>
                </div>
                
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Alert Criteria:</h4>
                  <div className="bg-gray-50 rounded-md p-3">
                    {Object.keys(alert.filters).length === 0 ? (
                      <p className="text-gray-600 text-sm">All vehicles</p>
                    ) : (
                      <ul className="space-y-1">
                        {Object.entries(alert.filters)
                          .filter(([key, value]) => value !== undefined && value !== '' && key !== 'query')
                          .map(([key, value]) => (
                            <li key={key} className="text-sm text-gray-700">
                              <span className="font-medium">
                                {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}:
                              </span>{' '}
                              {typeof value === 'number' && (key.includes('price') 
                                ? `$${value.toLocaleString()}` 
                                : key.includes('mileage') 
                                  ? `${value.toLocaleString()} miles`
                                  : value)}
                              {typeof value !== 'number' && value}
                            </li>
                          ))}
                        {alert.filters.query && (
                          <li className="text-sm text-gray-700">
                            <span className="font-medium">Search Query:</span> {alert.filters.query}
                          </li>
                        )}
                      </ul>
                    )}
                  </div>
                </div>
                
                <div className="text-xs text-gray-500 mb-4">
                  <div>Created: {formatDate(alert.createdAt)}</div>
                  {alert.lastSentAt && (
                    <div>Last sent: {formatDate(alert.lastSentAt)}</div>
                  )}
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleTest(alert.id)}
                    disabled={testingId === alert.id}
                    className={`flex-grow btn ${
                      testingId === alert.id 
                        ? testSuccess === null
                          ? 'bg-gray-300 text-gray-600 cursor-wait'
                          : testSuccess
                            ? 'bg-green-500 text-white'
                            : 'bg-red-500 text-white'
                        : 'btn-secondary'
                    }`}
                  >
                    {testingId === alert.id ? (
                      testSuccess === null ? (
                        <span className="flex items-center justify-center">
                          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Testing...
                        </span>
                      ) : testSuccess ? 'Test Sent!' : 'Test Failed'
                    ) : 'Test Alert'}
                  </button>
                  <Link
                    href={`/search?${new URLSearchParams(
                      Object.entries(alert.filters)
                        .filter(([_, v]) => v !== undefined && v !== '')
                        .reduce((acc, [k, v]) => ({ ...acc, [k]: v }), {})
                    ).toString()}`}
                    className="p-2 text-primary-600 hover:text-primary-800 bg-primary-50 hover:bg-primary-100 rounded-md"
                    title="View matching vehicles"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                      <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                    </svg>
                  </Link>
                  <button
                    onClick={() => handleDelete(alert.id)}
                    className="p-2 text-red-600 hover:text-red-800 bg-red-50 hover:bg-red-100 rounded-md"
                    title="Delete alert"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
