/**
 * SEO Analytics Dashboard - Google Search Console Integration
 * DESIGN SYSTEM COMPLIANT - Uses semantic tokens
 */

import { useState, useEffect } from 'react';
import {
  TrendingUp,
  Search,
  FileText,
  Monitor,
  Smartphone,
  Globe,
  Eye,
  MousePointer,
  Target,
  Zap,
  Calendar,
  ArrowUp,
  ArrowDown,
  Minus,
  ExternalLink,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { cn } from '../../../shared/lib/utils';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { Button } from '../../../shared/components/ui/button';
import {
  SEOMetrics,
  SEODashboard
} from '../types/seo-analytics.types';

const COLORS = {
  primary: '#D4AF37',
  secondary: '#8B5CF6',
  success: '#10B981',
  danger: '#EF4444',
  warning: '#F59E0B',
  info: '#3B82F6',
  desktop: '#8B5CF6',
  mobile: '#EC4899',
  tablet: '#F59E0B',
};

const CHART_COLORS = ['#D4AF37', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#3B82F6'];

export default function AnalyticsSEO() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboard, setDashboard] = useState<SEODashboard | null>(null);
  const [period, setPeriod] = useState(30);
  const [activeTab, setActiveTab] = useState<'overview' | 'queries' | 'pages' | 'toolai' | 'opportunities'>('overview');

  useEffect(() => {
    fetchDashboard();
  }, [period]);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('admin_token');
      const res = await fetch(`/api/v1/admin/google/search-console/dashboard?days=${period}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (res.status === 401) {
        setError('Sessione scaduta. Effettua nuovamente il login.');
        return;
      }

      const data = await res.json();

      if (data.connected === false) {
        setError(data.message || 'Google Search Console non connesso. Vai in Impostazioni per collegarlo.');
        return;
      }

      if (!res.ok) {
        throw new Error('Errore nel caricamento dei dati SEO');
      }

      setDashboard(data);
    } catch (err) {
      console.error('Error loading SEO dashboard:', err);
      setError(err instanceof Error ? err.message : 'Errore sconosciuto');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toLocaleString();
  };

  const formatCTR = (ctr: number) => `${ctr.toFixed(2)}%`;

  const formatPosition = (pos: number) => pos.toFixed(1);

  const renderChangeIndicator = (change: number, inverse: boolean = false) => {
    const isPositive = inverse ? change < 0 : change > 0;
    const isNegative = inverse ? change > 0 : change < 0;

    if (Math.abs(change) < 0.1) {
      return (
        <span className="flex items-center gap-1 text-muted-foreground">
          <Minus className="w-3 h-3" />
          <span>0%</span>
        </span>
      );
    }

    return (
      <span className={cn('flex items-center gap-1', isPositive ? 'text-green-500' : isNegative ? 'text-red-500' : 'text-muted-foreground')}>
        {isPositive ? <ArrowUp className="w-3 h-3" /> : isNegative ? <ArrowDown className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
        <span>{Math.abs(change).toFixed(1)}%</span>
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <Loader2 className="w-12 h-12 mx-auto text-primary animate-spin mb-4" />
          <p className="text-muted-foreground">Caricamento dati SEO...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] p-4 sm:p-6">
        <div className="text-center max-w-lg w-full">
          <div className="p-6 sm:p-8 bg-card border border-border rounded-2xl">
            <div className="p-4 bg-primary/10 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
              <Search className="w-10 h-10 text-primary" />
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-foreground mb-3">
              Google Search Console
            </h2>
            <p className="text-sm sm:text-base text-muted-foreground mb-6 leading-relaxed">
              {error}
            </p>
            <div className="space-y-3">
              <a
                href="/admin/settings?tab=integrations"
                className="inline-flex items-center justify-center gap-2 w-full sm:w-auto px-6 py-3 bg-primary text-primary-foreground font-medium rounded-xl hover:bg-primary/90 transition-all"
              >
                <ExternalLink className="w-5 h-5" />
                Connetti Google Search Console
              </a>
              <p className="text-xs text-muted-foreground">
                Dopo la connessione, potrai visualizzare click, impressioni, CTR e posizionamento delle tue pagine.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-muted-foreground">Nessun dato disponibile</p>
      </div>
    );
  }

  const { overview, top_queries, top_pages, devices, countries, daily_performance, toolai_performance, keyword_opportunities } = dashboard;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
            <Search className="w-5 h-5 text-primary" />
            SEO Analytics
          </h2>
          <p className="text-sm text-muted-foreground mt-1">Google Search Console</p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={period}
            onChange={(e) => setPeriod(Number(e.target.value))}
            className="px-4 py-2 bg-background border border-input rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value={7}>7 giorni</option>
            <option value={30}>30 giorni</option>
            <option value={90}>90 giorni</option>
            <option value={180}>6 mesi</option>
            <option value={365}>1 anno</option>
          </select>

          <Button variant="outline" size="icon" onClick={fetchDashboard}>
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Clicks */}
        <div className="bg-card border border-border rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground flex items-center gap-2">
              <MousePointer className="w-4 h-4" />
              Click
            </span>
            {renderChangeIndicator(overview.changes.clicks)}
          </div>
          <div className="text-2xl font-bold text-foreground">
            {formatNumber(overview.metrics.clicks)}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            vs {formatNumber(overview.previous.clicks)}
          </div>
        </div>

        {/* Impressions */}
        <div className="bg-card border border-border rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground flex items-center gap-2">
              <Eye className="w-4 h-4" />
              Impressioni
            </span>
            {renderChangeIndicator(overview.changes.impressions)}
          </div>
          <div className="text-2xl font-bold text-foreground">
            {formatNumber(overview.metrics.impressions)}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            vs {formatNumber(overview.previous.impressions)}
          </div>
        </div>

        {/* CTR */}
        <div className="bg-card border border-border rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground flex items-center gap-2">
              <Target className="w-4 h-4" />
              CTR
            </span>
            {renderChangeIndicator(overview.changes.ctr)}
          </div>
          <div className="text-2xl font-bold text-foreground">
            {formatCTR(overview.metrics.ctr)}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            vs {formatCTR(overview.previous.ctr)}
          </div>
        </div>

        {/* Position */}
        <div className="bg-card border border-border rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Posizione
            </span>
            {renderChangeIndicator(overview.changes.position, true)}
          </div>
          <div className="text-2xl font-bold text-foreground">
            {formatPosition(overview.metrics.position)}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            vs {formatPosition(overview.previous.position)}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 p-1 rounded-xl bg-muted/50 overflow-x-auto scrollbar-hide">
        {[
          { id: 'overview', label: 'Panoramica', icon: TrendingUp },
          { id: 'queries', label: 'Query', icon: Search },
          { id: 'pages', label: 'Pagine', icon: FileText },
          { id: 'toolai', label: 'ToolAI', icon: Zap },
          { id: 'opportunities', label: 'Opportunità', icon: Target },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={cn(
              'flex-shrink-0 min-w-max flex items-center justify-center gap-2 py-3 px-4 rounded-lg text-sm font-medium transition-all whitespace-nowrap',
              activeTab === tab.id
                ? 'bg-background text-foreground shadow-sm border border-border'
                : 'text-muted-foreground hover:text-foreground hover:bg-background/50'
            )}
          >
            <tab.icon className="w-4 h-4" />
            <span className="hidden sm:inline">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-4 sm:space-y-6">
          {/* Daily Performance Chart */}
          <div className="p-3 sm:p-4 md:p-6 bg-white/5 border border-white/10 rounded-lg sm:rounded-xl">
            <h3 className="text-base sm:text-lg md:text-xl font-bold mb-3 sm:mb-4 flex items-center gap-2">
              <Calendar className="w-4 h-4 sm:w-5 sm:h-5 text-gold" />
              <span>Performance Giornaliera</span>
            </h3>
            <div className="overflow-x-auto -mx-3 sm:mx-0">
              <div className="min-w-[300px]">
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={daily_performance}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="date" stroke="#999" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#999" tick={{ fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid rgba(255,255,255,0.1)', fontSize: '12px' }}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Line type="monotone" dataKey="clicks" stroke={COLORS.primary} name="Click" strokeWidth={2} />
                    <Line type="monotone" dataKey="impressions" stroke={COLORS.secondary} name="Impressioni" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Devices & Countries */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
            {/* Devices */}
            <div className="p-3 sm:p-4 md:p-6 bg-white/5 border border-white/10 rounded-lg sm:rounded-xl">
              <h3 className="text-base sm:text-lg md:text-xl font-bold mb-3 sm:mb-4 flex items-center gap-2">
                <Monitor className="w-4 h-4 sm:w-5 sm:h-5 text-gold" />
                <span>Dispositivi</span>
              </h3>
              <div className="space-y-2 sm:space-y-3">
                {Object.entries(devices).map(([device, metrics]) => {
                  const icon = device === 'DESKTOP' ? Monitor : device === 'MOBILE' ? Smartphone : Monitor;
                  const color = device === 'DESKTOP' ? COLORS.desktop : device === 'MOBILE' ? COLORS.mobile : COLORS.tablet;
                  const Icon = icon;

                  return (
                    <div key={device} className="flex items-center justify-between p-2.5 sm:p-3 bg-white/5 rounded-lg">
                      <div className="flex items-center gap-2 sm:gap-3">
                        <Icon className="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" style={{ color }} />
                        <span className="text-sm sm:text-base font-medium capitalize">{device.toLowerCase()}</span>
                      </div>
                      <div className="flex items-center gap-2 sm:gap-4 text-xs sm:text-sm">
                        <span className="hidden xs:inline">{formatNumber(metrics.clicks)} click</span>
                        <span className="xs:hidden text-gold">{formatNumber(metrics.clicks)}</span>
                        <span className="text-gray-400">{formatCTR(metrics.ctr)}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Countries */}
            <div className="p-3 sm:p-4 md:p-6 bg-white/5 border border-white/10 rounded-lg sm:rounded-xl">
              <h3 className="text-base sm:text-lg md:text-xl font-bold mb-3 sm:mb-4 flex items-center gap-2">
                <Globe className="w-4 h-4 sm:w-5 sm:h-5 text-gold" />
                <span>Top Paesi</span>
              </h3>
              <div className="space-y-2">
                {countries.slice(0, 5).map((country, i) => (
                  <div key={country.country} className="flex items-center justify-between p-2 bg-white/5 rounded">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500 w-4">{i + 1}</span>
                      <span className="text-sm sm:text-base font-medium truncate max-w-[120px] sm:max-w-none">{country.country}</span>
                    </div>
                    <div className="flex items-center gap-2 sm:gap-3 text-xs sm:text-sm">
                      <span className="text-gold">{formatNumber(country.clicks)}</span>
                      <span className="text-gray-400 hidden xs:inline">{formatCTR(country.ctr)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'queries' && (
        <div className="p-3 sm:p-4 md:p-6 bg-white/5 border border-white/10 rounded-lg sm:rounded-xl">
          <h3 className="text-base sm:text-lg md:text-xl font-bold mb-3 sm:mb-4">Top Query di Ricerca</h3>
          <div className="overflow-x-auto -mx-3 sm:mx-0">
            <table className="w-full min-w-[600px] text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 sm:py-3 px-1 sm:px-2">#</th>
                  <th className="text-left py-2 sm:py-3 px-2 sm:px-4">Query</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4">Click</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4 hidden sm:table-cell">Impressioni</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4">CTR</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4 hidden md:table-cell">Posizione</th>
                </tr>
              </thead>
              <tbody>
                {top_queries.map((query, i) => (
                  <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-2 sm:py-3 px-1 sm:px-2 text-gray-500">{i + 1}</td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 font-medium max-w-[150px] sm:max-w-[300px] truncate">{query.query}</td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 text-right text-gold">{formatNumber(query.clicks)}</td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 text-right text-gray-400 hidden sm:table-cell">{formatNumber(query.impressions)}</td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 text-right">{formatCTR(query.ctr)}</td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 text-right hidden md:table-cell">
                      <span className={query.position <= 3 ? 'text-gold' : query.position <= 10 ? 'text-gold' : 'text-gray-400'}>
                        {formatPosition(query.position)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'pages' && (
        <div className="p-3 sm:p-4 md:p-6 bg-white/5 border border-white/10 rounded-lg sm:rounded-xl">
          <h3 className="text-base sm:text-lg md:text-xl font-bold mb-3 sm:mb-4">Top Pagine</h3>
          <div className="overflow-x-auto -mx-3 sm:mx-0">
            <table className="w-full min-w-[600px] text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 sm:py-3 px-1 sm:px-2">#</th>
                  <th className="text-left py-2 sm:py-3 px-2 sm:px-4">Pagina</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4">Click</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4 hidden sm:table-cell">Impressioni</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4">CTR</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4 hidden md:table-cell">Posizione</th>
                  <th className="text-center py-2 sm:py-3 px-1 sm:px-2"></th>
                </tr>
              </thead>
              <tbody>
                {top_pages.map((page, i) => (
                  <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-2 sm:py-3 px-1 sm:px-2 text-gray-500">{i + 1}</td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 font-mono text-xs truncate max-w-[150px] sm:max-w-md">
                      {page.page.replace('https://studiocentos.com', '')}
                    </td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 text-right text-gold">{formatNumber(page.clicks)}</td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 text-right text-gray-400 hidden sm:table-cell">{formatNumber(page.impressions)}</td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 text-right">{formatCTR(page.ctr)}</td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 text-right hidden md:table-cell">
                      <span className={page.position <= 3 ? 'text-gold' : page.position <= 10 ? 'text-gold' : 'text-gray-400'}>
                        {formatPosition(page.position)}
                      </span>
                    </td>
                    <td className="py-2 sm:py-3 px-1 sm:px-2 text-center">
                      <a href={page.page} target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-gold">
                        <ExternalLink className="w-3 h-3 sm:w-4 sm:h-4" />
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'toolai' && (
        <div className="space-y-4 sm:space-y-6">
          {/* ToolAI Overview */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
            <div className="p-4 sm:p-5 md:p-6 bg-gradient-to-br from-gold/20 to-gold/10 border border-gold/30 rounded-lg sm:rounded-xl">
              <div className="text-xs sm:text-sm text-gold mb-1 sm:mb-2">Click ToolAI</div>
              <div className="text-xl sm:text-2xl md:text-3xl font-bold text-gold">
                {formatNumber(toolai_performance.total_clicks)}
              </div>
            </div>
            <div className="p-4 sm:p-5 md:p-6 bg-gradient-to-br from-gold/20 to-gold/10 border border-gold/30 rounded-lg sm:rounded-xl">
              <div className="text-xs sm:text-sm text-gold mb-1 sm:mb-2 truncate">Impressioni</div>
              <div className="text-xl sm:text-2xl md:text-3xl font-bold text-gold">
                {formatNumber(toolai_performance.total_impressions)}
              </div>
            </div>
            <div className="p-4 sm:p-5 md:p-6 bg-gradient-to-br from-gold/20 to-gold/10 border border-gold/30 rounded-lg sm:rounded-xl">
              <div className="text-xs sm:text-sm text-gold mb-1 sm:mb-2">CTR Medio</div>
              <div className="text-xl sm:text-2xl md:text-3xl font-bold text-gold">
                {formatCTR(toolai_performance.avg_ctr)}
              </div>
            </div>
            <div className="p-4 sm:p-5 md:p-6 bg-gradient-to-br from-gold/20 to-gold/10 border border-gold/30 rounded-lg sm:rounded-xl">
              <div className="text-xs sm:text-sm text-gold mb-1 sm:mb-2 truncate">Pagine</div>
              <div className="text-xl sm:text-2xl md:text-3xl font-bold text-gold">
                {toolai_performance.pages_count}
              </div>
            </div>
          </div>

          {/* Top ToolAI Pages */}
          <div className="p-3 sm:p-4 md:p-6 bg-white/5 border border-white/10 rounded-lg sm:rounded-xl">
            <h3 className="text-base sm:text-lg md:text-xl font-bold mb-3 sm:mb-4 flex items-center gap-2">
              <Zap className="w-4 h-4 sm:w-5 sm:h-5 text-gold" />
              <span>Top ToolAI Pages</span>
            </h3>
            <div className="space-y-2">
              {toolai_performance.top_pages.map((page, i) => (
                <div key={i} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 p-2.5 sm:p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                  <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
                    <span className="text-xs text-gray-500 w-5 flex-shrink-0">{i + 1}</span>
                    <span className="font-mono text-xs sm:text-sm truncate flex-1">
                      {page.page.replace('https://studiocentos.com', '')}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 sm:gap-4 text-xs sm:text-sm pl-7 sm:pl-0">
                    <span className="text-gold">{formatNumber(page.clicks)}</span>
                    <span className="text-gray-400">{formatCTR(page.ctr)}</span>
                    <span className={page.position <= 10 ? 'text-gold' : 'text-gray-400'}>
                      #{formatPosition(page.position)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'opportunities' && (
        <div className="p-3 sm:p-4 md:p-6 bg-white/5 border border-white/10 rounded-lg sm:rounded-xl">
          <div className="mb-3 sm:mb-4">
            <h3 className="text-base sm:text-lg md:text-xl font-bold flex items-center gap-2">
              <Target className="w-4 h-4 sm:w-5 sm:h-5 text-gold" />
              <span>Opportunità</span>
            </h3>
            <p className="text-xs sm:text-sm text-gray-400 mt-1">
              Keywords con alte impressioni ma CTR basso
            </p>
          </div>
          <div className="overflow-x-auto -mx-3 sm:mx-0">
            <table className="w-full min-w-[700px] text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 sm:py-3 px-1 sm:px-2">#</th>
                  <th className="text-left py-2 sm:py-3 px-2 sm:px-4">Query</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4 hidden sm:table-cell">Impressioni</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4 hidden md:table-cell">Click</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4">CTR</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4 hidden md:table-cell">Posizione</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4">Potenziale</th>
                </tr>
              </thead>
              <tbody>
                {keyword_opportunities.map((opp, i) => (
                  <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-2 sm:py-3 px-1 sm:px-2 text-gray-500">{i + 1}</td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 font-medium max-w-[150px] sm:max-w-none truncate">{opp.query}</td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 text-right text-gold hidden sm:table-cell">{formatNumber(opp.impressions)}</td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 text-right hidden md:table-cell">{formatNumber(opp.clicks)}</td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 text-right">
                      <span className="text-gray-400">{formatCTR(opp.ctr)}</span>
                    </td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 text-right hidden md:table-cell">
                      <span className="text-gold">#{formatPosition(opp.position)}</span>
                    </td>
                    <td className="py-2 sm:py-3 px-2 sm:px-4 text-right">
                      <span className="text-gold font-bold">+{formatNumber(opp.potential_clicks)}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
