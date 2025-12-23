// Centralized API configuration

export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || '',
  API_PATH: '/api',
  TIMEOUT: 30000,
} as const;

export const getApiBaseUrl = (): string => {
  const base = API_CONFIG.BASE_URL;
  const apiPath = API_CONFIG.API_PATH;

  if (!base) return apiPath;

  const normalizedBase = base.endsWith("/") ? base.slice(0, -1) : base;
  if (normalizedBase.endsWith(apiPath)) return normalizedBase;
  return `${normalizedBase}${apiPath}`;
};

export const getApiUrl = (path: string = ''): string => {
  const apiBase = getApiBaseUrl();
  if (!path) return apiBase;

  const p = path.startsWith("/") ? path : `/${path}`;
  const apiPath = API_CONFIG.API_PATH;
  if (p.startsWith(apiPath)) {
    return `${apiBase}${p.slice(apiPath.length)}`;
  }
  return `${apiBase}${p}`;
};

export const getFullUrl = (path: string): string => {
  return `${API_CONFIG.BASE_URL}${path}`;
};
