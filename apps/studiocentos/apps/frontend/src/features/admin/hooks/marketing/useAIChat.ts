/**
 * useAIChat Hook
 * Manages AI chat conversation state
 */

import { useState } from 'react';
import { toast } from 'sonner';
import { AIChatService, ChatMessage } from '../../services/ai-chat.service';

export function useAIChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isChatting, setIsChatting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (content: string): Promise<string | null> => {
    setIsChatting(true);
    setError(null);

    // Add user message immediately
    const userMessage: ChatMessage = {
      role: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await AIChatService.sendMessage(content);

      // Add assistant message
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        provider: response.provider
      };
      setMessages(prev => [...prev, assistantMessage]);

      return response.response;
    } catch (err: any) {
      const errorMessage = err.message || 'Errore nella chat';
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setIsChatting(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return {
    messages,
    isChatting,
    error,
    sendMessage,
    clearChat
  };
}
