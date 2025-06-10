import axios from 'axios';
import { SocialPost, SocialPostsResponse } from '@/types';

// Gemini AI configuration
const GEMINI_API_KEY = process.env.NEXT_PUBLIC_GEMINI_API_KEY;
const GEMINI_API_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';

// Cache for social media posts to avoid unnecessary API calls
const socialMediaCache = new Map<string, { data: SocialPostsResponse; timestamp: number }>();
const CACHE_DURATION = 30 * 60 * 1000; // 30 minutes

/**
 * Get trending social media posts about a specific vehicle
 */
export const getSocialPostsForVehicle = async (
  make: string,
  model: string,
  year?: number,
  limit: number = 10
): Promise<SocialPostsResponse> => {
  const cacheKey = `${make}-${model}-${year || 'all'}`;
  
  // Check cache first
  const cached = socialMediaCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }

  try {
    // Build search query
    const searchQuery = year 
      ? `${year} ${make} ${model} review test drive`
      : `${make} ${model} review test drive`;

    // Generate AI-powered social posts using Gemini
    const aiPosts = await generateAISocialPosts(make, model, year, limit);
    const allPosts: SocialPost[] = aiPosts;

    // Sort by relevance score and recency
    const sortedPosts = allPosts
      .sort((a, b) => {
        // First sort by relevance, then by date
        const relevanceDiff = b.relevanceScore - a.relevanceScore;
        if (relevanceDiff !== 0) return relevanceDiff;
        return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime();
      })
      .slice(0, limit);

    const result: SocialPostsResponse = {
      posts: sortedPosts,
      total: sortedPosts.length,
      hasMore: allPosts.length > limit
    };

    // Cache the result
    socialMediaCache.set(cacheKey, { data: result, timestamp: Date.now() });

    return result;
  } catch (error) {
    console.error('Error fetching social posts:', error);
    
    // Fallback to mock data only
    const mockPosts = await getMockSocialPosts(make, model, year, limit);
    return {
      posts: mockPosts,
      total: mockPosts.length,
      hasMore: false
    };
  }
};

/**
 * Generate AI-powered social posts using Gemini
 */
const generateAISocialPosts = async (
  make: string, 
  model: string, 
  year?: number, 
  limit: number = 10
): Promise<SocialPost[]> => {
  if (!GEMINI_API_KEY) {
    console.warn('Gemini API key not configured, using mock data');
    return getMockSocialPosts(make, model, year, limit);
  }

  try {
    const carName = year ? `${year} ${make} ${model}` : `${make} ${model}`;
    
    const prompt = `Generate ${limit} realistic social media posts about the ${carName}. Include a mix of platforms (YouTube, Reddit, TikTok, Instagram). For each post, provide:

1. Platform (youtube/reddit/tiktok/instagram/twitter)
2. Title (engaging and realistic)
3. Description (2-3 sentences)
4. Author name (realistic channel/username)
5. View count (realistic numbers)
6. Like count (realistic numbers)
7. Comment count (realistic numbers)
8. Days since published (1-90 days)
9. Relevance score (60-95)

Make the content diverse: reviews, comparisons, ownership experiences, test drives, etc. Use realistic engagement numbers and channel names. Format as JSON array.

Example format:
[
  {
    "platform": "youtube",
    "title": "2023 Toyota Camry Review - Worth The Hype?",
    "description": "After driving the new Camry for a week, here are my honest thoughts. The interior is impressive but there are some concerns.",
    "author": "AutoReview Central",
    "viewCount": 125000,
    "likeCount": 3400,
    "commentCount": 230,
    "daysAgo": 7,
    "relevanceScore": 85
  }
]`;

    const response = await axios.post(
      `${GEMINI_API_BASE_URL}?key=${GEMINI_API_KEY}`,
      {
        contents: [{
          parts: [{
            text: prompt
          }]
        }]
      },
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );

    const generatedText = response.data.candidates[0].content.parts[0].text;
    
    // Extract JSON from the response
    const jsonMatch = generatedText.match(/\[[\s\S]*\]/);
    if (!jsonMatch) {
      throw new Error('No valid JSON found in Gemini response');
    }

    const socialData = JSON.parse(jsonMatch[0]);
    
    return socialData.map((item: any, index: number) => ({
      id: `ai-${make}-${model}-${index}`,
      platform: item.platform,
      title: item.title,
      description: item.description,
      thumbnail: `https://picsum.photos/480/360?random=${make}${model}${index}`,
      url: generatePlatformUrl(item.platform, item.title, make, model),
      author: item.author,
      publishedAt: new Date(Date.now() - (item.daysAgo * 24 * 60 * 60 * 1000)).toISOString(),
      viewCount: item.viewCount || 0,
      likeCount: item.likeCount || 0,
      commentCount: item.commentCount || 0,
      tags: [make.toLowerCase(), model.toLowerCase(), 'review', 'car'],
      relevanceScore: item.relevanceScore || 75,
      isPinned: index === 0 // First post is pinned
    }));

  } catch (error) {
    console.error('Error generating AI social posts:', error);
    // Fallback to mock data
    return getMockSocialPosts(make, model, year, limit);
  }
};

/**
 * Generate platform-specific URLs
 */
const generatePlatformUrl = (platform: string, title: string, make: string, model: string): string => {
  const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  const carSlug = `${make}-${model}`.toLowerCase();
  
  switch (platform) {
    case 'youtube':
      return `https://youtube.com/watch?v=${carSlug}-${slug}`;
    case 'reddit':
      return `https://reddit.com/r/cars/comments/${carSlug}_${slug}`;
    case 'tiktok':
      return `https://tiktok.com/@user/${carSlug}-${slug}`;
    case 'instagram':
      return `https://instagram.com/p/${carSlug}-${slug}`;
    case 'twitter':
      return `https://twitter.com/user/status/${carSlug}-${slug}`;
    default:
      return `https://example.com/${platform}/${carSlug}-${slug}`;
  }
};

/**
 * Generate mock social posts for fallback
 */
const getMockSocialPosts = async (
  make: string,
  model: string,
  year?: number,
  limit: number = 5
): Promise<SocialPost[]> => {
  const carName = year ? `${year} ${make} ${model}` : `${make} ${model}`;
  
  const mockPosts: SocialPost[] = [
    {
      id: 'mock-1',
      platform: 'youtube',
      title: `${carName} Review - Everything You Need to Know!`,
      description: `Comprehensive review of the ${carName} covering performance, interior, exterior, and value. Is it worth buying?`,
      thumbnail: `https://picsum.photos/480/360?random=${make}${model}1`,
      url: `https://youtube.com/watch?v=mock-${make}-${model}-1`,
      author: 'AutoReview Pro',
      publishedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      viewCount: 125000,
      likeCount: 3400,
      commentCount: 230,
      tags: ['review', 'car', make.toLowerCase(), model.toLowerCase()],
      relevanceScore: 85,
      isPinned: true
    },
    {
      id: 'mock-2',
      platform: 'youtube',
      title: `${carName} vs Competition - Which Should You Buy?`,
      description: `Comparing the ${carName} against its main competitors. Which one offers the best value?`,
      thumbnail: `https://picsum.photos/480/360?random=${make}${model}2`,
      url: `https://youtube.com/watch?v=mock-${make}-${model}-2`,
      author: 'Car Comparison Central',
      publishedAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
      viewCount: 89000,
      likeCount: 2100,
      commentCount: 156,
      tags: ['comparison', 'vs', make.toLowerCase(), model.toLowerCase()],
      relevanceScore: 75
    },
    {
      id: 'mock-3',
      platform: 'youtube',
      title: `First Drive: ${carName} - Initial Impressions`,
      description: `Taking the ${carName} for its first test drive. Here are my honest first impressions.`,
      thumbnail: `https://picsum.photos/480/360?random=${make}${model}3`,
      url: `https://youtube.com/watch?v=mock-${make}-${model}-3`,
      author: 'Daily Drive Reviews',
      publishedAt: new Date(Date.now() - 21 * 24 * 60 * 60 * 1000).toISOString(),
      viewCount: 67000,
      likeCount: 1800,
      commentCount: 89,
      tags: ['first drive', 'test drive', make.toLowerCase(), model.toLowerCase()],
      relevanceScore: 70
    },
    {
      id: 'mock-4',
      platform: 'reddit',
      title: `Just bought a ${carName} - AMA!`,
      description: `Picked up my ${carName} yesterday. Happy to answer any questions about the buying experience and first impressions.`,
      thumbnail: `https://picsum.photos/480/360?random=${make}${model}4`,
      url: `https://reddit.com/r/cars/mock-${make}-${model}`,
      author: 'u/CarEnthusiast2024',
      publishedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      viewCount: 0,
      likeCount: 234,
      commentCount: 67,
      tags: ['ownership', 'experience', make.toLowerCase(), model.toLowerCase()],
      relevanceScore: 65
    },
    {
      id: 'mock-5',
      platform: 'youtube',
      title: `${carName} Long Term Review - 6 Months Later`,
      description: `After 6 months and 10,000 miles, here's my honest long-term review of the ${carName}.`,
      thumbnail: `https://picsum.photos/480/360?random=${make}${model}5`,
      url: `https://youtube.com/watch?v=mock-${make}-${model}-5`,
      author: 'Long Term Auto',
      publishedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      viewCount: 45000,
      likeCount: 1200,
      commentCount: 78,
      tags: ['long term', 'ownership', make.toLowerCase(), model.toLowerCase()],
      relevanceScore: 80
    }
  ];

  return mockPosts.slice(0, limit);
};

/**
 * Get popular hashtags for a vehicle
 */
export const getPopularHashtags = (make: string, model: string): string[] => {
  const baseTags = [`#${make}`, `#${model}`, `#${make}${model}`];
  const carTags = ['#CarReview', '#TestDrive', '#AutoReview', '#CarBuying', '#Cars'];
  
  return [...baseTags, ...carTags];
};

/**
 * Clear social media cache
 */
export const clearSocialMediaCache = (): void => {
  socialMediaCache.clear();
}; 