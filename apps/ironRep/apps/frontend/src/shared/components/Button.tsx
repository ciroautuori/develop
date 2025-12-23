import { forwardRef } from "react";
import { cn } from "../../lib/utils";
import { Loader2 } from "lucide-react";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger" | "outline";
  size?: "sm" | "md" | "lg";
  fullWidth?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "primary",
      size = "md",
      fullWidth,
      loading,
      icon,
      children,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        className={cn(
          // Base styles
          "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100",

          // Variant styles
          variant === "primary" &&
            "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm",
          variant === "secondary" &&
            "bg-secondary text-secondary-foreground hover:bg-secondary/80",
          variant === "ghost" && "hover:bg-accent hover:text-accent-foreground",
          variant === "danger" &&
            "bg-red-500 text-white hover:bg-red-600 shadow-sm",
          variant === "outline" &&
            "border border-border bg-background hover:bg-accent hover:text-accent-foreground",

          // Size styles (responsive)
          size === "sm" && "px-3 py-1.5 text-sm",
          size === "md" && "px-4 py-2 text-sm md:px-6 md:py-2.5 md:text-base",
          size === "lg" && "px-6 py-3 text-base md:px-8 md:py-4 md:text-lg",

          // Full width
          fullWidth && "w-full",

          className
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading && <Loader2 className="h-4 w-4 animate-spin" />}
        {!loading && icon && <span>{icon}</span>}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
