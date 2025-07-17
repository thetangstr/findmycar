// src/pages/api/autodev/vin.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

const AUTO_DEV_API_BASE_URL = 'https://auto.dev/api';
const API_KEY = process.env.NEXT_PUBLIC_AUTO_DEV_API_KEY;

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  const { vin } = req.query;

  if (!vin || typeof vin !== 'string') {
    return res.status(400).json({ error: 'VIN parameter is required' });
  }

  if (!API_KEY) {
    console.error('Auto.dev API key is not defined on the server.');
    return res.status(500).json({ error: 'API key not configured' });
  }

  try {
    // Make request to auto.dev API for VIN details
    const response = await axios.get(`${AUTO_DEV_API_BASE_URL}/vin/${vin}`, {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Accept': 'application/json',
      }
    });
    
    res.status(200).json(response.data);
  } catch (error: any) {
    console.error(`Error proxying VIN request to auto.dev for VIN ${vin}:`, error.message);
    if (axios.isAxiosError(error) && error.response) {
      console.error('auto.dev API Error Status:', error.response.status);
      console.error('auto.dev API Error Data:', error.response.data);
      return res.status(error.response.status || 500).json(error.response.data || { message: `Error fetching VIN details for ${vin} from auto.dev` });
    }
    res.status(500).json({ message: 'Internal server error while fetching VIN details' });
  }
}
