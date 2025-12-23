/**
 * ConversionDashboard - Real-time Acquisition Funnel
 *
 * Displays:
 * - Pipeline stages with lead counts
 * - Conversion rates at each stage
 * - Today/Week/Month metrics
 * - Grade distribution (A/B/C/D)
 */

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp, Users, Mail, Target, CheckCircle2,
  ArrowRight, Loader2, RefreshCw, Calendar, Zap,
  BarChart3, PieChart
} from 'lucide-react';
import { Button } from '../../../../../shared/components/ui/button';
import { toast } from 'sonner';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { cn } from '../../../../../shared/lib/utils';

// ============================================================================
// TYPES
// ============================================================================

interface AcquisitionStats {
  total_leads_found: number;
  leads_enriched: number;
  emails_sent: number;
  emails_opened: number;
  emails_clicked: number;
  meetings_scheduled: number;
  customers_converted: number;
  enrichment_rate: number;
  open_rate: number;
  click_rate: number;
  conversion_rate: number;
  today_leads: number;
  week_leads: number;
  month_leads: number;
  grade_a_count: number;
  grade_b_count: number;
  grade_c_count: number;
  last_campaign: string | null;
}

interface PipelineStage {
  name: string;
  count: number;
  percentage: number;
  leads: Array<{
    id: number;
    company: string;
    score: number;
    created_at: string;
  }>;
}

interface PipelineData {
  stages: PipelineStage[];
  total_value: number;
  avg_conversion_time_days: number;
}

// ============================================================================
// API
// ============================================================================

const AcquisitionStatsAPI = {
  async getStats(): Promise<AcquisitionStats> {
    const token = localStorage.getItem('admin_token');
    if (!token) throw new Error('Non autenticato');

    const res = await fetch('/api/v1/marketing/acquisition/stats', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!res.ok) {
      throw new Error('Failed to fetch acquisition stats');
    }

    return res.json();
  },

  async getPipeline(): Promise<PipelineData> {
    const token = localStorage.getItem('admin_token');
    if (!token) throw new Error('Non autenticato');

    const res = await fetch('/api/v1/marketing/acquisition/pipeline', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!res.ok) {
      throw new Error('Failed to fetch pipeline data');
    }

    return res.json();
  }
};

// ============================================================================
// COMPONENT
// ============================================================================

export function ConversionDashboard() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [stats, setStats] = useState<AcquisitionStats | null>(null);
  const [pipeline, setPipeline] = useState<PipelineData | null>(null);
  const [loading, setLoading] = useState(true);

  // Design classes - OFFICIAL DESIGN SYSTEM
  const cardBg = isDark ? 'bg-white/5 border-white/10' : 'bg-gray-50 border-gray-200';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [statsData, pipelineData] = await Promise.all([
        AcquisitionStatsAPI.getStats(),
        AcquisitionStatsAPI.getPipeline()
      ]);
      setStats(statsData);
      setPipeline(pipelineData);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      toast.error('Errore caricamento statistiche');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();

    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  if (loading || !stats || !pipeline) {
    return (
      <div className={cn(cardBg, 'rounded-2xl p-8 text-center')}>
        <Loader2 className="w-8 h-8 mx-auto animate-spin text-gold" />
        <p className={cn('mt-2', textSecondary)}>Caricamento statistiche...</p>
      </div>
    );
  }

  // Calculate funnel widths for visualization
  const maxCount = Math.max(...pipeline.stages.map(s => s.count), 1);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className={cn('text-xl font-bold', textPrimary)}>📊 Conversioni</h2>
            <p className={textSecondary}>Pipeline acquisizione clienti</p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={fetchData}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Aggiorna
        </Button>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(cardBg, 'rounded-xl p-4')}
        >
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-4 h-4 text-gold" />
            <span className={cn('text-sm', textSecondary)}>Lead Totali</span>
          </div>
          <div className={cn('text-2xl font-bold', textPrimary)}>{stats.total_leads_found}</div>
          <div className="text-xs text-emerald-500">+{stats.today_leads} oggi</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className={cn(cardBg, 'rounded-xl p-4')}
        >
          <div className="flex items-center gap-2 mb-2">
            <Mail className="w-4 h-4 text-blue-500" />
            <span className={cn('text-sm', textSecondary)}>Email Inviate</span>
          </div>
          <div className={cn('text-2xl font-bold', textPrimary)}>{stats.emails_sent}</div>
          <div className="text-xs text-blue-500">{stats.open_rate}% aperte</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className={cn(cardBg, 'rounded-xl p-4')}
        >
          <div className="flex items-center gap-2 mb-2">
            <Users className="w-4 h-4 text-amber-500" />
            <span className={cn('text-sm', textSecondary)}>Qualificati</span>
          </div>
          <div className={cn('text-2xl font-bold', textPrimary)}>{stats.leads_enriched}</div>
          <div className="text-xs text-amber-500">{stats.enrichment_rate}% del totale</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className={cn(cardBg, 'rounded-xl p-4')}
        >
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <span className={cn('text-sm', textSecondary)}>Convertiti</span>
          </div>
          <div className={cn('text-2xl font-bold', textPrimary)}>{stats.customers_converted}</div>
          <div className="text-xs text-emerald-500">{stats.conversion_rate}% conversion</div>
        </motion.div>
      </div>

      {/* Pipeline Funnel */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className={cn(cardBg, 'rounded-xl p-6')}
      >
        <h3 className={cn('text-lg font-bold mb-4 flex items-center gap-2', textPrimary)}>
          <BarChart3 className="w-5 h-5 text-gold" />
          Pipeline Acquisizione
        </h3>

        <div className="space-y-3">
          {pipeline.stages.map((stage, idx) => (
            <div key={stage.name} className="flex items-center gap-4">
              <div className={cn('w-24 text-sm text-right', textSecondary)}>
                {stage.name}
              </div>
              <div className="flex-1 relative">
                <div className={cn('h-8 rounded-lg', isDark ? 'bg-white/5' : 'bg-gray-100')}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(stage.count / maxCount) * 100}%` }}
                    transition={{ duration: 0.5, delay: idx * 0.1 }}
                    className={cn(
                      'h-full rounded-lg flex items-center justify-end px-3',
                      idx === 0 ? 'bg-gold' :
                      idx === pipeline.stages.length - 1 ? 'bg-emerald-500' :
                      'bg-gold/70'
                    )}
                  >
                    <span className="text-sm font-bold text-white">{stage.count}</span>
                  </motion.div>
                </div>
              </div>
              <div className={cn('w-16 text-sm text-right', textSecondary)}>
                {stage.percentage}%
              </div>
              {idx < pipeline.stages.length - 1 && (
                <ArrowRight className={cn('w-4 h-4', textSecondary, 'opacity-30')} />
              )}
            </div>
          ))}
        </div>

        {/* Conversion Summary */}
        <div className={cn(
          'mt-6 pt-4 border-t flex items-center justify-between',
          isDark ? 'border-white/10' : 'border-gray-200'
        )}>
          <div>
            <span className={textSecondary}>Tempo medio conversione:</span>
            <span className={cn('ml-2 font-bold', textPrimary)}>
              {pipeline.avg_conversion_time_days} giorni
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-gold" />
            <span className={textSecondary}>Ultimo aggiornamento: ora</span>
          </div>
        </div>
      </motion.div>

      {/* Grade Distribution */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className={cn(cardBg, 'rounded-xl p-6')}
      >
        <h3 className={cn('text-lg font-bold mb-4 flex items-center gap-2', textPrimary)}>
          <PieChart className="w-5 h-5 text-gold" />
          Distribuzione Lead per Qualità
        </h3>

        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-4 rounded-xl bg-emerald-500/10">
            <div className="text-3xl font-bold text-emerald-500">{stats.grade_a_count}</div>
            <div className={textSecondary}>Grade A</div>
            <div className="text-xs text-emerald-500">Priorità alta</div>
          </div>
          <div className="text-center p-4 rounded-xl bg-gold/10">
            <div className="text-3xl font-bold text-gold">{stats.grade_b_count}</div>
            <div className={textSecondary}>Grade B</div>
            <div className="text-xs text-gold">Buon potenziale</div>
          </div>
          <div className="text-center p-4 rounded-xl bg-gray-500/10">
            <div className={cn('text-3xl font-bold', textSecondary)}>{stats.grade_c_count}</div>
            <div className={textSecondary}>Grade C/D</div>
            <div className={cn('text-xs', textSecondary)}>Da valutare</div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
