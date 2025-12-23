import { motion, useAnimation, type PanInfo } from "framer-motion";
import type { ReactNode } from "react";
import { hapticFeedback } from "../../../lib/haptics";

interface SwipeableCardProps {
  children: ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  className?: string;
}

export function SwipeableCard({
  children,
  onSwipeLeft,
  onSwipeRight,
  className,
}: SwipeableCardProps) {
  const controls = useAnimation();

  const handleDragEnd = async (
    _: MouseEvent | TouchEvent | PointerEvent,
    info: PanInfo
  ) => {
    const threshold = 100;
    const velocity = 0.2;

    if (info.offset.x < -threshold || info.velocity.x < -velocity) {
      if (onSwipeLeft) {
        hapticFeedback.impact("light");
        await controls.start({
          x: -500,
          opacity: 0,
          transition: { duration: 0.2 },
        });
        onSwipeLeft();
        controls.set({ x: 0, opacity: 1 });
      } else {
        controls.start({ x: 0 });
      }
    } else if (info.offset.x > threshold || info.velocity.x > velocity) {
      if (onSwipeRight) {
        hapticFeedback.impact("light");
        await controls.start({
          x: 500,
          opacity: 0,
          transition: { duration: 0.2 },
        });
        onSwipeRight();
        controls.set({ x: 0, opacity: 1 });
      } else {
        controls.start({ x: 0 });
      }
    } else {
      controls.start({ x: 0 });
    }
  };

  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.7}
      onDragEnd={handleDragEnd}
      animate={controls}
      className={`bg-card border border-border rounded-xl shadow-sm touch-pan-y ${className}`}
      whileTap={{ scale: 0.98 }}
    >
      {children}
    </motion.div>
  );
}
