/**
 * Admin Dashboard - USA SOLO DESIGN SYSTEM ESISTENTE
 * Componenti: Card, Button da /shared/components/ui
 * Stili: design-system.css (card-solid, glass-dark, etc)
 * LIGHT MODE SUPPORT
 */

import { motion } from 'framer-motion';
import { Briefcase, Users, Calendar, TrendingUp, Activity, Clock, LayoutDashboard } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { SPACING } from '../../../shared/config/constants';
import { cn } from '../../../shared/lib/utils';

export function AdminDashboard() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // API REALI - Dashboard Analytics con KPI aggregati
  const { data: analytics, isLoading, error, refetch } = useQuery({
    queryKey: ['admin', 'dashboard-analytics'],
    queryFn: async () => {
      try {
        const token = localStorage.getItem('admin_token');
        if (!token) return null; // No token, no data

        const res = await fetch('/api/v1/admin/analytics/dashboard', {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) {
          console.warn('Dashboard analytics fetch failed:', res.status);
          return null; // Return null on error to show empty state instead of breaking
        }

        return res.json();
      } catch (e) {
        console.error('Dashboard analytics error:', e);
        return null;
      }
    },
    refetchInterval: 60000,
    refetchOnWindowFocus: false,
    retry: 1,
  });

  // KPI Helpers with safety checks
  const getMetric = (obj: any, path: string, fallback: any = 0) => {
    return path.split('.').reduce((acc, part) => acc && acc[part], obj) || fallback;
  };

  const businessKPIs = [
    {
      title: 'Fatturato Totale',
      value: `€${(getMetric(analytics, 'business.total_revenue') || 0).toLocaleString('it-IT')}`,
      trend: getMetric(analytics, 'business.revenue_trend', '+0%'),
      icon: TrendingUp,
      color: 'text-gold',
    },
    {
      title: 'Conversione Preventivi',
      value: `${getMetric(analytics, 'business.quote_conversion_rate', 0)}%`,
      subtitle: `${getMetric(analytics, 'business.accepted_quotes', 0)}/${getMetric(analytics, 'business.total_quotes', 0)} accettati`,
      icon: Briefcase,
      color: 'text-gold',
    },
    {
      title: 'Deal Size Medio',
      value: `€${(getMetric(analytics, 'business.avg_deal_size') || 0).toLocaleString('it-IT')}`,
      subtitle: `Pipeline: €${(getMetric(analytics, 'business.pipeline_value') || 0).toLocaleString('it-IT')}`,
      icon: TrendingUp,
      color: 'text-gold',
    },
    {
      title: 'Appuntamenti',
      value: getMetric(analytics, 'business.total_bookings', 0),
      subtitle: `${getMetric(analytics, 'business.confirmed_bookings', 0)} confermati`,
      icon: Calendar,
      color: 'text-gold',
    },
  ];

  const marketingKPIs = [
    {
      title: 'Leads Generati',
      value: getMetric(analytics, 'marketing.total_leads', 0),
      trend: getMetric(analytics, 'marketing.lead_trend', '+0%'),
      icon: Users,
      color: 'text-gold',
    },
    {
      title: 'Conversione Leads',
      value: `${getMetric(analytics, 'marketing.lead_conversion_rate', 0)}%`,
      subtitle: `${getMetric(analytics, 'marketing.active_customers', 0)} clienti attivi`,
      icon: TrendingUp,
      color: 'text-gold',
    },
    {
      title: 'ROI Marketing',
      value: `${getMetric(analytics, 'marketing.marketing_roi', 0)}%`,
      subtitle: `Costo: €${(getMetric(analytics, 'marketing.estimated_marketing_cost') || 0).toLocaleString('it-IT')}`,
      icon: TrendingUp,
      color: 'text-gold',
    },
    {
      title: 'Contenuti Pubblicati',
      value: getMetric(analytics, 'marketing.published_content', 0),
      subtitle: `${getMetric(analytics, 'marketing.scheduled_content', 0)} in programma`,
      icon: Activity,
      color: 'text-gold',
    },
  ];

  const customerKPIs = [
    {
      title: 'Clienti Totali',
      value: getMetric(analytics, 'customers.total_customers', 0),
      subtitle: `${getMetric(analytics, 'customers.active_customers', 0)} attivi`,
      icon: Users,
      color: 'text-gold',
    },
    {
      title: 'Churn Rate',
      value: `${getMetric(analytics, 'customers.churn_rate', 0)}%`,
      subtitle: `${getMetric(analytics, 'customers.inactive_customers', 0)} inattivi`,
      icon: TrendingUp,
      color: 'text-gray-400',
    },
    {
      title: 'Customer LTV',
      value: `€${(getMetric(analytics, 'customers.customer_lifetime_value') || 0).toLocaleString('it-IT')}`,
      subtitle: `Media: €${(getMetric(analytics, 'customers.avg_revenue_per_customer') || 0).toLocaleString('it-IT')}`,
      icon: TrendingUp,
      color: 'text-gold',
    },
    {
      title: 'Satisfaction',
      value: `${getMetric(analytics, 'customers.customer_satisfaction', 0)}/5`,
      trend: getMetric(analytics, 'customers.satisfaction_trend', '+0'),
      icon: Users,
      color: 'text-gold',
    },
  ];

  // TOKEN ECONOMY KPIs - MARKETTINA Core
  const tokenKPIs = [
    {
      title: 'Token Venduti (Totale)',
      value: (getMetric(analytics, 'tokens.total_purchased', 0)).toLocaleString('it-IT'),
      subtitle: `€${(getMetric(analytics, 'tokens.token_revenue', 0)).toLocaleString('it-IT')} revenue`,
      icon: TrendingUp,
      color: 'text-gold',
    },
    {
      title: 'Token Consumati',
      value: (getMetric(analytics, 'tokens.total_used', 0)).toLocaleString('it-IT'),
      subtitle: `${(getMetric(analytics, 'tokens.monthly_usage', 0)).toLocaleString('it-IT')} questo mese`,
      icon: Activity,
      color: 'text-gold',
    },
    {
      title: 'Wallet Attivi',
      value: getMetric(analytics, 'tokens.active_wallets', 0),
      subtitle: `su ${getMetric(analytics, 'tokens.total_wallets', 0)} totali`,
      icon: Users,
      color: 'text-gold',
    },
    {
      title: 'Low Balance Alert',
      value: getMetric(analytics, 'tokens.low_balance_wallets', 0),
      subtitle: `clienti con < 50 token`,
      icon: Activity,
      color: getMetric(analytics, 'tokens.low_balance_wallets', 0) > 5 ? 'text-red-500' : 'text-gold',
    },
  ];

  // AI USAGE KPIs
  const aiKPIs = [
    {
      title: 'Richieste AI Mese',
      value: (getMetric(analytics, 'ai.total_ai_requests_month', 0)).toLocaleString('it-IT'),
      icon: Briefcase,
      color: 'text-gold',
    },
    {
      title: 'Testi Generati',
      value: (getMetric(analytics, 'ai.content_generated.text', 0)).toLocaleString('it-IT'),
      subtitle: 'token usati',
      icon: Activity,
      color: 'text-gold',
    },
    {
      title: 'Immagini Generate',
      value: (getMetric(analytics, 'ai.content_generated.images', 0)).toLocaleString('it-IT'),
      subtitle: 'token usati',
      icon: Activity,
      color: 'text-gold',
    },
    {
      title: 'Video Generati',
      value: (getMetric(analytics, 'ai.content_generated.videos', 0)).toLocaleString('it-IT'),
      subtitle: 'token usati',
      icon: Activity,
      color: 'text-gold',
    },
  ];

  const recentActivity = analytics?.recent_activity || [];

  const quickActions = [
    { label: 'Nuovo Progetto', icon: Briefcase, href: '/admin/portfolio/project/new' },
    { label: 'Gestisci Utenti', icon: Users, href: '/admin/utenti' },
    { label: 'Vedi Calendario', icon: Calendar, href: '/admin/calendario' },
    { label: 'Analytics', icon: TrendingUp, href: '/admin/analytics' },
  ];

  // Dynamic classes based on theme
  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const iconBg = isDark ? 'bg-gold/10' : 'bg-gold/10';
  const hoverBg = isDark ? 'hover:bg-white/10' : 'hover:bg-gray-50';
  const itemBg = isDark ? 'bg-white/5' : 'bg-gray-50';
  const borderColor = isDark ? 'border-white/10' : 'border-gray-200';

  return (
    <div className={cn(SPACING.padding.full, 'space-y-4 sm:space-y-6')}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4"
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          {/* Title Row */}
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center shadow-lg shadow-primary/20">
              <LayoutDashboard className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
                Dashboard Analytics
              </h1>
              <p className="text-sm text-muted-foreground">
                KPI aggregati Business, Marketing e Clienti {isLoading && '• Aggiornamento...'}
              </p>
            </div>
          </div>

          {/* Refresh Button */}
          <button
            onClick={() => refetch()}
            disabled={isLoading}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors self-start sm:self-center',
              isDark ? 'bg-white/10 hover:bg-white/20 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-900',
              isLoading && 'opacity-50 cursor-not-allowed'
            )}
          >
            <Activity className={cn('h-4 w-4', isLoading && 'animate-spin')} />
            {isLoading ? 'Caricamento...' : 'Aggiorna'}
          </button>
        </div>
      </motion.div>

      {/* BUSINESS METRICS */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-8">
        <h2 className={`text-xl font-bold ${textPrimary} mb-4 flex items-center gap-2`}>
          <Briefcase className="h-5 w-5 text-gold" />
          Business Performance
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {businessKPIs.map((kpi, index) => {
            const Icon = kpi.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`${cardBg} rounded-xl p-5`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className={`p-2 rounded-lg ${iconBg}`}>
                    <Icon className={`h-5 w-5 ${kpi.color}`} />
                  </div>
                  {kpi.trend && (
                    <span className={`text-xs font-semibold ${kpi.trend.startsWith('+') ? 'text-gold' : 'text-gray-400'}`}>
                      {kpi.trend}
                    </span>
                  )}
                </div>
                <p className={`text-sm ${textSecondary} mb-1`}>{kpi.title}</p>
                <p className={`text-2xl font-bold ${textPrimary}`}>{kpi.value}</p>
                {kpi.subtitle && (
                  <p className={`text-xs ${textSecondary} mt-1`}>{kpi.subtitle}</p>
                )}
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* MARKETING METRICS */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-8">
        <h2 className={`text-xl font-bold ${textPrimary} mb-4 flex items-center gap-2`}>
          <TrendingUp className="h-5 w-5 text-gold" />
          Marketing Performance
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {marketingKPIs.map((kpi, index) => {
            const Icon = kpi.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`${cardBg} rounded-xl p-5`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className={`p-2 rounded-lg ${iconBg}`}>
                    <Icon className={`h-5 w-5 ${kpi.color}`} />
                  </div>
                  {kpi.trend && (
                    <span className={`text-xs font-semibold ${kpi.trend.startsWith('+') ? 'text-gold' : 'text-gray-400'}`}>
                      {kpi.trend}
                    </span>
                  )}
                </div>
                <p className={`text-sm ${textSecondary} mb-1`}>{kpi.title}</p>
                <p className={`text-2xl font-bold ${textPrimary}`}>{kpi.value}</p>
                {kpi.subtitle && (
                  <p className={`text-xs ${textSecondary} mt-1`}>{kpi.subtitle}</p>
                )}
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* CUSTOMER METRICS */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-8">
        <h2 className={`text-xl font-bold ${textPrimary} mb-4 flex items-center gap-2`}>
          <Users className="h-5 w-5 text-gold" />
          Customer Metrics
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {customerKPIs.map((kpi, index) => {
            const Icon = kpi.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`${cardBg} rounded-xl p-5`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className={`p-2 rounded-lg ${iconBg}`}>
                    <Icon className={`h-5 w-5 ${kpi.color}`} />
                  </div>
                  {kpi.trend && (
                    <span className={`text-xs font-semibold ${kpi.trend.startsWith('+') ? 'text-gold' : 'text-gray-400'}`}>
                      {kpi.trend}
                    </span>
                  )}
                </div>
                <p className={`text-sm ${textSecondary} mb-1`}>{kpi.title}</p>
                <p className={`text-2xl font-bold ${textPrimary}`}>{kpi.value}</p>
                {kpi.subtitle && (
                  <p className={`text-xs ${textSecondary} mt-1`}>{kpi.subtitle}</p>
                )}
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* TOKEN ECONOMY METRICS */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-8">
        <h2 className={`text-xl font-bold ${textPrimary} mb-4 flex items-center gap-2`}>
          <TrendingUp className="h-5 w-5 text-gold" />
          Token Economy
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {tokenKPIs.map((kpi, index) => {
            const Icon = kpi.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`${cardBg} rounded-xl p-5`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className={`p-2 rounded-lg ${iconBg}`}>
                    <Icon className={`h-5 w-5 ${kpi.color}`} />
                  </div>
                </div>
                <p className={`text-sm ${textSecondary} mb-1`}>{kpi.title}</p>
                <p className={`text-2xl font-bold ${textPrimary}`}>{kpi.value}</p>
                {kpi.subtitle && (
                  <p className={`text-xs ${textSecondary} mt-1`}>{kpi.subtitle}</p>
                )}
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* AI USAGE METRICS */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-8">
        <h2 className={`text-xl font-bold ${textPrimary} mb-4 flex items-center gap-2`}>
          <Briefcase className="h-5 w-5 text-gold" />
          AI Usage
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {aiKPIs.map((kpi, index) => {
            const Icon = kpi.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`${cardBg} rounded-xl p-5`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className={`p-2 rounded-lg ${iconBg}`}>
                    <Icon className={`h-5 w-5 ${kpi.color}`} />
                  </div>
                </div>
                <p className={`text-sm ${textSecondary} mb-1`}>{kpi.title}</p>
                <p className={`text-2xl font-bold ${textPrimary}`}>{kpi.value}</p>
                {kpi.subtitle && (
                  <p className={`text-xs ${textSecondary} mt-1`}>{kpi.subtitle}</p>
                )}
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* RECENT ACTIVITY */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h2 className={`text-xl font-bold ${textPrimary} mb-4 flex items-center gap-2`}>
          <Activity className="h-5 w-5 text-gold" />
          Attività Recente
        </h2>
        <div className={`${cardBg} rounded-xl p-6`}>
          <div className="space-y-4">
            {isLoading ? (
              <p className={textSecondary}>Caricamento...</p>
            ) : recentActivity.length === 0 ? (
              <p className={textSecondary}>Nessuna attività recente</p>
            ) : (
              recentActivity.map((activity: any, index: number) => (
                <div
                  key={index}
                  className={`flex items-center gap-4 p-3 rounded-lg ${itemBg} border ${borderColor}`}
                >
                  <div className={`p-2 rounded-lg ${iconBg}`}>
                    <Activity className="h-4 w-4 text-gold" />
                  </div>
                  <div className="flex-1">
                    <p className={`text-sm font-medium ${textPrimary}`}>{activity.action}</p>
                    <p className={`text-xs ${textSecondary}`}>{activity.entity || activity.user}</p>
                  </div>
                  <div className={`text-xs ${textSecondary} flex items-center gap-1`}>
                    <Clock className="h-3 w-3" />
                    {new Date(activity.time).toLocaleDateString('it-IT')}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
