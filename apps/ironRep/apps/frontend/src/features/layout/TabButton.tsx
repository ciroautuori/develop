import { cn } from "../../lib/utils";
import type { TabButtonProps } from "./types";

/**
 * TabButton - Mobile-first tab navigation button
 *
 * Touch target: 44px minimum height (iOS HIG)
 * Haptic feedback on tap
 */
export function TabButton({ active, onClick, icon: Icon, label }: TabButtonProps) {
  const handleClick = () => {
    if ('vibrate' in navigator) {
      navigator.vibrate(5);
    }
    onClick();
  };

  return (
    <button
      onClick={handleClick}
      className={cn(
        "flex flex-1 flex-col items-center justify-center",
        "min-h-[44px] min-w-[64px] px-2.5 py-1.5",
        "transition-colors select-none touch-manipulation",
        "border-b-2 -mb-[2px]",
        active
          ? "border-primary text-primary"
          : "border-transparent text-muted-foreground active:text-foreground",
      )}
      role="tab"
      aria-selected={active}
      id={`tab-${label.toLowerCase().replace(/\s+/g, '-')}`}
    >
      <Icon size={18} strokeWidth={active ? 2.5 : 2} className="shrink-0" />
      <span className={cn(
        "mt-0.5 text-[10px] whitespace-nowrap leading-tight",
        active ? "font-semibold" : "font-medium"
      )}>
        {label}
      </span>
    </button>
  );
}
