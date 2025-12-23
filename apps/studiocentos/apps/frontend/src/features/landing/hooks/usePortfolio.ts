/**
 * Portfolio Data Hook
 * Supporta traduzioni multilingua (it, en, es)
 * Includes Projects, Services, and Courses
 */

import { useState, useEffect, useCallback } from 'react';
import type { PortfolioData } from '../types/landing.types';

export function usePortfolio(language: string = 'it') {
  const [data, setData] = useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchPortfolio = useCallback(async (lang: string) => {
    try {
      setLoading(true);

      // Fetch portfolio (projects + services) and courses in parallel
      const [portfolioRes, coursesRes] = await Promise.all([
        fetch(`/api/v1/portfolio/public?lang=${lang}`),
        fetch(`/api/v1/courses/public?lang=${lang}`)
      ]);

      if (!portfolioRes.ok) {
        throw new Error(`Failed to fetch portfolio: ${portfolioRes.status} ${portfolioRes.statusText}`);
      }

      const portfolioData = await portfolioRes.json();

      // Courses endpoint might not exist yet, handle gracefully
      let coursesData: any[] = [];
      if (coursesRes.ok) {
        coursesData = await coursesRes.json();
      }

      setData({
        ...portfolioData,
        courses: coursesData
      });
      setError(null);
    } catch (err) {
      setError(err as Error);
      console.error('Error fetching portfolio:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPortfolio(language);
  }, [fetchPortfolio, language]);

  return { data, loading, error, refetch: () => fetchPortfolio(language) };
}

