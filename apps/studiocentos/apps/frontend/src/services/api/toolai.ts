/**
 * ToolAI API Service
 * Gestione chiamate API per ToolAI posts
 */

import type {
  ToolAIPost,
  ToolAIPostListResponse,
  ToolAIStats,
  GeneratePostRequest,
  GeneratePostResponse,
} from '../../features/landing/types/toolai.types';

const API_BASE = '/api/v1/toolai';

// =============================================================================
// PUBLIC API (Landing Page)
// =============================================================================

/**
 * Fetch public published posts
 */
export async function fetchPublicPosts(
  page: number = 1,
  perPage: number = 10,
  lang: string = 'it'
): Promise<ToolAIPostListResponse> {
  const response = await fetch(
    `${API_BASE}/posts/public?page=${page}&per_page=${perPage}&lang=${lang}`
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch posts: ${response.status}`);
  }

  return response.json();
}

/**
 * Fetch latest published post
 */
export async function fetchLatestPost(lang: string = 'it'): Promise<ToolAIPost | null> {
  const response = await fetch(`${API_BASE}/posts/public/latest?lang=${lang}`);

  if (!response.ok) {
    if (response.status === 404) return null;
    throw new Error(`Failed to fetch latest post: ${response.status}`);
  }

  const data = await response.json();
  return data || null;
}

/**
 * Fetch post by slug
 */
export async function fetchPostBySlug(slug: string, lang: string = 'it'): Promise<ToolAIPost> {
  const response = await fetch(`${API_BASE}/posts/public/${slug}?lang=${lang}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch post: ${response.status}`);
  }

  return response.json();
}

// =============================================================================
// ADMIN API (Backoffice)
// =============================================================================

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('admin_token');
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };
}

/**
 * Fetch all posts (admin)
 */
export async function fetchAdminPosts(
  page: number = 1,
  perPage: number = 10,
  status?: string
): Promise<ToolAIPostListResponse> {
  let url = `${API_BASE}/posts?page=${page}&per_page=${perPage}`;
  if (status) url += `&status=${status}`;

  const response = await fetch(url, { headers: getAuthHeaders() });

  if (!response.ok) {
    throw new Error(`Failed to fetch posts: ${response.status}`);
  }

  return response.json();
}

/**
 * Fetch single post by ID (admin)
 */
export async function fetchAdminPost(postId: number): Promise<ToolAIPost> {
  const response = await fetch(`${API_BASE}/posts/${postId}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch post: ${response.status}`);
  }

  return response.json();
}

/**
 * Update post (admin)
 */
export async function updatePost(
  postId: number,
  data: Partial<ToolAIPost>
): Promise<ToolAIPost> {
  const response = await fetch(`${API_BASE}/posts/${postId}`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to update post: ${response.status}`);
  }

  return response.json();
}

/**
 * Delete post (admin)
 */
export async function deletePost(postId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/posts/${postId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Failed to delete post: ${response.status}`);
  }
}

/**
 * Publish post (admin)
 */
export async function publishPost(postId: number): Promise<ToolAIPost> {
  const response = await fetch(`${API_BASE}/posts/${postId}/publish`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Failed to publish post: ${response.status}`);
  }

  return response.json();
}

/**
 * Generate new post via AI (admin)
 */
export async function generatePost(
  request: GeneratePostRequest
): Promise<GeneratePostResponse> {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to generate post: ${error}`);
  }

  return response.json();
}

/**
 * Get ToolAI stats (admin)
 */
export async function fetchStats(): Promise<ToolAIStats> {
  const response = await fetch(`${API_BASE}/stats`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.status}`);
  }

  return response.json();
}
