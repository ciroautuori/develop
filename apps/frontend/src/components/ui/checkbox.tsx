import React, { forwardRef } from 'react';
import { cn } from '@/utils/cn';
import { Check, Minus } from 'lucide-react';

export interface CheckboxProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange'> {
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  indeterminate?: boolean;
  className?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, checked, onCheckedChange, indeterminate = false, disabled, ...props }, ref) => {
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      onCheckedChange?.(event.target.checked);
    };

    return (
      <div className="relative inline-flex items-center">
        <input
          type="checkbox"
          ref={ref}
          checked={checked}
          onChange={handleChange}
          disabled={disabled}
          className="sr-only"
          {...props}
        />
        <div
          className={cn(
            'flex h-5 w-5 items-center justify-center rounded border-2 transition-all duration-150',
            'focus-within:ring-2 focus-within:ring-iss-bordeaux-500 focus-within:ring-offset-2',
            // Stati normali
            !checked && !indeterminate && [
              'border-gray-300 bg-white',
              'hover:border-gray-400',
              disabled && 'border-gray-200 bg-gray-50 cursor-not-allowed',
            ],
            // Stato checked
            checked && [
              'border-iss-bordeaux-600 bg-iss-bordeaux-600',
              'hover:border-iss-bordeaux-700 hover:bg-iss-bordeaux-700',
              disabled && 'border-iss-bordeaux-300 bg-iss-bordeaux-300 cursor-not-allowed',
            ],
            // Stato indeterminate
            indeterminate && [
              'border-iss-bordeaux-600 bg-iss-bordeaux-600',
              'hover:border-iss-bordeaux-700 hover:bg-iss-bordeaux-700',
              disabled && 'border-iss-bordeaux-300 bg-iss-bordeaux-300 cursor-not-allowed',
            ],
            className
          )}
          role="checkbox"
          aria-checked={indeterminate ? 'mixed' : checked}
          aria-disabled={disabled}
          tabIndex={disabled ? -1 : 0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              if (!disabled) {
                onCheckedChange?.(!checked);
              }
            }
          }}
        >
          {checked && !indeterminate && (
            <Check
              className={cn(
                'h-3 w-3 text-white transition-opacity duration-150',
                disabled ? 'opacity-70' : 'opacity-100'
              )}
              aria-hidden="true"
            />
          )}
          {indeterminate && (
            <Minus
              className={cn(
                'h-3 w-3 text-white transition-opacity duration-150',
                disabled ? 'opacity-70' : 'opacity-100'
              )}
              aria-hidden="true"
            />
          )}
        </div>
      </div>
    );
  }
);

Checkbox.displayName = 'Checkbox';
