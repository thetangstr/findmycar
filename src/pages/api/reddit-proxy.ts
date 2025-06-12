import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { searchQuery, subreddits = 'cars+carporn+autos+autodetailing+whatcarshouldibuy+UserCars+carbuying', limit = 10, sort = 'relevance', t = 'year' } = req.query;

  if (!searchQuery) {
    return res.status(400).json({ 
      error: 'Search query is required',
      data: { children: [] } // Provide empty data structure for client safety
    });
  }

  const subredditList = Array.isArray(subreddits) ? subreddits.join('+') : subreddits;
  const redditUrl = `https://www.reddit.com/r/${subredditList}/search.json?q=${encodeURIComponent(searchQuery as string)}&sort=${sort}&restrict_sr=on&t=${t}&limit=${limit}`;

  try {
    // Add timeout to fetch to prevent hanging requests
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
    
    const redditResponse = await fetch(redditUrl, {
      headers: {
        'User-Agent': 'FindMyCar/1.0 (Web App; findmycar-347ec.web.app)',
      },
      signal: controller.signal
    });
    
    clearTimeout(timeoutId); // Clear timeout if fetch completes

    if (!redditResponse.ok) {
      const errorText = await redditResponse.text();
      console.error(`Reddit API error (${redditResponse.status}): ${errorText}`);
      // Return a safe response structure even on error
      return res.status(200).json({ 
        error: `Failed to fetch from Reddit: ${redditResponse.statusText}`, 
        data: { children: [] } // Provide empty data structure for client safety
      });
    }

    const data = await redditResponse.json();
    
    // Validate the response structure
    if (!data || !data.data || !Array.isArray(data.data.children)) {
      console.error('Invalid Reddit API response structure:', data);
      return res.status(200).json({ 
        error: 'Invalid Reddit API response structure', 
        data: { children: [] } // Provide empty data structure for client safety
      });
    }
    
    res.status(200).json(data);
  } catch (error: any) {
    console.error('Error proxying Reddit request:', error);
    // Always return a safe structure even on errors
    res.status(200).json({ 
      error: 'Internal server error proxying Reddit request: ' + (error.message || 'Unknown error'),
      data: { children: [] } // Provide empty data structure for client safety
    });
  }
}
