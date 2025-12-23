import { useState, useCallback } from "react";
import {
  medicalApi,
  workoutCoachApi,
  nutritionApi,
  type OnCompleteData,
} from "../../../lib/api";
import { hapticFeedback } from "../../../lib/haptics";
import { logger } from "../../../lib/logger";
import type { Message, ChatMode } from "../types";

interface UseChatOptions {
  mode: ChatMode;
  onComplete?: (data: OnCompleteData) => void;
}

export function useChat({ mode, onComplete }: UseChatOptions) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const addMessage = useCallback((message: Message) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  const replaceMessage = useCallback((oldId: string, newMessage: Message) => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === oldId ? newMessage : msg))
    );
  }, []);

  const markMessageAsFailed = useCallback((messageId: string) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId
          ? { ...msg, isPending: false, isFailed: true }
          : msg
      )
    );
  }, []);

  const initSession = useCallback(async () => {
    // If messages already exist, don't re-init
    if (messages.length > 0) return;

    if (mode === "checkin") {
      try {
        setIsLoading(true);
        const data = await medicalApi.startCheckin();
        if (data.success) {
          setSessionId(data.session_id);
          addMessage({
            id: "init-medical",
            role: "assistant",
            content: data.message,
            timestamp: new Date(),
          });
          hapticFeedback.notification("success");
        }
      } catch (error) {
        logger.error("Failed to start medical conversation", { error });
        addMessage({
          id: "error-init",
          role: "assistant",
          content: "Errore nell'avvio della conversazione medica. Riprova.",
          timestamp: new Date(),
        });
      } finally {
        setIsLoading(false);
      }
    } else if (mode === "medical") {
      addMessage({
        id: "init-medical",
        role: "assistant",
        content: "Ciao! Sono il tuo AI Doctor. Dimmi cosa senti e da quanto tempo: ti aiuto a capire come gestire il recupero.",
        timestamp: new Date(),
      });
    } else if (mode === "workout") {
      addMessage({
        id: "init-workout",
        role: "assistant",
        content: "Ciao! Sono il tuo Workout Coach. Come posso aiutarti con gli allenamenti oggi?",
        timestamp: new Date(),
      });
    } else if (mode === "nutrition") {
      addMessage({
        id: "init-nutrition",
        role: "assistant",
        content: "Ciao! Sono il tuo Nutrizionista Sportivo. Parliamo di dieta, macro o integrazione?",
        timestamp: new Date(),
      });
    }
  }, [mode, messages.length, addMessage]);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    const tempId = `temp-${Date.now()}`;

    // OPTIMISTIC UI: Add user message immediately
    const userMessage: Message = {
      id: tempId,
      role: "user",
      content,
      timestamp: new Date(),
      isPending: true, // Mark as optimistic
    };

    addMessage(userMessage);
    setIsLoading(true);
    hapticFeedback.impact("light");

    try {
      let responseMessage = "Non ho capito, puoi ripetere?";
      let suggestedActions: string[] | undefined;
      let newSessionId = sessionId;

      if (mode === "checkin" && sessionId) {
        const data = await medicalApi.sendCheckinMessage(sessionId, content);
        responseMessage = data.message || responseMessage;
        if (data.completed && onComplete) {
          onComplete(data);
        }
      } else if (mode === "medical") {
        const response = await medicalApi.ask(content, sessionId || undefined);
        responseMessage = response.answer || responseMessage;
        newSessionId = response.session_id;
        suggestedActions = response.suggested_actions;
      } else if (mode === "workout") {
        const response = await workoutCoachApi.ask(content, sessionId || undefined);
        responseMessage = response.answer || responseMessage;
        newSessionId = response.session_id;
        suggestedActions = response.suggested_actions;
      } else if (mode === "nutrition") {
        const response = await nutritionApi.ask(content, sessionId || undefined);
        responseMessage = response.answer || responseMessage;
        newSessionId = response.session_id;
      }

      if (newSessionId && newSessionId !== sessionId) {
        setSessionId(newSessionId);
      }

      // OPTIMISTIC UI: Replace temp message with confirmed one
      const confirmedUserMessage: Message = {
        ...userMessage,
        id: `msg-${Date.now()}`,
        isPending: false,
      };
      replaceMessage(tempId, confirmedUserMessage);

      // Add assistant response
      addMessage({
        id: `msg-${Date.now() + 1}`,
        role: "assistant",
        content: responseMessage,
        timestamp: new Date(),
        suggestedActions,
      });
      hapticFeedback.notification("success");

    } catch (error) {
      logger.error("Chat error", { error });

      // OPTIMISTIC UI: Mark message as failed
      markMessageAsFailed(tempId);

      // Add error message
      addMessage({
        id: `error-${Date.now()}`,
        role: "assistant",
        content: "Problema di connessione. Riprova per favore.",
        timestamp: new Date(),
      });
      hapticFeedback.notification("error");
    } finally {
      setIsLoading(false);
    }
  }, [mode, sessionId, addMessage, replaceMessage, markMessageAsFailed, onComplete]);

  return {
    messages,
    isLoading,
    sendMessage,
    initSession,
  };
}
