/**
 * Notifications Dropdown Component
 * Mostra le notifiche admin con supporto light/dark mode
 */

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bell,
  Check,
  CheckCheck,
  X,
  Calendar,
  DollarSign,
  Users,
  AlertTriangle,
  Info,
  ExternalLink
} from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { cn } from '../../../shared/lib/utils';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { getAdminToken } from '../../../shared/lib/api';

interface Notification {
  id: number;
  type: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  title: string;
  message: string;
  action_url?: string;
  action_text?: string;
  is_read: boolean;
  read_at?: string;
  created_at: string;
}

const notificationIcons: Record<string, React.ElementType> = {
  booking: Calendar,
  finance: DollarSign,
  user: Users,
  warning: AlertTriangle,
  info: Info,
};

const priorityColors: Record<string, string> = {
  low: 'bg-gray-400',
  normal: 'bg-gold',
  high: 'bg-gold',
  urgent: 'bg-gray-500',
};

export function NotificationsDropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Fetch unread count
  const fetchUnreadCount = async () => {
    try {
      const token = getAdminToken();
      if (!token) return;

      const response = await fetch('/api/v1/admin/notifications/count', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.data?.unread_count || 0);
      }
    } catch (error) {
      console.error('Error fetching notification count:', error);
    }
  };

  // Fetch notifications
  const fetchNotifications = async () => {
    setIsLoading(true);
    try {
      const token = getAdminToken();
      if (!token) return;

      const response = await fetch('/api/v1/admin/notifications?limit=10', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setNotifications(data.data || []);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Mark as read
  const markAsRead = async (id: number) => {
    try {
      const token = getAdminToken();
      if (!token) return;

      await fetch(`/api/v1/admin/notifications/${id}/read`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, is_read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    try {
      const token = getAdminToken();
      if (!token) return;

      await fetch('/api/v1/admin/notifications/read-all', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  // Initial fetch and polling
  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  // Fetch notifications when dropdown opens
  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen]);

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Adesso';
    if (minutes < 60) return `${minutes}m fa`;
    if (hours < 24) return `${hours}h fa`;
    if (days < 7) return `${days}g fa`;
    return date.toLocaleDateString('it-IT');
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Bell Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsOpen(!isOpen)}
        className={cn("relative", isDark ? "hover:bg-white/10" : "hover:bg-gray-100")}
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center bg-gold text-black text-xs font-bold rounded-full px-1"
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </motion.span>
        )}
      </Button>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className={cn(
              "absolute right-0 mt-2 w-80 sm:w-96 rounded-xl shadow-xl z-50 overflow-hidden border",
              isDark
                ? "bg-[#0a0a0a] border-white/10"
                : "bg-white border-gray-200"
            )}
          >
            {/* Header */}
            <div className={cn(
              "flex items-center justify-between px-4 py-3 border-b",
              isDark ? "border-white/10" : "border-gray-200"
            )}>
              <div className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-gold" />
                <h3 className={cn("font-semibold", isDark ? "text-white" : "text-gray-900")}>
                  Notifiche
                </h3>
                {unreadCount > 0 && (
                  <span className="px-2 py-0.5 bg-gold/20 text-gold text-xs font-medium rounded-full">
                    {unreadCount} nuove
                  </span>
                )}
              </div>
              <div className="flex items-center gap-1">
                {unreadCount > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={markAllAsRead}
                    className="text-xs h-7 px-2"
                  >
                    <CheckCheck className="h-3.5 w-3.5 mr-1" />
                    Leggi tutte
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsOpen(false)}
                  className="h-7 w-7"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Notifications List */}
            <div className="max-h-[400px] overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="h-6 w-6 border-2 border-gold border-t-transparent rounded-full animate-spin" />
                </div>
              ) : notifications.length === 0 ? (
                <div className={cn("py-12 text-center", isDark ? "text-gray-400" : "text-gray-500")}>
                  <Bell className="h-10 w-10 mx-auto mb-3 opacity-30" />
                  <p className="text-sm">Nessuna notifica</p>
                </div>
              ) : (
                <div className="divide-y divide-white/5">
                  {notifications.map((notification) => {
                    const Icon = notificationIcons[notification.type] || Info;
                    return (
                      <motion.div
                        key={notification.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className={cn(
                          "px-4 py-3 transition-colors cursor-pointer",
                          !notification.is_read && (isDark ? "bg-gold/5" : "bg-gold/10"),
                          isDark ? "hover:bg-white/5" : "hover:bg-gray-50"
                        )}
                        onClick={() => {
                          if (!notification.is_read) {
                            markAsRead(notification.id);
                          }
                          if (notification.action_url) {
                            window.location.href = notification.action_url;
                          }
                        }}
                      >
                        <div className="flex gap-3">
                          <div className={cn(
                            "flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center",
                            isDark ? "bg-white/10" : "bg-gray-100"
                          )}>
                            <Icon className={cn(
                              "h-5 w-5",
                              notification.priority === 'urgent' ? "text-gray-400" :
                                notification.priority === 'high' ? "text-gold" :
                                  "text-gold"
                            )} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between gap-2">
                              <p className={cn(
                                "text-sm font-medium truncate",
                                isDark ? "text-white" : "text-gray-900"
                              )}>
                                {notification.title}
                              </p>
                              {!notification.is_read && (
                                <span className={cn(
                                  "flex-shrink-0 w-2 h-2 rounded-full mt-1.5",
                                  priorityColors[notification.priority]
                                )} />
                              )}
                            </div>
                            <p className={cn(
                              "text-sm mt-0.5 line-clamp-2",
                              isDark ? "text-gray-400" : "text-gray-600"
                            )}>
                              {notification.message}
                            </p>
                            <div className="flex items-center gap-2 mt-1.5">
                              <span className={cn(
                                "text-xs",
                                isDark ? "text-gray-500" : "text-gray-400"
                              )}>
                                {formatTime(notification.created_at)}
                              </span>
                              {notification.action_url && (
                                <span className="text-xs text-gold flex items-center gap-0.5">
                                  <ExternalLink className="h-3 w-3" />
                                  {notification.action_text || 'Vedi'}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Footer */}
            {notifications.length > 0 && (
              <div className={cn(
                "px-4 py-2 border-t text-center",
                isDark ? "border-white/10" : "border-gray-200"
              )}>
                <a
                  href="/admin/impostazioni"
                  className="text-sm text-gold hover:underline"
                >
                  Gestisci notifiche
                </a>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
