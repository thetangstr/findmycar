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
                onError={(e) => {
                  // Multiple fallback strategy for better reliability
                  const currentSrc = e.currentTarget.src;
                  if (currentSrc.includes('images.unsplash.com')) {
                    // If Unsplash fails, try a placeholder
                    e.currentTarget.src = `https://via.placeholder.com/1200x675/dc2626/ffffff?text=Porsche+911`;
                  } else if (currentSrc.includes('via.placeholder.com')) {
                    // If placeholder fails, try a different one
                    e.currentTarget.src = `https://dummyimage.com/1200x675/2563eb/ffffff&text=Reddit+Post`;
                  } else {
                    // Final fallback - hide image and show fallback div
                    e.currentTarget.style.display = 'none';
                    const fallbackDiv = e.currentTarget.parentElement?.querySelector('.fallback-thumbnail');
                    if (fallbackDiv) {
                      (fallbackDiv as HTMLElement).style.display = 'flex';
                    }
                  }
                }}
              />
              <div className="fallback-thumbnail hidden w-full h-full bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center text-white">
                <div className="text-center">
                  <svg className="w-8 h-8 mx-auto mb-2" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14.238 15.348c.085-.4.122-.83.122-1.348 0-.434-.056-.822-.146-1.238.08-.06.146-.14.198-.24.096-.18.154-.38.154-.58 0-.34-.174-.66-.474-.84-.31-.18-.72-.28-1.14-.28-.42 0-.83.1-1.14.28-.3.18-.474.5-.474.84 0 .2.058.4.154.58.052.1.118.18.198.24-.09.416-.146.804-.146 1.238 0 .518.037.948.122 1.348.17.8.518 1.522 1.006 2.02.488.498 1.088.798 1.686.798.598 0 1.198-.3 1.686-.798.488-.498.836-1.22 1.006-2.02zm-4.69-2.262c-.118-.386-.132-.932-.132-1.086 0-.154.014-.7.132-1.086.118-.386.366-.614.502-.614.136 0 .384.228.502.614.118.386.132.932.132 1.086 0 .154-.014.7-.132 1.086-.118.386-.366.614-.502.614-.136 0-.384-.228-.502-.614zm7.662-1.656c0-2.07-1.68-3.75-3.75-3.75s-3.75 1.68-3.75 3.75 1.68 3.75 3.75 3.75 3.75-1.68 3.75-3.75z"/>
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                  </svg>
                  <span className="text-xs font-medium">Reddit Post</span>
                </div>
              </div>
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