import axios from 'axios';
import { generateCarImage } from './socialMediaService';

/**
 * Interface for Reddit posts returned by the API
 */
export interface RedditPost {
  id: string;
  title: string;
  author: string;
  permalink: string;
  url: string;
  thumbnail: string;
  created_utc: number;
  num_comments: number;
  score: number;
  selftext: string;
  is_video: boolean;
  media?: {
    reddit_video?: {
      fallback_url: string;
    };
  };
  preview?: {
    images: Array<{
      source: {
        url: string;
      };
      resolutions: Array<{
        url: string;
        width: number;
        height: number;
      }>;
    }>;
  };
}

/**
 * Interface for processed Reddit posts for display in the UI
 */
export interface ProcessedRedditPost {
  id: string;
  title: string;
  description: string;
  author: string;
  url: string;
  thumbnail: string;
  publishedAt: string;
  commentCount: number;
  likeCount: number;
  viewCount?: number;
  platform: string;
  relevanceScore: number;
  isPinned: boolean;
}

/**
 * Format a Reddit post into a standard format for the app
 */
const formatRedditPost = (post: RedditPost, relevanceToQuery: number): ProcessedRedditPost => {
  // Get the best thumbnail image available
  let thumbnailUrl = post.thumbnail;
  if (post.preview && post.preview.images && post.preview.images.length > 0) {
    // Get medium resolution if available
    const resolutions = post.preview.images[0].resolutions;
    if (resolutions && resolutions.length > 0) {
      // Find a medium-sized image (around 400-600px wide)
      const mediumImage = resolutions.find(res => res.width >= 400 && res.width <= 600);
      if (mediumImage) {
        thumbnailUrl = mediumImage.url.replace(/&amp;/g, '&');
      } else {
        // Use the largest available
        thumbnailUrl = resolutions[resolutions.length - 1].url.replace(/&amp;/g, '&');
      }
    } else if (post.preview.images[0].source) {
      thumbnailUrl = post.preview.images[0].source.url.replace(/&amp;/g, '&');
    }
  }
  
  // If it's a video post, try to get a video thumbnail
  if (post.is_video && post.media?.reddit_video) {
    thumbnailUrl = `https://i.ytimg.com/vi/${post.id}/hqdefault.jpg`;
  }
  
  // If thumbnail is "self" or "default", it's not a real image
  if (thumbnailUrl === 'self' || thumbnailUrl === 'default' || thumbnailUrl === 'nsfw' || !thumbnailUrl) {
    // Generate a car-related image using the post ID as lock parameter
    const postMake = post.title.split(' ')[0] || 'car';
    const postModel = post.title.split(' ')[1] || 'auto';
    thumbnailUrl = generateCarImage(postMake, postModel, parseInt(post.id.substring(0, 8), 16) % 1000);
  }

  // Get a description from the post
  let description = post.selftext;
  if (description.length > 150) {
    description = description.substring(0, 147) + '...';
  }
  if (!description) {
    description = post.title;
  }

  return {
    id: post.id,
    title: post.title,
    description,
    author: post.author,
    url: `https://www.reddit.com${post.permalink}`,
    thumbnail: thumbnailUrl,
    publishedAt: new Date(post.created_utc * 1000).toISOString(),
    commentCount: post.num_comments,
    likeCount: post.score,
    viewCount: undefined, // Reddit doesn't provide view counts
    platform: 'reddit',
    relevanceScore: relevanceToQuery,
    isPinned: false
  };
};

/**
 * Calculate the relevance score of a post to the search query
 */
const calculateRelevanceScore = (post: RedditPost, make: string, model: string): number => {
  let score = 0;
  const title = post.title.toLowerCase();
  const selftext = post.selftext.toLowerCase();
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
  
  // Check for exact mentions in post content
  if (selftext.includes(`${makeLower} ${modelLower}`)) {
    score += 25;
  } else {
    // Check for individual mentions in post content
    if (selftext.includes(makeLower)) score += 10;
    if (selftext.includes(modelLower)) score += 15;
  }
  
  // Check for variants and common misspellings
  const modelVariants = getModelVariants(makeLower, modelLower);
  modelVariants.forEach(variant => {
    if (title.includes(variant)) score += 15;
    if (selftext.includes(variant)) score += 10;
  });

  // If post has high engagement, boost its score
  if (post.score > 100) score += 10;
  if (post.num_comments > 50) score += 10;
  
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
 * Fetch Reddit posts related to a specific car make and model
 */
export const fetchCarRelatedRedditPosts = async (
  make: string, 
  model: string,
  year?: number,
  limit = 25
): Promise<ProcessedRedditPost[]> => {
  try {
    // Build search query - starting with most specific terms
    let searchQuery = `${make} ${model}`;
    if (year) searchQuery += ` ${year}`;

    // Base subreddits relevant to cars
    const baseSubreddits = [
      'cars', 'carporn', 'autos', 'autodetailing',
      'whatcarshouldibuy', 'UserCars', 'carbuying'
    ];

    // Add make-specific subreddits if they are common, otherwise they are part of the query
    // For the proxy, we can let it handle a broader query and rely on Reddit's search for sub-community relevance.
    // We can include the make and model in the list passed to the proxy if desired, or keep it simpler.
    // For now, let's keep the subreddit list somewhat generic for the proxy, 
    // as the searchQuery itself is quite specific.
    const subredditListParam = baseSubreddits.join('+');

    // Use the new proxy endpoint
    const proxyUrl = `/api/reddit-proxy`;
    const params = {
      searchQuery: searchQuery, // searchQuery already includes make, model, year
      subreddits: subredditListParam,
      limit: limit.toString(),
      sort: 'relevance',
      t: 'year'
    };

    const response = await axios.get(proxyUrl, { params });
    
    if (response.status !== 200) {
      throw new Error(`Reddit API returned status code ${response.status}`);
    }
    
    // Check if response has the expected structure
    if (!response.data || !response.data.data || !response.data.data.children) {
      console.warn('Invalid Reddit API response structure:', response.data);
      return [];
    }
    
    // Extract posts from response
    const posts: RedditPost[] = response.data.data.children.map((child: any) => child.data).filter(Boolean);
    
    // Process and filter posts
    const processedPosts = posts
      .filter(post => {
        // Filter out posts that are not directly related to the car
        const relevance = calculateRelevanceScore(post, make, model);
        return relevance >= 30; // Only include posts with at least 30% relevance
      })
      .map(post => {
        const relevance = calculateRelevanceScore(post, make, model);
        return formatRedditPost(post, relevance);
      })
      .sort((a, b) => b.relevanceScore - a.relevanceScore); // Sort by relevance
    
    return processedPosts;
  } catch (error) {
    console.error('Error fetching Reddit posts:', error);
    return [];
  }
};
