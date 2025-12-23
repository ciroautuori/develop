/**
 * ToolAI Types - Landing & Backoffice
 */

export interface AITool {
  id: number;
  post_id: number;
  name: string;
  source: string | null;
  source_url: string | null;
  description_it: string;
  description_en: string | null;
  description_es: string | null;
  relevance_it: string | null;
  relevance_en: string | null;
  relevance_es: string | null;
  category: string | null;
  tags: string[];
  stars: number | null;
  downloads: number | null;
  trending_score: number | null;
  display_order: number;
  created_at: string;
}

export interface ToolAIPost {
  id: number;
  post_date: string;
  status: 'draft' | 'published' | 'scheduled' | 'archived';
  title_it: string;
  title_en: string | null;
  title_es: string | null;
  summary_it: string;
  summary_en: string | null;
  summary_es: string | null;
  content_it: string;
  content_en: string | null;
  content_es: string | null;
  insights_it: string | null;
  insights_en: string | null;
  insights_es: string | null;
  takeaway_it: string | null;
  takeaway_en: string | null;
  takeaway_es: string | null;
  meta_description: string | null;
  meta_keywords: string[];
  slug: string | null;
  image_url: string | null;
  ai_generated: boolean;
  ai_model: string | null;
  generation_time: number | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
  tools: AITool[];
}

export interface ToolAIPostListResponse {
  total: number;
  page: number;
  per_page: number;
  posts: ToolAIPost[];
}

export interface ToolAIStats {
  total_posts: number;
  published_posts: number;
  draft_posts: number;
  total_tools_discovered: number;
  recent_posts: {
    id: number;
    date: string;
    title: string;
    status: string;
  }[];
}

export interface GeneratePostRequest {
  target_date?: string;
  num_tools?: number;
  categories?: string[];
  auto_publish?: boolean;
  translate?: boolean;
  generate_image?: boolean;
}

export interface GeneratePostResponse {
  success: boolean;
  post_id: number | null;
  post: ToolAIPost | null;
  tools_discovered: number;
  generation_time_seconds: number;
  ai_model: string;
  message: string;
}

// Helper per ottenere campo tradotto
export function getLocalizedField<T extends ToolAIPost | AITool>(
  item: T,
  field: 'title' | 'summary' | 'content' | 'insights' | 'takeaway' | 'description' | 'relevance',
  lang: 'it' | 'en' | 'es'
): string {
  const key = `${field}_${lang}` as keyof T;
  const fallbackKey = `${field}_it` as keyof T;
  return (item[key] as string) || (item[fallbackKey] as string) || '';
}
