import type React from "react";
import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { cn } from "../../../lib/utils";
import type { Message } from "../types";
import { Bot, User, Copy, Check } from "lucide-react";
import { GestureWrapper } from "../../../components/ui/mobile/GestureWrapper";
import { toast } from "../../../components/ui/Toast";
import { hapticFeedback } from "../../../lib/haptics";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const MAX_VISIBLE_MESSAGES = 12;
  const containerRef = useRef<HTMLDivElement>(null);
  const visibleMessages = messages.slice(-MAX_VISIBLE_MESSAGES);
  const isTruncated = messages.length > MAX_VISIBLE_MESSAGES;

  return (
    <div
      ref={containerRef}
      className="flex-1 min-h-0 overflow-hidden px-3 pt-1 pb-2 flex flex-col justify-end gap-2"
    >
      <div className="flex-1" />
      {isTruncated && (
        <div className="text-[11px] text-muted-foreground/70 bg-secondary/40 border border-border/40 rounded-xl px-3 py-2">
          Conversazione lunga: mostro gli ultimi {MAX_VISIBLE_MESSAGES} messaggi (NO SCROLL attivo).
        </div>
      )}

      {visibleMessages.map((message, index) => (
        <MessageBubble key={message.id} message={message} index={index} />
      ))}

      {/* Typing Indicator */}
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-card border border-border/50 rounded-2xl rounded-tl-sm px-3 py-2 shadow-sm">
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              <span className="text-[11px] text-muted-foreground">Sto pensando...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// MESSAGE BUBBLE with Gestures
// ============================================================================

interface MessageBubbleProps {
  message: Message;
  index: number;
}

function MessageBubble({ message, index }: MessageBubbleProps) {
  const [showCopyFeedback, setShowCopyFeedback] = useState(false);
  const isAssistant = message.role !== "user";

  const handleCopyMessage = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setShowCopyFeedback(true);
      hapticFeedback.notification('success');
      toast.success("Messaggio copiato!");
      setTimeout(() => setShowCopyFeedback(false), 2000);
    } catch (error) {
      toast.error("Impossibile copiare il messaggio");
    }
  };

  const handleShowContextMenu = () => {
    hapticFeedback.impact('medium');
    toast.info({
      title: "Menu contestuale",
      description: "Presto disponibili azioni: Modifica, Elimina, Condividi",
      duration: 2000,
    });
  };

  const handleSwipeAction = () => {
    if (message.role === "user") {
      toast.info("Modifica messaggio - in arrivo!");
    } else {
      handleCopyMessage();
    }
  };

  return (
    <div
      className="flex gap-2 max-w-full animate-bubble-in"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      <GestureWrapper
        onSwipeLeft={handleSwipeAction}
        onLongPress={handleShowContextMenu}
        hapticFeedback="light"
        className="w-full"
      >
        <div
          className={cn(
            "flex gap-2 max-w-full w-full",
            message.role === "user" ? "flex-row-reverse" : "flex-row"
          )}
        >
          {/* Avatar */}
          <div
            className={cn(
              "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
              message.role === "user"
                ? "bg-primary text-primary-foreground"
                : "bg-gradient-to-br from-primary/20 to-primary/10 border border-primary/20"
            )}
            aria-hidden="true"
          >
            {message.role === "user" ? (
              <User size={14} />
            ) : (
              <Bot size={14} className="text-primary" />
            )}
          </div>

          {/* Message Bubble */}
          <div
            className={cn(
              "rounded-2xl px-3 py-2 max-w-[84%] shadow-sm relative group",
              message.role === "user"
                ? "bg-primary text-primary-foreground rounded-tr-sm"
                : "bg-card border border-border/50 rounded-tl-sm"
            )}
            role="article"
            aria-label={`Messaggio ${message.role === "user" ? "utente" : "assistente"}`}
          >
            {/* Copy feedback */}
            {showCopyFeedback && (
              <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-green-500 text-white text-xs px-2 py-1 rounded-lg flex items-center gap-1 animate-in fade-in slide-in-from-bottom-2">
                <Check size={12} />
                Copiato!
              </div>
            )}

            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  p: ({ children }: { children?: React.ReactNode }) => (
                    <p
                      className={cn(
                        "mb-1 last:mb-0 text-[14px] leading-relaxed",
                        isAssistant &&
                          "overflow-hidden [display:-webkit-box] [-webkit-box-orient:vertical] [-webkit-line-clamp:6] md:overflow-visible md:[display:block] md:[-webkit-line-clamp:initial]"
                      )}
                    >
                      {children}
                    </p>
                  ),
                  strong: ({ children }: { children?: React.ReactNode }) => (
                    <strong className="font-semibold">{children}</strong>
                  ),
                  ul: ({ children }: { children?: React.ReactNode }) => (
                    <ul className="list-disc list-inside space-y-0.5 my-1.5 text-[14px]">
                      {children}
                    </ul>
                  ),
                  ol: ({ children }: { children?: React.ReactNode }) => (
                    <ol className="list-decimal list-inside space-y-0.5 my-1.5 text-[14px]">
                      {children}
                    </ol>
                  ),
                  li: ({ children }: { children?: React.ReactNode }) => (
                    <li
                      className={cn(
                        "text-[14px] leading-relaxed",
                        isAssistant &&
                          "overflow-hidden [display:-webkit-box] [-webkit-box-orient:vertical] [-webkit-line-clamp:6] md:overflow-visible md:[display:list-item] md:[-webkit-line-clamp:initial]"
                      )}
                    >
                      {children}
                    </li>
                  ),
                  code({ inline, className, children, ...props }: { inline?: boolean; className?: string; children?: React.ReactNode }) {
                    const match = /language-(\w+)/.exec(className || "");
                    return !inline && match ? (
                      <CodeBlock
                        language={match[1]}
                        code={String(children).replace(/\n$/, "")}
                      />
                    ) : (
                      <code
                        className="bg-secondary px-1.5 py-0.5 rounded text-sm font-mono"
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  },
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>

            {/* Timestamp */}
            <time
              className="text-[10px] opacity-40 mt-1 block"
              dateTime={message.timestamp.toISOString()}
            >
              {message.timestamp.toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </time>

            {/* Quick copy button (hover) */}
            <button
              onClick={handleCopyMessage}
              className="absolute -right-8 top-2 p-1.5 rounded-full bg-secondary border border-border opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity active:scale-90"
              aria-label="Copia messaggio"
            >
              {showCopyFeedback ? (
                <Check size={14} className="text-green-600" />
              ) : (
                <Copy size={14} className="text-muted-foreground" />
              )}
            </button>
          </div>
        </div>
      </GestureWrapper>
    </div>
  );
}

// ============================================================================
// CODE BLOCK with Copy Button
// ============================================================================

interface CodeBlockProps {
  language: string;
  code: string;
}

function CodeBlock({ language, code }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      hapticFeedback.notification('success');
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error("Impossibile copiare il codice");
    }
  };

  return (
    <div className="relative group my-2">
      {/* Language badge */}
      <div className="absolute top-2 left-2 z-10 flex items-center gap-2">
        <span className="text-[10px] font-mono bg-black/30 text-white px-2 py-1 rounded uppercase">
          {language}
        </span>
      </div>

      {/* Copy button */}
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 z-10 p-2 rounded-lg bg-black/30 hover:bg-black/50 transition-colors opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 active:scale-90"
        aria-label={copied ? "Codice copiato" : "Copia codice"}
      >
        {copied ? (
          <Check size={16} className="text-green-400" />
        ) : (
          <Copy size={16} className="text-white" />
        )}
      </button>

      <SyntaxHighlighter
        style={vscDarkPlus}
        language={language}
        PreTag="div"
        className="rounded-lg text-sm !mt-0"
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}
