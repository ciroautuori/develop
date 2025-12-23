/**
 * useToolAI Hook - Landing Page
 * Fetch ToolAI posts per la landing page
 */

import { useState, useEffect, useCallback } from 'react';
import type { ToolAIPost, ToolAIPostListResponse } from '../types/toolai.types';
import { fetchPublicPosts, fetchLatestPost } from '../../../services/api/toolai';

interface UseToolAIOptions {
  page?: number;
  perPage?: number;
  lang?: string;
}

interface UseToolAIReturn {
  posts: ToolAIPost[];
  latestPost: ToolAIPost | null;
  total: number;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useToolAI(options: UseToolAIOptions = {}): UseToolAIReturn {
  const { page = 1, perPage = 5, lang = 'it' } = options;

  const [posts, setPosts] = useState<ToolAIPost[]>([]);
  const [latestPost, setLatestPost] = useState<ToolAIPost | null>(null);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [postsData, latest] = await Promise.all([
        fetchPublicPosts(page, perPage, lang),
        fetchLatestPost(lang),
      ]);

      setPosts(postsData.posts);
      setTotal(postsData.total);
      setLatestPost(latest);
    } catch (err) {
      setError(err as Error);
      console.error('Error fetching ToolAI data:', err);
    } finally {
      setLoading(false);
    }
  }, [page, perPage, lang]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    posts,
    latestPost,
    total,
    loading,
    error,
    refetch: fetchData,
  };
}

/**
 * useLatestToolAI - Solo l'ultimo post
 */
export function useLatestToolAI(lang: string = 'it') {
  const [post, setPost] = useState<ToolAIPost | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchLatestPost(lang);
      setPost(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { post, loading, error, refetch: fetchData };
}
