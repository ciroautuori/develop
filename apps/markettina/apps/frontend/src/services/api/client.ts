import axios from 'axios';
import { STORAGE_KEYS } from '../../shared/config/constants';

// Create axios instance with base URL
const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1/admin',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Flag to prevent multiple refresh attempts
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else {
      promise.resolve(token!);
    }
  });
  failedQueue = [];
};

// Refresh token function
const refreshToken = async (): Promise<string | null> => {
  const refreshToken = localStorage.getItem(STORAGE_KEYS.adminRefreshToken);
  if (!refreshToken) return null;

  try {
    const response = await axios.post('/api/v1/admin/auth/refresh', {
      refresh_token: refreshToken,
    });

    const { access_token, refresh_token: newRefreshToken } = response.data;

    localStorage.setItem(STORAGE_KEYS.adminToken, access_token);
    if (newRefreshToken) {
      localStorage.setItem(STORAGE_KEYS.adminRefreshToken, newRefreshToken);
    }

    return access_token;
  } catch (error) {
    // Refresh failed, clear tokens
    localStorage.removeItem(STORAGE_KEYS.adminToken);
    localStorage.removeItem(STORAGE_KEYS.adminRefreshToken);
    return null;
  }
};

// Add request interceptor to attach token
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(STORAGE_KEYS.adminToken);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling and auto-refresh
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Wait for the refresh to complete
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return client(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newToken = await refreshToken();

        if (newToken) {
          processQueue(null, newToken);
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return client(originalRequest);
        } else {
          // No refresh token or refresh failed - redirect to login
          processQueue(error, null);
          window.location.href = '/admin/login';
          return Promise.reject(error);
        }
      } catch (refreshError) {
        processQueue(refreshError, null);
        window.location.href = '/admin/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Log auth errors for debugging
    if (error.response?.status === 401 || error.response?.status === 403) {
      console.error('Auth error:', error.response.status, error.config.url);
    }
    return Promise.reject(error);
  }
);

export default client;
