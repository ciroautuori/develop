/**
 * GA4 Analytics Types
 * Specific for Google Analytics 4 integration
 */

export interface GAOverviewMetrics {
  active_users: number;
  new_users: number;
  sessions: number;
  page_views: number;
  bounce_rate: number;
  avg_session_duration: number;
  conversions: number;
  period: string;
}

export interface GATrafficSource {
  source: string;
  medium: string;
  users: number;
  sessions: number;
  percentage: number;
}

export interface GATopPage {
  path: string;
  page_views: number;
  unique_views: number;
  avg_time_on_page: number;
}

export interface GADeviceBreakdown {
  device: string;
  users: number;
  sessions: number;
  percentage: number;
}

export interface GADailyTraffic {
  date: string;
  users: number;
  sessions: number;
  pageViews: number;
}

export interface GADashboardResponse {
  overview: GAOverviewMetrics;
  traffic_sources: GATrafficSource[];
  top_pages: GATopPage[];
  device_breakdown: GADeviceBreakdown[];
  daily_traffic: GADailyTraffic[];
  last_updated: string;
}

export interface GoogleConnectionStatus {
  analytics_connected: boolean;
  business_profile_connected: boolean;
  analytics_property_id?: string;
  token_expires_at?: string;
}
