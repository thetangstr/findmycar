import axios from 'axios';
import { generateCarImage } from './socialMediaService';

/**
 * Interface for YouTube videos returned by the API
 */
export interface YouTubeVideo {
  id: {
    kind: string;
    videoId: string;
  };
  snippet: {
    publishedAt: string;
    channelId: string;
    title: string;
    description: string;
    thumbnails: {
      default?: { url: string; width: number; height: number };
      medium?: { url: string; width: number; height: number };
      high?: { url: string; width: number; height: number };
      standard?: { url: string; width: number; height: number };
      maxres?: { url: string; width: number; height: number };
    };
    channelTitle: string;
    tags?: string[];
  };
  statistics?: {
    viewCount: string;
    likeCount: string;
    commentCount: string;
  };
}

/**
 * Interface for processed YouTube videos for display in the UI
 */
export interface ProcessedYouTubeVideo {
  id: string;
  title: string;
  description: string;
  author: string;
  url: string;
  thumbnail: string;
  publishedAt: string;
  commentCount: number;
  likeCount: number;
  viewCount: number;
  platform: string;
  relevanceScore: number;
  isPinned: boolean;
}

/**
 * Format a YouTube video into a standard format for the app
 */
const formatYouTubeVideo = (video: YouTubeVideo, relevanceToQuery: number): ProcessedYouTubeVideo => {
  // Get the best thumbnail using maxres if available (highest quality)
  // YouTube API provides multiple thumbnail qualities
  let thumbnail;
  
  if (video.snippet.thumbnails) {
    // Try to get the highest quality thumbnail available
    thumbnail = video.snippet.thumbnails.maxres?.url || 
                video.snippet.thumbnails.high?.url || 
                video.snippet.thumbnails.medium?.url || 
                video.snippet.thumbnails.default?.url;
  }

  // If no thumbnail is found or if URL is invalid, use a reliable car-related image
  if (!thumbnail) {
    // Extract make/model from title more carefully
    const titleParts = video.snippet.title.toLowerCase().split(' ');
    let videoMake = 'car';
    let videoModel = 'automotive';
    
    // Try to extract a car make/model from the title
    const commonMakes = ['toyota', 'honda', 'ford', 'bmw', 'audi', 'mercedes', 'porsche', 'ferrari', 'lamborghini'];
    for (const make of commonMakes) {
      if (titleParts.includes(make)) {
        videoMake = make;
        const makeIndex = titleParts.indexOf(make);
        if (makeIndex >= 0 && titleParts.length > makeIndex + 1) {
          videoModel = titleParts[makeIndex + 1];
        }
        break;
      }
    }
    
    // Use high-quality car image from unsplash with the video ID as a seed
    const seed = parseInt(video.id.videoId.substring(0, 8), 16) % 1000;
    thumbnail = generateCarImage(videoMake, videoModel, seed);
  }
  
  // Get video stats or provide defaults
  const statistics = video.statistics || {
    viewCount: '0',
    likeCount: '0',
    commentCount: '0'
  };

  // Extract a shorter description
  let description = video.snippet.description;
  if (description.length > 150) {
    description = description.substring(0, 147) + '...';
  }

  return {
    id: video.id.videoId,
    title: video.snippet.title,
    description,
    author: video.snippet.channelTitle,
    url: `https://www.youtube.com/watch?v=${video.id.videoId}`,
    thumbnail,
    publishedAt: video.snippet.publishedAt,
    commentCount: parseInt(statistics.commentCount, 10) || 0,
    likeCount: parseInt(statistics.likeCount, 10) || 0,
    viewCount: parseInt(statistics.viewCount, 10) || 0,
    platform: 'youtube',
    relevanceScore: relevanceToQuery,
    isPinned: false
  };
};

/**
 * Calculate the relevance score of a video to the search query
 */
const calculateRelevanceScore = (video: YouTubeVideo, make: string, model: string): number => {
  let score = 0;
  const title = video.snippet.title.toLowerCase();
  const description = video.snippet.description.toLowerCase();
  const makeLower = make.toLowerCase();
  const modelLower = model.toLowerCase();
  
  // Check for exact mentions in title (most important)
  if (title.includes(`${makeLower} ${modelLower}`)) {
    score += 50;
  } else {
    // Check for individual mentions in title
    if (title.includes(makeLower)) score += 20;
    if (title.includes(modelLower)) score += 25;
  }
  
  // Check for exact mentions in description
  if (description.includes(`${makeLower} ${modelLower}`)) {
    score += 25;
  } else {
    // Check for individual mentions in description
    if (description.includes(makeLower)) score += 10;
    if (description.includes(modelLower)) score += 15;
  }
  
  // Check for variants and common misspellings
  const modelVariants = getModelVariants(makeLower, modelLower);
  modelVariants.forEach(variant => {
    if (title.includes(variant)) score += 15;
    if (description.includes(variant)) score += 10;
  });

  // If title contains review-related keywords, boost score
  const reviewKeywords = ['review', 'test drive', 'driving', 'pov', 'walkaround', 'tour'];
  if (reviewKeywords.some(keyword => title.includes(keyword))) {
    score += 15;
  }
  
  // Cap the score at 100
  return Math.min(score, 100);
};

/**
 * Get common variations of model names for better matching
 */
const getModelVariants = (make: string, model: string): string[] => {
  const variants: string[] = [];
  
  // Handle special cases
  if (make === 'bmw' && model.match(/^\d+$/)) {
    // For BMW numeric models (e.g. "330i"), add variants
    variants.push(`${make} ${model[0]}-series`);
    variants.push(`${model[0]}-series`);
    variants.push(`${model}`);
  } else if (make === 'mercedes-benz' || make === 'mercedes') {
    variants.push(`mb ${model}`);
    // For Mercedes classes (e.g. "C-Class", "E-Class")
    if (model.includes('class')) {
      const classLetter = model.split(' ')[0].replace('-', '');
      variants.push(classLetter);
      variants.push(`${classLetter} class`);
    }
  } else if (make === 'porsche' && model.match(/^\d+$/)) {
    variants.push(`${model}`);
  } else if (make === 'tesla') {
    variants.push(`model ${model}`);
  }
  
  // Common abbreviations and variations
  variants.push(model.replace(' ', ''));  // No spaces
  variants.push(model.replace('-', '')); // No hyphens
  
  return variants.filter(v => v !== model && v !== make); // Remove duplicates
};

/**
 * Fetch YouTube videos related to a specific car make and model
 */
export const fetchCarRelatedYouTubeVideos = async (
  make: string, 
  model: string,
  year?: number,
  limit = 10
): Promise<ProcessedYouTubeVideo[]> => {
  const apiKey = process.env.NEXT_PUBLIC_YOUTUBE_API_KEY;

  if (!apiKey || apiKey.trim() === '') {
    console.warn('[YouTubeService] YouTube API key (NEXT_PUBLIC_YOUTUBE_API_KEY) not found or is empty. YouTube video fetching will be disabled.');
    return []; // Return empty array if API key is missing
  }

  try {
    // Build search query - starting with most specific terms
    let searchQuery = `${make} ${model}`;
    if (year) searchQuery += ` ${year}`;
    
    // Add relevant search terms for car content
    // Adding "automotive" helps filter out non-car content
    searchQuery += ' review test drive automotive';

    // YouTube search API - with higher result count to ensure enough car-related videos
    const searchUrl = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(searchQuery)}&type=video&maxResults=${Math.min(limit * 2, 50)}&relevanceLanguage=en&videoDuration=medium&key=${apiKey}`;
    
    const searchResponse = await axios.get(searchUrl);
    
    if (searchResponse.status !== 200) {
      throw new Error(`YouTube API returned status code ${searchResponse.status}`);
    }
    
    // Extract videos from response
    const videos: YouTubeVideo[] = searchResponse.data.items;
    
    if (videos.length === 0) {
      console.warn(`[YouTubeService] No videos found for query: ${searchQuery}`);
      return [];
    }
    
    // Get additional video details including statistics and contentDetails
    // This fetches better thumbnails as well as video stats
    const videoIds = videos.map(video => video.id.videoId).join(',');
    const detailsUrl = `https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id=${videoIds}&key=${apiKey}`;
    
    let videoDetails: any[] = [];
    try {
      const detailsResponse = await axios.get(detailsUrl);
      videoDetails = detailsResponse.data.items;
    } catch (error) {
      console.error('[YouTubeService] Error fetching video details:', error);
    }
    
    // Merge detailed info into videos
    const videosWithStats = videos.map(video => {
      const details = videoDetails.find(detail => detail.id === video.id.videoId);
      if (details) {
        // Update with better quality snippet/thumbnails from details API
        video.statistics = details.statistics;
        if (details.snippet && details.snippet.thumbnails) {
          video.snippet.thumbnails = details.snippet.thumbnails;
        }
      }
      return video;
    });
    
    // Process and filter videos
    const processedVideos = videosWithStats
      .filter(video => {
        // Filter out videos that are not directly related to the car
        const relevance = calculateRelevanceScore(video, make, model);
        return relevance >= 40; // Only include videos with at least 40% relevance
      })
      .map(video => {
        const relevance = calculateRelevanceScore(video, make, model);
        return formatYouTubeVideo(video, relevance);
      })
      .sort((a, b) => b.relevanceScore - a.relevanceScore); // Sort by relevance
    
    // Limit to requested number
    return processedVideos.slice(0, limit);
  } catch (error) {
    console.error('[YouTubeService] Error fetching YouTube videos:', error);
    return [];
  }
};
