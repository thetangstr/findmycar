export interface Vehicle {
  id: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  exteriorColor: string;
  interiorColor: string;
  fuelType: string;
  transmission: string;
  engine: string;
  vin: string;
  description: string;
  features: string[];
  images: string[];
  location: string;
  dealer: string;
  listingDate: string;
  source: string;
  url: string;
  // Image loading state properties
  hasErrorLoadingImage?: boolean;
  _retryCount?: number;
}

export interface SearchFilters {
  make?: string;
  model?: string;
  yearMin?: number;
  yearMax?: number;
  priceMin?: number;
  priceMax?: number;
  mileageMin?: number;
  mileageMax?: number;
  fuelType?: string;
  transmission?: string;
  exteriorColor?: string;
  interiorColor?: string;
  bodyType?: string;
  features?: string[];
  drivetrain?: string;
  sellerType?: string;
  distance?: number;
  zipCode?: string;
  query?: string;
  sortBy?: string;
  sortDirection?: 'asc' | 'desc';
}

export interface SavedSearch {
  id: string;
  name: string;
  filters: SearchFilters;
  createdAt: string;
}

export interface ComparisonItem {
  vehicleId: string;
  addedAt: string;
}

export interface RecentlyViewedItem {
  vehicleId: string;
  viewedAt: string;
}

export interface FavoriteItem {
  vehicleId: string;
  addedAt: string;
}

export interface SocialPost {
  id: string;
  platform: 'youtube' | 'tiktok' | 'instagram' | 'twitter' | 'reddit';
  title: string;
  description: string;
  thumbnail: string;
  url: string;
  author: string;
  authorAvatar?: string;
  publishedAt: string;
  viewCount?: number;
  likeCount?: number;
  commentCount?: number;
  tags: string[];
  relevanceScore: number;
  isPinned?: boolean;
}

export interface SocialPostsResponse {
  posts: SocialPost[];
  total: number;
  hasMore: boolean;
}
