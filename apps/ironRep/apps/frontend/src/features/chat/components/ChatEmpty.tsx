import { cn } from "../../../lib/utils";
import type { LucideIcon } from "lucide-react";
import { hapticFeedback } from "../../../lib/haptics";

const COLOR_STYLES: Record<
  string,
  { iconBg: string; iconText: string; border: string; borderHover: string }
> = {
  primary: {
    iconBg: "bg-primary/10",
    iconText: "text-primary",
    border: "border-primary/20",
    borderHover: "hover:border-primary/40",
  },
  red: {
    iconBg: "bg-red-500/10",
    iconText: "text-red-500",
    border: "border-red-500/20",
    borderHover: "hover:border-red-500/40",
  },
  blue: {
    iconBg: "bg-blue-500/10",
    iconText: "text-blue-500",
    border: "border-blue-500/20",
    borderHover: "hover:border-blue-500/40",
  },
  green: {
    iconBg: "bg-green-500/10",
    iconText: "text-green-500",
    border: "border-green-500/20",
    borderHover: "hover:border-green-500/40",
  },
  orange: {
    iconBg: "bg-orange-500/10",
    iconText: "text-orange-500",
    border: "border-orange-500/20",
    borderHover: "hover:border-orange-500/40",
  },
  amber: {
    iconBg: "bg-amber-500/10",
    iconText: "text-amber-500",
    border: "border-amber-500/20",
    borderHover: "hover:border-amber-500/40",
  },
  violet: {
    iconBg: "bg-violet-500/10",
    iconText: "text-violet-500",
    border: "border-violet-500/20",
    borderHover: "hover:border-violet-500/40",
  },
};

interface ChatEmptyProps {
  icon: LucideIcon;
  title: string;
  subtitle: string;
  suggestions: string[];
  onSuggestionClick: (suggestion: string) => void;
  color?: string;
}

export function ChatEmpty({
  icon: Icon,
  title,
  subtitle,
  suggestions,
  onSuggestionClick,
  color = "primary",
}: ChatEmptyProps) {
  const styles = COLOR_STYLES[color] ?? COLOR_STYLES.primary;

  return (
    <div className="h-full flex flex-col items-center justify-center px-4 py-4 md:p-8 overflow-hidden gap-4 md:gap-6">
      {/* Icon - Larger and colored */}
      <div className={cn("p-5 md:p-8 rounded-full", styles.iconBg)}>
        <Icon className={cn("w-16 h-16 md:w-24 md:h-24", styles.iconText)} strokeWidth={1.5} />
      </div>

      {/* Title & Subtitle */}
      <div className="text-center flex flex-col gap-2 max-w-md">
        <h3 className="font-bold text-xl md:text-3xl">
          Benvenuto al {title}
        </h3>
        <p className="text-sm md:text-lg text-muted-foreground leading-relaxed">
          {subtitle}
        </p>
      </div>

      {/* Suggested Questions */}
      <div className="w-full max-w-2xl flex flex-col gap-3">
        <p className="text-[11px] md:text-base text-muted-foreground text-center font-semibold">
          💬 Domande suggerite
        </p>
        <div className="flex gap-3 overflow-x-auto no-scrollbar md:grid md:grid-cols-2 md:overflow-visible">
          {suggestions.map((question, index) => (
            <button
              key={index}
              onClick={() => {
                hapticFeedback.selection();
                onSuggestionClick(question);
              }}
              className={cn(
                "shrink-0 md:shrink px-3 py-2 md:p-5 text-left text-[12px] md:text-base rounded-full md:rounded-xl border-2",
                "bg-card hover:bg-accent/50 transition-all duration-200",
                "active:scale-95 touch-manipulation min-h-[44px]",
                styles.border,
                styles.borderHover,
                "hover:shadow-md"
              )}
            >
              {question}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
