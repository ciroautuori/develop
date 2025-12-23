/**
 * Brand DNA Context API
 * Fetches the AI-formatted Brand DNA from the backend.
 */

export interface BrandContextResponse {
  context: string | null;
  brand_name: string | null;
  tone: string | null;
  colors: {
    primary: string | null;
    secondary: string | null;
    accent: string | null;
  };
}

export const BrandContextAPI = {
  async getContext(): Promise<string | null> {
    try {
      const token = localStorage.getItem('admin_token');
      if (!token) return null;

      const res = await fetch('/api/v1/marketing/brand-dna/ai-context', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!res.ok) {
        console.warn('Failed to fetch Brand DNA context');
        return null;
      }

      const data: BrandContextResponse = await res.json();
      return data.context;
    } catch (error) {
      console.error('Error fetching Brand DNA context:', error);
      return null;
    }
  }
};
