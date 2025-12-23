/**
 * useScheduledPosts Hook
 * Manages scheduled posts state with CRUD operations
 * ELIMINATES 6x duplicate fetch() calls!
 */

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import {
  MarketingApiService,
  ScheduledPost,
  PostFilters,
  CreatePostDto,
  UpdatePostDto
} from '../../services/marketing-api.service';

export function useScheduledPosts(autoFetch: boolean = false) {
  const [posts, setPosts] = useState<ScheduledPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const fetchPosts = useCallback(async (filters?: PostFilters) => {
    setLoading(true);
    setError(null);

    try {
      const result = await MarketingApiService.getScheduledPosts(filters);
      setPosts(result.items || []);
      setTotal(result.total || 0);
      return result.items;
    } catch (err: any) {
      const errorMessage = err.message || 'Errore nel caricamento dei post';
      setError(errorMessage);
      console.error('[useScheduledPosts] fetch error:', err);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const createPost = async (post: CreatePostDto): Promise<ScheduledPost | null> => {
    try {
      const newPost = await MarketingApiService.createScheduledPost(post);
      setPosts(prev => [newPost, ...prev]);
      setTotal(prev => prev + 1);
      toast.success('Post programmato con successo!');
      return newPost;
    } catch (err: any) {
      toast.error('Errore nella creazione del post');
      console.error('[useScheduledPosts] create error:', err);
      return null;
    }
  };

  const updatePost = async (id: number, updates: UpdatePostDto): Promise<ScheduledPost | null> => {
    try {
      const updated = await MarketingApiService.updatePost(id, updates);
      setPosts(prev => prev.map(p => p.id === id ? updated : p));
      toast.success('Post aggiornato!');
      return updated;
    } catch (err: any) {
      toast.error('Errore nell\'aggiornamento');
      console.error('[useScheduledPosts] update error:', err);
      return null;
    }
  };

  const deletePost = async (id: number): Promise<boolean> => {
    try {
      await MarketingApiService.deletePost(id);
      setPosts(prev => prev.filter(p => p.id !== id));
      setTotal(prev => prev - 1);
      toast.success('Post eliminato');
      return true;
    } catch (err: any) {
      toast.error('Errore nell\'eliminazione');
      console.error('[useScheduledPosts] delete error:', err);
      return false;
    }
  };

  const publishNow = async (id: number): Promise<ScheduledPost | null> => {
    try {
      const published = await MarketingApiService.publishPostNow(id);
      setPosts(prev => prev.map(p => p.id === id ? published : p));
      toast.success('Pubblicazione avviata!');
      return published;
    } catch (err: any) {
      toast.error('Errore nella pubblicazione');
      console.error('[useScheduledPosts] publish error:', err);
      return null;
    }
  };

  const cancelPost = async (id: number): Promise<ScheduledPost | null> => {
    try {
      const cancelled = await MarketingApiService.cancelPost(id);
      setPosts(prev => prev.map(p => p.id === id ? cancelled : p));
      toast.success('Post annullato');
      return cancelled;
    } catch (err: any) {
      toast.error('Errore nell\'annullamento');
      console.error('[useScheduledPosts] cancel error:', err);
      return null;
    }
  };

  // Auto-fetch on mount if enabled
  useEffect(() => {
    if (autoFetch) {
      fetchPosts();
    }
  }, [autoFetch, fetchPosts]);

  return {
    posts,
    loading,
    error,
    total,
    fetchPosts,
    createPost,
    updatePost,
    deletePost,
    publishNow,
    cancelPost
  };
}
