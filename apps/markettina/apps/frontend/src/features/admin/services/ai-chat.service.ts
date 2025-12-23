/**
 * AI Chat Service
 * Marketing chatbot integration
 */

import { toast } from 'sonner';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  provider?: string;
}

export interface ChatResponse {
  response: string;
  provider: string;
}

function getAuthToken(): string {
  const token = localStorage.getItem('admin_token');
  if (!token) throw new Error('Authentication required');
  return token;
}

async function handleApiResponse<T>(response: Response, context: string): Promise<T> {
  if (!response.ok) {
    const error = await response.text();
    console.error(`[ChatAPI] ${context} failed:`, error);
    toast.error(`Errore: ${context}`);
    throw new Error(`${context}: ${response.status}`);
  }

  return response.json();
}

export class AIChatService {
  private static readonly BASE_URL = '/api/v1';

  static async sendMessage(message: string, context?: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.BASE_URL}/copilot/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({
          message,
          context: context || 'marketing',
          conversation_id: null
        })
      });

      return handleApiResponse<ChatResponse>(response, 'AI chat');
    } catch (error) {
      console.error('[ChatAPI] sendMessage error:', error);
      throw error;
    }
  }
}
