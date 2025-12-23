import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { cn } from "../../../lib/utils";
import { VoiceInput } from "../VoiceInput";
import { toast } from "sonner";
import { hapticFeedback } from "../../../lib/haptics";

interface MessageInputProps {
  onSend: (content: string) => void;
  disabled?: boolean;
}

export function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [content, setContent] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleVoiceTranscript = (transcript: string) => {
    // Append voice transcript to current content
    setContent((prev) => (prev ? `${prev} ${transcript}` : transcript));

    // Haptic feedback for mobile
    hapticFeedback.notification("success");

    toast.success("Capito!", { duration: 1500 });
  };

  const handleVoiceError = (error: string) => {
    // Haptic feedback for error
    hapticFeedback.notification("error");
    toast.error(error);
  };

  const adjustHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  };

  useEffect(() => {
    adjustHeight();
  }, [content]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (!content.trim() || disabled) return;
    hapticFeedback.impact("medium");
    onSend(content);
    setContent("");
  };

  return (
    <div className="p-2">
      <div className="w-full">
        {/* Input Row */}
        <div className="flex items-end gap-1.5">
          {/* Text Input */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Scrivi un messaggio..."
              disabled={disabled}
              className="w-full min-h-[44px] max-h-[120px] rounded-2xl border-0 bg-secondary/50 px-3 py-2.5 text-[16px] leading-relaxed placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:bg-secondary disabled:opacity-50 resize-none transition-all"
              rows={1}
              style={{ fontSize: '16px' }} /* Prevent iOS zoom */
            />
          </div>

          {/* Voice Button */}
          <div className="shrink-0">
            <VoiceInput
              onTranscript={handleVoiceTranscript}
              onError={handleVoiceError}
            />
          </div>

          {/* Send Button */}
          <button
            onClick={handleSubmit}
            disabled={!content.trim() || disabled}
            className={cn(
              "shrink-0 h-11 w-11 flex items-center justify-center rounded-full",
              "bg-primary text-primary-foreground shadow-lg shadow-primary/25",
              "active:scale-95 transition-all duration-150",
              "disabled:opacity-40 disabled:shadow-none disabled:cursor-not-allowed",
              "haptic-btn touch-target"
            )}
          >
            <Send size={18} className={cn(
              "transition-transform",
              content.trim() && "translate-x-0.5"
            )} />
          </button>
        </div>

        {/* Hint text - smaller on mobile */}
        <p className="text-center text-[10px] text-muted-foreground/50 mt-2 hidden sm:block">
          Invio per inviare • Shift+Invio per nuova riga
        </p>
      </div>
    </div>
  );
}
