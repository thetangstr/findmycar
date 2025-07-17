// src/pages/api/autodev/listings.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

const AUTO_DEV_API_BASE_URL = 'https://auto.dev/api';
const API_KEY = process.env.NEXT_PUBLIC_AUTO_DEV_API_KEY;

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  console.log('[API DEBUG] Received listings request with query:', req.query);
  
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  if (!API_KEY) {
    console.error('[API DEBUG] Auto.dev API key is not defined on the server.');
    return res.status(500).json({ error: 'API key not configured' });
  }

  try {
    console.log('[API DEBUG] Making request to auto.dev API');
    
    // Forward query parameters from the client to the auto.dev API
    const response = await axios.get(`${AUTO_DEV_API_BASE_URL}/listings`, {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Accept': 'application/json',
      },
      params: req.query, // Forwards any query params like filters
    });
    
    console.log('[API DEBUG] auto.dev API response status:', response.status);
    console.log('[API DEBUG] auto.dev API response structure:', {
      hasRecords: !!response.data?.records,
      recordsLength: response.data?.records?.length || 0,
      hasListings: !!response.data?.listings,
      listingsLength: response.data?.listings?.length || 0,
      keys: Object.keys(response.data || {})
    });
    
    // Transform the response to a consistent format
    // The auto.dev API might return data in 'records' or 'listings' depending on the endpoint
    const transformedData = {
      listings: response.data.records || response.data.listings || []
    };
    
    console.log('[API DEBUG] Sending transformed data with', transformedData.listings.length, 'listings');
    
    res.status(200).json(transformedData);
  } catch (error: any) {
    console.error('[API DEBUG] Error proxying listings request to auto.dev:', error.message);
    if (axios.isAxiosError(error) && error.response) {
      console.error('[API DEBUG] auto.dev API Error Status:', error.response.status);
      console.error('[API DEBUG] auto.dev API Error Data:', error.response.data);
      return res.status(error.response.status || 500).json(error.response.data || { message: 'Error fetching listings from auto.dev' });
    }
    res.status(500).json({ message: 'Internal server error while fetching listings' });
  }
}