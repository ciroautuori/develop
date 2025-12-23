import { useCallback } from 'react';
import client from '../../services/api/client';
import { AxiosRequestConfig } from 'axios';

/**
 * useApiClient Hook
 *
 * Provides a standardized way to make API calls using the configured axios client.
 * Handles auth tokens automatically via interceptors in client.ts.
 */
export function useApiClient() {
  const get = useCallback(async <T>(url: string, config?: AxiosRequestConfig) => {
    const response = await client.get<T>(url, config);
    return response.data;
  }, []);

  const post = useCallback(async <T>(url: string, data?: any, config?: AxiosRequestConfig) => {
    const response = await client.post<T>(url, data, config);
    return response.data;
  }, []);

  const put = useCallback(async <T>(url: string, data?: any, config?: AxiosRequestConfig) => {
    const response = await client.put<T>(url, data, config);
    return response.data;
  }, []);

  const del = useCallback(async <T>(url: string, config?: AxiosRequestConfig) => {
    const response = await client.delete<T>(url, config);
    return response.data;
  }, []);

  const patch = useCallback(async <T>(url: string, data?: any, config?: AxiosRequestConfig) => {
    const response = await client.patch<T>(url, data, config);
    return response.data;
  }, []);

  return { get, post, put, del, patch, client };
}
