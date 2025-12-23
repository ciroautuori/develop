/**
 * useStreamingChat Hook
 *
 * Hook for consuming SSE streaming responses from AI agents.
 */
import { useState, useCallback, useRef } from 'react';
import { authToken } from "../lib/authToken";
import { getApiUrl } from "../config/api.config";

export interface StreamEvent {
  type: 'agent_start' | 'start' | 'token' | 'end' | 'agent_end' | 'error';
  content?: string;
  agent?: string;
  provider?: string;
  model?: string;
  message?: string;
  fatal?: boolean;
  timestamp?: string;
  full_response?: string;
}

export interface StreamingMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isStreaming: boolean;
  agent?: string;
  provider?: string;
  timestamp: Date;
}

export interface UseStreamingChatOptions {
  onStart?: (agent: string) => void;
  onToken?: (token: string) => void;
  onEnd?: (fullResponse: string) => void;
  onError?: (error: string) => void;
}

export function useStreamingChat(options: UseStreamingChatOptions = {}) {
  const [messages, setMessages] = useState<StreamingMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const currentMessageIdRef = useRef<string | null>(null);

  const sendMessage = useCallback(async (
    question: string,
    mode: 'medical' | 'workout' | 'nutrition' | 'chat' = 'chat',
    sessionId?: string
  ) => {
    // Abort any existing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    setError(null);
    setIsStreaming(true);

    // Add user message
    const userMessageId = `user-${Date.now()}`;
    const userMessage: StreamingMessage = {
      id: userMessageId,
      role: 'user',
      content: question,
      isStreaming: false,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    // Add placeholder for assistant message
    const assistantMessageId = `assistant-${Date.now()}`;
    currentMessageIdRef.current = assistantMessageId;
    const assistantMessage: StreamingMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      isStreaming: true,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, assistantMessage]);

    // Build URL
    const baseUrl = "";
    const params = new URLSearchParams({
      question,
      mode,
      ...(sessionId && { session_id: sessionId }),
    });
    const url = getApiUrl(`/stream/chat?${params.toString()}`);

    try {
      abortControllerRef.current = new AbortController();

      // Get token from storage
      const token = authToken.get();

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'text/event-stream',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process SSE events
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6);
            try {
              const event: StreamEvent = JSON.parse(jsonStr);

              switch (event.type) {
                case 'agent_start':
                  setCurrentAgent(event.agent || null);
                  options.onStart?.(event.agent || '');
                  break;

                case 'start':
                  // Update provider info
                  setMessages(prev => prev.map(msg =>
                    msg.id === currentMessageIdRef.current
                      ? { ...msg, provider: event.provider }
                      : msg
                  ));
                  break;

                case 'token':
                  if (event.content) {
                    options.onToken?.(event.content);
                    setMessages(prev => prev.map(msg =>
                      msg.id === currentMessageIdRef.current
                        ? { ...msg, content: msg.content + event.content }
                        : msg
                    ));
                  }
                  break;

                case 'end':
                  options.onEnd?.(event.full_response || '');
                  break;

                case 'agent_end':
                  setMessages(prev => prev.map(msg =>
                    msg.id === currentMessageIdRef.current
                      ? { ...msg, isStreaming: false, agent: event.agent }
                      : msg
                  ));
                  break;

                case 'error':
                  if (event.fatal) {
                    setError(event.message || 'Unknown error');
                    options.onError?.(event.message || 'Unknown error');
                  }
                  break;
              }
            } catch (e) {
              console.error('Error parsing SSE event:', e);
            }
          }
        }
      }

    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        // Request was aborted, not an error
        return;
      }

      const errorMessage = (err as Error).message;
      setError(errorMessage);
      options.onError?.(errorMessage);

      // Update assistant message with error
      setMessages(prev => prev.map(msg =>
        msg.id === currentMessageIdRef.current
          ? {
              ...msg,
              content: `❌ Errore: ${errorMessage}`,
              isStreaming: false
            }
          : msg
      ));
    } finally {
      setIsStreaming(false);
      currentMessageIdRef.current = null;
      abortControllerRef.current = null;
    }
  }, [options]);

  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isStreaming,
    error,
    currentAgent,
    sendMessage,
    stopStreaming,
    clearMessages,
  };
}

export default useStreamingChat;
