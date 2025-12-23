/**
 * Lead API Service
 * Lead search, enrichment, CRM integration
 */

import { toast } from 'sonner';

export interface LeadSearchParams {
  industry: string;
  location: string;
  radius_km: number;
  size?: string;
  need?: string;
}

export interface Lead {
  name: string;
  address: string;
  phone?: string;
  website?: string;
  rating?: number;
  review_count?: number;
  category: string;
  lat: number;
  lng: number;
  distance_km: number;
  score: number;
  needs_match: string[];
  opportunity_level: 'high' | 'medium' | 'low';
}

export interface Customer {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  source: string;
}

function getAuthToken(): string {
  const token = localStorage.getItem('admin_token');
  if (!token) throw new Error('Authentication required');
  return token;
}

async function handleApiResponse<T>(response: Response, context: string): Promise<T> {
  if (!response.ok) {
    const error = await response.text();
    console.error(`[LeadAPI] ${context} failed:`, error);

    if (response.status === 401) {
      toast.error('Sessione scaduta');
    } else if (response.status === 429) {
      toast.error('Troppe richieste');
    } else {
      toast.error(`Errore: ${context}`);
    }

    throw new Error(`${context}: ${response.status}`);
  }

  return response.json();
}

export class LeadApiService {
  private static readonly BASE_URL = '/api/v1';

  static async searchLeads(params: LeadSearchParams): Promise<Lead[]> {
    try {
      const response = await fetch(`${this.BASE_URL}/copilot/leads/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify(params)
      });

      return handleApiResponse<Lead[]>(response, 'Lead search');
    } catch (error) {
      console.error('[LeadAPI] searchLeads error:', error);
      throw error;
    }
  }

  static async saveToCRM(leads: Lead[]): Promise<Customer[]> {
    try {
      const response = await fetch(`${this.BASE_URL}/admin/customers/bulk-create-from-leads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({ leads })
      });

      return handleApiResponse<Customer[]>(response, 'Save leads to CRM');
    } catch (error) {
      console.error('[LeadAPI] saveToCRM error:', error);
      throw error;
    }
  }
}
