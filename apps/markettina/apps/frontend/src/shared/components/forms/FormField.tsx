/**
 * FormField Component - Input field with validation feedback.
 */

import { forwardRef, InputHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

interface FormFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  success?: boolean;
  hint?: string;
}

export const FormField = forwardRef<HTMLInputElement, FormFieldProps>(
  ({ label, error, success, hint, className, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="block text-sm font-medium text-gray-900 dark:text-white">
            {label}
            {props.required && <span className="text-gray-400 ml-1">*</span>}
          </label>
        )}
        
        <input
          ref={ref}
          className={cn(
            'w-full px-4 py-3 rounded-lg border transition-all duration-200',
            'bg-white dark:bg-[#0A0A0A]',
            'text-gray-900 dark:text-white',
            'placeholder:text-gray-400 dark:placeholder:text-gray-600',
            'focus:outline-none focus:ring-2 focus:ring-offset-2',
            error && 'border-gray-500 focus:ring-gray-500',
            success && 'border-gold focus:ring-gold',
            !error && !success && 'border-gray-300 dark:border-gray-700 focus:ring-gold',
            props.disabled && 'opacity-50 cursor-not-allowed',
            className
          )}
          {...props}
        />
        
        {error && (
          <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1">
            <span>❌</span>
            {error}
          </p>
        )}
        
        {success && !error && (
          <p className="text-sm text-gold dark:text-gold flex items-center gap-1">
            <span>✅</span>
            Valid
          </p>
        )}
        
        {hint && !error && (
          <p className="text-xs text-gray-500 dark:text-gray-400">{hint}</p>
        )}
      </div>
    );
  }
);

FormField.displayName = 'FormField';
