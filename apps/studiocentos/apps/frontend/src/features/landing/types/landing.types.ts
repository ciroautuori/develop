/**
 * Landing Page Types
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
  demo_url?: string;
  technologies: string[];
  metrics: Record<string, string>;
  status: string;
  is_featured: boolean;
  is_public: boolean;
  order: number;
  thumbnail_url?: string;
  images: string[];
  created_at: string;
  updated_at?: string;
}

export interface Service {
  id: number;
  title: string;
  slug: string;
  description: string;
  icon: string;
  category: string;
  features: string[];
  value_indicator?: string;
  cta_text: string;
  cta_url?: string;
  is_active: boolean;
  order: number;
  thumbnail_url?: string;
  images?: string[];
}

export interface Course {
  id: number;
  title: string;
  slug: string;
  description: string;
  icon: string;
  module_number: number;
  purchase_url: string;
  preview_url?: string;
  duration_hours?: number;
  difficulty: string;
  topics: string[];
  price?: string;
  is_featured: boolean;
  is_new: boolean;
  thumbnail_url?: string;
  cover_image?: string;
}

export interface PortfolioStats {
  total_projects: number;
  total_services: number;
  years_experience: number;
  technologies: number;
}

export interface PortfolioData {
  projects: Project[];
  services: Service[];
  courses: Course[];
  stats: PortfolioStats;
}

export interface ContactFormData {
  name: string;
  email: string;
  company?: string;
  phone?: string;
  subject: string;
  message: string;
  request_type: string;
}

export interface ContactFormProps {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

