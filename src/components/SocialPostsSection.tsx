import React, { useState } from 'react';
import { useSocialPosts } from '@/hooks/useSocialPosts';
import { getPopularHashtags } from '@/services/socialMediaService';

interface SocialPostsSectionProps {
  make: string;
  model: string;
  year?: number;
  className?: string;
}

const SocialPostsSection: React.FC<SocialPostsSectionProps> = ({
  make,
  model,
  year,
  className = ''
}) => {
  const { posts, loading, error, getAvailablePlatforms } = useSocialPosts(make, model, year, 12);
  const [showAll, setShowAll] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState<string>('all');

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'youtube':
        return (
          <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 24 24">
            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
          </svg>
        );
      case 'tiktok':
        return (
          <svg className="w-5 h-5 text-black" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12.53.02C13.84 0 15.14.01 16.44 0c.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>
          </svg>
        );
      case 'instagram':
        return (
          <svg className="w-5 h-5 text-pink-600" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12.017 0C8.396 0 7.999.01 6.756.048 5.517.087 4.668.222 3.935.42 3.176.628 2.534.895 1.893 1.536 1.253 2.177.985 2.819.778 3.578.579 4.311.444 5.16.405 6.399.366 7.642.356 8.039.356 11.017v1.983c0 2.978.01 3.375.048 4.618.039 1.24.173 2.089.372 2.822.207.759.474 1.401 1.115 2.042.641.641 1.283.908 2.042 1.115.733.199 1.582.333 2.822.372C7.999 23.99 8.396 24 12.017 24s4.018-.01 5.261-.048c1.24-.039 2.089-.173 2.822-.372.759-.207 1.401-.474 2.042-1.115.641-.641.908-1.283 1.115-2.042.199-.733.333-1.582.372-2.822.039-1.243.048-1.64.048-4.618v-1.983c0-2.978-.01-3.375-.048-4.618-.039-1.24-.173-2.089-.372-2.822-.207-.759-.474-1.401-1.115-2.042C22.419.985 21.777.718 21.018.511 20.285.312 19.436.178 18.196.139 16.953.099 16.556.089 13.978.089H12.017zm-.017 2.158c2.98 0 3.331.01 4.506.048 1.087.049 1.678.228 2.071.378.521.202.892.444 1.283.835.391.391.633.762.835 1.283.15.393.329.984.378 2.071.038 1.175.048 1.526.048 4.506s-.01 3.331-.048 4.506c-.049 1.087-.228 1.678-.378 2.071-.202.521-.444.892-.835 1.283-.391.391-.762.633-1.283.835-.393.15-.984.329-2.071.378-1.175.038-1.526.048-4.506.048s-3.331-.01-4.506-.048c-1.087-.049-1.678-.228-2.071-.378-.521-.202-.892-.444-1.283-.835-.391-.391-.633-.762-.835-1.283-.15-.393-.329-.984-.378-2.071-.038-1.175-.048-1.526-.048-4.506s.01-3.331.048-4.506c.049-1.087.228-1.678.378-2.071.202-.521.444-.892.835-1.283.391-.391.762-.633 1.283-.835.393-.15.984-.329 2.071-.378 1.175-.038 1.526-.048 4.506-.048z"/>
            <path d="M12.017 15.84a3.824 3.824 0 1 1 0-7.648 3.824 3.824 0 0 1 0 7.648zm0-6.706a2.882 2.882 0 1 0 0 5.764 2.882 2.882 0 0 0 0-5.764zm5.444-1.404a.893.893 0 1 1-1.786 0 .893.893 0 0 1 1.786 0z"/>
          </svg>
        );
      case 'twitter':
        return (
          <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
          </svg>
        );
      case 'reddit':
        return (
          <svg className="w-5 h-5 text-orange-600" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2.04c-5.5 0-10 4.49-10 10.02 0 5 3.66 9.15 8.44 9.9v-7H7.9v-2.9h2.54V9.85c0-2.51 1.49-3.89 3.78-3.89 1.09 0 2.23.19 2.23.19v2.47h-1.26c-1.24 0-1.63.77-1.63 1.56v1.88h2.78l-.45 2.9h-2.33v7a10 10 0 0 0 8.44-9.9c0-5.53-4.5-10.02-10-10.02z"/>
          </svg>
        );
    }
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffInDays === 0) return 'Today';
    if (diffInDays === 1) return 'Yesterday';
    if (diffInDays < 7) return `${diffInDays} days ago`;
    if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
    if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`;
    return `${Math.floor(diffInDays / 365)} years ago`;
  };

  const filteredPosts = selectedPlatform === 'all' 
    ? posts 
    : posts.filter(post => post.platform === selectedPlatform);

  const displayedPosts = showAll ? filteredPosts : filteredPosts.slice(0, 6);

  const platforms = getAvailablePlatforms();
  const hashtags = getPopularHashtags(make, model);

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4 w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="border rounded-lg p-4">
                <div className="h-40 bg-gray-200 rounded mb-3"></div>
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || posts.length === 0) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Trending Social Posts</h2>
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.47.943-6.01 2.472" />
          </svg>
          <p className="text-gray-500">No social posts found for this vehicle.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Trending Social Posts
          </h2>
          <p className="text-gray-600 text-sm">
            Latest reviews and discussions about the {year} {make} {model}
          </p>
        </div>
        
        {/* Platform Filters */}
        <div className="flex flex-wrap gap-2 mt-4 lg:mt-0">
          {platforms.map(platform => (
            <button
              key={platform}
              onClick={() => setSelectedPlatform(platform)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                selectedPlatform === platform
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {platform === 'all' ? 'All' : platform.charAt(0).toUpperCase() + platform.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Popular Hashtags */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Popular Hashtags</h3>
        <div className="flex flex-wrap gap-2">
          {hashtags.map(tag => (
            <span
              key={tag}
              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Posts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        {displayedPosts.map(post => (
          <div
            key={post.id}
            className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow duration-200"
          >
            {/* Thumbnail */}
            <div className="relative">
              <img
                src={post.thumbnail}
                alt={post.title}
                className="w-full h-40 object-cover"
                onError={(e) => {
                  e.currentTarget.src = 'https://via.placeholder.com/480x360/f3f4f6/9ca3af?text=No+Image';
                }}
              />
              {post.isPinned && (
                <div className="absolute top-2 left-2 bg-yellow-500 text-white px-2 py-1 rounded text-xs font-medium">
                  📌 Pinned
                </div>
              )}
              <div className="absolute top-2 right-2 bg-black bg-opacity-70 text-white p-1 rounded">
                {getPlatformIcon(post.platform)}
              </div>
              {post.platform === 'youtube' && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-12 h-12 bg-red-600 bg-opacity-80 rounded-full flex items-center justify-center text-white">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </div>
                </div>
              )}
            </div>

            {/* Content */}
            <div className="p-4">
              <h3 className="font-medium text-gray-900 text-sm mb-2 line-clamp-2">
                {post.title}
              </h3>
              
              <p className="text-gray-600 text-xs mb-3 line-clamp-2">
                {post.description}
              </p>

              {/* Author and Date */}
              <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                <span className="truncate">{post.author}</span>
                <span>{formatDate(post.publishedAt)}</span>
              </div>

              {/* Stats */}
              <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                <div className="flex items-center space-x-3">
                  {post.viewCount && post.viewCount > 0 && (
                    <span className="flex items-center">
                      <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                      </svg>
                      {formatNumber(post.viewCount)}
                    </span>
                  )}
                  {post.likeCount && post.likeCount > 0 && (
                    <span className="flex items-center">
                      <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8.864 15.674c-.956.24-1.939-.924-1.383-1.641.265-.339.652-.558 1.08-.617.948-.129 1.853.533 2.05 1.446a1.5 1.5 0 01-1.747 1.812zM12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.77 5.82 22 7 14.14 2 9.27l6.91-1.01L12 2z"/>
                      </svg>
                      {formatNumber(post.likeCount)}
                    </span>
                  )}
                  {post.commentCount && post.commentCount > 0 && (
                    <span className="flex items-center">
                      <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M21 6h-2v9H6v2c0 .55.45 1 1 1h11l4 4V7c0-.55-.45-1-1-1zm-4 6V3c0-.55-.45-1-1-1H3c-.55 0-1 .45-1 1v14l4-4h11c.55 0 1-.45 1-1z"/>
                      </svg>
                      {formatNumber(post.commentCount)}
                    </span>
                  )}
                </div>
                <div className={`px-2 py-1 rounded text-xs font-medium ${
                  post.relevanceScore >= 80 ? 'bg-green-100 text-green-800' :
                  post.relevanceScore >= 60 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {post.relevanceScore}% relevant
                </div>
              </div>

              {/* View Button */}
              <a
                href={post.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full bg-primary-600 text-white text-center py-2 px-4 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
              >
                Watch {post.platform === 'youtube' ? 'Video' : 'Post'}
              </a>
            </div>
          </div>
        ))}
      </div>

      {/* Show More Button */}
      {filteredPosts.length > 6 && (
        <div className="text-center">
          <button
            onClick={() => setShowAll(!showAll)}
            className="bg-gray-100 text-gray-700 px-6 py-2 rounded-md font-medium hover:bg-gray-200 transition-colors"
          >
            {showAll ? 'Show Less' : `Show All ${filteredPosts.length} Posts`}
          </button>
        </div>
      )}
    </div>
  );
};

export default SocialPostsSection; 