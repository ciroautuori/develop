/**
 * Marketing Analytics Types
 * Backend: /apps/backend/app/domain/marketing/routers.py:429
 */

export interface MarketingStats {
  status_counts: Record<string, number>;
  upcoming_week: number;
  platform_stats_last_30_days: Record<string, number>;
  total_posts: number;
}

export const PLATFORM_LABELS: Record<string, { label: string; color: string; icon: string }> = {
  facebook: { label: 'Facebook', color: '#1877F2', icon: '👍' },
  instagram: { label: 'Instagram', color: '#E4405F', icon: '📸' },
  linkedin: { label: 'LinkedIn', color: '#0A66C2', icon: '💼' },
  twitter: { label: 'Twitter/X', color: '#1DA1F2', icon: '🐦' },
  tiktok: { label: 'TikTok', color: '#000000', icon: '🎵' }
};

export const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  draft: { label: 'Bozza', color: 'bg-gray-500' },
  scheduled: { label: 'Programmato', color: 'bg-blue-500' },
  publishing: { label: 'Pubblicando', color: 'bg-yellow-500' },
  published: { label: 'Pubblicato', color: 'bg-green-500' },
  failed: { label: 'Fallito', color: 'bg-red-500' },
  cancelled: { label: 'Annullato', color: 'bg-gray-600' }
};
