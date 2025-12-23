/**
 * TokenUsageChart Component
 * Visual breakdown of token usage by category
 */

import { motion } from 'framer-motion';
import {
  FileText,
  Image,
  Video,
  Search,
  Mail,
  BarChart3
} from 'lucide-react';
import { cn } from '../../../shared/lib/utils';

interface UsageCategory {
  id: string;
  name: string;
  tokens: number;
  icon: React.ElementType;
  color: string;
}

interface TokenUsageChartProps {
  data: {
    textGeneration?: number;
    imageGeneration?: number;
    videoGeneration?: number;
    leadSearch?: number;
    emailCampaigns?: number;
    other?: number;
  };
  period?: 'week' | 'month' | 'year';
  className?: string;
}

export function TokenUsageChart({
  data,
  period = 'month',
  className,
}: TokenUsageChartProps) {
  const categories: UsageCategory[] = [
    { id: 'text', name: 'Testi', tokens: data.textGeneration || 0, icon: FileText, color: 'bg-blue-500' },
    { id: 'image', name: 'Immagini', tokens: data.imageGeneration || 0, icon: Image, color: 'bg-purple-500' },
    { id: 'video', name: 'Video', tokens: data.videoGeneration || 0, icon: Video, color: 'bg-pink-500' },
    { id: 'lead', name: 'Lead Finder', tokens: data.leadSearch || 0, icon: Search, color: 'bg-green-500' },
    { id: 'email', name: 'Email', tokens: data.emailCampaigns || 0, icon: Mail, color: 'bg-orange-500' },
    { id: 'other', name: 'Altro', tokens: data.other || 0, icon: BarChart3, color: 'bg-gray-500' },
  ].filter(c => c.tokens > 0);

  const totalTokens = categories.reduce((acc, c) => acc + c.tokens, 0);

  const periodLabel = {
    week: 'questa settimana',
    month: 'questo mese',
    year: 'quest\'anno',
  }[period];

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
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="font-semibold text-foreground">Uso Token</h3>
          <p className="text-sm text-muted-foreground capitalize">{periodLabel}</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-foreground">{totalTokens.toLocaleString()}</p>
          <p className="text-sm text-muted-foreground">token usati</p>
        </div>
      </div>

      {/* Stacked Bar */}
      <div className="h-4 rounded-full bg-muted overflow-hidden flex mb-6">
        {categories.map((category, index) => {
          const width = totalTokens > 0 ? (category.tokens / totalTokens) * 100 : 0;
          return (
            <motion.div
              key={category.id}
              initial={{ width: 0 }}
              animate={{ width: `${width}%` }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={cn('h-full', category.color)}
              title={`${category.name}: ${category.tokens} token`}
            />
          );
        })}
      </div>

      {/* Legend */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {categories.map((category) => {
          const Icon = category.icon;
          const percent = totalTokens > 0 ? ((category.tokens / totalTokens) * 100).toFixed(0) : 0;

          return (
            <div
              key={category.id}
              className="flex items-center gap-2 p-2 rounded-lg hover:bg-muted/50 transition-colors"
            >
              <div className={cn('w-3 h-3 rounded-full', category.color)} />
              <Icon className="h-4 w-4 text-muted-foreground" />
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-foreground truncate">{category.name}</p>
                <p className="text-xs text-muted-foreground">{category.tokens} ({percent}%)</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {totalTokens === 0 && (
        <div className="text-center py-8">
          <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground/30 mb-3" />
          <p className="text-muted-foreground">Nessun consumo registrato</p>
          <p className="text-sm text-muted-foreground mt-1">
            Inizia a generare contenuti per vedere le statistiche
          </p>
        </div>
      )}
    </motion.div>
  );
}
