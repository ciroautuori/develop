import { cn } from "../../../lib/utils";
import type { ChatMetadata } from "../types";

interface ChatHeaderProps {
  config: ChatMetadata;
}

export function ChatHeader({ config }: ChatHeaderProps) {
  const Icon = config.icon;

  return (
    <div
      className={cn(
        "px-3 md:px-6 py-2 md:py-4 text-white shadow-sm md:shadow-lg transition-all",
        `bg-gradient-to-r ${config.gradient}`
      )}
    >
      <div className="flex items-center gap-3">
        <Icon className="w-5 h-5 md:w-8 md:h-8 shrink-0" />
        <div className="min-w-0 flex-1">
          <h1 className="text-base md:text-2xl font-bold leading-tight truncate">
            {config.title}
          </h1>
          <p className="text-xs md:text-sm opacity-90 mt-0.5 truncate">
            {config.subtitle}
          </p>
        </div>
      </div>
    </div>
  );
}
