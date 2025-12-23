/**
 * TokenBalance Component
 * Displays customer's current token balance with visual indicator
 */

import { motion } from 'framer-motion';
import { Coins, TrendingUp, AlertCircle, Sparkles } from 'lucide-react';
import { cn } from '../../../shared/lib/utils';

interface TokenBalanceProps {
  balance: number;
  used: number;
  total: number;
  planName?: string;
  expiresAt?: string;
  compact?: boolean;
  className?: string;
}

export function TokenBalance({
  balance,
  used,
  total,
  planName = 'Growth',
  expiresAt,
  compact = false,
  className,
}: TokenBalanceProps) {
  const usagePercent = total > 0 ? (used / total) * 100 : 0;
  const remainingPercent = 100 - usagePercent;

  // Status colors based on remaining balance
  const getStatusColor = () => {
    if (remainingPercent > 50) return 'text-green-500';
    if (remainingPercent > 20) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getProgressColor = () => {
    if (remainingPercent > 50) return 'bg-green-500';
    if (remainingPercent > 20) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (compact) {
    return (
      <div className={cn('flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary/10', className)}>
        <Coins className="h-4 w-4 text-primary" />
        <span className="font-semibold text-foreground">{balance.toLocaleString()}</span>
        <span className="text-xs text-muted-foreground">token</span>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'bg-card border border-border rounded-2xl p-6 shadow-sm',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-primary/10">
            <Coins className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h3 className="font-semibold text-foreground">Saldo Token</h3>
            <p className="text-sm text-muted-foreground">Piano {planName}</p>
          </div>
        </div>

        {balance < 100 && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-yellow-500/10 text-yellow-600">
            <AlertCircle className="h-3.5 w-3.5" />
            <span className="text-xs font-medium">Ricarica</span>
          </div>
        )}
      </div>

      {/* Balance Display */}
      <div className="mb-6">
        <div className="flex items-end gap-2">
          <span className={cn('text-4xl font-bold', getStatusColor())}>
            {balance.toLocaleString()}
          </span>
          <span className="text-lg text-muted-foreground mb-1">token disponibili</span>
        </div>

        {expiresAt && (
          <p className="text-sm text-muted-foreground mt-1">
            Validi fino al {new Date(expiresAt).toLocaleDateString('it-IT')}
          </p>
        )}
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Consumo</span>
          <span className="font-medium text-foreground">
            {used.toLocaleString()} / {total.toLocaleString()}
          </span>
        </div>

        <div className="h-3 rounded-full bg-muted overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${usagePercent}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className={cn('h-full rounded-full', getProgressColor())}
          />
        </div>

        <div className="flex justify-between text-xs text-muted-foreground">
          <span>{usagePercent.toFixed(0)}% usato</span>
          <span>{remainingPercent.toFixed(0)}% rimanente</span>
        </div>
      </div>

      {/* Quick Action */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full mt-6 py-3 px-4 rounded-xl bg-primary text-primary-foreground font-medium flex items-center justify-center gap-2 hover:bg-primary/90 transition-colors"
      >
        <Sparkles className="h-4 w-4" />
        Acquista Token
      </motion.button>
    </motion.div>
  );
}
