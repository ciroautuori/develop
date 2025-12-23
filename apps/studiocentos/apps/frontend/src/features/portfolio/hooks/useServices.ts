/**
 * useServices Hook - Fetch services data
 */

import { useState, useEffect } from 'react';
import type { Service } from '../api/portfolioApi';

interface UseServicesParams {
  featured?: boolean;
}

interface UseServicesReturn {
  services: Service[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useServices({ featured = false }: UseServicesParams = {}): UseServicesReturn {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchServices = async () => {
    try {
      setLoading(true);
      setError(null);

      const { portfolioApi } = await import('../api/portfolioApi');
      const data = featured
        ? await portfolioApi.getFeaturedServices()
        : await portfolioApi.getServices();

      setServices(data.services || []);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
      console.error('Error fetching services:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServices();
  }, [featured]);

  return {
    services,
    loading,
    error,
    refetch: fetchServices,
  };
}
