/**
 * QuickActions - MARKET READY
 * Pulsanti rapidi per aprire i modali principali
 */

import { motion } from 'framer-motion';
import {
  PenSquare, Video, Mail, Users, Settings,
  Sparkles, TrendingUp, Calendar, Globe
} from 'lucide-react';
import { cn } from '../../../../../../shared/lib/utils';
import { useTheme } from '../../../../../../shared/contexts/ThemeContext';

// ============================================================================
// TYPES
// ============================================================================

interface ActionButton {
  id: string;
  label: string;
  description: string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
  hoverColor: string;
  onClick: () => void;
}

interface QuickActionsProps {
  onCreatePost: () => void;
  onCreateVideo: () => void;
  onCreateEmail: () => void;
  onFindLeads: () => void;
  onOpenSettings: () => void;
  onCreateMultiPlatformPost?: () => void;
  onOpenAnalytics?: () => void;
  className?: string;
}

// ============================================================================
// COMPONENT
// ============================================================================

export function QuickActions({
  onCreatePost,
  onCreateVideo,
  onCreateEmail,
  onFindLeads,
  onOpenSettings,
  onCreateMultiPlatformPost,
  onOpenAnalytics,
  className,
}: QuickActionsProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const cardBg = isDark ? 'bg-white/5 border-white/10' : 'bg-white border-gray-200';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';

  const actions: ActionButton[] = [
    ...(onCreateMultiPlatformPost
      ? [
          {
            id: 'multi-platform',
            label: 'Multi-Platform',
            description: 'FB + IG + Stories',
            icon: Globe,
            color: 'text-emerald-500',
            bgColor: 'bg-emerald-500/10',
            hoverColor: 'hover:bg-emerald-500/20',
            onClick: onCreateMultiPlatformPost,
          },
        ]
      : []),
    {
      id: 'post',
      label: 'Nuovo Post',
      description: 'Crea post con AI',
      icon: PenSquare,
      color: 'text-gold',
      bgColor: 'bg-gold/10',
      hoverColor: 'hover:bg-gold/20',
      onClick: onCreatePost,
    },
    {
      id: 'video',
      label: 'Crea Video',
      description: 'Avatar AI HeyGen',
      icon: Video,
      color: 'text-gold',
      bgColor: 'bg-gold/10',
      hoverColor: 'hover:bg-gold/20',
      onClick: onCreateVideo,
    },
    {
      id: 'email',
      label: 'Email Campaign',
      description: 'Newsletter & drip',
      icon: Mail,
      color: 'text-gold',
      bgColor: 'bg-gold/10',
      hoverColor: 'hover:bg-gold/20',
      onClick: onCreateEmail,
    },
    {
      id: 'leads',
      label: 'Trova Lead',
      description: 'AI Lead Finder',
      icon: Users,
      color: 'text-gold',
      bgColor: 'bg-gold/10',
      hoverColor: 'hover:bg-gold/20',
      onClick: onFindLeads,
    },
  ];

  const secondaryActions = [
    ...(onOpenAnalytics
      ? [
          {
            id: 'analytics',
            label: 'Analytics',
            icon: TrendingUp,
            onClick: onOpenAnalytics,
          },
        ]
      : []),
    {
      id: 'settings',
      label: 'Impostazioni',
      icon: Settings,
      onClick: onOpenSettings,
    },
  ];

  return (
    <div className={cn('space-y-4', className)}>
      {/* Main Actions Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {actions.map((action, index) => {
          const Icon = action.icon;

          return (
            <motion.button
              key={action.id}
              onClick={action.onClick}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                'group flex flex-col items-center p-4 sm:p-6 rounded-xl border transition-all',
                cardBg,
                action.hoverColor
              )}
            >
              <motion.div
                className={cn(
                  'w-12 h-12 sm:w-14 sm:h-14 rounded-xl flex items-center justify-center mb-3 transition-transform',
                  action.bgColor
                )}
                whileHover={{ rotate: 5 }}
              >
                <Icon className={cn('w-6 h-6 sm:w-7 sm:h-7', action.color)} />
              </motion.div>

              <span className={cn('text-sm sm:text-base font-semibold mb-1', textPrimary)}>
                {action.label}
              </span>

              <span className={cn('text-xs text-center', textSecondary)}>
                {action.description}
              </span>

              {/* Sparkle effect on hover */}
              <motion.div
                className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                animate={{ rotate: [0, 15, -15, 0] }}
                transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 1 }}
              >
                <Sparkles className={cn('w-4 h-4', action.color)} />
              </motion.div>
            </motion.button>
          );
        })}
      </div>

      {/* Secondary Actions */}
      <div className="flex justify-center gap-3">
        {secondaryActions.map((action) => {
          const Icon = action.icon;
          return (
            <motion.button
              key={action.id}
              onClick={action.onClick}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors',
                isDark
                  ? 'border-white/10 hover:bg-white/10 text-gray-300'
                  : 'border-gray-200 hover:bg-gray-100 text-gray-600'
              )}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium">{action.label}</span>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
