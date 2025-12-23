import { format } from "date-fns";
import { it } from "date-fns/locale";
import { cn } from "../../../lib/utils";
import type { Message } from "../types";
import { User, Bot } from "lucide-react";

interface MessageBubbleProps {
  message: Message;
}

/**
 * MessageBubble - Mobile-first chat message component
 *
 * Optimized for 70% mobile usage with:
 * - Proper touch spacing
 * - Mobile-first typography
 * - Readable font sizes
 */
export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 animate-in fade-in slide-in-from-bottom-1 duration-200",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar - Mobile optimized */}
      <div
        className={cn(
          "shrink-0 w-9 h-9 rounded-full flex items-center justify-center shadow-sm",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-card border text-muted-foreground"
        )}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      {/* Message Content */}
      <div
        className={cn(
          "flex-1 flex flex-col gap-2 max-w-[calc(100%-4rem)]", // Space for avatar + gap
          isUser ? "items-end" : "items-start"
        )}
      >
        <div
          className={cn(
            "px-4 py-3 rounded-2xl shadow-sm",
            // Mobile-first text size (16px base to prevent iOS zoom)
            "text-[16px] leading-relaxed",
            isUser
              ? "bg-primary text-primary-foreground rounded-br-md"
              : "bg-card border text-foreground rounded-bl-md"
          )}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>

        {/* Timestamp */}
        <p
          className={cn(
            "text-xs text-muted-foreground/70 px-2",
            isUser ? "text-right" : "text-left"
          )}
        >
          {format(message.timestamp, "HH:mm", { locale: it })}
        </p>

        {/* Suggested Actions - Touch optimized */}
        {message.suggestedActions && message.suggestedActions.length > 0 && (
          <div className="flex gap-2 mt-2 overflow-x-auto no-scrollbar">
            {message.suggestedActions.map((action, index) => (
              <button
                key={index}
                className="px-4 py-2 min-h-[36px] text-sm font-medium rounded-xl bg-primary/10 text-primary border border-primary/20 transition-colors active:scale-[0.98] touch-manipulation"
              >
                {action}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
