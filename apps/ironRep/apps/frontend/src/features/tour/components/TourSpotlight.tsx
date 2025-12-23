/**
 * TourSpotlight - Overlay che evidenzia un elemento target
 * Stile Google con animazioni Framer Motion
 */

import type React from "react";
import { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../../../lib/utils';

interface SpotlightRect {
  top: number;
  left: number;
  width: number;
  height: number;
}

interface TourSpotlightProps {
  targetId: string | null;
  isActive: boolean;
  padding?: number;
  borderRadius?: number;
  children: React.ReactNode;
}

export function TourSpotlight({
  targetId,
  isActive,
  padding = 8,
  borderRadius = 16,
  children,
}: TourSpotlightProps) {
  const [rect, setRect] = useState<SpotlightRect | null>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  // Find and track target element
  useEffect(() => {
    if (!isActive || !targetId) {
      setRect(null);
      return;
    }

    const updateRect = () => {
      const element = document.querySelector(`[data-tour-id="${targetId}"]`);
      if (element) {
        const bounds = element.getBoundingClientRect();
        setRect({
          top: bounds.top - padding,
          left: bounds.left - padding,
          width: bounds.width + padding * 2,
          height: bounds.height + padding * 2,
        });
      }
    };

    updateRect();

    // Update on resize
    window.addEventListener('resize', updateRect);

    return () => {
      window.removeEventListener('resize', updateRect);
    };
  }, [targetId, isActive, padding]);

  if (!isActive) return null;

  // Fullscreen mode (no target)
  if (!targetId) {
    return (
      <AnimatePresence>
        <motion.div
          ref={overlayRef}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[9999] flex items-center justify-center"
        >
          {/* Dark overlay */}
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

          {/* Content */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="relative z-10"
          >
            {children}
          </motion.div>
        </motion.div>
      </AnimatePresence>
    );
  }

  // Spotlight mode (with target)
  return (
    <AnimatePresence>
      <motion.div
        ref={overlayRef}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[9999] pointer-events-none"
      >
        {/* SVG overlay with cutout */}
        <svg className="absolute inset-0 w-full h-full pointer-events-auto">
          <defs>
            <mask id="spotlight-mask">
              <rect x="0" y="0" width="100%" height="100%" fill="white" />
              {rect && (
                <motion.rect
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  x={rect.left}
                  y={rect.top}
                  width={rect.width}
                  height={rect.height}
                  rx={borderRadius}
                  fill="black"
                />
              )}
            </mask>
          </defs>
          <rect
            x="0"
            y="0"
            width="100%"
            height="100%"
            fill="rgba(0, 0, 0, 0.75)"
            mask="url(#spotlight-mask)"
          />
        </svg>

        {/* Highlight ring around target */}
        {rect && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className={cn(
              "absolute pointer-events-none",
              "ring-4 ring-primary ring-offset-2 ring-offset-transparent"
            )}
            style={{
              top: rect.top,
              left: rect.left,
              width: rect.width,
              height: rect.height,
              borderRadius: borderRadius,
            }}
          />
        )}

        {/* Tooltip content */}
        <div className="pointer-events-auto">
          {children}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
