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
    // Use mock data directly since API routes don't work in static export mode
    // This provides realistic Reddit posts with proper links and thumbnails
    const mockPosts = await getMockSocialPosts(make, model, year, limit);
    
    // Sort by relevance score and recency
    const sortedPosts = mockPosts
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
      total: sortedPosts.length,
      hasMore: false
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
 * Generate a high-quality car-related image URL using multiple reliable sources
 */
export const generateCarImage = (make: string, model: string, idx: number): string => {
  // Clean and normalize the make and model for better image results
  const cleanMake = make.toLowerCase().trim();
  const cleanModel = model.toLowerCase().trim();
  
  // For Porsche 911, use high-quality car images from multiple sources
  if (cleanMake === 'porsche' && cleanModel === '911') {
    const porscheImages = [
      // Better quality images that are more reliable
      `https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?w=1200&h=675&fit=crop&auto=format&q=80&ixlib=rb-4.0.3`, // Classic white 964
      `https://images.unsplash.com/photo-1544829099-b9a0c5303bea?w=1200&h=675&fit=crop&auto=format&q=80&ixlib=rb-4.0.3`, // Red Porsche 964 Turbo
      `https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1200&h=675&fit=crop&auto=format&q=80&ixlib=rb-4.0.3`, // Black Porsche
      `https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1200&h=675&fit=crop&auto=format&q=80&ixlib=rb-4.0.3`, // White Porsche
      `https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1200&h=675&fit=crop&auto=format&q=80&ixlib=rb-4.0.3`, // Blue Porsche
    ];
    const imageIndex = idx % porscheImages.length;
    return porscheImages[imageIndex];
  }
  
  // Fallback to high-quality placeholder images
  const fallbackImages = [
    `https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?w=1200&h=675&fit=crop&auto=format&q=80&ixlib=rb-4.0.3`,
    `https://images.unsplash.com/photo-1544829099-b9a0c5303bea?w=1200&h=675&fit=crop&auto=format&q=80&ixlib=rb-4.0.3`,
    `https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1200&h=675&fit=crop&auto=format&q=80&ixlib=rb-4.0.3`,
    `https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1200&h=675&fit=crop&auto=format&q=80&ixlib=rb-4.0.3`,
    `https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1200&h=675&fit=crop&auto=format&q=80&ixlib=rb-4.0.3`,
  ];
  
  const sourceIndex = idx % fallbackImages.length;
  return fallbackImages[sourceIndex];
};



/**
 * Generate mock social posts with real Reddit URLs and local images
 */
const getMockSocialPosts = async (
  make: string,
  model: string,
  year?: number,
  limit: number = 5
): Promise<SocialPost[]> => {
  const carName = year ? `${year} ${make} ${model}` : `${make} ${model}`;
  
  // Use the actual images from your other_porsche directory
  const mockPosts: SocialPost[] = [
    {
      id: 'reddit-mock-1',
      platform: 'reddit',
      title: '964 pricing has left reality',
      description: 'Anyone else feeling like 964 prices have completely lost touch with reality? Seeing decent examples at $150k+ now. Remember when these were $40k cars just a few years ago?',
      thumbnail: '/images/other_porsche/black.webp', // Use your actual local image
      url: 'https://www.reddit.com/r/porsche911/comments/1cmba8r/964_pricing_has_left_reality/',
      author: 'u/ClassicCarLament',
      publishedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      viewCount: 0,
      likeCount: 423,
      commentCount: 156,
      tags: ['pricing', 'market discussion', make.toLowerCase(), model.toLowerCase()],
      relevanceScore: 98,
      isPinned: true
    },
    {
      id: 'reddit-mock-2',
      platform: 'reddit',
      title: '964 Turbo with 6000 miles',
      description: 'Found this pristine 964 Turbo with only 6,000 miles on the odometer. The condition is absolutely mint but the asking price is astronomical. Are these low-mileage examples worth the premium?',
      thumbnail: '/images/other_porsche/red.jpg', // Use your actual local image
      url: 'https://www.reddit.com/r/Porsche/comments/1j9z76x/964_turbo_with_6000_miles/',
      author: 'u/LowMileageHunter',
      publishedAt: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
      viewCount: 0,
      likeCount: 634,
      commentCount: 128,
      tags: ['low mileage', 'turbo', make.toLowerCase(), model.toLowerCase()],
      relevanceScore: 94
    },
    {
      id: 'reddit-mock-3',
      platform: 'reddit',
      title: 'Porsche 911 Turbo 964 - which one is your style?',
      description: 'Comparison of different 964 Turbo styles and configurations. Love seeing all the variations - from stock to modified, each has its own character. Which setup speaks to you most?',
      thumbnail: '/images/other_porsche/blue.jpg', // Use your actual local image
      url: 'https://www.reddit.com/r/Porsche/comments/1k75i1x/porsche_911_turbo_964_which_one_is_your_style/',
      author: 'u/TurboStyleGuide',
      publishedAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
      viewCount: 0,
      likeCount: 287,
      commentCount: 91,
      tags: ['style comparison', 'turbo', make.toLowerCase(), model.toLowerCase()],
      relevanceScore: 90
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