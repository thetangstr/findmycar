import React from 'react';
import { SocialPost } from '@/types';
import { useSocialPosts } from '@/hooks/useSocialPosts';
import { FaReddit, FaYoutube, FaInstagram, FaTiktok, FaTwitter } from 'react-icons/fa';

interface SocialPostsCarouselProps {
  make: string;
  model: string;
  year?: number;
  className?: string;
}

const MAX_POSTS = 3; // Show only 3 posts

const platformIcon = {
  youtube: <FaYoutube className="text-red-600" />,
  reddit: <FaReddit className="text-orange-500" />,
  instagram: <FaInstagram className="text-pink-500" />,
  tiktok: <FaTiktok className="text-black" />,
  twitter: <FaTwitter className="text-blue-400" />,
};

const SocialPostsCarousel: React.FC<SocialPostsCarouselProps> = ({ make, model, year, className = '' }) => {
  const { posts, loading, error } = useSocialPosts(make, model, year, MAX_POSTS);

  // Helper: format date
  const formatDate = (date: string) => new Date(date).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  if (loading) {
    return <div className={className}>Loading social posts...</div>;
  }

  if (error) {
    return <div className={className}>Failed to load social posts.</div>;
  }

  // Get only the first MAX_POSTS posts
  const displayPosts = posts.slice(0, MAX_POSTS);

  return (
    <div className={`${className} mt-4`}>
      <h2 className="text-xl font-semibold mb-4">Social Media</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {displayPosts.map((post) => (
          <a
            key={post.id}
            href={post.url}
            target="_blank"
            rel="noopener noreferrer"
            className={`bg-white rounded-lg shadow-md hover:shadow-lg transition-all overflow-hidden flex flex-col h-full relative ${
              post.isPinned ? 'ring-2 ring-primary-500' : ''
            }`}
          >
            <div className="relative h-48 overflow-hidden bg-gray-100 flex items-center justify-center">
              <img
                src={post.thumbnail}
                alt={post.title}
                className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
              />
              <div className="absolute bottom-2 left-2 bg-black/60 text-white text-xs px-2 py-1 rounded flex items-center space-x-1">
                {platformIcon[post.platform]}
                <span className="capitalize">{post.platform}</span>
              </div>
              {post.isPinned && (
                <div className="absolute top-2 right-2 bg-primary-500 text-white text-xs px-2 py-1 rounded">
                  Featured
                </div>
              )}
            </div>

            <div className="p-4 text-sm flex-1 flex flex-col">
              <h3 className="font-medium text-gray-900 line-clamp-2 mb-2">{post.title}</h3>
              <p className="text-gray-500 line-clamp-3 mb-3 flex-1">{post.description}</p>
              <div className="flex justify-between text-xs text-gray-400 mt-auto pt-2 border-t border-gray-100">
                <span>{post.author}</span>
                <span>{formatDate(post.publishedAt)}</span>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
};

export default SocialPostsCarousel;