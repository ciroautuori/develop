import React, { createContext, useContext, useState, type ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { bandoAPI } from '@/services/api';
import type { BandoStats, ISSStats } from '@/types/api';

interface DashboardContextValue {
  // Data
  bandoStats: BandoStats | null;
  issStats: ISSStats | null;

  // Loading states
  isBandoStatsLoading: boolean;
  isISSStatsLoading: boolean;

  // Error states
  bandoStatsError: Error | null;
  issStatsError: Error | null;

  // Actions
  refetchBandoStats: () => void;
  refetchISSStats: () => void;
  refetchAll: () => void;

  // UI State
  activeView: 'bandi' | 'iss' | 'both';
  setActiveView: (view: 'bandi' | 'iss' | 'both') => void;
}

const DashboardContext = createContext<DashboardContextValue | undefined>(undefined);

export const useDashboard = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboard must be used within a DashboardProvider');
  }
  return context;
};

interface DashboardProviderProps {
  children: ReactNode;
}

export const DashboardProvider: React.FC<DashboardProviderProps> = ({ children }) => {
  const [activeView, setActiveView] = useState<'bandi' | 'iss' | 'both'>('both');

  // Bando Stats Query
  const {
    data: bandoStats,
    isLoading: isBandoStatsLoading,
    error: bandoStatsError,
    refetch: refetchBandoStats,
  } = useQuery({
    queryKey: ['bando-stats'],
    queryFn: bandoAPI.getStats,
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchInterval: 1000 * 60 * 10, // 10 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  // ISS Stats - Values initialized to 0, will be populated by admin backoffice
  const issStats = {
    studenti_formati: 0,
    corsi_completati: 0,
    eventi_organizzati: 0,
    progetti_attivi: 0,
    volontari_attivi: 0,
    ore_formazione_erogate: 0,
    partner_collaborazioni: 0,
    impatto_sociale: {
      persone_raggiunte: 0,
      competenze_certificate: 0,
      progetti_finanziati: 0,
    },
    trends: {
      iscrizioni_mensili: [],
      corsi_per_categoria: {
        alfabetizzazione: 0,
        professionale: 0,
        assistive: 0,
        avanzato: 0,
      },
      eventi_per_tipo: {
        hackathon: 0,
        workshop: 0,
        conferenza: 0,
        laboratorio: 0,
      },
    },
  };

  const isISSStatsLoading = false;
  const issStatsError = null;
  const refetchISSStats = () => Promise.resolve();

  const refetchAll = () => {
    refetchBandoStats();
    refetchISSStats();
  };

  const value: DashboardContextValue = {
    // Data
    bandoStats: bandoStats || null,
    issStats: issStats || null,

    // Loading states
    isBandoStatsLoading,
    isISSStatsLoading,

    // Error states
    bandoStatsError: bandoStatsError as Error | null,
    issStatsError: issStatsError as Error | null,

    // Actions
    refetchBandoStats,
    refetchISSStats,
    refetchAll,

    // UI State
    activeView,
    setActiveView,
  };

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
};
