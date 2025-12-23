/**
 * Skeleton Component - Loading placeholders with shimmer effect.
 */

import { cn } from '../../lib/utils';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
}

export function Skeleton({
  className,
  variant = 'rectangular',
  width,
  height,
  animation = 'wave'
}: SkeletonProps) {
  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  };

  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'relative overflow-hidden before:absolute before:inset-0 before:-translate-x-full before:bg-gradient-to-r before:from-transparent before:via-white/20 before:to-transparent before:animate-shimmer',
    none: '',
  };

  return (
    <div
      className={cn(
        'bg-gray-200 dark:bg-gray-800',
        variantClasses[variant],
        animationClasses[animation],
        className
      )}
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
      }}
    />
  );
}

// Pre-built skeleton components

export function SkeletonText({ lines = 3, className }: { lines?: number; className?: string }) {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          variant="text"
          width={i === lines - 1 ? '70%' : '100%'}
        />
      ))}
    </div>
  );
}

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn('p-6 space-y-4 bg-white dark:bg-[#0A0A0A] rounded-xl border border-gray-200 dark:border-gray-800', className)}>
      <Skeleton variant="rectangular" height={200} />
      <Skeleton variant="text" width="60%" />
      <SkeletonText lines={2} />
      <div className="flex gap-2">
        <Skeleton variant="rectangular" width={80} height={32} />
        <Skeleton variant="rectangular" width={80} height={32} />
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={`header-${i}`} variant="text" height={40} />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={`row-${rowIndex}`}
          className="grid gap-4"
          style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={`cell-${rowIndex}-${colIndex}`} variant="text" height={60} />
          ))}
        </div>
      ))}
    </div>
  );
}

export function SkeletonAvatar({ size = 40 }: { size?: number }) {
  return <Skeleton variant="circular" width={size} height={size} />;
}

export function SkeletonProject() {
  return (
    <div className="grid md:grid-cols-2 gap-12 items-center">
      <div className="space-y-6">
        <Skeleton variant="text" width="30%" height={20} />
        <Skeleton variant="text" width="80%" height={40} />
        <SkeletonText lines={3} />
        <div className="flex gap-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} variant="rectangular" width={80} height={32} />
          ))}
        </div>
      </div>
      <Skeleton variant="rectangular" height={400} />
    </div>
  );
}

export function SkeletonService() {
  return (
    <div className="p-8 space-y-6 bg-white dark:bg-[#0A0A0A] rounded-2xl border border-gray-200 dark:border-gray-800">
      <div className="flex items-start gap-4">
        <Skeleton variant="rectangular" width={60} height={60} />
        <div className="flex-1 space-y-3">
          <Skeleton variant="text" width="60%" height={28} />
          <SkeletonText lines={2} />
        </div>
      </div>
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} variant="text" height={24} />
        ))}
      </div>
      <Skeleton variant="rectangular" width={120} height={40} />
    </div>
  );
}

export function SkeletonDashboardCard() {
  return (
    <div className="p-6 space-y-4 bg-white dark:bg-[#0A0A0A] rounded-xl border border-gray-200 dark:border-gray-800">
      <div className="flex items-center justify-between">
        <Skeleton variant="text" width={100} height={20} />
        <Skeleton variant="circular" width={40} height={40} />
      </div>
      <Skeleton variant="text" width={60} height={36} />
      <Skeleton variant="text" width="80%" height={16} />
    </div>
  );
}
