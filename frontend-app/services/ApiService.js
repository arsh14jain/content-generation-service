import { API_CONFIG } from '../constants/config';
import { SecureStorage } from './SecureStorage';

export class ApiService {
  /**
   * Make authenticated API request
   */
  static async makeRequest(endpoint, options = {}) {
    try {
      // Get API key from secure storage
      const apiKey = await SecureStorage.getApiKey();
      
      if (!apiKey) {
        throw new Error('API key not found. Please configure the app.');
      }

      // Prepare headers
      const headers = {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey,
        ...options.headers,
      };

      // Make request
      const response = await fetch(`${API_CONFIG.BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });

      // Handle authentication errors
      if (response.status === 401) {
        throw new Error('Invalid API key. Please reconfigure the app.');
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  /**
   * Get mobile feed
   */
  static async getMobileFeed(limit = 20, offset = 0) {
    const response = await this.makeRequest(
      `/api/v1/mobile/feed?limit=${limit}&offset=${offset}`
    );
    return response.json();
  }

  /**
   * Update post feedback
   */
  static async updatePostFeedback(postId, feedback) {
    const response = await this.makeRequest(
      `/api/v1/mobile/posts/${postId}/feedback`,
      {
        method: 'PUT',
        body: JSON.stringify(feedback),
      }
    );
    return response.json();
  }

  /**
   * Get mobile stats
   */
  static async getMobileStats() {
    const response = await this.makeRequest('/api/v1/mobile/stats');
    return response.json();
  }
}