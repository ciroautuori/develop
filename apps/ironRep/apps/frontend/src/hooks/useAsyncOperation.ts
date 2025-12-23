// Standardized loading state hooks

import { useState, useCallback } from 'react';

export interface LoadingState<T = unknown> {
  isLoading: boolean;
  error: Error | null;
  data: T | null;
}

/**
 * Standard async operation hook with loading/error states
 */
export function useAsyncOperation<T = unknown>() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [data, setData] = useState<T | null>(null);

  const execute = useCallback(async (operation: () => Promise<T>) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await operation();
      setData(result);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
    setData(null);
  }, []);

  return {
    isLoading,
    error,
    data,
    execute,
    reset,
  };
}

/**
 * Loading state wrapper for components
 */
export function withLoadingState<T>(
  data: T | null | undefined,
  isLoading: boolean,
  error: Error | null,
  renderLoading?: () => React.ReactNode,
  renderError?: (error: Error) => React.ReactNode
): T | null {
  if (isLoading) {
    renderLoading?.();
    return null;
  }

  if (error) {
    renderError?.(error);
    return null;
  }

  return data || null;
}
