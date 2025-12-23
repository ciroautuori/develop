/**
 * Customers API Service
 *
 * Handles all API calls to the customers (CRM) backend endpoints.
 */

import api from './client';

export interface Customer {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company_name?: string;
  company_vat_id?: string;
  company_website?: string;
  status: 'lead' | 'prospect' | 'active' | 'inactive' | 'churned';
  customer_type: 'individual' | 'business' | 'agency' | 'non_profit';
  source: 'website' | 'referral' | 'advertising' | 'event' | 'direct' | 'organic' | 'other';
  lifetime_value: number;
  total_spent: number;
  avg_deal_size: number;
  completed_projects: number;
  last_contact_date?: string;
  next_followup_date?: string;
  created_at: string;
  updated_at: string;
}

export interface CustomerListItem {
  id: number;
  name: string;
  email: string;
  company_name?: string;
  status: string;
  customer_type: string;
  source: string;
  lifetime_value: number;
  total_spent: number;
  last_contact_date?: string;
  next_followup_date?: string;
  created_at: string;
}

export interface CustomerCreate {
  name: string;
  email: string;
  phone?: string;
  company_name?: string;
  company_vat_id?: string;
  company_website?: string;
  status?: string;
  customer_type?: string;
  source?: string;
  tags?: string;
  notes?: string;
  marketing_consent?: boolean;
}

export interface CustomerUpdate extends Partial<CustomerCreate> {
  next_followup_date?: string;
  next_followup_notes?: string;
}

export interface CustomerNote {
  id: number;
  customer_id: number;
  note: string;
  created_by: number;
  created_at: string;
}

export interface CustomerInteraction {
  id: number;
  customer_id: number;
  interaction_type: string;
  subject?: string;
  description?: string;
  outcome?: string;
  next_action?: string;
  scheduled_at?: string;
  completed_at?: string;
  created_by: number;
  created_at: string;
}

export interface CustomerStats {
  total_customers: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  by_source: Record<string, number>;
  total_lifetime_value: number;
  avg_lifetime_value: number;
  top_customers: CustomerListItem[];
}

export interface CustomerFilters {
  status?: string;
  customer_type?: string;
  source?: string;
  assigned_to?: number;
  search?: string;
  tags?: string;
  needs_followup?: boolean;
  skip?: number;
  limit?: number;
}

const customersApi = {
  // CRUD operations
  list: async (filters?: CustomerFilters) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    const response = await api.get<CustomerListItem[]>(`/customers/?${params}`);
    return response.data;
  },

  count: async (filters?: CustomerFilters) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    const response = await api.get<{ total: number }>(`/customers/count?${params}`);
    return response.data.total;
  },

  get: async (id: number) => {
    const response = await api.get<Customer>(`/customers/${id}`);
    return response.data;
  },

  create: async (data: CustomerCreate) => {
    const response = await api.post<Customer>('/customers/', data);
    return response.data;
  },

  update: async (id: number, data: CustomerUpdate) => {
    const response = await api.put<Customer>(`/customers/${id}`, data);
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/customers/${id}`);
  },

  restore: async (id: number) => {
    const response = await api.post<Customer>(`/customers/${id}/restore`);
    return response.data;
  },

  // Notes
  addNote: async (customerId: number, note: string) => {
    const response = await api.post<CustomerNote>(`/customers/${customerId}/notes`, { note });
    return response.data;
  },

  getNotes: async (customerId: number, limit = 50) => {
    const response = await api.get<CustomerNote[]>(`/customers/${customerId}/notes?limit=${limit}`);
    return response.data;
  },

  deleteNote: async (noteId: number) => {
    await api.delete(`/customers/notes/${noteId}`);
  },

  // Interactions
  logInteraction: async (customerId: number, data: Partial<CustomerInteraction>) => {
    const response = await api.post<CustomerInteraction>(`/customers/${customerId}/interactions`, data);
    return response.data;
  },

  getInteractions: async (customerId: number, limit = 50) => {
    const response = await api.get<CustomerInteraction[]>(`/customers/${customerId}/interactions?limit=${limit}`);
    return response.data;
  },

  deleteInteraction: async (interactionId: number) => {
    await api.delete(`/customers/interactions/${interactionId}`);
  },

  // Analytics
  getStats: async () => {
    const response = await api.get<CustomerStats>('/customers/stats/overview');
    return response.data;
  },

  getFollowupNeeded: async () => {
    const response = await api.get<CustomerListItem[]>('/customers/followup/needed');
    return response.data;
  },

  getInactive: async (days = 90) => {
    const response = await api.get<CustomerListItem[]>(`/customers/inactive?days=${days}`);
    return response.data;
  },

  // Bulk operations
  bulkUpdateStatus: async (customerIds: number[], newStatus: string) => {
    const response = await api.post<{ updated: number }>('/customers/bulk/update-status', {
      customer_ids: customerIds,
      new_status: newStatus,
    });
    return response.data.updated;
  },

  bulkAssign: async (customerIds: number[], assignedTo: number) => {
    const response = await api.post<{ assigned: number }>('/customers/bulk/assign', {
      customer_ids: customerIds,
      assigned_to: assignedTo,
    });
    return response.data.assigned;
  },

  // Deduplication
  findDuplicates: async (limit = 50) => {
    const response = await api.get<any[]>(`/customers/duplicates/find?limit=${limit}`);
    return response.data;
  },

  mergeCustomers: async (primaryId: number, customerIdsToMerge: number[]) => {
    const response = await api.post<Customer>('/customers/merge', {
      primary_customer_id: primaryId,
      customer_ids_to_merge: customerIdsToMerge,
    });
    return response.data;
  },
};

export default customersApi;
