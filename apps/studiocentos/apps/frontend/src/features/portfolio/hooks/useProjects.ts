/**
 * useProjects Hook - Fetch projects data
 */

import { useState, useEffect } from 'react';
import type { Project } from '../api/portfolioApi';

interface UseProjectsParams {
  featured?: boolean;
}

interface UseProjectsReturn {
  projects: Project[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useProjects({ featured = false }: UseProjectsParams = {}): UseProjectsReturn {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);

      const { portfolioApi } = await import('../api/portfolioApi');
      const data = featured
        ? await portfolioApi.getFeaturedProjects()
        : await portfolioApi.getProjects();

      setProjects(data.projects || []);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
      console.error('Error fetching projects:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [featured]);

  return {
    projects,
    loading,
    error,
    refetch: fetchProjects,
  };
}
