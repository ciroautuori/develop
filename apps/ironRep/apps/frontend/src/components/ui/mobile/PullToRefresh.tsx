/**
 * PullToRefresh - Native-like Pull-to-Refresh
 *
 * iOS/Android style pull-to-refresh component with:
 * - Visual indicator with spinner + text
 * - Configurable threshold
 * - Haptic feedback on trigger
 * - Smooth spring animations
 * - Works with any scrollable container
 *
 * @example
 * ```tsx
 * <PullToRefresh
 *   onRefresh={async () => {
 *     await refetchData();
 *   }}
 * >
 *   <YourScrollableContent />
 * </PullToRefresh>
 * ```
 */

import * as React from "react";
import { motion, useMotionValue, useTransform } from "framer-motion";
import { Loader2, ChevronDown } from "lucide-react";
import { cn } from "../../../lib/utils";
import { hapticFeedback } from "../../../lib/haptics";

export interface PullToRefreshProps {
  children: React.ReactNode;
  /** Refresh callback - should return a Promise */
  onRefresh: () => Promise<void>;
  /** Pull threshold in pixels (default: 80) */
  threshold?: number;
  /** Disabled state */
  disabled?: boolean;
  /** Custom className for wrapper */
  className?: string;
  /** Custom loading text */
  loadingText?: string;
  /** Custom pull text */
  pullText?: string;
  /** Custom release text */
  releaseText?: string;
}

type RefreshState = "idle" | "pulling" | "ready" | "refreshing";

export function PullToRefresh({
  children,
  onRefresh,
  threshold = 80,
  disabled = false,
  className,
  loadingText = "Aggiornamento...",
  pullText = "Trascina per aggiornare",
  releaseText = "Rilascia per aggiornare",
}: PullToRefreshProps) {
  const [state, setState] = React.useState<RefreshState>("idle");
  const containerRef = React.useRef<HTMLDivElement>(null);
  const pullDistance = useMotionValue(0);

  // Transform pull distance to indicator height (capped at threshold * 1.5)
  const indicatorHeight = useTransform(
    pullDistance,
    [0, threshold, threshold * 1.5],
    [0, threshold, threshold * 1.2]
  );

  // Transform pull distance to indicator opacity
  const indicatorOpacity = useTransform(
    pullDistance,
    [0, threshold * 0.3, threshold],
    [0, 0.5, 1]
  );

  // Transform pull distance to rotation for arrow
  const arrowRotation = useTransform(
    pullDistance,
    [0, threshold],
    [0, 180]
  );

  const handleTouchStart = React.useCallback((e: TouchEvent) => {
    if (disabled || state === "refreshing") return;

    const container = containerRef.current;
    if (!container) return;

    // Only trigger if scrolled to top
    if (container.scrollTop === 0) {
      setState("pulling");
    }
  }, [disabled, state]);

  const handleTouchMove = React.useCallback((e: TouchEvent) => {
    if (disabled || state !== "pulling") return;

    const container = containerRef.current;
    if (!container || container.scrollTop > 0) {
      setState("idle");
      return;
    }

    const touch = e.touches[0];
    const startY = touch.clientY;

    const move = (moveEvent: TouchEvent) => {
      const currentTouch = moveEvent.touches[0];
      const deltaY = currentTouch.clientY - startY;

      if (deltaY > 0) {
        // User is pulling down
        e.preventDefault();

        // Apply rubber-band effect
        const distance = Math.min(deltaY * 0.5, threshold * 1.5);
        pullDistance.set(distance);

        // Update state based on distance
        if (distance >= threshold && state === "pulling") {
          setState("ready");
          hapticFeedback.impact("medium");
        } else if (distance < threshold && state === "ready") {
          setState("pulling");
        }
      }
    };

    const end = async () => {
      document.removeEventListener("touchmove", move);
      document.removeEventListener("touchend", end);

      const currentDistance = pullDistance.get();

      if (currentDistance >= threshold) {
        // Trigger refresh
        setState("refreshing");
        hapticFeedback.impact("heavy");

        try {
          await onRefresh();
        } catch (error) {
          console.error("[PullToRefresh] Refresh failed:", error);
        }

        setState("idle");
      } else {
        setState("idle");
      }

      // Animate back to 0
      pullDistance.set(0);
    };

    document.addEventListener("touchmove", move, { passive: false });
    document.addEventListener("touchend", end);
  }, [disabled, state, threshold, pullDistance, onRefresh]);

  React.useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener("touchstart", handleTouchStart);
    container.addEventListener("touchmove", handleTouchMove, { passive: false });

    return () => {
      container.removeEventListener("touchstart", handleTouchStart);
      container.removeEventListener("touchmove", handleTouchMove);
    };
  }, [handleTouchStart, handleTouchMove]);

  const getIndicatorContent = () => {
    if (state === "refreshing") {
      return (
        <>
          <Loader2 className="w-5 h-5 animate-spin text-primary" />
          <span className="text-sm font-medium text-foreground">{loadingText}</span>
        </>
      );
    }

    if (state === "ready") {
      return (
        <>
          <motion.div style={{ rotate: arrowRotation }}>
            <ChevronDown className="w-5 h-5 text-primary" />
          </motion.div>
          <span className="text-sm font-medium text-primary">{releaseText}</span>
        </>
      );
    }

    return (
      <>
        <motion.div style={{ rotate: arrowRotation }}>
          <ChevronDown className="w-5 h-5 text-muted-foreground" />
        </motion.div>
        <span className="text-sm font-medium text-muted-foreground">{pullText}</span>
      </>
    );
  };

  return (
    <div className={cn("relative h-full overflow-hidden", className)}>
      {/* Pull Indicator */}
      <motion.div
        style={{
          height: indicatorHeight,
          opacity: indicatorOpacity,
        }}
        className="absolute top-0 left-0 right-0 flex items-center justify-center gap-2 bg-background/80 backdrop-blur-sm border-b z-10 overflow-hidden"
      >
        {getIndicatorContent()}
      </motion.div>

      {/* Scrollable Content */}
      <div
        ref={containerRef}
        className="h-full overflow-hidden"
      >
        {children}
      </div>
    </div>
  );
}

export default PullToRefresh;
