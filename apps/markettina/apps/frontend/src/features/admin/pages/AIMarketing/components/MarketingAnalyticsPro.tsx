/**
 * MarketingAnalyticsPro Component
 * Advanced analytics dashboard with GA4, social metrics, and ROI tracking
 *
 * @uses types/analytics.types - Types centralizzati
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Users,
  Eye,
  MousePointer,
  DollarSign,
  Calendar,
  RefreshCw,
  Loader2,
  Globe,
  Instagram,
  Facebook,
  Linkedin,
  Twitter,
  Mail,
  Share2,
  Target,
  Zap,
  ArrowUpRight,
  ArrowDownRight,
  PieChart,
  Activity,
} from 'lucide-react';
import { Button } from '../../../../../shared/components/ui/button';

// Types centralizzati
import {
  DATE_RANGES,
  PLATFORM_LABELS,
  STATUS_LABELS,
  type DateRange,
  type PlatformMetrics,
  type GA4Metrics,
} from '../types/analytics.types';

// Hook centralizzato per analytics
import { useMarketingAnalytics } from '../../../hooks/marketing/useMarketingAnalytics';

// Types locali (non esportati)
interface MetricCard {
  label: string;
  value: string | number;
  change: number;
  icon: React.ElementType;
  color: string;
}

interface CampaignPerformance {
  name: string;
  type: 'email' | 'social' | 'ads';
  sent: number;
  opened: number;
  clicked: number;
  converted: number;
  roi: number;
}

// API Service
const AnalyticsApiService = {
  baseUrl: '/api/v1',

  async getMarketingStats(): Promise<any> {
    const res = await fetch(`${this.baseUrl}/marketing/scheduler/status`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) return null;
    return res.json();
  },

  async getGA4Metrics(dateRange: DateRange): Promise<any> {
    // Calculate days from dateRange
    let days = 30;
    if (dateRange.start === 'today') days = 1;
    else if (dateRange.start === '7daysAgo') days = 7;
    else if (dateRange.start === '30daysAgo') days = 30;
    else if (dateRange.start === '90daysAgo') days = 90;

    const res = await fetch(
      `${this.baseUrl}/admin/google/analytics/dashboard?days=${days}`,
      {
        headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
      }
    );
    if (!res.ok) return null;
    return res.json();
  },

  async getEmailStats(): Promise<any> {
    const res = await fetch(`${this.baseUrl}/marketing/email/campaigns?limit=10`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) return [];
    return res.json();
  },

  async getSocialStats(dateRange: DateRange): Promise<any> {
    let days = 30;
    if (dateRange.start === 'today') days = 1;
    else if (dateRange.start === '7daysAgo') days = 7;
    else if (dateRange.start === '30daysAgo') days = 30;
    else if (dateRange.start === '90daysAgo') days = 90;

    const res = await fetch(`${this.baseUrl}/marketing/analytics/platforms?date_range=last_30_days`, { // TODO: pass dynamic range
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) return null;
    return res.json();
  },

  async getLeadStats(): Promise<any> {
    const res = await fetch(`${this.baseUrl}/marketing/leads/search/places`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
      },
      body: JSON.stringify({ query: 'aziende', location: 'Salerno', radius: 50000 }),
    });
    if (!res.ok) return null;
    return res.json();
  },
};

// DATE_RANGES importato da types/analytics.types

export function MarketingAnalyticsPro() {

  // Hook centralizzato per statistiche marketing
  const { stats: hookStats, loading: hookLoading, refresh: refreshStats } = useMarketingAnalytics(true);

  // State
  const [isLoading, setIsLoading] = useState(true);
  const [dateRange, setDateRange] = useState<DateRange>(DATE_RANGES[2]);
  const [marketingStats, setMarketingStats] = useState<any>(null);
  const [ga4Metrics, setGa4Metrics] = useState<any>(null);
  const [emailCampaigns, setEmailCampaigns] = useState<any[]>([]);
  const [socialMetrics, setSocialMetrics] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'social' | 'email' | 'website'>('overview');

  // Styles - Design System tokens
  const cardBg = 'bg-card border border-border shadow-sm';
  const textPrimary = 'text-foreground';
  const textSecondary = 'text-muted-foreground';

  // Sincronizza stats dall'hook
  useEffect(() => {
    if (hookStats) {
      setMarketingStats(hookStats);
    }
  }, [hookStats]);

  // Load additional data (GA4, Email, Social)
  useEffect(() => {
    loadAdditionalData();
  }, [dateRange]);

  const loadAdditionalData = async () => {
    setIsLoading(true);
    try {
      const [ga4, emails, social] = await Promise.all([
        AnalyticsApiService.getGA4Metrics(dateRange),
        AnalyticsApiService.getEmailStats(),
        AnalyticsApiService.getSocialStats(dateRange),
      ]);

      setGa4Metrics(ga4);
      setEmailCampaigns(Array.isArray(emails) ? emails : []);
      if (social && social.platforms) {
        setSocialMetrics(social.platforms);
      }
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Combinazione loading state
  const isDataLoading = isLoading || hookLoading;

  // Calculate metrics
  const getOverviewMetrics = (): MetricCard[] => {
    const totalPosts = marketingStats?.total_scheduled || 0;
    const totalImpressions = ga4Metrics?.totals?.screenPageViews || 0;
    const totalUsers = ga4Metrics?.totals?.activeUsers || 0;
    const emailsSent = emailCampaigns.reduce((sum, c) => sum + (c.total_sent || 0), 0);

    return [
      {
        label: 'Contenuti Pubblicati',
        value: totalPosts,
        change: 12,
        icon: Share2,
        color: 'from-purple-500 to-indigo-500',
      },
      {
        label: 'Impressioni Totali',
        value: totalImpressions.toLocaleString('it-IT'),
        change: 8,
        icon: Eye,
        color: 'from-blue-500 to-cyan-500',
      },
      {
        label: 'Utenti Attivi',
        value: totalUsers.toLocaleString('it-IT'),
        change: -3,
        icon: Users,
        color: 'from-green-500 to-emerald-500',
      },
      {
        label: 'Email Inviate',
        value: emailsSent.toLocaleString('it-IT'),
        change: 25,
        icon: Mail,
        color: 'from-orange-500 to-amber-500',
      },
    ];
  };

  const getPlatformMetrics = (): PlatformMetrics[] => {
    // Se abbiamo dati reali dal backend, usiamoli
    if (socialMetrics && socialMetrics.length > 0) {
      return socialMetrics.map(p => ({
        platform: p.platform.charAt(0).toUpperCase() + p.platform.slice(1), // Capitalize
        followers: p.followers || 0,
        posts_count: p.posts_count || 0,
        impressions: p.impressions || 0,
        engagement: p.engagement_rate || 0,
        engagement_rate: p.engagement_rate || 0,
        clicks: p.clicks || 0,
        reach: p.reach || 0,
      }));
    }

    // Fallback: nessun dato disponibile
    return [];
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'instagram':
        return Instagram;
      case 'facebook':
        return Facebook;
      case 'linkedin':
        return Linkedin;
      case 'twitter/x':
        return Twitter;
      default:
        return Globe;
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'instagram':
        return '#E4405F';
      case 'facebook':
        return '#1877F2';
      case 'linkedin':
        return '#0A66C2';
      case 'twitter/x':
        return '#1DA1F2';
      default:
        return '#6B7280';
    }
  };

  const overviewMetrics = getOverviewMetrics();
  const platformMetrics = getPlatformMetrics();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className={`text-2xl font-bold ${textPrimary}`}>Analytics Pro</h2>
          <p className={`${textSecondary} mt-1`}>
            Performance marketing cross-platform in tempo reale
          </p>
        </div>
        <div className="flex items-center gap-3 w-full md:w-auto overflow-hidden">
          {/* Date Range Selector */}
          <div className="flex gap-1 p-1 rounded-lg bg-muted/50 overflow-x-auto scrollbar-hide flex-1 md:flex-none">
            {DATE_RANGES.map((range) => (
              <button
                key={range.label}
                onClick={() => setDateRange(range)}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors whitespace-nowrap flex-shrink-0 ${dateRange.label === range.label
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground'
                  }`}
              >
                {range.label}
              </button>
            ))}
          </div>
          <Button variant="outline" onClick={() => { refreshStats(); loadAdditionalData(); }} disabled={isDataLoading} className="flex-shrink-0">
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Aggiorna</span>
          </Button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 p-1 rounded-xl bg-muted/30 overflow-x-auto scrollbar-hide">
        {[
          { id: 'overview', label: 'Overview', icon: PieChart },
          { id: 'social', label: 'Social', icon: Share2 },
          { id: 'email', label: 'Email', icon: Mail },
          { id: 'website', label: 'Website', icon: Globe },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex-shrink-0 min-w-[100px] flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${activeTab === tab.id
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-gold" />
          <span className={`ml-3 ${textPrimary}`}>Caricamento analytics...</span>
        </div>
      ) : (
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Key Metrics */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {overviewMetrics.map((metric, idx) => {
                  const Icon = metric.icon;
                  const isPositive = metric.change >= 0;

                  return (
                    <motion.div
                      key={metric.label}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className={`${cardBg} rounded-2xl p-5`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div
                          className={`w-10 h-10 rounded-xl bg-gradient-to-r ${metric.color} flex items-center justify-center`}
                        >
                          <Icon className="w-5 h-5 text-white" />
                        </div>
                        <div
                          className={`flex items-center gap-1 text-sm ${isPositive ? 'text-gold' : 'text-gray-400'
                            }`}
                        >
                          {isPositive ? (
                            <ArrowUpRight className="w-4 h-4" />
                          ) : (
                            <ArrowDownRight className="w-4 h-4" />
                          )}
                          {Math.abs(metric.change)}%
                        </div>
                      </div>
                      <div className={`text-2xl font-bold ${textPrimary}`}>{metric.value}</div>
                      <div className={`text-sm ${textSecondary}`}>{metric.label}</div>
                    </motion.div>
                  );
                })}
              </div>

              {/* Platform Performance */}
              <div className={`${cardBg} rounded-2xl p-6`}>
                <h3 className={`text-lg font-bold mb-4 ${textPrimary}`}>
                  Performance per Piattaforma
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className={`text-sm ${textSecondary}`}>
                        <th className="text-left pb-3">Piattaforma</th>
                        <th className="text-right pb-3">Impressioni</th>
                        <th className="text-right pb-3">Followers</th>
                        <th className="text-right pb-3">Post</th>
                        <th className="text-right pb-3">Click</th>
                        <th className="text-right pb-3">Engagement %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {platformMetrics.map((platform) => {
                        const Icon = getPlatformIcon(platform.platform);
                        const color = getPlatformColor(platform.platform);

                        return (
                          <tr
                            key={platform.platform}
                            className="border-t border-border"
                          >
                            <td className="py-3">
                              <div className="flex items-center gap-2">
                                <Icon className="w-5 h-5" style={{ color }} />
                                <span className={textPrimary}>{platform.platform}</span>
                              </div>
                            </td>
                            <td className={`text-right ${textPrimary}`}>
                              {platform.impressions.toLocaleString('it-IT')}
                            </td>
                            <td className={`text-right font-bold text-gold`}>
                              {platform.followers.toLocaleString('it-IT')}
                            </td>
                            <td className={`text-right ${textPrimary}`}>
                              {platform.posts_count.toLocaleString('it-IT')}
                            </td>
                            <td className={`text-right ${textPrimary}`}>
                              {platform.clicks.toLocaleString('it-IT')}
                            </td>
                            <td className={`text-right ${textPrimary}`}>
                              {platform.engagement_rate.toFixed(1)}%
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Email Campaigns Performance */}
              {emailCampaigns.length > 0 && (
                <div className={`${cardBg} rounded-2xl p-6`}>
                  <h3 className={`text-lg font-bold mb-4 ${textPrimary}`}>
                    Campagne Email Recenti
                  </h3>
                  <div className="space-y-3">
                    {emailCampaigns.slice(0, 5).map((campaign) => (
                      <div
                        key={campaign.id}
                        className="p-4 rounded-xl bg-muted/50"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className={`font-medium ${textPrimary}`}>{campaign.name}</span>
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full ${campaign.is_sent
                              ? 'bg-gold/20 text-gold'
                              : 'bg-gold/20 text-gold'
                              }`}
                          >
                            {campaign.is_sent ? 'Inviata' : 'Bozza'}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm">
                          <span className={textSecondary}>
                            <Mail className="w-4 h-4 inline mr-1" />
                            {campaign.total_sent || 0} inviate
                          </span>
                          <span className="text-gold">
                            <Eye className="w-4 h-4 inline mr-1" />
                            {campaign.open_rate || 0}% aperture
                          </span>
                          <span className="text-gold">
                            <MousePointer className="w-4 h-4 inline mr-1" />
                            {campaign.click_rate || 0}% click
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'social' && (
            <motion.div
              key="social"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              <div className={`${cardBg} rounded-2xl p-6`}>
                <h3 className={`text-lg font-bold mb-4 ${textPrimary}`}>
                  Dettaglio Social Media
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {platformMetrics.map((platform) => {
                    const Icon = getPlatformIcon(platform.platform);
                    const color = getPlatformColor(platform.platform);

                    return (
                      <div
                        key={platform.platform}
                        className="p-5 rounded-xl bg-muted/50"
                      >
                        <div className="flex items-center gap-3 mb-4">
                          <div
                            className="w-12 h-12 rounded-xl flex items-center justify-center"
                            style={{ backgroundColor: `${color}20` }}
                          >
                            <Icon className="w-6 h-6" style={{ color }} />
                          </div>
                          <div>
                            <h4 className={`font-semibold ${textPrimary}`}>{platform.platform}</h4>
                            <p className={`text-sm ${textSecondary}`}>Ultimi 30 giorni</p>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <div className="text-xl font-bold text-gold">
                              {platform.followers.toLocaleString('it-IT')}
                            </div>
                            <div className={`text-xs ${textSecondary}`}>Followers</div>
                          </div>
                          <div>
                            <div className={`text-xl font-bold ${textPrimary}`}>
                              {platform.posts_count.toLocaleString('it-IT')}
                            </div>
                            <div className={`text-xs ${textSecondary}`}>Post</div>
                          </div>
                          <div>
                            <div className={`text-xl font-bold ${textPrimary}`}>
                              {platform.impressions.toLocaleString('it-IT')}
                            </div>
                            <div className={`text-xs ${textSecondary}`}>Impressioni</div>
                          </div>
                          <div>
                            <div className={`text-xl font-bold ${textPrimary}`}>
                              {platform.engagement_rate.toFixed(1)}%
                            </div>
                            <div className={`text-xs ${textSecondary}`}>Engagement</div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'email' && (
            <motion.div
              key="email"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              <div className={`${cardBg} rounded-2xl p-6`}>
                <h3 className={`text-lg font-bold mb-4 ${textPrimary}`}>
                  Email Marketing Analytics
                </h3>
                {emailCampaigns.length === 0 ? (
                  <div className={`text-center py-12 ${textSecondary}`}>
                    <Mail className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>Nessuna campagna email</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {emailCampaigns.map((campaign) => (
                      <div
                        key={campaign.id}
                        className="p-5 rounded-xl bg-muted/50"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h4 className={`font-semibold ${textPrimary}`}>{campaign.name}</h4>
                            <p className={`text-sm ${textSecondary}`}>{campaign.subject}</p>
                          </div>
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full ${campaign.is_sent
                              ? 'bg-gold/20 text-gold'
                              : 'bg-gold/20 text-gold'
                              }`}
                          >
                            {campaign.is_sent ? 'Inviata' : 'Bozza'}
                          </span>
                        </div>
                        <div className="grid grid-cols-4 gap-4">
                          <div>
                            <div className={`text-xl font-bold ${textPrimary}`}>
                              {campaign.total_sent || 0}
                            </div>
                            <div className={`text-xs ${textSecondary}`}>Inviate</div>
                          </div>
                          <div>
                            <div className="text-xl font-bold text-gold">
                              {campaign.open_rate || 0}%
                            </div>
                            <div className={`text-xs ${textSecondary}`}>Open Rate</div>
                          </div>
                          <div>
                            <div className="text-xl font-bold text-gold">
                              {campaign.click_rate || 0}%
                            </div>
                            <div className={`text-xs ${textSecondary}`}>Click Rate</div>
                          </div>
                          <div>
                            <div className={`text-xl font-bold ${textPrimary}`}>
                              {campaign.total_clicked || 0}
                            </div>
                            <div className={`text-xs ${textSecondary}`}>Click Totali</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'website' && (
            <motion.div
              key="website"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              <div className={`${cardBg} rounded-2xl p-6`}>
                <h3 className={`text-lg font-bold mb-4 ${textPrimary}`}>
                  Google Analytics 4
                </h3>
                {ga4Metrics ? (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-4 rounded-xl bg-muted/50">
                      <div className={`text-2xl font-bold ${textPrimary}`}>
                        {(ga4Metrics.totals?.activeUsers || 0).toLocaleString('it-IT')}
                      </div>
                      <div className={`text-sm ${textSecondary}`}>Utenti Attivi</div>
                    </div>
                    <div className="p-4 rounded-xl bg-muted/50">
                      <div className={`text-2xl font-bold ${textPrimary}`}>
                        {(ga4Metrics.totals?.screenPageViews || 0).toLocaleString('it-IT')}
                      </div>
                      <div className={`text-sm ${textSecondary}`}>Visualizzazioni</div>
                    </div>
                    <div className="p-4 rounded-xl bg-muted/50">
                      <div className={`text-2xl font-bold ${textPrimary}`}>
                        {(ga4Metrics.totals?.sessions || 0).toLocaleString('it-IT')}
                      </div>
                      <div className={`text-sm ${textSecondary}`}>Sessioni</div>
                    </div>
                    <div className="p-4 rounded-xl bg-muted/50">
                      <div className={`text-2xl font-bold ${textPrimary}`}>
                        {Math.round(ga4Metrics.totals?.averageSessionDuration || 0)}s
                      </div>
                      <div className={`text-sm ${textSecondary}`}>Durata Media</div>
                    </div>
                  </div>
                ) : (
                  <div className={`text-center py-12 ${textSecondary}`}>
                    <Globe className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>GA4 non configurato</p>
                    <p className="text-sm mt-1">Connetti Google Analytics per vedere le metriche</p>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      )}
    </div>
  );
}

export default MarketingAnalyticsPro;
