import { useState, useEffect } from 'react';
import { authToken } from "../lib/authToken";

/**
 * Custom hook for secure authentication token storage
 * Uses sessionStorage instead of localStorage for improved XSS protection
 */
export function useAuthStorage() {
  const [token, setTokenState] = useState<string | null>(null);

  useEffect(() => {
    const stored = authToken.get();
    if (stored) setTokenState(stored);
  }, []);

  const setToken = (newToken: string) => {
    authToken.set(newToken);
    setTokenState(newToken);
  };

  const removeToken = () => {
    authToken.clear();
    setTokenState(null);
  };

  return { token, setToken, removeToken };
}
