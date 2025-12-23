import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "../../../lib/utils";

export interface TouchInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const TouchInput = forwardRef<HTMLInputElement, TouchInputProps>(
  ({ className, label, type, ...props }, ref) => {
    return (
      <div className="space-y-1">
        {label && (
          <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
            {label}
          </label>
        )}
        <input
          type={type}
          className={cn(
            "flex h-12 w-full rounded-md border border-input bg-background px-3 py-2 text-lg ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 touch-manipulation",
            className
          )}
          ref={ref}
          {...props}
        />
      </div>
    );
  }
);
TouchInput.displayName = "TouchInput";
