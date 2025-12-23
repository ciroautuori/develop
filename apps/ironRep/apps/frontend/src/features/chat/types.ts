/**
 * Chat Feature Types
 *
 * Centralized type definitions for chat functionality
 */

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  suggestedActions?: string[];
  relevantExercises?: string[];
  /** Indicates message is pending API response (optimistic UI) */
  isPending?: boolean;
  /** Indicates message send failed */
  isFailed?: boolean;
}

export type ChatMode = "chat" | "checkin" | "medical" | "workout" | "nutrition";

export interface ChatSession {
  id: string;
  mode: ChatMode;
  startedAt: Date;
  lastActivityAt: Date;
}

export interface AgentInfo {
  id: ChatMode;
  name: string;
  description: string;
  color: string;
  icon: string;
}
