/**
 * SEO Analytics Types
 * Specific for Google Search Console integration
 */

export interface SEOMetrics {
  clicks: number;
  impressions: number;
  ctr: number;
  position: number;
}

export interface SEOChanges {
  clicks: number;
  impressions: number;
  ctr: number;
  position: number;
}

export interface SEOOverview {
  period: { start: string; end: string; days: number };
  metrics: SEOMetrics;
  changes: SEOChanges;
  previous: SEOMetrics;
}

export interface Query {
  query: string;
  clicks: number;
  impressions: number;
  ctr: number;
  position: number;
}

export interface Page {
  page: string;
  clicks: number;
  impressions: number;
  ctr: number;
  position: number;
}

export interface DailyData {
  date: string;
  clicks: number;
  impressions: number;
  ctr: number;
  position: number;
}

export interface KeywordOpportunity {
  query: string;
  impressions: number;
  clicks: number;
  ctr: number;
  position: number;
  potential_clicks: number;
}

export interface SEODashboard {
  overview: SEOOverview;
  top_queries: Query[];
  top_pages: Page[];
  devices: Record<string, SEOMetrics>;
  countries: Array<{ country: string } & SEOMetrics>;
  daily_performance: DailyData[];
  toolai_performance: {
    total_clicks: number;
    total_impressions: number;
    avg_ctr: number;
    pages_count: number;
    top_pages: Page[];
  };
  keyword_opportunities: KeywordOpportunity[];
}
