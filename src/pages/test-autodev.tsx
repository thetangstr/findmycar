import React, { useState } from 'react';
import { fetchAutoDevListings, fetchAutoDevVinDetails } from '../services/autoDevApi'; // Adjusted path
import { Vehicle } from '@/types'; // Assuming AutoDevVinDetails is similar enough or we adapt

const TestAutoDevPage = () => {
  const [listingsResult, setListingsResult] = useState<any>(null);
  const [vinDetailsResult, setVinDetailsResult] = useState<any>(null);
  const [loadingListings, setLoadingListings] = useState(false);
  const [loadingVinDetails, setLoadingVinDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testVin = 'ZPBUA1ZL9KLA00848'; // The example VIN you provided

  const handleFetchListings = async () => {
    setLoadingListings(true);
    setError(null);
    setListingsResult(null);
    try {
      console.log('Fetching listings from auto.dev...');
      const data = await fetchAutoDevListings(); // No filters for initial test
      console.log('Listings API Response:', data);
      setListingsResult(data);
      if (data.length === 0) {
        console.warn('Received empty array for listings. Check API or if data source is empty.');
      }
    } catch (err: any) {
      console.error('Error fetching listings:', err);
      setError(`Failed to fetch listings: ${err.message}`);
      setListingsResult({ error: err.message, details: err.response?.data });
    } finally {
      setLoadingListings(false);
    }
  };

  const handleFetchVinDetails = async () => {
    setLoadingVinDetails(true);
    setError(null);
    setVinDetailsResult(null);
    try {
      console.log(`Fetching VIN details for ${testVin} from auto.dev...`);
      const data = await fetchAutoDevVinDetails(testVin);
      console.log('VIN Details API Response:', data);
      setVinDetailsResult(data);
      if (!data) {
        console.warn('Received null for VIN details. Check VIN or API.');
      }
    } catch (err: any) {
      console.error('Error fetching VIN details:', err);
      setError(`Failed to fetch VIN details: ${err.message}`);
      setVinDetailsResult({ error: err.message, details: err.response?.data });
    } finally {
      setLoadingVinDetails(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Test auto.dev API Integration</h1>
      <p>Open your browser's developer console to see detailed logs.</p>
      
      <div style={{ marginBottom: '20px' }}>
        <button onClick={handleFetchListings} disabled={loadingListings}>
          {loadingListings ? 'Fetching Listings...' : 'Fetch Vehicle Listings'}
        </button>
        {listingsResult && (
          <pre style={{ maxHeight: '300px', overflow: 'auto', border: '1px solid #ccc', padding: '10px', background: '#f9f9f9' }}>
            {JSON.stringify(listingsResult, null, 2)}
          </pre>
        )}
      </div>

      <div style={{ marginBottom: '20px' }}>
        <button onClick={handleFetchVinDetails} disabled={loadingVinDetails}>
          {loadingVinDetails ? 'Fetching VIN Details...' : `Fetch VIN Details for ${testVin}`}
        </button>
        {vinDetailsResult && (
          <pre style={{ maxHeight: '300px', overflow: 'auto', border: '1px solid #ccc', padding: '10px', background: '#f9f9f9' }}>
            {JSON.stringify(vinDetailsResult, null, 2)}
          </pre>
        )}
      </div>
      
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
    </div>
  );
};

export default TestAutoDevPage;
