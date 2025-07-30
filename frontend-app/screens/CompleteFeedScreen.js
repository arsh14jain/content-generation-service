import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  FlatList,
  StyleSheet,
  Text,
  ActivityIndicator,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SPACING, API_CONFIG } from '../constants/config';

const CompleteFeedScreen = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState(null);
  const [offset, setOffset] = useState(0);

  const LIMIT = 20;

  useEffect(() => {
    loadPosts(true);
  }, []);

  const loadPosts = useCallback(async (reset = false) => {
    try {
      if (reset) {
        setLoading(true);
        setOffset(0);
      } else {
        setLoadingMore(true);
      }
      
      setError(null);
      
      const currentOffset = reset ? 0 : offset;
      const response = await fetch(
        `${API_CONFIG.BASE_URL}/api/v1/mobile/feed?limit=${LIMIT}&offset=${currentOffset}`,
        {
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': API_CONFIG.API_KEY,
          },
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.posts) {
        if (reset) {
          setPosts(data.posts);
          setOffset(data.posts.length);
        } else {
          setPosts(prevPosts => [...prevPosts, ...data.posts]);
          setOffset(prev => prev + data.posts.length);
        }
        
        // Use API metadata if available
        if (data.has_more !== undefined) {
          setHasMore(data.has_more);
        } else {
          setHasMore(data.posts.length === LIMIT);
        }
      } else {
        setError('No posts received from API');
        setHasMore(false);
      }
    } catch (err) {
      console.error('Error loading posts:', err);
      setError('Failed to load posts from API');
      
      // Only set fallback data on initial load
      if (reset) {
        setPosts([
          {
            post_id: 1,
            post_content: "🧠 Your brain grows with effort! Embrace challenges and see mistakes as learning opportunities. Growth mindset is the key to unlocking your potential!",
            timestamp: new Date().toISOString(),
            like_status: false,
            dislike_status: false,
            topic: { id: 1, topic_name: "Growth Mindset" }
          },
          {
            post_id: 2,
            post_content: "📚 Active recall beats passive reading every time. Quiz yourself, create flashcards, teach others. Your brain learns by doing, not just seeing!",
            timestamp: new Date().toISOString(),
            like_status: false,
            dislike_status: false,
            topic: { id: 2, topic_name: "Study Techniques" }
          },
          {
            post_id: 3,
            post_content: "🔄 Spaced repetition is learning's superpower. Review material at increasing intervals. Your memory will thank you with better retention!",
            timestamp: new Date().toISOString(),
            like_status: false,
            dislike_status: false,
            topic: { id: 3, topic_name: "Memory" }
          },
          {
            post_id: 4,
            post_content: "🎯 Focus on deep work! Single-tasking leads to better results than multitasking. Give your brain the attention it deserves for quality learning.",
            timestamp: new Date().toISOString(),
            like_status: false,
            dislike_status: false,
            topic: { id: 4, topic_name: "Focus" }
          },
          {
            post_id: 5,
            post_content: "💡 Learning is not a spectator sport. Engage actively with material through questioning, discussing, and applying concepts in real situations.",
            timestamp: new Date().toISOString(),
            like_status: false,
            dislike_status: false,
            topic: { id: 5, topic_name: "Active Learning" }
          }
        ]);
      }
      setHasMore(false);
    } finally {
      setLoading(false);
      setRefreshing(false);
      setLoadingMore(false);
    }
  }, [offset]);

  const handleLike = async (postId) => {
    try {
      const postIndex = posts.findIndex(p => p.post_id === postId);
      if (postIndex === -1) return;

      const currentPost = posts[postIndex];
      const newLikeStatus = !currentPost.like_status;

      // Update UI immediately (optimistic update)
      setPosts(prevPosts =>
        prevPosts.map(post =>
          post.post_id === postId
            ? { ...post, like_status: newLikeStatus, dislike_status: false }
            : post
        )
      );

      // Send to backend
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/mobile/posts/${postId}/feedback`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_CONFIG.API_KEY,
        },
        body: JSON.stringify({
          like_status: newLikeStatus,
          dislike_status: false
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update like status');
      }

      console.log('Like status updated successfully');
    } catch (error) {
      console.error('Error updating like:', error);
      // Revert optimistic update
      setPosts(prevPosts =>
        prevPosts.map(post =>
          post.post_id === postId
            ? { ...post, like_status: !post.like_status }
            : post
        )
      );
    }
  };

  const handleDislike = async (postId) => {
    try {
      const postIndex = posts.findIndex(p => p.post_id === postId);
      if (postIndex === -1) return;

      const currentPost = posts[postIndex];
      const newDislikeStatus = !currentPost.dislike_status;

      // Update UI immediately (optimistic update)
      setPosts(prevPosts =>
        prevPosts.map(post =>
          post.post_id === postId
            ? { ...post, dislike_status: newDislikeStatus, like_status: false }
            : post
        )
      );

      // Send to backend
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/mobile/posts/${postId}/feedback`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_CONFIG.API_KEY,
        },
        body: JSON.stringify({
          dislike_status: newDislikeStatus,
          like_status: false
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update dislike status');
      }

      console.log('Dislike status updated successfully');
    } catch (error) {
      console.error('Error updating dislike:', error);
      // Revert optimistic update
      setPosts(prevPosts =>
        prevPosts.map(post =>
          post.post_id === postId
            ? { ...post, dislike_status: !post.dislike_status }
            : post
        )
      );
    }
  };

  const handleRefresh = useCallback(() => {
    setRefreshing(true);
    loadPosts(true);
  }, []);

  const handleLoadMore = useCallback(() => {
    if (!loadingMore && hasMore && !loading) {
      loadPosts(false);
    }
  }, [loadingMore, hasMore, loading, loadPosts]);

  const renderFooter = () => {
    if (!loadingMore) return null;
    
    return (
      <View style={styles.footerLoader}>
        <ActivityIndicator size="small" color={COLORS.accent} />
        <Text style={styles.footerText}>Loading more posts...</Text>
      </View>
    );
  };

  const renderPost = ({ item }) => (
    <View style={styles.postCard}>
      <View style={styles.topicBadge}>
        <Text style={styles.topicText}>{item.topic.topic_name}</Text>
      </View>
      
      <Text style={styles.postContent}>{item.post_content}</Text>
      
      <View style={styles.postFooter}>
        <Text style={styles.timestamp}>
          {new Date(item.timestamp).toLocaleTimeString()}
        </Text>
        
        <View style={styles.actionButtons}>
          <TouchableOpacity
            style={[styles.actionButton, item.like_status && styles.likedButton]}
            onPress={() => handleLike(item.post_id)}
          >
            <Ionicons
              name={item.like_status ? 'heart' : 'heart-outline'}
              size={20}
              color={item.like_status ? COLORS.liked : COLORS.like}
            />
            <Text style={[styles.actionText, item.like_status && styles.likedText]}>
              {item.like_status ? 'Liked' : 'Like'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, item.dislike_status && styles.dislikedButton]}
            onPress={() => handleDislike(item.post_id)}
          >
            <Ionicons
              name={item.dislike_status ? 'thumbs-down' : 'thumbs-down-outline'}
              size={20}
              color={item.dislike_status ? COLORS.disliked : COLORS.dislike}
            />
            <Text style={[styles.actionText, item.dislike_status && styles.dislikedText]}>
              {item.dislike_status ? 'Disliked' : 'Dislike'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={COLORS.accent} />
          <Text style={styles.loadingText}>Loading educational content...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🎓 Educational Feed</Text>
        <Text style={styles.headerSubtitle}>
          {posts.length} posts • {error ? 'Offline mode' : 'Live from API'}
        </Text>
      </View>

      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>⚠️ {error}</Text>
        </View>
      )}

      <FlatList
        data={posts}
        renderItem={renderPost}
        keyExtractor={(item) => item.post_id.toString()}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={[COLORS.accent]}
            tintColor={COLORS.accent}
          />
        }
        onEndReached={handleLoadMore}
        onEndReachedThreshold={0.3}
        ListFooterComponent={renderFooter}
        removeClippedSubviews={true}
        maxToRenderPerBatch={10}
        windowSize={10}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  headerTitle: {
    color: COLORS.text,
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: SPACING.xs,
  },
  headerSubtitle: {
    color: COLORS.textSecondary,
    fontSize: 14,
  },
  errorBanner: {
    backgroundColor: '#ff4757',
    padding: SPACING.sm,
    marginHorizontal: SPACING.md,
    marginVertical: SPACING.sm,
    borderRadius: 4,
  },
  errorText: {
    color: COLORS.text,
    fontSize: 12,
    textAlign: 'center',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: COLORS.textSecondary,
    fontSize: 16,
    marginTop: SPACING.md,
  },
  listContainer: {
    paddingTop: SPACING.sm,
    paddingBottom: SPACING.xl,
  },
  postCard: {
    backgroundColor: COLORS.cardBackground,
    marginHorizontal: SPACING.md,
    marginVertical: SPACING.xs,
    padding: SPACING.md,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  topicBadge: {
    backgroundColor: COLORS.accent,
    paddingHorizontal: SPACING.sm,
    paddingVertical: SPACING.xs,
    borderRadius: 4,
    alignSelf: 'flex-start',
    marginBottom: SPACING.sm,
  },
  topicText: {
    color: COLORS.background,
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  postContent: {
    color: COLORS.text,
    fontSize: 16,
    lineHeight: 24,
    marginBottom: SPACING.md,
  },
  postFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  timestamp: {
    color: COLORS.textSecondary,
    fontSize: 12,
  },
  actionButtons: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: SPACING.sm,
    paddingVertical: SPACING.xs,
    borderRadius: 4,
    marginLeft: SPACING.sm,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  likedButton: {
    borderColor: COLORS.liked,
    backgroundColor: `${COLORS.liked}20`,
  },
  dislikedButton: {
    borderColor: COLORS.disliked,
    backgroundColor: `${COLORS.disliked}20`,
  },
  actionText: {
    color: COLORS.textSecondary,
    fontSize: 12,
    marginLeft: SPACING.xs,
    fontWeight: '500',
  },
  likedText: {
    color: COLORS.liked,
  },
  dislikedText: {
    color: COLORS.disliked,
  },
  footerLoader: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: SPACING.md,
  },
  footerText: {
    color: COLORS.textSecondary,
    fontSize: 14,
    marginLeft: SPACING.sm,
  },
});

export default CompleteFeedScreen;