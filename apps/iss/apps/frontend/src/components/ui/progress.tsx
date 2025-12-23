import React from 'react';
import { cn } from '@/utils/cn';

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number;
  max?: number;
  size?: 'sm' | 'default' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'error';
  showValue?: boolean;
  animated?: boolean;
  className?: string;
}

export const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({
    value = 0,
    max = 100,
    size = 'default',
    variant = 'default',
    showValue = false,
    animated = false,
    className,
    ...props
  }, ref) => {
    // Normalizza il valore tra 0 e 100
    const normalizedValue = Math.min(Math.max((value / max) * 100, 0), 100);
    
    const sizeClasses = {
      sm: 'h-2',
      default: 'h-3',
      lg: 'h-4',
    };

    const variantClasses = {
      default: 'bg-iss-bordeaux-600',
      success: 'bg-green-600',
      warning: 'bg-yellow-600',
      error: 'bg-red-600',
    };

    const textSizeClasses = {
      sm: 'text-xs',
      default: 'text-sm',
      lg: 'text-base',
    };

    return (
      <div
        ref={ref}
        className={cn('w-full', className)}
        {...props}
      >
        {/* Label con valore se richiesto */}
        {showValue && (
          <div className="flex justify-between items-center mb-2">
            <span className={cn('font-medium text-gray-700', textSizeClasses[size])}>
              Progresso
            </span>
            <span className={cn('font-medium text-gray-900', textSizeClasses[size])}>
              {Math.round(normalizedValue)}%
            </span>
          </div>
        )}
        
        {/* Barra di progresso */}
        <div
          className={cn(
            'w-full bg-gray-200 rounded-full overflow-hidden',
            sizeClasses[size]
          )}
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={max}
          aria-valuenow={value}
          aria-label={`Progresso: ${Math.round(normalizedValue)}%`}
        >
          <div
            className={cn(
              'h-full transition-all duration-300 ease-in-out rounded-full',
              variantClasses[variant],
              animated && [
                'relative overflow-hidden',
                'before:absolute before:inset-0',
                'before:bg-gradient-to-r before:from-transparent before:via-white/20 before:to-transparent',
                'before:animate-pulse',
              ]
            )}
            style={{ width: `${normalizedValue}%` }}
          >
            {/* Animazione strisce per caricamento */}
            {animated && (
              <div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-pulse"
                style={{
                  backgroundSize: '2rem 100%',
                  animation: 'progress-stripes 1s linear infinite',
                }}
              />
            )}
          </div>
        </div>
        
        {/* Testo accessibile per screen reader */}
        <span className="sr-only">
          Progresso: {value} di {max} ({Math.round(normalizedValue)}% completato)
        </span>
      </div>
    );
  }
);

Progress.displayName = 'Progress';

// Variante circolare per casi specifici
export interface CircularProgressProps {
  value?: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  variant?: 'default' | 'success' | 'warning' | 'error';
  showValue?: boolean;
  className?: string;
}

export const CircularProgress: React.FC<CircularProgressProps> = ({
  value = 0,
  max = 100,
  size = 120,
  strokeWidth = 8,
  variant = 'default',
  showValue = false,
  className
}) => {
  const normalizedValue = Math.min(Math.max((value / max) * 100, 0), 100);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (normalizedValue / 100) * circumference;

  const variantColors = {
    default: '#7a2426', // iss-bordeaux-600
    success: '#059669', // green-600
    warning: '#d97706', // yellow-600
    error: '#dc2626',   // red-600
  };

  return (
    <div
      className={cn('relative inline-flex items-center justify-center', className)}
      style={{ width: size, height: size }}
    >
      <svg
        className="transform -rotate-90"
        width={size}
        height={size}
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={max}
        aria-valuenow={value}
        aria-label={`Progresso circolare: ${Math.round(normalizedValue)}%`}
      >
        {/* Cerchio di sfondo */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        
        {/* Cerchio di progresso */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={variantColors[variant]}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-300 ease-in-out"
        />
      </svg>
      
      {/* Valore centrale */}
      {showValue && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-semibold text-gray-900">
            {Math.round(normalizedValue)}%
          </span>
        </div>
      )}
    </div>
  );
};
