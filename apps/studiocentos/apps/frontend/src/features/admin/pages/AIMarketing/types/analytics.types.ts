/**
 * Types per Analytics centralizzati
 * @module types/analytics
 */

export interface MarketingStats {
  total_posts: number;
  total_scheduled: number;
  upcoming_week: number;
  status_counts: Record<string, number>;
  platform_stats_last_30_days: Record<string, number>;
}

export interface GA4Metrics {
  totals: {
    activeUsers: number;
    screenPageViews: number;
    sessions: number;
    averageSessionDuration: number;
    bounceRate?: number;
  };
  daily?: {
    date: string;
    activeUsers: number;
    screenPageViews: number;
  }[];
}

export interface PlatformMetrics {
  platform: string;
  followers: number;
  posts_count: number;
  impressions: number;
  engagement: number;
  engagement_rate: number;
  clicks: number;
  reach: number;
}

export interface DateRange {
  start: string;
  end: string;
  label: string;
}

export const DATE_RANGES: DateRange[] = [
  { start: 'today', end: 'today', label: 'Oggi' },
  { start: '7daysAgo', end: 'today', label: '7 giorni' },
  { start: '30daysAgo', end: 'today', label: '30 giorni' },
  { start: '90daysAgo', end: 'today', label: '90 giorni' },
];

export interface PlatformLabel {
  label: string;
  color: string;
  icon: string;
}

export const PLATFORM_LABELS: Record<string, PlatformLabel> = {
  instagram: { label: 'Instagram', color: '#E4405F', icon: '📸' },
  facebook: { label: 'Facebook', color: '#1877F2', icon: '📘' },
  linkedin: { label: 'LinkedIn', color: '#0A66C2', icon: '💼' },
  twitter: { label: 'X (Twitter)', color: '#1DA1F2', icon: '🐦' },
  tiktok: { label: 'TikTok', color: '#000000', icon: '🎵' },
  youtube: { label: 'YouTube', color: '#FF0000', icon: '📺' },
};

export interface StatusLabel {
  label: string;
  color: string;
}

export const STATUS_LABELS: Record<string, StatusLabel> = {
  draft: { label: 'Bozza', color: 'bg-gray-500' },
  scheduled: { label: 'Programmato', color: 'bg-gold' },
  published: { label: 'Pubblicato', color: 'bg-green-500' },
  failed: { label: 'Fallito', color: 'bg-red-500' },
};
