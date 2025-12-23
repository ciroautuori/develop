/**
 * Toast System - Healthcare Focused
 *
 * Production-ready toast notifications with:
 * - Healthcare-specific variants (medical, success, error, warning, info)
 * - Swipe-to-dismiss gesture
 * - Auto-dismiss with configurable duration
 * - Action buttons inline
 * - Stack management (max 3 visible)
 * - Accessibility (ARIA live regions)
 *
 * @example
 * ```tsx
 * import { toast } from '@/components/ui/Toast';
 *
 * // Simple toast
 * toast.success("Workout completato!");
 *
 * // With description and action
 * toast.error({
 *   title: "Errore di connessione",
 *   description: "Riprova tra qualche istante",
 *   action: { label: "Riprova", onClick: retry }
 * });
 * ```
 */

import * as React from "react";
import { X, CheckCircle2, AlertCircle, AlertTriangle, Info, Activity } from "lucide-react";
import { motion, useMotionValue, useTransform } from "framer-motion";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";

export type ToastVariant = "success" | "error" | "warning" | "info" | "medical";

export interface ToastAction {
  label: string;
  onClick: () => void;
}

export interface ToastOptions {
  title: string;
  description?: string;
  variant?: ToastVariant;
  duration?: number; // milliseconds, 0 = no auto-dismiss
  action?: ToastAction;
  id?: string;
}

export interface Toast extends Required<Omit<ToastOptions, 'action' | 'description'>> {
  description?: string;
  action?: ToastAction;
}

// Toast state management
let toastCounter = 0;
const listeners = new Set<(toasts: Toast[]) => void>();
let toasts: Toast[] = [];

function notifyListeners() {
  listeners.forEach((listener) => listener([...toasts]));
}

/**
 * Main toast API
 */
export const toast = {
  success: (options: string | Omit<ToastOptions, 'variant'>) => {
    return addToast({
      ...(typeof options === 'string' ? { title: options } : options),
      variant: 'success'
    });
  },

  error: (options: string | Omit<ToastOptions, 'variant'>) => {
    return addToast({
      ...(typeof options === 'string' ? { title: options } : options),
      variant: 'error'
    });
  },

  warning: (options: string | Omit<ToastOptions, 'variant'>) => {
    return addToast({
      ...(typeof options === 'string' ? { title: options } : options),
      variant: 'warning'
    });
  },

  info: (options: string | Omit<ToastOptions, 'variant'>) => {
    return addToast({
      ...(typeof options === 'string' ? { title: options } : options),
      variant: 'info'
    });
  },

  medical: (options: string | Omit<ToastOptions, 'variant'>) => {
    return addToast({
      ...(typeof options === 'string' ? { title: options } : options),
      variant: 'medical'
    });
  },

  dismiss: (id: string) => {
    toasts = toasts.filter((t) => t.id !== id);
    notifyListeners();
  },

  dismissAll: () => {
    toasts = [];
    notifyListeners();
  },
};

function addToast(options: ToastOptions): string {
  const id = options.id || `toast-${++toastCounter}`;
  const duration = options.duration ?? 5000;
  const variant = options.variant ?? 'info';

  const newToast: Toast = {
    id,
    title: options.title,
    description: options.description,
    variant,
    duration,
    action: options.action,
  };

  // Stack management: keep max 3 toasts
  if (toasts.length >= 3) {
    toasts.shift();
  }

  toasts.push(newToast);
  notifyListeners();

  // Auto-dismiss
  if (duration > 0) {
    setTimeout(() => {
      toast.dismiss(id);
    }, duration);
  }

  // Haptic feedback based on variant
  switch (variant) {
    case 'success':
      hapticFeedback.notification('success');
      break;
    case 'error':
    case 'medical':
      hapticFeedback.notification('error');
      break;
    case 'warning':
      hapticFeedback.notification('warning');
      break;
  }

  return id;
}

/**
 * Hook to access toasts
 */
export function useToasts() {
  const [state, setState] = React.useState<Toast[]>(toasts);

  React.useEffect(() => {
    listeners.add(setState);
    return () => {
      listeners.delete(setState);
    };
  }, []);

  return state;
}

/**
 * Toast Icon Component
 */
function ToastIcon({ variant }: { variant: ToastVariant }) {
  const iconClass = "w-5 h-5 shrink-0";

  switch (variant) {
    case 'success':
      return <CheckCircle2 className={cn(iconClass, "text-green-600")} />;
    case 'error':
      return <AlertCircle className={cn(iconClass, "text-red-600")} />;
    case 'warning':
      return <AlertTriangle className={cn(iconClass, "text-yellow-600")} />;
    case 'medical':
      return <Activity className={cn(iconClass, "text-red-600")} />;
    case 'info':
    default:
      return <Info className={cn(iconClass, "text-blue-600")} />;
  }
}

/**
 * Individual Toast Component
 */
function ToastItem({ toast: item }: { toast: Toast }) {
  const x = useMotionValue(0);
  const opacity = useTransform(x, [-200, 0, 200], [0, 1, 0]);

  function handleDragEnd(_: unknown, info: { offset: { x: number } }) {
    if (Math.abs(info.offset.x) > 100) {
      // Swipe threshold reached
      hapticFeedback.impact('light');
      toast.dismiss(item.id);
    }
  }

  const variantStyles = {
    success: "bg-green-50 border-green-200 dark:bg-green-950/20 dark:border-green-800",
    error: "bg-red-50 border-red-200 dark:bg-red-950/20 dark:border-red-800",
    warning: "bg-yellow-50 border-yellow-200 dark:bg-yellow-950/20 dark:border-yellow-800",
    info: "bg-blue-50 border-blue-200 dark:bg-blue-950/20 dark:border-blue-800",
    medical: "bg-red-50 border-red-300 dark:bg-red-950/30 dark:border-red-700",
  };

  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={handleDragEnd}
      style={{ x, opacity }}
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, x: 100, scale: 0.9 }}
      transition={{ type: "spring", duration: 0.3 }}
      className={cn(
        "relative flex items-start gap-3 p-4 rounded-xl border shadow-lg backdrop-blur-sm pointer-events-auto touch-pan-y",
        variantStyles[item.variant]
      )}
      role="alert"
      aria-live={item.variant === 'error' ? 'assertive' : 'polite'}
    >
      {/* Icon */}
      <ToastIcon variant={item.variant} />

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className="font-semibold text-sm text-foreground leading-tight">
          {item.title}
        </p>
        {item.description && (
          <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
            {item.description}
          </p>
        )}
        {item.action && (
          <button
            onClick={() => {
              item.action?.onClick();
              toast.dismiss(item.id);
            }}
            className="mt-2 text-xs font-medium text-primary hover:underline active:scale-95 transition-transform"
          >
            {item.action.label}
          </button>
        )}
      </div>

      {/* Close Button */}
      <button
        onClick={() => toast.dismiss(item.id)}
        className="shrink-0 p-1 rounded-full hover:bg-black/5 dark:hover:bg-white/10 transition-colors active:scale-90"
        aria-label="Chiudi notifica"
      >
        <X className="w-4 h-4 text-muted-foreground" />
      </button>
    </motion.div>
  );
}

/**
 * Toast Container - renders all toasts
 */
export function Toaster() {
  const toastList = useToasts();

  return (
    <div
      className="fixed top-0 left-0 right-0 z-50 flex flex-col gap-2 p-4 pointer-events-none safe-area-top"
      aria-live="polite"
      aria-atomic="false"
    >
      {toastList.map((item) => (
        <ToastItem key={item.id} toast={item} />
      ))}
    </div>
  );
}

export default toast;
