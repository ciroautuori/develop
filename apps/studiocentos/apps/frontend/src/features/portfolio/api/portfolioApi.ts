/**
 * Portfolio API Client - Centralized API calls
 */

export interface Project {
  id: number;
  title: string;
  slug: string;
  description: string;
  year: number;
  category: string;
  live_url?: string;
  github_url?: string;
  image_url?: string;
  technologies: string[];
  featured: boolean;
  order?: number;
  created_at: string;
  updated_at: string;
}

export interface Service {
  id: number;
  title: string;
  slug: string;
  description: string;
  icon?: string;
  features: string[];
  price_from?: number;
  order?: number;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ContactFormData {
  name: string;
  email: string;
  company?: string;
  phone?: string;
  subject: string;
  message: string;
  service_interest?: string;
  budget_range?: string;
}

const API_BASE = '/api/v1/portfolio';

export class PortfolioApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'PortfolioApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new PortfolioApiError(
      errorData.detail || `API Error: ${response.statusText}`,
      response.status,
      errorData
    );
  }
  return response.json();
}

export const portfolioApi = {
  /**
   * Get all public projects
   */
  async getProjects(): Promise<{ projects: Project[] }> {
    const response = await fetch(`${API_BASE}/public/projects`);
    return handleResponse(response);
  },

  /**
   * Get featured projects only
   */
  async getFeaturedProjects(): Promise<{ projects: Project[] }> {
    const response = await fetch(`${API_BASE}/public/projects?featured=true`);
    return handleResponse(response);
  },

  /**
   * Get project by slug
   */
  async getProjectBySlug(slug: string): Promise<Project> {
    const response = await fetch(`${API_BASE}/public/projects/${slug}`);
    return handleResponse(response);
  },

  /**
   * Get all active services
   */
  async getServices(): Promise<{ services: Service[] }> {
    const response = await fetch(`${API_BASE}/public/services`);
    return handleResponse(response);
  },

  /**
   * Get featured services only
   */
  async getFeaturedServices(): Promise<{ services: Service[] }> {
    const response = await fetch(`${API_BASE}/public/services?featured=true`);
    return handleResponse(response);
  },

  /**
   * Submit contact form
   */
  async submitContact(data: ContactFormData): Promise<{ message: string; request_id: number }> {
    const response = await fetch(`${API_BASE}/public/contact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Get portfolio stats
   */
  async getStats(): Promise<{
    total_projects: number;
    total_services: number;
    years_experience: number;
    clients_served: number;
  }> {
    const response = await fetch(`${API_BASE}/public/stats`);
    return handleResponse(response);
  },
};
