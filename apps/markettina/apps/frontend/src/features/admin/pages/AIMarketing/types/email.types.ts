/**
 * Types per Email Campaign centralizzati
 * @module types/email
 */

export interface Campaign {
  id: number;
  name: string;
  subject: string;
  html_content?: string;
  text_content?: string;
  target_region: string | null;
  target_industry: string | null;
  is_sent: boolean;
  total_sent: number;
  total_opened: number;
  total_clicked: number;
  open_rate: number;
  click_rate: number;
  created_at: string;
  sent_date: string | null;
  ai_generated?: boolean;
}

export interface CampaignStats {
  campaign_id: number;
  total_sent: number;
  total_delivered: number;
  total_opened: number;
  total_clicked: number;
  total_bounced: number;
  total_unsubscribed: number;
  open_rate: number;
  click_rate: number;
  bounce_rate: number;
}

export interface EmailGenerateRequest {
  campaign_name: string;
  target_region: string;
  target_industry: string;
  tone: 'professional' | 'friendly' | 'casual';
  language: 'it' | 'en';
  company_name?: string;
  contact_name?: string;
}

export interface EmailGenerateResult {
  subject: string;
  html_content: string;
  text_content: string;
  ai_model: string;
}

export interface CreateCampaignRequest {
  name: string;
  subject: string;
  html_content: string;
  text_content?: string;
  target_region?: string;
  target_industry?: string;
  ai_generated?: boolean;
}

export interface SendCampaignResult {
  campaign_id: number;
  total_sent: number;
  success: boolean;
  error?: string;
}

export interface TestEmailResult {
  success: boolean;
  message_id?: string;
  error?: string;
}
