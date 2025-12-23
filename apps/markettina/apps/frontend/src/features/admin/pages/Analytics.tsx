/**
 * Analytics Hub - Internal + Google Analytics GA4
 * @deprecated Use AIMarketing Hub instead
 * Unified analytics dashboard with tabs
 * LIGHT MODE SUPPORT
 */
import { useState } from 'react';
import { TrendingUp, Users, Eye, MousePointer, BarChart3, ExternalLink } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { SPACING } from '../../../shared/config/constants';
import { cn } from '../../../shared/lib/utils';
import { Button } from '../../../shared/components/ui/button';
import { AnalyticsGA4 } from './AnalyticsGA4';
import AnalyticsSEO from './AnalyticsSEO';

export function Analytics() {
  const [activeTab, setActiveTab] = useState<'internal' | 'ga4' | 'seo'>('ga4');
  const [period, setPeriod] = useState(30);
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Check if GA4 is connected
  const { data: connectionStatus } = useQuery({
    queryKey: ['google-status'],
    queryFn: async () => {
      const token = localStorage.getItem('admin_token');
      const res = await fetch('/api/v1/admin/google/status', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return { analytics_connected: false };
      return res.json();
    },
  });

  // Internal stats API
  const { data: stats, isLoading } = useQuery({
    queryKey: ['internal-analytics', period],
    queryFn: async () => {
      const token = localStorage.getItem('admin_token');
      const res = await fetch(`/api/v1/admin/bookings/stats`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return res.json();
    },
    enabled: activeTab === 'internal',
  });

  const kpiCards = [
    { title: 'Prenotazioni', value: stats?.total_bookings || 0, icon: Eye },
    { title: 'Utenti Unici', value: stats?.unique_users || 0, icon: Users },
    { title: 'Confermate', value: stats?.confirmed_count || 0, icon: TrendingUp },
    { title: 'In Attesa', value: stats?.pending_count || 0, icon: MousePointer },
  ];

  // Dynamic classes based on theme
  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const iconBg = isDark ? 'bg-gold/10' : 'bg-gold/10';
  const buttonInactive = isDark
    ? 'bg-white/5 text-white hover:bg-white/10'
    : 'bg-gray-100 text-gray-700 hover:bg-gray-200';
  const tabBg = isDark ? 'bg-white/5 border-white/10' : 'bg-gray-100 border-gray-200';

  // Header Unificato
  const renderHeader = () => (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4 mb-6"
    >
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center shadow-lg shadow-primary/20">
          <BarChart3 className="w-6 h-6 text-primary-foreground" />
        </div>
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
            Analytics Hub
          </h1>
          <p className="text-sm text-muted-foreground">
            Statistiche integrate: GA4, SEO e dati interni
          </p>
        </div>
      </div>

      {/* Tab Navigation - Pattern AIMarketing */}
      <div className="bg-card border border-border rounded-xl p-2 shadow-sm">
        <div className="flex gap-1 overflow-x-auto">
          <button
            onClick={() => setActiveTab('ga4')}
            className={cn(
              'flex-1 min-w-[120px] flex flex-col items-center gap-1 py-3 px-4 rounded-xl transition-all',
              activeTab === 'ga4'
                ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-white shadow-lg'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
            )}
          >
            <BarChart3 className="w-5 h-5" />
            <span className="text-xs font-medium whitespace-nowrap">Google Analytics</span>
          </button>
          <button
            onClick={() => setActiveTab('seo')}
            className={cn(
              'flex-1 min-w-[120px] flex flex-col items-center gap-1 py-3 px-4 rounded-xl transition-all',
              activeTab === 'seo'
                ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-white shadow-lg'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
            )}
          >
            <Eye className="w-5 h-5" />
            <span className="text-xs font-medium whitespace-nowrap">SEO</span>
          </button>
          <button
            onClick={() => setActiveTab('internal')}
            className={cn(
              'flex-1 min-w-[120px] flex flex-col items-center gap-1 py-3 px-4 rounded-xl transition-all',
              activeTab === 'internal'
                ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-white shadow-lg'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
            )}
          >
            <TrendingUp className="w-5 h-5" />
            <span className="text-xs font-medium whitespace-nowrap">Interno</span>
          </button>
        </div>
      </div>
    </motion.div>
  );

  // Show SEO tab
  if (activeTab === 'seo') {
    return (
      <div className={cn(SPACING.padding.full, 'space-y-4 sm:space-y-6')}>
        {renderHeader()}
        <AnalyticsSEO />
      </div>
    );
  }

  // Show GA4 tab
  if (activeTab === 'ga4') {
    return (
      <div className={cn(SPACING.padding.full, 'space-y-4 sm:space-y-6')}>
        {renderHeader()}
        {connectionStatus?.analytics_connected && (
          <div className="flex justify-end mb-4">
            <span className="px-3 py-1 rounded-full bg-green-500/10 text-green-500 text-sm flex items-center gap-2 border border-green-500/20">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              GA4 Connesso
            </span>
          </div>
        )}
        <AnalyticsGA4 />
      </div>
    );
  }

  // Internal Analytics Tab
  return (
    <div className={cn(SPACING.padding.full, 'space-y-4 sm:space-y-6')}>
      {renderHeader()}

      {/* Period Selector */}
      <div className="flex justify-end mb-4">
        <div className="bg-card border border-border rounded-lg p-1 inline-flex">
          {[7, 30, 90].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={cn(
                'px-3 py-1.5 rounded-md text-sm font-medium transition-all',
                period === p
                  ? 'bg-gold text-white shadow-sm'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted'
              )}
            >
              {p} giorni
            </button>
          ))}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 md:gap-6 lg:grid-cols-4 mt-6">
        {kpiCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className={`${cardBg} rounded-2xl sm:rounded-3xl p-4 sm:p-6`}>
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                  <div className="flex-1">
                    <p className={`text-xs sm:text-sm mb-1 sm:mb-2 ${textSecondary}`}>
                      {card.title}
                    </p>
                    {isLoading ? (
                      <div
                        className={`h-6 sm:h-8 rounded w-3/4 animate-pulse ${isDark ? 'bg-white/10' : 'bg-gray-200'
                          }`}
                      />
                    ) : (
                      <p className={`text-xl sm:text-2xl lg:text-3xl font-bold ${textPrimary}`}>
                        {card.value}
                      </p>
                    )}
                  </div>
                  <div
                    className={`p-2 sm:p-4 ${iconBg} rounded-lg sm:rounded-xl self-start sm:self-auto`}
                  >
                    <Icon className="h-5 w-5 sm:h-6 sm:w-6 lg:h-8 lg:w-8 text-gold" />
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Upgrade Banner */}
      {!connectionStatus?.analytics_connected && (
        <div className={`${cardBg} rounded-2xl p-6 mt-6 border-gold/30`}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className={`font-semibold ${textPrimary}`}>
                🚀 Potenzia le tue Analytics con Google Analytics 4
              </h3>
              <p className={`text-sm ${textSecondary} mt-1`}>
                Collega GA4 per ottenere dati dettagliati su traffico, sorgenti e comportamento
                utenti.
              </p>
            </div>
            <Button
              onClick={() => (window.location.href = '/admin/settings?tab=integrations')}
              className="bg-gold hover:bg-gold-dark text-black"
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Connetti GA4
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
