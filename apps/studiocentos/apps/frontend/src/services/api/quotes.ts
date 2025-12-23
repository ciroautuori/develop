/**
 * Quotes API Service
 *
 * Handles all API calls to the quotes backend endpoints.
 */

import api from './client';

export interface QuoteLineItem {
  id?: number;
  quote_id?: number;
  name: string;
  description?: string;
  sku?: string;
  quantity: number;
  unit_price: number;
  discount_percentage?: number;
  discount_amount?: number;
  subtotal?: number;
  position?: number;
}

export interface Quote {
  id: number;
  quote_number: string;
  title: string;
  description?: string;
  customer_id: number;
  version: number;
  is_latest: boolean;
  parent_quote_id?: number;
  currency: string;
  subtotal: number;
  tax_rate: number;
  tax_amount: number;
  discount_percentage: number;
  discount_amount: number;
  total: number;
  issue_date: string;
  valid_until: string;
  payment_terms_days: number;
  delivery_date?: string;
  status: 'draft' | 'sent' | 'viewed' | 'accepted' | 'rejected' | 'expired' | 'cancelled';
  sent_at?: string;
  viewed_at?: string;
  accepted_at?: string;
  rejected_at?: string;
  payment_terms?: string;
  terms_and_conditions?: string;
  notes_to_customer?: string;
  internal_notes?: string;
  pdf_file_path?: string;
  pdf_generated_at?: string;
  line_items: QuoteLineItem[];
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface QuoteListItem {
  id: number;
  quote_number: string;
  title: string;
  customer_id: number;
  status: string;
  version: number;
  is_latest: boolean;
  total: number;
  currency: string;
  valid_until: string;
  created_at: string;
  sent_at?: string;
  accepted_at?: string;
}

export interface QuoteCreate {
  title: string;
  description?: string;
  customer_id: number;
  currency?: string;
  tax_rate?: number;
  discount_percentage?: number;
  issue_date?: string;
  valid_until: string;
  payment_terms_days?: number;
  delivery_date?: string;
  payment_terms?: string;
  terms_and_conditions?: string;
  notes_to_customer?: string;
  internal_notes?: string;
  line_items: Omit<QuoteLineItem, 'id' | 'quote_id' | 'discount_amount' | 'subtotal'>[];
}

export interface QuoteUpdate {
  title?: string;
  description?: string;
  tax_rate?: number;
  discount_percentage?: number;
  valid_until?: string;
  payment_terms_days?: number;
  delivery_date?: string;
  payment_terms?: string;
  terms_and_conditions?: string;
  notes_to_customer?: string;
  internal_notes?: string;
}

export interface QuoteStats {
  total_quotes: number;
  by_status: Record<string, number>;
  total_value: number;
  accepted_value: number;
  conversion_rate: number;
  avg_quote_value: number;
  avg_conversion_time_days?: number;
}

export interface QuoteFilters {
  customer_id?: number;
  status?: string;
  currency?: string;
  is_latest?: boolean;
  from_date?: string;
  to_date?: string;
  min_value?: number;
  max_value?: number;
  search?: string;
  skip?: number;
  limit?: number;
}

const quotesApi = {
  // CRUD operations
  list: async (filters?: QuoteFilters) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    const response = await api.get<QuoteListItem[]>(`/quotes/?${params}`);
    return response.data;
  },

  count: async (filters?: QuoteFilters) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    const response = await api.get<{ total: number }>(`/quotes/count?${params}`);
    return response.data.total;
  },

  get: async (id: number) => {
    const response = await api.get<Quote>(`/quotes/${id}`);
    return response.data;
  },

  create: async (data: QuoteCreate) => {
    const response = await api.post<Quote>('/quotes/', data);
    return response.data;
  },

  update: async (id: number, data: QuoteUpdate) => {
    const response = await api.put<Quote>(`/quotes/${id}`, data);
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/quotes/${id}`);
  },

  // Line Items
  addLineItem: async (quoteId: number, data: Omit<QuoteLineItem, 'id' | 'quote_id' | 'discount_amount' | 'subtotal'>) => {
    const response = await api.post<QuoteLineItem>(`/quotes/${quoteId}/line-items`, data);
    return response.data;
  },

  updateLineItem: async (lineItemId: number, data: Partial<QuoteLineItem>) => {
    const response = await api.put<QuoteLineItem>(`/quotes/line-items/${lineItemId}`, data);
    return response.data;
  },

  deleteLineItem: async (lineItemId: number) => {
    await api.delete(`/quotes/line-items/${lineItemId}`);
  },

  // Actions
  send: async (quoteId: number, customerEmail?: string, ccEmails?: string[], customMessage?: string) => {
    const response = await api.post<Quote>(`/quotes/${quoteId}/send`, {
      customer_email: customerEmail,
      cc_emails: ccEmails,
      custom_message: customMessage,
    });
    return response.data;
  },

  markViewed: async (quoteId: number) => {
    const response = await api.post<Quote>(`/quotes/${quoteId}/viewed`);
    return response.data;
  },

  accept: async (quoteId: number, acceptedByName: string, acceptedByEmail: string, notes?: string) => {
    const response = await api.post<Quote>(`/quotes/${quoteId}/accept`, {
      accepted_by_name: acceptedByName,
      accepted_by_email: acceptedByEmail,
      notes,
    });
    return response.data;
  },

  reject: async (quoteId: number, reason: string) => {
    const response = await api.post<Quote>(`/quotes/${quoteId}/reject`, {
      rejection_reason: reason,
    });
    return response.data;
  },

  duplicate: async (quoteId: number, reason?: string, changesSummary?: string) => {
    const response = await api.post<Quote>(`/quotes/${quoteId}/duplicate`, {
      reason,
      changes_summary: changesSummary,
    });
    return response.data;
  },

  // Analytics
  getStats: async () => {
    const response = await api.get<QuoteStats>('/quotes/stats/overview');
    return response.data;
  },

  // PDF
  downloadPDF: async (quoteId: number) => {
    const response = await api.get(`/quotes/${quoteId}/pdf`, {
      responseType: 'blob',
    });
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `quote-${quoteId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
};

export default quotesApi;
