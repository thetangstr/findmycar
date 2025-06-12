import axios from 'axios';
import { SocialPost, SocialPostsResponse } from '@/types';
import { fetchCarRelatedRedditPosts, ProcessedRedditPost } from '@/services/redditService';
import { fetchCarRelatedYouTubeVideos, ProcessedYouTubeVideo } from '@/services/youtubeService';

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
    // Fetch posts from both platforms concurrently
    const [redditPosts, youtubePosts] = await Promise.all([
      fetchCarRelatedRedditPosts(make, model, year, Math.ceil(limit/2)),
      fetchCarRelatedYouTubeVideos(make, model, year, Math.ceil(limit/2))
    ]);
    
    // Combine posts from different platforms
    let allPosts: SocialPost[] = [
      ...redditPosts as SocialPost[],
      ...youtubePosts as SocialPost[]
    ];
    
    // If we don't have enough posts, fall back to mock data to fill the gap
    if (allPosts.length < limit) {
      const mockPosts = await getMockSocialPosts(make, model, year, limit - allPosts.length);
      allPosts = [...allPosts, ...mockPosts];
    }

    // Sort by relevance score and recency
    const sortedPosts = allPosts
      .sort((a, b) => {
        // First sort by relevance, then by date
        const relevanceDiff = b.relevanceScore - a.relevanceScore;
        if (relevanceDiff !== 0) return relevanceDiff;
        return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime();
      })
      .slice(0, limit);

    // Pin the most relevant post
    if (sortedPosts.length > 0) {
      sortedPosts[0].isPinned = true;
    }

    const result: SocialPostsResponse = {
      posts: sortedPosts,
      total: allPosts.length,
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
 * Generate platform-specific URLs for mock data
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
 * Generate a high-quality car-related image URL using Unsplash
 * This uses Unsplash's Source API which is free for public use and provides high-quality images.
 * We prioritize specific car makes and models but fall back to general automotive categories
 * when specific models aren't available.
 */
export const generateCarImage = (make: string, model: string, idx: number): string => {
  // Clean and normalize the make and model for better image results
  const cleanMake = make.toLowerCase().trim();
  const cleanModel = model.toLowerCase().trim();
  
  // Create an array of search terms from most specific to most general
  const searchTerms = [
    // Try specific make+model first
    `${cleanMake} ${cleanModel} car`,
    // Then just the make
    `${cleanMake} car`,
    // Then general car categories based on common vehicle types
    'sports car',
    'luxury car',
    'sedan car',
    'automotive'
  ];
  
  // Select a search term based on the idx to ensure variety
  // but still prioritize the specific make/model when available
  const termIndex = Math.min(idx % searchTerms.length, searchTerms.length - 1);
  const searchTerm = searchTerms[termIndex];
  
  // Unsplash Source API with customized parameters
  // Using 800x450 for high-quality 16:9 images ideal for thumbnails
  // The random seed is based on the idx parameter to ensure consistency
  return `https://source.unsplash.com/800x450/?${encodeURIComponent(searchTerm)}&sig=${idx}`;
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
      thumbnail: generateCarImage(make, model, 1),
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
      thumbnail: generateCarImage(make, model, 2),
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
      thumbnail: generateCarImage(make, model, 3),
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
      thumbnail: generateCarImage(make, model, 4),
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
      thumbnail: generateCarImage(make, model, 5),
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