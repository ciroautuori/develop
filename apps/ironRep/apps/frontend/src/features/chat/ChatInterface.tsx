import { useEffect } from "react";
import { ChatMessages } from "./components/ChatMessages";
import { MessageInput } from "./components/MessageInput";
import { type OnCompleteData } from "../../lib/api";
import { QuickActions } from "./QuickActions";
import { Sparkles } from "lucide-react";
import { useChat } from "./hooks/useChat";
import type { ChatMode } from "./types";

export function ChatInterface({
  mode = "chat",
  onComplete,
}: {
  mode?: ChatMode;
  onComplete?: (data: OnCompleteData) => void;
} = {}) {
  const { messages, isLoading, sendMessage, initSession } = useChat({ mode, onComplete });

  // Initialize session on mount
  useEffect(() => {
    initSession();
  }, [initSession]);

  return (
    <div className="flex flex-col h-full min-h-0 bg-background overflow-hidden">
      {/* Messages Area - NO SCROLL (must fit viewport) */}
      <div className="flex-1 overflow-hidden px-3 py-2 flex flex-col gap-2">
        {/* Empty State / Quick Actions */}
        {messages.length <= 1 && !isLoading && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="bg-card border rounded-2xl p-2.5 shadow-sm">
              <h3 className="font-semibold text-sm mb-1.5 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary" />
                {mode === "workout" ? "Come posso aiutarti oggi?" :
                  mode === "medical" ? "Gestisci il tuo recupero" :
                    mode === "nutrition" ? "Ottimizza la tua alimentazione" :
                      "Suggerimenti"}
              </h3>
              <QuickActions onAction={sendMessage} mode={mode} />
            </div>
          </div>
        )}

        <ChatMessages messages={messages} isLoading={isLoading} />

      </div>

      {/* Input Area - Fixed at bottom */}
      <div className="shrink-0 px-3 py-1.5 bg-background border-t">
        <div className="bg-card border rounded-2xl shadow-sm overflow-hidden focus-within:ring-2 focus-within:ring-primary/20">
          <MessageInput onSend={sendMessage} disabled={isLoading} />
        </div>
        {/* Privacy notice - small text */}
        <p className="hidden md:block text-[10px] text-muted-foreground/60 text-center mt-2">
          🔒 HIPAA Compliant & Secure
        </p>
      </div>
    </div>
  );
}
