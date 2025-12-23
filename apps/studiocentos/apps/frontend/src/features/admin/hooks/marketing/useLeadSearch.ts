/**
 * useLeadSearch Hook
 * Manages lead search and CRM integration
 */

import { useState } from 'react';
import { toast } from 'sonner';
import { LeadApiService, Lead, LeadSearchParams, Customer } from '../../services/lead-api.service';

export function useLeadSearch() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = async (params: LeadSearchParams): Promise<Lead[]> => {
    setIsSearching(true);
    setError(null);

    try {
      const results = await LeadApiService.searchLeads(params);
      setLeads(results);
      toast.success(`Trovati ${results.length} lead!`);
      return results;
    } catch (err: any) {
      const errorMessage = err.message || 'Errore nella ricerca';
      setError(errorMessage);
      toast.error(errorMessage);
      return [];
    } finally {
      setIsSearching(false);
    }
  };

  const saveToCRM = async (leadsToSave: Lead[]): Promise<Customer[]> => {
    try {
      const customers = await LeadApiService.saveToCRM(leadsToSave);
      toast.success(`${customers.length} lead salvati nel CRM!`);
      return customers;
    } catch (err: any) {
      toast.error('Errore nel salvataggio CRM');
      return [];
    }
  };

  const reset = () => {
    setLeads([]);
    setError(null);
  };

  return {
    leads,
    isSearching,
    error,
    search,
    saveToCRM,
    reset
  };
}
