import { forwardRef } from "react";
import { cn } from "../../lib/utils";

/**
 * MobileInput - Mobile-first input component
 *
 * Ensures:
 * - 16px font size to prevent iOS zoom
 * - 48px minimum height for touch targets
 * - Consistent styling across forms
 */

interface MobileInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  containerClassName?: string;
}

export const MobileInput = forwardRef<HTMLInputElement, MobileInputProps>(
  ({ label, error, containerClassName, className, ...props }, ref) => {
    return (
      <div className={cn("space-y-2", containerClassName)}>
        {label && (
          <label
            htmlFor={props.id}
            className="text-base font-medium block"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={cn(
            "w-full min-h-[48px] px-4 py-3 text-[16px] bg-secondary/50 border rounded-xl",
            "focus:ring-2 focus:ring-primary/20 focus:outline-none focus:border-primary",
            "disabled:opacity-50 transition-all placeholder:text-muted-foreground",
            error && "border-destructive focus:ring-destructive/20",
            className
          )}
          {...props}
        />
        {error && (
          <p className="text-sm text-destructive">{error}</p>
        )}
      </div>
    );
  }
);

MobileInput.displayName = "MobileInput";

/**
 * MobileTextarea - Mobile-first textarea component
 */
interface MobileTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  containerClassName?: string;
}

export const MobileTextarea = forwardRef<HTMLTextAreaElement, MobileTextareaProps>(
  ({ label, error, containerClassName, className, ...props }, ref) => {
    return (
      <div className={cn("space-y-2", containerClassName)}>
        {label && (
          <label
            htmlFor={props.id}
            className="text-base font-medium block"
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          className={cn(
            "w-full min-h-[100px] px-4 py-3 text-[16px] bg-secondary/50 border rounded-xl resize-none",
            "focus:ring-2 focus:ring-primary/20 focus:outline-none focus:border-primary",
            "disabled:opacity-50 transition-all placeholder:text-muted-foreground",
            error && "border-destructive focus:ring-destructive/20",
            className
          )}
          {...props}
        />
        {error && (
          <p className="text-sm text-destructive">{error}</p>
        )}
      </div>
    );
  }
);

MobileTextarea.displayName = "MobileTextarea";

/**
 * MobileButton - Mobile-first button component
 */
interface MobileButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "destructive";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const MobileButton = forwardRef<HTMLButtonElement, MobileButtonProps>(
  ({ variant = "primary", size = "md", isLoading, children, className, ...props }, ref) => {
    const sizeClasses = {
      sm: "h-10 px-3 text-sm",
      md: "h-12 px-4 text-base",
      lg: "h-14 px-6 text-lg",
    };

    const variantClasses = {
      primary: "bg-primary text-primary-foreground",
      secondary: "bg-secondary text-secondary-foreground",
      destructive: "bg-destructive text-destructive-foreground",
    };

    return (
      <button
        ref={ref}
        className={cn(
          "w-full flex items-center justify-center font-semibold rounded-xl",
          "transition-transform active:scale-[0.98] touch-manipulation",
          "disabled:opacity-50 disabled:pointer-events-none shadow-lg",
          sizeClasses[size],
          variantClasses[variant],
          className
        )}
        disabled={isLoading || props.disabled}
        {...props}
      >
        {children}
      </button>
    );
  }
);

MobileButton.displayName = "MobileButton";
