import axios, { type AxiosInstance, type AxiosResponse } from 'axios';
import type {
  Bando,
  BandoSearchParams,
  BandoSearchResponse,
  BandoStats,
  BandoFilters,
  Corso,
  Evento,
  Progetto,
  OpportunitaVolontariato,
  ISSSearchParams,
  ISSSearchResponse,
  ISSStats,
  User,
  AuthResponse,
  APIError,
  SemanticSearchResult,
  SemanticSearchRequest,
  ProfileMatchRequest,
  SuggestionsRequest,
} from '@/types/api';

class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = '/api/v1') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Clear token and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // ========== BANDI ENDPOINTS ==========

  async searchBandi(params: BandoSearchParams = {}): Promise<BandoSearchResponse> {
    const response: AxiosResponse<BandoSearchResponse> = await this.client.get('/bandi/', {
      params,
    });
    return response.data;
  }

  async getBandoById(id: number): Promise<Bando> {
    const response: AxiosResponse<Bando> = await this.client.get(`/bandi/${id}`);
    return response.data;
  }

  async getBandoStats(): Promise<BandoStats> {
    const response: AxiosResponse<BandoStats> = await this.client.get('/bandi/stats');
    return response.data;
  }

  async getRecentBandi(limit: number = 10): Promise<BandoSearchResponse> {
    const response: AxiosResponse<BandoSearchResponse> = await this.client.get(
      '/bandi/recent',
      {
        params: { limit },
      }
    );
    return response.data;
  }

  async getBandoFilters(): Promise<BandoFilters> {
    const response: AxiosResponse<BandoFilters> = await this.client.get('/bandi/filters');
    return response.data;
  }

  // ========== ISS APS ACTIVITIES ENDPOINTS ==========

  async searchCorsi(params: ISSSearchParams = {}): Promise<ISSSearchResponse<Corso>> {
    const response: AxiosResponse<ISSSearchResponse<Corso>> = await this.client.get('/corsi/', {
      params,
    });
    return response.data;
  }

  async getCorsoById(id: number): Promise<Corso> {
    const response: AxiosResponse<Corso> = await this.client.get(`/corsi/${id}`);
    return response.data;
  }

  async iscrivitiCorso(corsoId: number, userData: any): Promise<{ success: boolean; message: string }> {
    const response = await this.client.post(`/corsi/${corsoId}/iscrizione`, userData);
    return response.data;
  }

  async searchEventi(params: ISSSearchParams = {}): Promise<ISSSearchResponse<Evento>> {
    const response: AxiosResponse<ISSSearchResponse<Evento>> = await this.client.get('/eventi/', {
      params,
    });
    return response.data;
  }

  async getEventoById(id: number): Promise<Evento> {
    const response: AxiosResponse<Evento> = await this.client.get(`/eventi/${id}`);
    return response.data;
  }

  async partecipaEvento(eventoId: number, userData: any): Promise<{ success: boolean; message: string }> {
    const response = await this.client.post(`/eventi/${eventoId}/partecipazione`, userData);
    return response.data;
  }

  async getProgetti(params: ISSSearchParams = {}): Promise<ISSSearchResponse<Progetto>> {
    const response: AxiosResponse<ISSSearchResponse<Progetto>> = await this.client.get('/progetti/', {
      params,
    });
    return response.data;
  }

  async getProgettoById(id: number): Promise<Progetto> {
    const response: AxiosResponse<Progetto> = await this.client.get(`/progetti/${id}`);
    return response.data;
  }

  async candidatiVolontario(progettoId: number, userData: any): Promise<{ success: boolean; message: string }> {
    const response = await this.client.post(`/progetti/${progettoId}/volontariato`, userData);
    return response.data;
  }

  async getOpportunitaVolontariato(params: ISSSearchParams = {}): Promise<ISSSearchResponse<OpportunitaVolontariato>> {
    const response: AxiosResponse<ISSSearchResponse<OpportunitaVolontariato>> = await this.client.get(
      '/volontariato/',
      { params }
    );
    return response.data;
  }

  async candidatiVolontariato(opportunitaId: number, userData: any): Promise<{ success: boolean; message: string }> {
    const response = await this.client.post(`/volontariato/${opportunitaId}/candidatura`, userData);
    return response.data;
  }

  // ========== STATS & ANALYTICS ==========

  async getISSStats(): Promise<ISSStats> {
    const response: AxiosResponse<ISSStats> = await this.client.get('/stats/iss');
    return response.data;
  }

  async getDashboardData(): Promise<{
    bandoStats: BandoStats;
    issStats: ISSStats;
    recentBandi: Bando[];
    prossimi_corsi: Corso[];
    eventi_programmati: Evento[];
  }> {
    const response = await this.client.get('/dashboard/data');
    return response.data;
  }

  // ========== USER & AUTH ==========

  async login(email: string, password: string): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.client.post('/auth/login', {
      email,
      password,
    });

    // Store token and user data
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));

    return response.data;
  }

  async register(userData: {
    email: string;
    password: string;
    nome: string;
    cognome: string;
    role: 'cittadino' | 'aps_esterno';
    organizzazione?: string;
  }): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.client.post('/auth/register', userData);

    // Store token and user data
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));

    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/auth/logout');
    } finally {
      // Always clear local storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    }
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.client.get('/auth/me');
    return response.data;
  }

  async updateProfile(userData: Partial<User>): Promise<User> {
    const response: AxiosResponse<User> = await this.client.put('/auth/profile', userData);
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  }

  // ========== NOTIFICATIONS ==========

  async saveNotificationSettings(settings: any): Promise<{ success: boolean }> {
    const response = await this.client.post('/notifications/settings', settings);
    return response.data;
  }

  async getNotificationSettings(): Promise<any> {
    const response = await this.client.get('/notifications/settings');
    return response.data;
  }

  // ========== UTILITY METHODS ==========

  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  getCurrentToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getStoredUser(): User | null {
    const userData = localStorage.getItem('user');
    return userData ? JSON.parse(userData) : null;
  }

  isAuthenticated(): boolean {
    return !!this.getCurrentToken();
  }

  // Helper method to handle API errors
  handleError(error: any): APIError {
    if (error.response?.data) {
      return error.response.data;
    }
    return {
      detail: error.message || 'An unexpected error occurred',
      status_code: error.response?.status || 500,
    };
  }
}

// Create singleton instance
export const apiClient = new APIClient();

// Export individual service methods for easier imports
export const bandoService = {
  search: (params?: BandoSearchParams) => apiClient.searchBandi(params),
  getById: (id: number) => apiClient.getBandoById(id),
  getProgetto: (id: number) => apiClient.getProgettoById(id),
  getStats: () => apiClient.getISSStats(),
};

export const authService = {
  login: (email: string, password: string) => apiClient.login(email, password),
  register: (userData: any) => apiClient.register(userData),
  logout: () => apiClient.logout(),
  getCurrentUser: () => apiClient.getCurrentUser(),
  getStoredUser: () => apiClient.getStoredUser(),
  updateProfile: (data: Partial<User>) => apiClient.updateProfile(data),
  isAuthenticated: () => apiClient.isAuthenticated(),
};

// Export bandoAPI alias per compatibilità con i componenti
export const bandoAPI = {
  search: (params?: BandoSearchParams) => apiClient.searchBandi(params),
  getById: (id: number) => apiClient.getBandoById(id),
  getStats: () => apiClient.getBandoStats(),
  getRecent: (limit?: number) => apiClient.getRecentBandi(limit),
  getFilters: () => apiClient.getBandoFilters(),
  // Save/unsave bandi (MVP - salvataggio locale + conferma backend)
  save: async (bandoId: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient['client'].post(`/bandi/${bandoId}/save`);
    return response.data;
  },
  unsave: async (bandoId: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient['client'].delete(`/bandi/${bandoId}/save`);
    return response.data;
  },
};

// ========== AI SEMANTIC SEARCH SERVICE ==========

class AISemanticSearchService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api/v1/ai',
      timeout: 30000, // 30s timeout for AI operations
    });
  }

  async semanticSearch(params: {
    query: string;
    limit?: number;
    threshold?: number;
  }): Promise<SemanticSearchResult[]> {
    const response: AxiosResponse<SemanticSearchResult[]> = await this.client.post('/search', params);
    return response.data;
  }

  async matchProfile(profile: {
    organization_type?: string;
    sectors?: string[];
    target_groups?: string[];
    keywords?: string[];
    geographical_area?: string;
    max_amount?: number;
    limit?: number;
  }): Promise<SemanticSearchResult[]> {
    const response: AxiosResponse<SemanticSearchResult[]> = await this.client.post('/match-profile', profile);
    return response.data;
  }

  async getSimilarBandi(bandoId: number, limit: number = 5): Promise<SemanticSearchResult[]> {
    const response: AxiosResponse<SemanticSearchResult[]> = await this.client.get(`/similar/${bandoId}`, {
      params: { limit }
    });
    return response.data;
  }

  async getIntelligentSuggestions(params: {
    search_history?: string[];
    context?: string;
    limit?: number;
  }): Promise<string[]> {
    const searchHistory = params.search_history?.join(',') || '';
    const response: AxiosResponse<string[]> = await this.client.get('/suggestions', {
      params: {
        search_history: searchHistory,
        context: params.context,
        limit: params.limit
      }
    });
    return response.data;
  }

  async refreshEmbeddings(): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await this.client.post('/refresh-embeddings');
    return response.data;
  }

  async getStats(): Promise<{
    total_embeddings: number;
    last_update: string;
    model_name: string;
    cache_valid: boolean;
  }> {
    const response = await this.client.get('/stats');
    return response.data;
  }
}

export const aiService = new AISemanticSearchService();

// ISS Service - Calls real backend APIs
class ISSService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async searchCorsi(params?: any): Promise<{ items: any[], total: number }> {
    try {
      const response = await this.client.get('/corsi/', { params });
      return response.data;
    } catch (error) {
      console.warn('Error fetching corsi:', error);
      return { items: [], total: 0 };
    }
  }

  async searchEventi(params?: any): Promise<{ items: any[], total: number }> {
    try {
      const response = await this.client.get('/eventi/', { params });
      return response.data;
    } catch (error) {
      console.warn('Error fetching eventi:', error);
      return { items: [], total: 0 };
    }
  }

  async getProgetti(params?: any): Promise<{ items: any[], total: number }> {
    try {
      const response = await this.client.get('/progetti/', { params });
      return response.data;
    } catch (error) {
      console.warn('Error fetching progetti:', error);
      return { items: [], total: 0 };
    }
  }

  async getOpportunitaVolontariato(params?: any): Promise<{ items: any[], total: number }> {
    try {
      const response = await this.client.get('/volontariato/', { params });
      return response.data;
    } catch (error) {
      console.warn('Error fetching volontariato:', error);
      return { items: [], total: 0 };
    }
  }

  async searchNewspost(params?: any): Promise<{ items: any[], total: number }> {
    try {
      const response = await this.client.get('/news/', { params });
      return response.data;
    } catch (error) {
      console.warn('Error fetching news:', error);
      return { items: [], total: 0 };
    }
  }

  async getTestimonials(): Promise<any[]> {
    try {
      const response = await this.client.get('/testimonials/');
      return response.data.items || [];
    } catch (error) {
      console.warn('Error fetching testimonials:', error);
      return [];
    }
  }

  async getPartners(params?: any): Promise<{ partners: any[], total: number }> {
    try {
      const response = await this.client.get('/partners/', { params });
      return response.data;
    } catch (error) {
      console.warn('Error fetching partners:', error);
      return { partners: [], total: 0 };
    }
  }

  async getPartnerById(id: number): Promise<any> {
    const response = await this.client.get(`/partners/${id}`);
    return response.data;
  }

  async createPartner(data: any): Promise<any> {
    const response = await this.client.post('/partners/', data);
    return response.data;
  }

  async updatePartner(id: number, data: any): Promise<any> {
    const response = await this.client.put(`/partners/${id}`, data);
    return response.data;
  }

  async deletePartner(id: number): Promise<any> {
    const response = await this.client.delete(`/partners/${id}`);
    return response.data;
  }

  // Events CRUD
  async getEvents(params?: any): Promise<{ items: any[], total: number }> {
    const response = await this.client.get('/eventi/', { params });
    return response.data;
  }

  async createEvent(data: any): Promise<any> {
    const response = await this.client.post('/eventi/', data);
    return response.data;
  }

  async updateEvent(id: number, data: any): Promise<any> {
    const response = await this.client.put(`/eventi/${id}`, data);
    return response.data;
  }

  async deleteEvent(id: number): Promise<any> {
    const response = await this.client.delete(`/eventi/${id}`);
    return response.data;
  }

  // Volunteers CRUD
  async getVolunteerApplications(params?: any): Promise<any[]> {
    const response = await this.client.get('/volontariato/', { params });
    return response.data;
  }

  async updateVolunteerApplication(id: number, data: any): Promise<any> {
    const response = await this.client.put(`/volontariato/${id}`, data);
    return response.data;
  }

  // Stats
  async getAnalyticsKpi(): Promise<any> {
    const response = await this.client.get('/analytics/kpi');
    return response.data;
  }

  async getAnalyticsTrends(days?: number): Promise<any> {
    const response = await this.client.get('/analytics/trends', { params: { days } });
    return response.data;
  }
}

export const issService = new ISSService();

export const eventsAPI = {
  list: (params?: any) => issService.getEvents(params),
  create: (data: any) => issService.createEvent(data),
  update: (id: number, data: any) => issService.updateEvent(id, data),
  delete: (id: number) => issService.deleteEvent(id),
};

export const volunteerAPI = {
  list: (params?: any) => issService.getVolunteerApplications(params),
  update: (id: number, data: any) => issService.updateVolunteerApplication(id, data),
};

export const partnerAPI = {
  list: (params?: any) => issService.getPartners(params),
  get: (id: number) => issService.getPartnerById(id),
  create: (data: any) => issService.createPartner(data),
  update: (id: number, data: any) => issService.updatePartner(id, data),
  delete: (id: number) => issService.deletePartner(id),
};

export default apiClient;
