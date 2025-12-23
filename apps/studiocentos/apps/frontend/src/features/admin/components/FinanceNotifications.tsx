/**
 * FinanceNotifications - Sistema notifiche finanziarie frontend
 * Alert in tempo reale, toast notifications, bell icon con badge
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import {
  Bell, BellRing, X, AlertTriangle, Info, CheckCircle,
  Clock, Euro, TrendingUp, Calendar, Eye, EyeOff,
  Settings, Filter, MoreVertical
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/components/ui/card';
import { Button } from '../../../shared/components/ui/button';
import { Badge } from '../../../shared/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from '../../../shared/components/ui/dropdown-menu';
import { cn } from '../../../shared/lib/utils';

// Helper function for date formatting
const formatDateHelper = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

  if (diffMinutes < 1) return 'Ora';
  if (diffMinutes < 60) return `${diffMinutes}m fa`;
  if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h fa`;
  return `${Math.floor(diffMinutes / 1440)}g fa`;
};

// Types
interface FinanceAlert {
  id: number;
  alert_type: string;
  title: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  trigger_date: string;
  due_date?: string;
  status: 'active' | 'dismissed' | 'resolved' | 'snoozed';
  is_overdue: boolean;
  is_snoozed: boolean;
  expense_id?: number;
  budget_id?: number;
  roi_id?: number;
  created_at: string;
}

interface NotificationPreferences {
  email_enabled: boolean;
  push_enabled: boolean;
  alert_types: string[];
  severity_threshold: 'low' | 'medium' | 'high' | 'critical';
}

interface FinanceNotificationsProps {
  className?: string;
  maxAlerts?: number;
  showBellIcon?: boolean;
  autoRefreshInterval?: number;
}

const SEVERITY_CONFIG = {
  critical: {
    color: 'text-gray-400',
    bgColor: 'bg-gray-500/10',
    borderColor: 'border-gray-500/20',
    icon: AlertTriangle,
    badge: 'destructive' as const
  },
  high: {
    color: 'text-gold',
    bgColor: 'bg-gold/10',
    borderColor: 'border-gold/20',
    icon: AlertTriangle,
    badge: 'secondary' as const
  },
  medium: {
    color: 'text-gold',
    bgColor: 'bg-gold/10',
    borderColor: 'border-gold/20',
    icon: Info,
    badge: 'outline' as const
  },
  low: {
    color: 'text-gray-500',
    bgColor: 'bg-gray-500/10',
    borderColor: 'border-gray-500/20',
    icon: Info,
    badge: 'outline' as const
  }
};

const ALERT_TYPE_CONFIG = {
  expense_due: {
    icon: Euro,
    label: 'Scadenza Spesa',
    color: 'text-gray-400'
  },
  budget_exceeded: {
    icon: TrendingUp,
    label: 'Budget Superato',
    color: 'text-gold'
  },
  roi_milestone: {
    icon: TrendingUp,
    label: 'ROI Milestone',
    color: 'text-gold'
  },
  cashflow_warning: {
    icon: AlertTriangle,
    label: 'Cashflow Warning',
    color: 'text-gray-400'
  },
  payment_overdue: {
    icon: Clock,
    label: 'Pagamento Scaduto',
    color: 'text-gray-500'
  }
};

export function FinanceNotifications({
  className,
  maxAlerts = 10,
  showBellIcon = true,
  autoRefreshInterval = 30000 // 30 seconds
}: FinanceNotificationsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [showOnlyUnread, setShowOnlyUnread] = useState(false);
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    email_enabled: true,
    push_enabled: true,
    alert_types: ['expense_due', 'budget_exceeded'],
    severity_threshold: 'medium'
  });

  const queryClient = useQueryClient();

  // Fetch alerts
  const { data: alerts = [], isLoading } = useQuery({
    queryKey: ['finance-alerts', filterSeverity, filterType],
    queryFn: async (): Promise<FinanceAlert[]> => {
      const token = localStorage.getItem('admin_token');
      const params = new URLSearchParams();

      if (filterSeverity !== 'all') params.append('severity', filterSeverity);
      if (filterType !== 'all') params.append('alert_type', filterType);
      params.append('page_size', maxAlerts.toString());

      const res = await fetch(`/api/v1/admin/finance/alerts?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!res.ok) throw new Error('Failed to fetch alerts');
      const data = await res.json();
      return data.items || [];
    },
    refetchInterval: autoRefreshInterval,
    refetchIntervalInBackground: true
  });

  // Dismiss alert mutation
  const dismissMutation = useMutation({
    mutationFn: async (alertId: number) => {
      const token = localStorage.getItem('admin_token');
      const res = await fetch(`/api/v1/admin/finance/alerts/${alertId}/dismiss`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Failed to dismiss alert');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finance-alerts'] });
    }
  });

  // Snooze alert mutation
  const snoozeMutation = useMutation({
    mutationFn: async ({ alertId, hours }: { alertId: number; hours: number }) => {
      const token = localStorage.getItem('admin_token');
      const res = await fetch(`/api/v1/admin/finance/alerts/${alertId}/snooze?hours=${hours}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Failed to snooze alert');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finance-alerts'] });
    }
  });

  // Filtered alerts
  const filteredAlerts = alerts.filter(alert => {
    if (showOnlyUnread && alert.status !== 'active') return false;
    return true;
  });

  // Active alerts count
  const activeAlertsCount = alerts.filter(alert => alert.status === 'active').length;
  const criticalAlertsCount = alerts.filter(alert =>
    alert.status === 'active' && alert.severity === 'critical'
  ).length;

  // Handle dismiss
  const handleDismiss = useCallback((alertId: number) => {
    dismissMutation.mutate(alertId);
  }, [dismissMutation]);

  // Handle snooze
  const handleSnooze = useCallback((alertId: number, hours: number) => {
    snoozeMutation.mutate({ alertId, hours });
  }, [snoozeMutation]);

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffMinutes < 1) return 'Ora';
    if (diffMinutes < 60) return `${diffMinutes}m fa`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h fa`;
    return `${Math.floor(diffMinutes / 1440)}g fa`;
  };

  // Auto-show critical alerts
  useEffect(() => {
    if (criticalAlertsCount > 0 && !isOpen) {
      // Auto-open se ci sono alert critici
      const timer = setTimeout(() => setIsOpen(true), 1000);
      return () => clearTimeout(timer);
    }
  }, [criticalAlertsCount, isOpen]);

  if (!showBellIcon) {
    return (
      <div className={className}>
        <NotificationsList
          alerts={filteredAlerts}
          onDismiss={handleDismiss}
          onSnooze={handleSnooze}
          isLoading={isLoading}
        />
      </div>
    );
  }

  return (
    <div className={cn("relative", className)}>
      {/* Bell Icon with Badge */}
      <Button
        variant="ghost"
        size="sm"
        className="relative h-9 w-9 p-0"
        onClick={() => setIsOpen(!isOpen)}
      >
        <motion.div
          animate={criticalAlertsCount > 0 ? {
            rotate: [0, -10, 10, -10, 0],
            scale: [1, 1.1, 1]
          } : {}}
          transition={{
            duration: 0.5,
            repeat: criticalAlertsCount > 0 ? Infinity : 0,
            repeatDelay: 3
          }}
        >
          {criticalAlertsCount > 0 ? (
            <BellRing className="h-5 w-5 text-gray-400" />
          ) : (
            <Bell className="h-5 w-5 text-gray-400" />
          )}
        </motion.div>

        {activeAlertsCount > 0 && (
          <Badge
            className={cn(
              "absolute -top-1 -right-1 h-5 w-5 p-0 text-xs font-bold",
              criticalAlertsCount > 0
                ? "bg-gray-500 hover:bg-gray-500"
                : "bg-gold hover:bg-gold/80"
            )}
          >
            {activeAlertsCount > 99 ? '99+' : activeAlertsCount}
          </Badge>
        )}
      </Button>

      {/* Dropdown Panel */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-40"
              onClick={() => setIsOpen(false)}
            />

            {/* Panel */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              className="absolute right-0 top-full mt-2 w-96 max-h-[500px] bg-[#0A0A0A] border border-white/10 rounded-lg shadow-2xl z-50 overflow-hidden"
            >
              {/* Header */}
              <div className="p-4 border-b border-white/10">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-white">
                      Notifiche Finance
                    </h3>
                    <p className="text-sm text-gray-400">
                      {activeAlertsCount} alert attivi
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Filters */}
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          <Filter className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-48">
                        <DropdownMenuItem
                          onClick={() => setShowOnlyUnread(!showOnlyUnread)}
                        >
                          {showOnlyUnread ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
                          {showOnlyUnread ? 'Mostra tutti' : 'Solo attivi'}
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem>Severità: {filterSeverity}</DropdownMenuItem>
                        <DropdownMenuItem>Tipo: {filterType}</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsOpen(false)}
                      className="h-8 w-8 p-0"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Alerts List */}
              <div className="max-h-96 overflow-y-auto">
                {isLoading ? (
                  <div className="p-4 space-y-3">
                    {[...Array(3)].map((_, i) => (
                      <div key={i} className="animate-pulse">
                        <div className="h-16 bg-white/5 rounded-lg"></div>
                      </div>
                    ))}
                  </div>
                ) : filteredAlerts.length > 0 ? (
                  <div className="p-2 space-y-2">
                    {filteredAlerts.map((alert) => (
                      <NotificationItem
                        key={alert.id}
                        alert={alert}
                        onDismiss={handleDismiss}
                        onSnooze={handleSnooze}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center text-gray-400">
                    <CheckCircle className="h-12 w-12 mx-auto mb-3 opacity-50" />
                    <p>Nessun alert attivo</p>
                    <p className="text-sm">Tutto sotto controllo! 🎉</p>
                  </div>
                )}
              </div>

              {/* Footer */}
              {filteredAlerts.length > 0 && (
                <div className="p-3 border-t border-white/10 bg-white/5">
                  <div className="flex items-center justify-between">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-xs"
                      onClick={() => {
                        filteredAlerts.forEach(alert => {
                          if (alert.status === 'active') {
                            handleDismiss(alert.id);
                          }
                        });
                      }}
                    >
                      Dismissi tutti
                    </Button>

                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-xs text-gold hover:text-gold/80"
                      onClick={() => {
                        setIsOpen(false);
                        // Navigate to finance dashboard
                        window.location.href = '/admin/finance';
                      }}
                    >
                      Vai al Dashboard →
                    </Button>
                  </div>
                </div>
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}

// Notification Item Component
function NotificationItem({
  alert,
  onDismiss,
  onSnooze
}: {
  alert: FinanceAlert;
  onDismiss: (id: number) => void;
  onSnooze: (id: number, hours: number) => void;
}) {
  const severityConfig = SEVERITY_CONFIG[alert.severity];
  const alertTypeConfig = ALERT_TYPE_CONFIG[alert.alert_type as keyof typeof ALERT_TYPE_CONFIG];
  const SeverityIcon = severityConfig.icon;
  const TypeIcon = alertTypeConfig?.icon || Info;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className={cn(
        "p-3 rounded-lg border transition-all duration-200 hover:bg-white/5",
        severityConfig.bgColor,
        severityConfig.borderColor,
        alert.status !== 'active' && "opacity-60"
      )}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={cn("p-1.5 rounded-full", severityConfig.bgColor)}>
          <TypeIcon className={cn("h-4 w-4", alertTypeConfig?.color || severityConfig.color)} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="text-sm font-medium text-white truncate">
                {alert.title}
              </h4>
              <p className="text-xs text-gray-300 mt-1 line-clamp-2">
                {alert.message}
              </p>

              <div className="flex items-center gap-2 mt-2">
                <Badge variant={severityConfig.badge} className="text-xs">
                  {alert.severity}
                </Badge>

                <span className="text-xs text-gray-400">
                  {formatDateHelper(alert.trigger_date)}
                </span>

                {alert.is_snoozed && (
                  <Badge variant="outline" className="text-xs">
                    Snoozed
                  </Badge>
                )}
              </div>
            </div>

            {/* Actions */}
            {alert.status === 'active' && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <MoreVertical className="h-3 w-3" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-40">
                  <DropdownMenuItem onClick={() => onDismiss(alert.id)}>
                    <X className="h-4 w-4 mr-2" />
                    Dismissi
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onSnooze(alert.id, 1)}>
                    <Clock className="h-4 w-4 mr-2" />
                    Snooze 1h
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onSnooze(alert.id, 24)}>
                    <Clock className="h-4 w-4 mr-2" />
                    Snooze 24h
                  </DropdownMenuItem>
                  {alert.expense_id && (
                    <>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem>
                        <Euro className="h-4 w-4 mr-2" />
                        Vedi Spesa
                      </DropdownMenuItem>
                    </>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Notifications List Component (for standalone use)
function NotificationsList({
  alerts,
  onDismiss,
  onSnooze,
  isLoading
}: {
  alerts: FinanceAlert[];
  onDismiss: (id: number) => void;
  onSnooze: (id: number, hours: number) => void;
  isLoading: boolean;
}) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-20 bg-white/5 rounded-lg"></div>
          </div>
        ))}
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <Card className="bg-white/5 border-white/10">
        <CardContent className="p-8 text-center">
          <CheckCircle className="h-16 w-16 mx-auto mb-4 text-gold opacity-50" />
          <h3 className="text-lg font-semibold text-white mb-2">
            Tutto sotto controllo!
          </h3>
          <p className="text-gray-400">
            Nessun alert finanziario attivo al momento.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <NotificationItem
          key={alert.id}
          alert={alert}
          onDismiss={onDismiss}
          onSnooze={onSnooze}
        />
      ))}
    </div>
  );
}

export { NotificationsList };
