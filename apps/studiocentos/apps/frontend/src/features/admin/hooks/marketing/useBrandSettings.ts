/**
 * Custom Hook: useBrandSettings
 * Manages Brand DNA persistence (load/save from API)
 * Uses localStorage as cache for offline access
 */

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import type { BrandSettings, BrandSettingsCreate } from '../../types/business-dna.types';
import { DEFAULT_BRAND_SETTINGS } from '../../types/business-dna.types';

const CACHE_KEY = 'brand_settings_cache';
const API_BASE = '/api/v1/marketing';

interface UseBrandSettingsReturn {
  // State
  brandSettings: BrandSettings | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;

  // Actions
  load: () => Promise<void>;
  save: (data: BrandSettingsCreate) => Promise<BrandSettings | null>;
  patch: (data: Partial<BrandSettingsCreate>) => Promise<BrandSettings | null>;
  reset: () => void;

  // Utilities
  getAIContext: () => Promise<{ context: string | null; brand_name: string | null } | null>;
  hasSettings: boolean;
}

export function useBrandSettings(): UseBrandSettingsReturn {
  const [brandSettings, setBrandSettings] = useState<BrandSettings | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get auth token
  const getToken = useCallback(() => {
    return localStorage.getItem('admin_token');
  }, []);

  // Save to localStorage cache
  const saveToCache = useCallback((data: BrandSettings) => {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify({
        data,
        timestamp: Date.now()
      }));
    } catch (err) {
      console.warn('Failed to cache brand settings:', err);
    }
  }, []);

  // Load from localStorage cache
  const loadFromCache = useCallback((): BrandSettings | null => {
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        // Cache valid for 1 hour
        if (Date.now() - timestamp < 3600000) {
          return data;
        }
      }
    } catch (err) {
      console.warn('Failed to load cached brand settings:', err);
    }
    return null;
  }, []);

  // Load brand settings from API
  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    const token = getToken();
    if (!token) {
      setError('Non autenticato');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/brand-dna`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data) {
          setBrandSettings(data);
          saveToCache(data);
        } else {
          // No settings yet, use defaults
          setBrandSettings(null);
        }
      } else if (response.status === 401) {
        setError('Sessione scaduta');
        toast.error('Sessione scaduta, effettua nuovamente il login');
      } else {
        throw new Error('Errore nel caricamento');
      }
    } catch (err) {
      // Try loading from cache on error
      const cached = loadFromCache();
      if (cached) {
        setBrandSettings(cached);
        toast.info('Caricato da cache locale');
      } else {
        const message = err instanceof Error ? err.message : 'Errore sconosciuto';
        setError(message);
      }
    } finally {
      setIsLoading(false);
    }
  }, [getToken, saveToCache, loadFromCache]);

  // Save brand settings (create or update)
  const save = useCallback(async (data: BrandSettingsCreate): Promise<BrandSettings | null> => {
    setIsSaving(true);
    setError(null);

    const token = getToken();
    if (!token) {
      setError('Non autenticato');
      setIsSaving(false);
      return null;
    }

    try {
      const response = await fetch(`${API_BASE}/brand-dna`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        const savedData = await response.json();
        setBrandSettings(savedData);
        saveToCache(savedData);
        toast.success('Brand DNA salvato con successo!');
        return savedData;
      } else if (response.status === 401) {
        setError('Sessione scaduta');
        toast.error('Sessione scaduta');
        return null;
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Errore nel salvataggio');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Errore sconosciuto';
      setError(message);
      toast.error(message);
      return null;
    } finally {
      setIsSaving(false);
    }
  }, [getToken, saveToCache]);

  // Partial update
  const patch = useCallback(async (data: Partial<BrandSettingsCreate>): Promise<BrandSettings | null> => {
    setIsSaving(true);
    setError(null);

    const token = getToken();
    if (!token) {
      setError('Non autenticato');
      setIsSaving(false);
      return null;
    }

    try {
      const response = await fetch(`${API_BASE}/brand-dna`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        const savedData = await response.json();
        setBrandSettings(savedData);
        saveToCache(savedData);
        toast.success('Brand DNA aggiornato!');
        return savedData;
      } else if (response.status === 404) {
        // No existing settings, create new
        return save(data as BrandSettingsCreate);
      } else if (response.status === 401) {
        setError('Sessione scaduta');
        toast.error('Sessione scaduta');
        return null;
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Errore nell\'aggiornamento');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Errore sconosciuto';
      setError(message);
      toast.error(message);
      return null;
    } finally {
      setIsSaving(false);
    }
  }, [getToken, saveToCache, save]);

  // Get AI context for agents
  const getAIContext = useCallback(async () => {
    const token = getToken();
    if (!token) return null;

    try {
      const response = await fetch(`${API_BASE}/brand-dna/ai-context`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        return await response.json();
      }
      return null;
    } catch (err) {
      console.error('Failed to get AI context:', err);
      return null;
    }
  }, [getToken]);

  // Reset local state
  const reset = useCallback(() => {
    setBrandSettings(null);
    setError(null);
    localStorage.removeItem(CACHE_KEY);
  }, []);

  // Load from cache on mount and fetch fresh data
  useEffect(() => {
    const cached = loadFromCache();
    if (cached) {
      setBrandSettings(cached);
    }
    // Always fetch fresh data from API to ensure sync
    load();
  }, [loadFromCache, load]);

  return {
    brandSettings,
    isLoading,
    isSaving,
    error,
    load,
    save,
    patch,
    reset,
    getAIContext,
    hasSettings: brandSettings !== null
  };
}

export default useBrandSettings;
