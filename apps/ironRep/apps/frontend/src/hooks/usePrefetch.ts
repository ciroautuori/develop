/**
 * Data Prefetching Hooks & Utilities
 * Smart prefetching strategies for improved perceived performance
 */

import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useCallback } from 'react';
import { workoutsApi, progressApi, usersApi, biometricsApi } from '../lib/api';

/**
 * Prefetch workout data on app initialization
 */
export function usePrefetchCriticalData() {
  const queryClient = useQueryClient();

  useEffect(() => {
    // Prefetch today's workout (most likely to be accessed)
    queryClient.prefetchQuery({
      queryKey: ['workout', 'today'],
      queryFn: async () => {
        const response = await workoutsApi.getToday();
        return response.data;
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
    });

    // Prefetch user profile
    queryClient.prefetchQuery({
      queryKey: ['user', 'profile'],
      queryFn: async () => {
        const response = await usersApi.getProfile();
        return response.data;
      },
      staleTime: 10 * 60 * 1000, // 10 minutes
    });

    // Prefetch latest biometrics
    queryClient.prefetchQuery({
      queryKey: ['biometrics', 'latest'],
      queryFn: async () => {
        const response = await biometricsApi.getLatest();
        return response.data;
      },
      staleTime: 15 * 60 * 1000, // 15 minutes
    });
  }, [queryClient]);
}

/**
 * Prefetch data on link hover (desktop only)
 */
export function usePrefetchOnHover() {
  const queryClient = useQueryClient();

  const prefetchWorkout = useCallback(() => {
    queryClient.prefetchQuery({
      queryKey: ['workout', 'today'],
      queryFn: async () => {
        const response = await workoutsApi.getToday();
        return response.data;
      },
    });
  }, [queryClient]);

  const prefetchProgress = useCallback(() => {
    queryClient.prefetchQuery({
      queryKey: ['progress', 'dashboard'],
      queryFn: async () => {
        const response = await progressApi.getDashboard();
        return response.data;
      },
    });
  }, [queryClient]);

  const prefetchProfile = useCallback(() => {
    queryClient.prefetchQuery({
      queryKey: ['user', 'profile'],
      queryFn: async () => {
        const response = await usersApi.getProfile();
        return response.data;
      },
    });
  }, [queryClient]);

  return {
    prefetchWorkout,
    prefetchProgress,
    prefetchProfile,
  };
}

/**
 * Prefetch based on time of day and user patterns
 */
export function useSmartPrefetch() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const hour = new Date().getHours();

    // Morning (6-11): Prefetch workout
    if (hour >= 6 && hour < 11) {
      queryClient.prefetchQuery({
        queryKey: ['workout', 'today'],
        queryFn: async () => {
          const response = await workoutsApi.getToday();
          return response.data;
        },
      });
    }

    // Evening (18-22): Prefetch progress data
    if (hour >= 18 && hour < 22) {
      queryClient.prefetchQuery({
        queryKey: ['progress', 'dashboard'],
        queryFn: async () => {
          const response = await progressApi.getDashboard();
          return response.data;
        },
      });
    }
  }, [queryClient]);
}

/**
 * Prefetch next/previous items in a list
 */
export function usePrefetchAdjacent<T>(
  items: T[],
  currentIndex: number,
  queryKeyFn: (item: T) => unknown[],
  queryFn: (item: T) => Promise<unknown>
) {
  const queryClient = useQueryClient();

  useEffect(() => {
    // Prefetch next item
    if (currentIndex < items.length - 1) {
      const nextItem = items[currentIndex + 1];
      queryClient.prefetchQuery({
        queryKey: queryKeyFn(nextItem),
        queryFn: () => queryFn(nextItem),
      });
    }

    // Prefetch previous item
    if (currentIndex > 0) {
      const prevItem = items[currentIndex - 1];
      queryClient.prefetchQuery({
        queryKey: queryKeyFn(prevItem),
        queryFn: () => queryFn(prevItem),
      });
    }
  }, [currentIndex, items, queryClient, queryKeyFn, queryFn]);
}

/**
 * Prefetch images in viewport + next screen
 */
export function usePrefetchImages(imageUrls: string[]) {
  useEffect(() => {
    const prefetchImage = (url: string) => {
      const img = new Image();
      img.src = url;
    };

    // Prefetch all images
    imageUrls.forEach(prefetchImage);
  }, [imageUrls]);
}

/**
 * Invalidate and refetch stale data on window focus
 */
export function useRefetchOnFocus() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const handleFocus = () => {
      // Refetch all active queries
      queryClient.refetchQueries({ type: 'active' });
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [queryClient]);
}

/**
 * Background sync for non-critical data
 */
export function useBackgroundSync(interval: number = 5 * 60 * 1000) {
  const queryClient = useQueryClient();

  useEffect(() => {
    const syncInterval = setInterval(() => {
      // Sync user data
      queryClient.invalidateQueries({ queryKey: ['user'] });

      // Sync biometrics
      queryClient.invalidateQueries({ queryKey: ['biometrics'] });
    }, interval);

    return () => clearInterval(syncInterval);
  }, [queryClient, interval]);
}
