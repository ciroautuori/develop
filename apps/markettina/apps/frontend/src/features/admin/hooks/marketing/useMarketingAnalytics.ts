/**
 * Custom Hook: useMarketingAnalytics
 * Manages marketing statistics and analytics data
 */

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { MarketingApiService } from '../../services/marketing-api.service';

interface MarketingStats {
  status_counts: Record<string, number>;
  upcoming_week: number;
  platform_stats_last_30_days: Record<string, number>;
  total_posts: number;
}

export function useMarketingAnalytics(autoFetch = false) {
  const [stats, setStats] = useState<MarketingStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await MarketingApiService.getStats();
      setStats(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Errore nel caricamento statistiche';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (autoFetch) {
      fetchStats();
    }
  }, [autoFetch]);

  return {
    stats,
    loading,
    error,
    fetchStats,
    refresh: fetchStats
  };
}
