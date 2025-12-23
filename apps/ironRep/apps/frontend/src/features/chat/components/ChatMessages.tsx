import { MessageList } from "./MessageList";
import type { Message } from "../types";

interface ChatMessagesProps {
  messages: Message[];
  isLoading: boolean;
}

export function ChatMessages({ messages, isLoading }: ChatMessagesProps) {
  return <MessageList messages={messages} isLoading={isLoading} />;
}
