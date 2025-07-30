// API Configuration
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  API_KEY: 'your_secure_api_key_here', // Replace with your actual API key
  ENDPOINTS: {
    POSTS: '/api/v1/posts',
    MOBILE_FEED: '/api/v1/mobile/feed',
    POST_FEEDBACK: (postId) => `/api/v1/posts/${postId}/feedback`,
    MOBILE_POST_FEEDBACK: (postId) => `/api/v1/mobile/posts/${postId}/feedback`,
    MOBILE_STATS: '/api/v1/mobile/stats',
  },
  PAGINATION: {
    LIMIT: 20,
    INITIAL_OFFSET: 0,
  },
};

// UI Constants
export const COLORS = {
  background: '#000000',
  cardBackground: '#1a1a1a',
  text: '#ffffff',
  textSecondary: '#b0b0b0',
  border: '#333333',
  like: '#ff6b6b',
  liked: '#ff4757',
  dislike: '#4834d4',
  disliked: '#40739e',
  accent: '#2ed573',
};

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
};

export const SIZES = {
  icon: 24,
  iconLarge: 32,
  borderRadius: 8,
  cardPadding: 16,
};