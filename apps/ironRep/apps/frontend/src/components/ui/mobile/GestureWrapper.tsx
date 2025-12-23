/**
 * GestureWrapper - Universal Gesture Handler
 *
 * Reusable wrapper for common mobile gestures:
 * - Swipe (left, right, up, down)
 * - Long press
 * - Double tap
 * - Haptic feedback integration
 *
 * Built on Framer Motion for performance and smoothness.
 *
 * @example
 * ```tsx
 * <GestureWrapper
 *   onSwipeLeft={() => console.log('Swiped left')}
 *   onLongPress={() => console.log('Long pressed')}
 *   hapticFeedback="medium"
 * >
 *   <YourComponent />
 * </GestureWrapper>
 * ```
 */

import * as React from "react";
import { motion, useMotionValue } from "framer-motion";
import type { PanInfo } from "framer-motion";
import { hapticFeedback } from "../../../lib/haptics";

export interface GestureWrapperProps {
  children: React.ReactNode;
  /** Swipe left callback */
  onSwipeLeft?: () => void;
  /** Swipe right callback */
  onSwipeRight?: () => void;
  /** Swipe up callback */
  onSwipeUp?: () => void;
  /** Swipe down callback */
  onSwipeDown?: () => void;
  /** Long press callback */
  onLongPress?: () => void;
  /** Double tap callback */
  onDoubleTap?: () => void;
  /** Haptic feedback intensity (triggers on gesture detection) */
  hapticFeedback?: "light" | "medium" | "heavy" | "none";
  /** Swipe threshold in pixels (default: 100) */
  swipeThreshold?: number;
  /** Long press duration in ms (default: 500) */
  longPressDuration?: number;
  /** Double tap max interval in ms (default: 300) */
  doubleTapInterval?: number;
  /** Enable/disable dragging */
  enableDrag?: boolean;
  /** Additional className */
  className?: string;
}

export function GestureWrapper({
  children,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  onLongPress,
  onDoubleTap,
  hapticFeedback: haptic = "light",
  swipeThreshold = 100,
  longPressDuration = 500,
  doubleTapInterval = 300,
  enableDrag = true,
  className,
}: GestureWrapperProps) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  // Long press state
  const longPressTimerRef = React.useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const isLongPressActive = React.useRef(false);

  // Double tap state
  const lastTapTimeRef = React.useRef(0);

  const handleDragEnd = (_: unknown, info: PanInfo) => {
    const { offset } = info;

    // Determine swipe direction
    const absX = Math.abs(offset.x);
    const absY = Math.abs(offset.y);

    // Check if swipe threshold is met
    if (absX > swipeThreshold || absY > swipeThreshold) {
      // Trigger haptic feedback
      if (haptic !== "none") {
        hapticFeedback.impact(haptic);
      }

      // Determine primary axis
      if (absX > absY) {
        // Horizontal swipe
        if (offset.x > 0 && onSwipeRight) {
          onSwipeRight();
        } else if (offset.x < 0 && onSwipeLeft) {
          onSwipeLeft();
        }
      } else {
        // Vertical swipe
        if (offset.y > 0 && onSwipeDown) {
          onSwipeDown();
        } else if (offset.y < 0 && onSwipeUp) {
          onSwipeUp();
        }
      }
    }

    // Reset position
    x.set(0);
    y.set(0);
  };

  const handleTapStart = () => {
    // Start long press timer
    if (onLongPress) {
      isLongPressActive.current = false;
      longPressTimerRef.current = setTimeout(() => {
        isLongPressActive.current = true;
        if (haptic !== "none") {
          hapticFeedback.impact("heavy"); // Heavy for long press
        }
        onLongPress();
      }, longPressDuration);
    }
  };

  const handleTapEnd = () => {
    // Clear long press timer
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
    }

    // Don't trigger tap if long press was activated
    if (isLongPressActive.current) {
      isLongPressActive.current = false;
      return;
    }
  };

  const handleTap = () => {
    if (!onDoubleTap) return;

    const now = Date.now();
    const timeSinceLastTap = now - lastTapTimeRef.current;

    if (timeSinceLastTap < doubleTapInterval && timeSinceLastTap > 0) {
      // Double tap detected
      if (haptic !== "none") {
        hapticFeedback.impact("medium");
      }
      onDoubleTap();
      lastTapTimeRef.current = 0; // Reset to prevent triple-tap
    } else {
      // First tap
      lastTapTimeRef.current = now;
    }
  };

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      if (longPressTimerRef.current) {
        clearTimeout(longPressTimerRef.current);
      }
    };
  }, []);

  return (
    <motion.div
      drag={enableDrag}
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      dragElastic={0}
      onDragEnd={handleDragEnd}
      onTapStart={handleTapStart}
      onTap={handleTap}
      onTapCancel={handleTapEnd}
      className={className}
      style={{ x, y }}
    >
      {children}
    </motion.div>
  );
}

export default GestureWrapper;
