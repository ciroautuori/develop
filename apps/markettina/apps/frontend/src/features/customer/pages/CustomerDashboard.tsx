/**
 * Customer Dashboard - MARKETTINA Customer Portal
 * Fetches REAL data from /api/v1/customer/* endpoints
 *
 * Features:
 * - Token balance with visual progress
 * - Usage breakdown by category
 * - Quick actions for content generation
 * - Recent content history
 * - Performance metrics
 */

import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import {
  Coins,
  Sparkles,
  FileText,
  Image,
  Video,
  Calendar,
  TrendingUp,
  Activity,
  Users,
  Zap,
  Clock,
  RefreshCw,
  ChevronRight,
  AlertTriangle,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '../../../shared/lib/utils';
import { useTheme } from '../../../shared/contexts/ThemeContext';

// API fetch helper
const fetchAPI = async (endpoint: string) => {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No access token');

  const res = await fetch(`/api/v1/customer${endpoint}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
};

export function CustomerDashboard() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Fetch dashboard data from real API
  const { data: dashboard, isLoading, error, refetch } = useQuery({
    queryKey: ['customer', 'dashboard'],
    queryFn: () => fetchAPI('/dashboard'),
    refetchInterval: 60000,
    refetchOnWindowFocus: false,
    retry: 2,
  });

  // Extract data with fallbacks
  const tokens = dashboard?.tokens || { balance: 0, used: 0, total: 0, plan_name: 'Free' };
  const usage = dashboard?.usage || { text_generation: 0, image_generation: 0, video_generation: 0, lead_search: 0, email_campaigns: 0 };

  const tokenPercentage = tokens.total > 0 ? Math.round((tokens.balance / tokens.total) * 100) : 0;
  const isLowBalance = tokenPercentage < 20;

  // Quick actions
  const quickActions = [
    { icon: FileText, label: 'Genera Post', href: '/customer/ai-marketing', color: 'from-blue-500 to-cyan-500', tokens: '5-15' },
    { icon: Image, label: 'Crea Immagine', href: '/customer/ai-marketing', color: 'from-purple-500 to-pink-500', tokens: '15-80' },
    { icon: Video, label: 'Genera Video', href: '/customer/ai-marketing', color: 'from-pink-500 to-rose-500', tokens: '80-400' },
    { icon: Calendar, label: 'Calendario', href: '/customer/ai-marketing', color: 'from-emerald-500 to-teal-500', tokens: '0' },
  ];

  // Stats cards
  const statsCards = [
    {
      title: 'Contenuti Totali',
      value: dashboard?.recent_content_count || 0,
      icon: FileText,
      color: 'text-blue-500',
      bg: 'bg-blue-500/10'
    },
    {
      title: 'Post Schedulati',
      value: dashboard?.scheduled_posts_count || 0,
      icon: Calendar,
      color: 'text-purple-500',
      bg: 'bg-purple-500/10'
    },
    {
      title: 'Immagini Generate',
      value: dashboard?.generated_images_count || 0,
      icon: Image,
      color: 'text-pink-500',
      bg: 'bg-pink-500/10'
    },
    {
      title: 'Video Generati',
      value: dashboard?.generated_videos_count || 0,
      icon: Video,
      color: 'text-amber-500',
      bg: 'bg-amber-500/10'
    },
  ];

  // Usage breakdown data for chart
  const usageBreakdown = [
    { name: 'Testo', value: usage.text_generation, color: 'bg-blue-500' },
    { name: 'Immagini', value: usage.image_generation, color: 'bg-purple-500' },
    { name: 'Video', value: usage.video_generation, color: 'bg-pink-500' },
    { name: 'Lead', value: usage.lead_search, color: 'bg-emerald-500' },
    { name: 'Email', value: usage.email_campaigns, color: 'bg-amber-500' },
  ];

  const totalUsage = usageBreakdown.reduce((sum, item) => sum + item.value, 0);

  // Dynamic styles
  const cardBg = isDark ? 'bg-card border border-border' : 'bg-white border border-gray-200 shadow-sm';
  const textPrimary = isDark ? 'text-foreground' : 'text-gray-900';
  const textSecondary = isDark ? 'text-muted-foreground' : 'text-gray-500';

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
            Dashboard
          </h1>
          <p className="text-muted-foreground mt-1">
            Benvenuto nel tuo centro di controllo MARKETTINA
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isLoading}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            'bg-muted hover:bg-muted/80 text-foreground',
            isLoading && 'opacity-50 cursor-not-allowed'
          )}
        >
          <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
          {isLoading ? 'Caricamento...' : 'Aggiorna'}
        </button>
      </motion.div>

      {/* Token Balance Card - Hero */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={cn(
          'relative overflow-hidden rounded-2xl p-6',
          'bg-gradient-to-br from-primary via-primary/90 to-primary/70',
          'text-primary-foreground'
        )}
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white/20 flex items-center justify-center">
              <Coins className="h-7 w-7" />
            </div>
            <div>
              <p className="text-sm opacity-80">Token Disponibili</p>
              <p className="text-4xl font-bold">{tokens.balance.toLocaleString('it-IT')}</p>
              <p className="text-sm opacity-80">
                Piano {tokens.plan_name} • {tokens.used.toLocaleString('it-IT')} usati questo mese
              </p>
            </div>
          </div>

          <div className="flex-1 max-w-md">
            <div className="flex justify-between text-sm mb-2">
              <span>Utilizzo {tokenPercentage}%</span>
              <span>{tokens.balance.toLocaleString('it-IT')} / {tokens.total.toLocaleString('it-IT')}</span>
            </div>
            <div className="h-3 bg-white/20 rounded-full overflow-hidden">
              <div
                className={cn(
                  'h-full rounded-full transition-all duration-500',
                  isLowBalance ? 'bg-red-400' : 'bg-white'
                )}
                style={{ width: `${tokenPercentage}%` }}
              />
            </div>
            {isLowBalance && (
              <div className="flex items-center gap-2 mt-2 text-sm">
                <AlertTriangle className="h-4 w-4" />
                Token in esaurimento! Ricarica per continuare a generare contenuti.
              </div>
            )}
          </div>

          <Link
            to="/customer/tokens"
            className="flex items-center gap-2 px-6 py-3 bg-white text-primary rounded-xl font-semibold hover:bg-white/90 transition-colors"
          >
            <Zap className="h-4 w-4" />
            Ricarica Token
          </Link>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h2 className={`text-lg font-semibold ${textPrimary} mb-4`}>Azioni Rapide</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <Link
                key={index}
                to={action.href}
                className={cn(
                  'group relative overflow-hidden rounded-xl p-5 transition-all hover:scale-[1.02]',
                  `bg-gradient-to-br ${action.color}`,
                  'text-white'
                )}
              >
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
                <Icon className="h-8 w-8 mb-3" />
                <p className="font-semibold">{action.label}</p>
                {action.tokens !== '0' && (
                  <p className="text-xs opacity-80 mt-1">~{action.tokens} token</p>
                )}
                <ChevronRight className="absolute bottom-4 right-4 h-5 w-5 opacity-50 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
              </Link>
            );
          })}
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className={`text-lg font-semibold ${textPrimary} mb-4`}>I Tuoi Contenuti</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {statsCards.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.05 }}
                className={cn(cardBg, 'rounded-xl p-5')}
              >
                <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center mb-3', stat.bg)}>
                  <Icon className={cn('h-5 w-5', stat.color)} />
                </div>
                <p className={cn('text-sm', textSecondary)}>{stat.title}</p>
                <p className={cn('text-2xl font-bold', textPrimary)}>{stat.value}</p>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Usage Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className={cn(cardBg, 'rounded-xl p-6')}
      >
        <h3 className={cn('text-lg font-semibold mb-4', textPrimary)}>
          Utilizzo Token (Questo Mese)
        </h3>

        {totalUsage > 0 ? (
          <>
            {/* Bar chart */}
            <div className="h-8 bg-muted rounded-lg overflow-hidden flex mb-4">
              {usageBreakdown.map((item, index) => {
                const width = totalUsage > 0 ? (item.value / totalUsage) * 100 : 0;
                if (width === 0) return null;
                return (
                  <div
                    key={index}
                    className={cn('h-full transition-all', item.color)}
                    style={{ width: `${width}%` }}
                    title={`${item.name}: ${item.value} token`}
                  />
                );
              })}
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-4">
              {usageBreakdown.map((item, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className={cn('w-3 h-3 rounded-full', item.color)} />
                  <span className={cn('text-sm', textSecondary)}>
                    {item.name}: <span className={textPrimary}>{item.value.toLocaleString('it-IT')}</span>
                  </span>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="text-center py-8">
            <Activity className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
            <p className={textSecondary}>Nessun utilizzo questo mese</p>
            <Link to="/customer/ai-marketing" className="text-primary hover:underline text-sm">
              Inizia a generare contenuti →
            </Link>
          </div>
        )}
      </motion.div>

      {/* CTA Section */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className={cn(
          'rounded-2xl p-6 text-center',
          'bg-gradient-to-r from-purple-500/10 to-pink-500/10',
          'border border-purple-500/20'
        )}
      >
        <Sparkles className="h-10 w-10 mx-auto text-purple-500 mb-3" />
        <h3 className={cn('text-xl font-bold mb-2', textPrimary)}>
          Genera Contenuti AI
        </h3>
        <p className={cn('text-sm mb-4', textSecondary)}>
          Crea post, immagini e video per i tuoi social in pochi secondi
        </p>
        <Link
          to="/customer/ai-marketing"
          className="inline-flex items-center gap-2 px-6 py-3 bg-purple-500 text-white rounded-xl font-semibold hover:bg-purple-600 transition-colors"
        >
          <Sparkles className="h-4 w-4" />
          Inizia a Creare
        </Link>
      </motion.div>
    </div>
  );
}
