/**
 * TourTooltip - Tooltip elegante per tour steps
 * Design enterprise con progress indicator e navigazione
 */

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronRight, ChevronLeft, X, Sparkles } from 'lucide-react';
import { cn } from '../../../lib/utils';
import type { TourStep } from '../hooks/useTour';

interface TourTooltipProps {
  step: TourStep;
  currentIndex: number;
  totalSteps: number;
  onNext: () => void;
  onPrev: () => void;
  onSkip: () => void;
}

interface TooltipPosition {
  top?: number;
  bottom?: number;
  left?: number;
  right?: number;
  transform?: string;
}

export function TourTooltip({
  step,
  currentIndex,
  totalSteps,
  onNext,
  onPrev,
  onSkip,
}: TourTooltipProps) {
  const [position, setPosition] = useState<TooltipPosition>({});
  const isFirst = currentIndex === 0;
  const isLast = currentIndex === totalSteps - 1;
  const isCentered = step.position === 'center' || !step.targetId;

  // Calculate position based on target
  useEffect(() => {
    if (isCentered || !step.targetId) {
      setPosition({});
      return;
    }

    const element = document.querySelector(`[data-tour-id="${step.targetId}"]`);
    if (!element) return;

    const rect = element.getBoundingClientRect();
    const tooltipWidth = 320;
    const tooltipHeight = 200;
    const offset = 16;

    let pos: TooltipPosition = {};

    switch (step.position) {
      case 'top':
        pos = {
          top: rect.top + window.scrollY - tooltipHeight - offset,
          left: rect.left + rect.width / 2 - tooltipWidth / 2,
        };
        break;
      case 'bottom':
        pos = {
          top: rect.bottom + window.scrollY + offset,
          left: rect.left + rect.width / 2 - tooltipWidth / 2,
        };
        break;
      case 'left':
        pos = {
          top: rect.top + window.scrollY + rect.height / 2 - tooltipHeight / 2,
          left: rect.left - tooltipWidth - offset,
        };
        break;
      case 'right':
        pos = {
          top: rect.top + window.scrollY + rect.height / 2 - tooltipHeight / 2,
          left: rect.right + offset,
        };
        break;
    }

    // Clamp to viewport
    if (pos.left !== undefined) {
      pos.left = Math.max(16, Math.min(window.innerWidth - tooltipWidth - 16, pos.left));
    }
    if (pos.top !== undefined) {
      pos.top = Math.max(16, pos.top);
    }

    setPosition(pos);
  }, [step, isCentered]);

  const containerClass = isCentered
    ? "fixed inset-0 flex items-center justify-center p-4"
    : "fixed z-[10000]";

  return (
    <div className={containerClass} style={!isCentered ? { ...position } : {}}>
      <motion.div
        initial={{ opacity: 0, y: 10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 10, scale: 0.95 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        className={cn(
          "bg-card border border-border rounded-2xl shadow-2xl overflow-hidden",
          isCentered ? "max-w-md w-full" : "w-80"
        )}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-primary/10 via-primary/5 to-transparent px-5 py-4 border-b border-border">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-primary" />
              </div>
              <div>
                <h3 className="font-bold text-foreground text-lg leading-tight">
                  {step.title}
                </h3>
                <span className="text-xs text-muted-foreground">
                  Step {currentIndex + 1} di {totalSteps}
                </span>
              </div>
            </div>
            <button
              onClick={onSkip}
              className="p-1.5 rounded-full hover:bg-accent transition-colors"
              aria-label="Chiudi tour"
            >
              <X className="w-4 h-4 text-muted-foreground" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="px-5 py-4">
          <p className="text-foreground/80 text-sm leading-relaxed">
            {step.description}
          </p>
        </div>

        {/* Progress bar */}
        <div className="px-5 pb-2">
          <div className="h-1 bg-muted rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-primary rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${((currentIndex + 1) / totalSteps) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-border bg-muted/30 flex items-center justify-between">
          <button
            onClick={onSkip}
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Salta tour
          </button>

          <div className="flex items-center gap-2">
            {!isFirst && (
              <button
                onClick={onPrev}
                className="flex items-center gap-1 px-3 py-2 rounded-lg hover:bg-accent transition-colors text-sm font-medium"
              >
                <ChevronLeft className="w-4 h-4" />
                Indietro
              </button>
            )}
            <button
              onClick={onNext}
              className={cn(
                "flex items-center gap-1 px-4 py-2 rounded-lg font-medium text-sm transition-all",
                isLast
                  ? "bg-primary text-primary-foreground hover:bg-primary/90"
                  : "bg-primary text-primary-foreground hover:bg-primary/90"
              )}
            >
              {isLast ? 'Inizia!' : 'Avanti'}
              {!isLast && <ChevronRight className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
