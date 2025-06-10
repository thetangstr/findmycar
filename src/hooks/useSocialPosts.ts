import { useState, useEffect } from 'react';
import { SocialPost, SocialPostsResponse } from '@/types';
import { getSocialPostsForVehicle } from '@/services/socialMediaService';

export const useSocialPosts = (make: string, model: string, year?: number, limit: number = 10) => {
  const [posts, setPosts] = useState<SocialPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    fetchSocialPosts();
  }, [make, model, year, limit]);

  const fetchSocialPosts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response: SocialPostsResponse = await getSocialPostsForVehicle(make, model, year, limit);
      
      setPosts(response.posts);
      setHasMore(response.hasMore);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load social posts';
      setError(errorMessage);
      console.error('Error fetching social posts:', err);
      
      // Set empty posts on error
      setPosts([]);
      setHasMore(false);
    } finally {
      setLoading(false);
    }
  };

  const refetch = () => {
    fetchSocialPosts();
  };

  const filterByPlatform = (platform: string): SocialPost[] => {
    if (platform === 'all') {
      return posts;
    }
    return posts.filter(post => post.platform === platform);
  };

  const getAvailablePlatforms = (): string[] => {
    const platforms = Array.from(new Set(posts.map(post => post.platform)));
    return ['all', ...platforms];
  };

  return {
    posts,
    loading,
    error,
    hasMore,
    refetch,
    filterByPlatform,
    getAvailablePlatforms
  };
}; 