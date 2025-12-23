import type { Message } from "../types";

/** Response structure from agent chat APIs */
interface ChatResponse {
  answer?: string;
  message?: string;
  suggested_actions?: string[];
  relevant_exercises?: string[];
}

export function createUserMessage(content: string): Message {
  return {
    id: `user-${Date.now()}`,
    role: "user",
    content,
    timestamp: new Date(),
  };
}

export function createAssistantMessage(response: ChatResponse): Message {
  return {
    id: `assistant-${Date.now()}`,
    role: "assistant",
    content: response.answer || response.message || "Risposta ricevuta.",
    timestamp: new Date(),
    suggestedActions: response.suggested_actions || [],
    relevantExercises: response.relevant_exercises || [],
  };
}

export function createErrorMessage(errorText?: string): Message {
  return {
    id: `error-${Date.now()}`,
    role: "assistant",
    content: errorText || "Mi dispiace, c'è stato un errore. Riprova.",
    timestamp: new Date(),
  };
}
