import * as SecureStore from 'expo-secure-store';

const API_KEY_STORAGE_KEY = 'educational_app_api_key';

export class SecureStorage {
  /**
   * Store API key securely on device
   */
  static async storeApiKey(apiKey) {
    try {
      await SecureStore.setItemAsync(API_KEY_STORAGE_KEY, apiKey);
      return true;
    } catch (error) {
      console.error('Failed to store API key:', error);
      return false;
    }
  }

  /**
   * Retrieve API key from secure storage
   */
  static async getApiKey() {
    try {
      const apiKey = await SecureStore.getItemAsync(API_KEY_STORAGE_KEY);
      return apiKey;
    } catch (error) {
      console.error('Failed to retrieve API key:', error);
      return null;
    }
  }

  /**
   * Remove API key from storage
   */
  static async removeApiKey() {
    try {
      await SecureStore.deleteItemAsync(API_KEY_STORAGE_KEY);
      return true;
    } catch (error) {
      console.error('Failed to remove API key:', error);
      return false;
    }
  }

  /**
   * Check if API key exists
   */
  static async hasApiKey() {
    const apiKey = await this.getApiKey();
    return apiKey !== null && apiKey.length > 0;
  }
}