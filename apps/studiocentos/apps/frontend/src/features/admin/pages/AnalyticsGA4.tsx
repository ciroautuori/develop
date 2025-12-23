/**
 * Analytics Dashboard - Google Analytics GA4 Integration
 * Real data from GA4 Data API
 * LIGHT MODE SUPPORT
 */
import { useState } from 'react';
import {
  TrendingUp,
  Users,
  Eye,
  MousePointer,
  Clock,
  Globe,
  Smartphone,
  Monitor,
  Tablet,
  ExternalLink,
  RefreshCw,
  AlertCircle,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { SPACING } from '../../../shared/config/constants';
import { cn } from '../../../shared/lib/utils';
import { Button } from '../../../shared/components/ui/button';
import {
  GADashboardResponse,
  GoogleConnectionStatus
} from '../types/ga4-analytics.types';

const getDeviceIcon = (device: string) => {
  switch (device.toLowerCase()) {
    case 'desktop':
      return Monitor;
    case 'mobile':
      return Smartphone;
    case 'tablet':
      return Tablet;
    default:
      return Monitor;
  }
};

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}m ${secs}s`;
};

export function AnalyticsGA4() {
  const [period, setPeriod] = useState(30);
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Check connection status
  const { data: connectionStatus } = useQuery<GoogleConnectionStatus>({
    queryKey: ['google-status'],
    queryFn: async () => {
      const token = localStorage.getItem('admin_token');
      const res = await fetch('/api/v1/admin/google/status', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return { analytics_connected: false, business_profile_connected: false };
      return res.json();
    },
  });

  // Fetch GA4 dashboard data
  const {
    data: dashboard,
    isLoading,
    isError,
    refetch,
  } = useQuery<GADashboardResponse>({
    queryKey: ['ga4-dashboard', period],
    queryFn: async () => {
      const token = localStorage.getItem('admin_token');
      const res = await fetch(`/api/v1/admin/google/analytics/dashboard?days=${period}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to fetch analytics');
      return res.json();
    },
    enabled: connectionStatus?.analytics_connected === true,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Theme classes
  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const iconBg = isDark ? 'bg-gold/10' : 'bg-gold/10';
  const buttonInactive = isDark
    ? 'bg-white/5 text-white hover:bg-white/10'
    : 'bg-gray-100 text-gray-700 hover:bg-gray-200';

  // Not connected state
  if (!connectionStatus?.analytics_connected) {
    return (
      <div className={cn(SPACING.padding.full, SPACING.lg)}>
        <div className={`${cardBg} rounded-2xl p-8 text-center`}>
          <AlertCircle className={`h-16 w-16 mx-auto mb-4 ${textSecondary}`} />
          <h2 className={`text-xl font-semibold mb-2 ${textPrimary}`}>
            Google Analytics Non Connesso
          </h2>
          <p className={`${textSecondary} mb-6`}>
            Collega il tuo account Google per visualizzare i dati di Google Analytics 4.
          </p>
          <Button
            onClick={() => (window.location.href = '/admin/settings?tab=integrations')}
            className="bg-gold hover:bg-gold-dark text-black"
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            Vai alle Impostazioni
          </Button>
        </div>
      </div>
    );
  }

  const overview = dashboard?.overview;

  const kpiCards = [
    {
      title: 'Utenti Attivi',
      value: overview?.active_users || 0,
      icon: Users,
      color: 'text-gold',
    },
    {
      title: 'Visualizzazioni',
      value: overview?.page_views || 0,
      icon: Eye,
      color: 'text-gold',
    },
    {
      title: 'Sessioni',
      value: overview?.sessions || 0,
      icon: BarChart3,
      color: 'text-gold',
    },
    {
      title: 'Bounce Rate',
      value: `${overview?.bounce_rate || 0}%`,
      icon: TrendingUp,
      color: 'text-gold',
      isPercentage: true,
    },
  ];

  return (
    <div className={cn(SPACING.padding.full, SPACING.lg)}>
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className={`text-2xl sm:text-3xl lg:text-4xl font-bold ${textPrimary}`}>
            Google Analytics
          </h1>
          <p className={`text-sm sm:text-base mt-1 ${textSecondary}`}>
            Dati in tempo reale da GA4 • Property: {connectionStatus?.analytics_property_id || 'Default'}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isLoading}
            className={isDark ? 'border-white/20' : ''}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Aggiorna
          </Button>
          <div className="flex gap-1 overflow-x-auto">
            {[7, 30, 90].map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-3 py-2 rounded-lg transition text-sm whitespace-nowrap ${period === p ? 'bg-gold text-black' : buttonInactive
                  }`}
              >
                {p}g
              </button>
            ))}
          </div>
        </div>
      </div>

      {isError && (
        <div className={`${cardBg} rounded-xl p-4 mb-6 border-gray-500/50`}>
          <p className="text-gray-400 flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            Errore nel caricamento dei dati. Riprova.
          </p>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 md:gap-6 lg:grid-cols-4 mb-6">
        {kpiCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className={`${cardBg} rounded-2xl p-4 sm:p-6`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className={`text-xs sm:text-sm mb-2 ${textSecondary}`}>{card.title}</p>
                    {isLoading ? (
                      <div
                        className={`h-8 rounded w-3/4 animate-pulse ${isDark ? 'bg-white/10' : 'bg-gray-200'
                          }`}
                      />
                    ) : (
                      <p className={`text-2xl sm:text-3xl font-bold ${textPrimary}`}>
                        {typeof card.value === 'number'
                          ? card.value.toLocaleString('it-IT')
                          : card.value}
                      </p>
                    )}
                  </div>
                  <div className={`p-3 ${iconBg} rounded-xl`}>
                    <Icon className={`h-6 w-6 ${card.color}`} />
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Traffic Over Time */}
        <div className={`${cardBg} rounded-2xl p-6`}>
          <h3 className={`font-semibold mb-4 ${textPrimary}`}>Traffico Giornaliero</h3>
          {isLoading ? (
            <div className="h-48 flex items-center justify-center">
              <RefreshCw className={`h-8 w-8 animate-spin ${textSecondary}`} />
            </div>
          ) : (
            <div className="space-y-2 max-h-64 overflow-auto">
              {dashboard?.daily_traffic?.slice(-10).map((day, idx) => (
                <div
                  key={idx}
                  className={`flex items-center justify-between p-2 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'
                    }`}
                >
                  <span className={`text-sm ${textSecondary}`}>{day.date}</span>
                  <div className="flex gap-4 text-sm">
                    <span className={textPrimary}>
                      <Users className="h-3 w-3 inline mr-1" />
                      {day.users}
                    </span>
                    <span className={textPrimary}>
                      <Eye className="h-3 w-3 inline mr-1" />
                      {day.pageViews}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Traffic Sources */}
        <div className={`${cardBg} rounded-2xl p-6`}>
          <h3 className={`font-semibold mb-4 ${textPrimary}`}>Sorgenti di Traffico</h3>
          {isLoading ? (
            <div className="h-48 flex items-center justify-center">
              <RefreshCw className={`h-8 w-8 animate-spin ${textSecondary}`} />
            </div>
          ) : (
            <div className="space-y-3">
              {dashboard?.traffic_sources?.slice(0, 5).map((source, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Globe className={`h-4 w-4 ${textSecondary}`} />
                    <span className={`text-sm ${textPrimary}`}>
                      {source.source} / {source.medium}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div
                      className="h-2 bg-gold rounded-full"
                      style={{ width: `${Math.min(source.percentage, 100)}px` }}
                    />
                    <span className={`text-sm ${textSecondary}`}>{source.percentage}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Top Pages */}
        <div className={`${cardBg} rounded-2xl p-6`}>
          <h3 className={`font-semibold mb-4 ${textPrimary}`}>Pagine Più Viste</h3>
          {isLoading ? (
            <div className="h-48 flex items-center justify-center">
              <RefreshCw className={`h-8 w-8 animate-spin ${textSecondary}`} />
            </div>
          ) : (
            <div className="space-y-2">
              {dashboard?.top_pages?.slice(0, 5).map((page, idx) => (
                <div
                  key={idx}
                  className={`flex items-center justify-between p-2 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'
                    }`}
                >
                  <span className={`text-sm truncate max-w-[200px] ${textPrimary}`}>
                    {page.path}
                  </span>
                  <div className="flex gap-3 text-sm">
                    <span className={textSecondary}>{page.page_views.toLocaleString()}</span>
                    <span className={textSecondary}>{formatDuration(page.avg_time_on_page)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Device Breakdown */}
        <div className={`${cardBg} rounded-2xl p-6`}>
          <h3 className={`font-semibold mb-4 ${textPrimary}`}>Dispositivi</h3>
          {isLoading ? (
            <div className="h-48 flex items-center justify-center">
              <RefreshCw className={`h-8 w-8 animate-spin ${textSecondary}`} />
            </div>
          ) : (
            <div className="space-y-4">
              {dashboard?.device_breakdown?.map((device, idx) => {
                const DeviceIcon = getDeviceIcon(device.device);
                return (
                  <div key={idx} className="flex items-center gap-4">
                    <div className={`p-2 ${iconBg} rounded-lg`}>
                      <DeviceIcon className="h-5 w-5 text-gold" />
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between mb-1">
                        <span className={`text-sm capitalize ${textPrimary}`}>{device.device}</span>
                        <span className={`text-sm ${textSecondary}`}>{device.percentage}%</span>
                      </div>
                      <div
                        className={`h-2 rounded-full ${isDark ? 'bg-white/10' : 'bg-gray-200'}`}
                      >
                        <div
                          className="h-2 bg-gold rounded-full transition-all"
                          style={{ width: `${device.percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Additional Stats */}
      <div className={`${cardBg} rounded-2xl p-6 mt-6`}>
        <h3 className={`font-semibold mb-4 ${textPrimary}`}>Metriche Aggiuntive</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className={`text-2xl font-bold ${textPrimary}`}>{overview?.new_users || 0}</p>
            <p className={`text-sm ${textSecondary}`}>Nuovi Utenti</p>
          </div>
          <div className="text-center">
            <p className={`text-2xl font-bold ${textPrimary}`}>
              {formatDuration(overview?.avg_session_duration || 0)}
            </p>
            <p className={`text-sm ${textSecondary}`}>Durata Media</p>
          </div>
          <div className="text-center">
            <p className={`text-2xl font-bold ${textPrimary}`}>{overview?.conversions || 0}</p>
            <p className={`text-sm ${textSecondary}`}>Conversioni</p>
          </div>
          <div className="text-center">
            <p className={`text-sm ${textSecondary}`}>Ultimo aggiornamento</p>
            <p className={`text-sm ${textPrimary}`}>
              {dashboard?.last_updated
                ? new Date(dashboard.last_updated).toLocaleString('it-IT')
                : '-'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
