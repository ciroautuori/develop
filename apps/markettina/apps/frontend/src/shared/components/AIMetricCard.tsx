/**
 * AIMetricCard - Reusable metric card for AI features
 * Unified component to eliminate duplication across AI pages
 * Migrated from legacy components/ directory
 */

import { memo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { TrendingUp, TrendingDown, type LucideIcon } from 'lucide-react';
import { cn } from '../lib/utils';

export interface AIMetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  status?: 'healthy' | 'warning' | 'error' | 'idle';
  subtitle?: string;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
  className?: string;
}

const statusColors = {
  healthy: 'border-l-gold bg-gold/10 dark:bg-gold/20',
  warning: 'border-l-gold bg-gold/10 dark:bg-gold/20',
  error: 'border-l-gray-500 bg-gray-50 dark:bg-gray-800',
  idle: 'border-l-gray-500 bg-gray-50 dark:bg-gray-950',
} as const;

const statusBadgeColors = {
  healthy: 'bg-gold/10 text-gold dark:bg-gold dark:text-gold',
  warning: 'bg-gold/10 text-gold dark:bg-gold/20 dark:text-gold',
  error: 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-300',
  idle: 'bg-gray-100 text-gray-800 dark:bg-[#0A0A0A] dark:text-gray-200',
} as const;

export const AIMetricCard = memo<AIMetricCardProps>(({
  title,
  value,
  icon: Icon,
  status = 'idle',
  subtitle,
  trend,
  className
}) => {
  return (
    <Card className={cn(
      'border-l-4 transition-all hover:shadow-lg',
      statusColors[status],
      className
    )}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {title}
          </CardTitle>
          <Icon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex items-baseline justify-between">
            <div className="text-3xl font-bold text-gray-900 dark:text-white">
              {value}
            </div>
            {status && (
              <Badge className={cn('text-xs', statusBadgeColors[status])}>
                {status}
              </Badge>
            )}
          </div>
          
          {subtitle && (
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {subtitle}
            </p>
          )}
          
          {trend && (
            <div className="flex items-center gap-1 text-sm">
              {trend.direction === 'up' ? (
                <TrendingUp className="w-4 h-4 text-gold" />
              ) : (
                <TrendingDown className="w-4 h-4 text-gray-400" />
              )}
              <span className={cn(
                'font-medium',
                trend.direction === 'up' ? 'text-gold' : 'text-gray-500'
              )}>
                {trend.value}%
              </span>
              <span className="text-gray-500">vs last period</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
});

AIMetricCard.displayName = 'AIMetricCard';
