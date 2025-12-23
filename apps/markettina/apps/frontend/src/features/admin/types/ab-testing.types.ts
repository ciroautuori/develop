/**
 * A/B Testing Types
 * Shared between frontend and backend (mirrored)
 */

export interface Variant {
  id: string;
  name: string;
  content: string;
  traffic_percent: number;
  impressions: number;
  conversions: number;
  conversion_rate: number;
  is_winner?: boolean;
}

export interface ABTestResult {
  confidence: number;
  significant: boolean;
  lift: number;
  recommendation: string;
}

export interface ABTest {
  id: string;
  name: string;
  status: 'draft' | 'running' | 'paused' | 'completed';
  type: string;
  variants: Variant[];
  result?: ABTestResult;
  started_at?: string;
  ended_at?: string;
}
