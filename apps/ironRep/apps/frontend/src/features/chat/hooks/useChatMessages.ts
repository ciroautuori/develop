import { useState, useCallback } from "react";
import { logger } from '../../../lib/logger';
import type { Message, ChatConfig } from "../types";
import {
  createUserMessage,
  createAssistantMessage,
  createErrorMessage,
} from "../utils/messageFactory";

export function useChatMessages(config: ChatConfig, sessionId: string | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(
    async (content: string, onSessionUpdate?: (sessionId: string) => void) => {
      // Create user message
      const userMessage = createUserMessage(content);
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        // Call API
        const response = await config.api.endpoint(
          content,
          sessionId || undefined
        );

        // Update session if new
        if (response.session_id && !sessionId && onSessionUpdate) {
          onSessionUpdate(response.session_id);
        }

        // Create assistant message
        const assistantMessage = createAssistantMessage(response);
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (error) {
        logger.error('Failed to send message', { error });
        const errorMessage = createErrorMessage();
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [config, sessionId]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
  };
}
