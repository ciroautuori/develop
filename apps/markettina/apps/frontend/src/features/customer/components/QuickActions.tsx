/**
 * QuickActions Component
 * Fast access buttons for common customer tasks
 */

import { motion } from 'framer-motion';
import {
  Wand2,
  Image,
  Video,
  Calendar,
  Search,
  Mail,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { cn } from '../../../shared/lib/utils';

interface QuickAction {
  id: string;
  label: string;
  description: string;
  icon: React.ElementType;
  href: string;
  color: string;
  tokens?: number;
}

interface QuickActionsProps {
  className?: string;
  onActionClick?: (actionId: string) => void;
}

const ACTIONS: QuickAction[] = [
  {
    id: 'content',
    label: 'Genera Contenuto',
    description: 'Post, blog, newsletter',
    icon: Wand2,
    href: '/customer/ai-marketing?tab=content',
    color: 'from-blue-500 to-cyan-500',
    tokens: 5,
  },
  {
    id: 'image',
    label: 'Crea Immagine',
    description: 'Immagini AI brand-aligned',
    icon: Image,
    href: '/customer/ai-marketing?tab=image',
    color: 'from-purple-500 to-pink-500',
    tokens: 10,
  },
  {
    id: 'video',
    label: 'Genera Video',
    description: 'Stories e Reels',
    icon: Video,
    href: '/customer/ai-marketing?tab=video',
    color: 'from-pink-500 to-rose-500',
    tokens: 50,
  },
  {
    id: 'calendar',
    label: 'Pianifica Post',
    description: 'Calendario editoriale',
    icon: Calendar,
    href: '/customer/ai-marketing?tab=calendar',
    color: 'from-emerald-500 to-teal-500',
    tokens: 0,
  },
  {
    id: 'leads',
    label: 'Trova Lead',
    description: 'Ricerca B2B intelligente',
    icon: Search,
    href: '/customer/ai-marketing?tab=leads',
    color: 'from-orange-500 to-amber-500',
    tokens: 10,
  },
  {
    id: 'email',
    label: 'Email Campaign',
    description: 'Newsletter automatiche',
    icon: Mail,
    href: '/customer/ai-marketing?tab=email',
    color: 'from-indigo-500 to-violet-500',
    tokens: 15,
  },
];

export function QuickActions({ className, onActionClick }: QuickActionsProps) {
  return (
    <div className={cn('space-y-4', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <h3 className="font-semibold text-foreground">Azioni Rapide</h3>
        </div>
      </div>

      {/* Actions Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {ACTIONS.map((action, index) => {
          const Icon = action.icon;

          return (
            <motion.a
              key={action.id}
              href={action.href}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={(e) => {
                if (onActionClick) {
                  e.preventDefault();
                  onActionClick(action.id);
                }
              }}
              className={cn(
                'group relative p-4 rounded-xl border border-border',
                'bg-card hover:bg-muted/50 transition-all duration-200',
                'cursor-pointer overflow-hidden'
              )}
            >
              {/* Gradient Background on Hover */}
              <div className={cn(
                'absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity',
                `bg-gradient-to-br ${action.color}`
              )} />

              <div className="relative flex items-start gap-3">
                {/* Icon */}
                <div className={cn(
                  'p-2.5 rounded-xl bg-gradient-to-br shrink-0',
                  action.color
                )}>
                  <Icon className="h-5 w-5 text-white" />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-foreground group-hover:text-primary transition-colors">
                      {action.label}
                    </h4>
                    <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-0.5 transition-all" />
                  </div>
                  <p className="text-sm text-muted-foreground mt-0.5 truncate">
                    {action.description}
                  </p>

                  {/* Token Cost */}
                  {action.tokens !== undefined && action.tokens > 0 && (
                    <div className="mt-2 flex items-center gap-1">
                      <span className="text-xs px-1.5 py-0.5 rounded bg-primary/10 text-primary font-medium">
                        ~{action.tokens} token
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </motion.a>
          );
        })}
      </div>
    </div>
  );
}
