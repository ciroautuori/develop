/**
 * Admin Layout - Layout principale unificato back-office
 * Design System Compliant (Semantic Tailwind + Shadcn)
 */

import { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Wallet,
  Cpu,
  Settings,
  LogOut,
  Menu,
  X,
  Search,
  Briefcase,
  User,
  Sun,
  Moon,
  GraduationCap
} from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { cn } from '../../../shared/lib/utils';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { ChatWidget } from '../../../shared/components/ui/chat-widget';
import { NotificationsDropdown } from '../components/NotificationsDropdown';
import { STORAGE_KEYS } from '../../../shared/config/constants';
import { toast } from 'sonner';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navigation: NavItem[] = [
  { name: 'Business Hub', href: '/admin/business', icon: LayoutDashboard },
  { name: 'Finance Hub', href: '/admin/finance', icon: Wallet },
  { name: 'AI Marketing', href: '/admin/ai-marketing', icon: Cpu },
  { name: 'Portfolio Hub', href: '/admin/portfolio', icon: Briefcase },
  { name: 'Impostazioni', href: '/admin/settings', icon: Settings },
];

export function AdminLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  const isActive = (href: string) => {
    // Exact match for root or specific paths
    if (href === '/admin/business') return location.pathname === href || location.pathname === '/admin';
    return location.pathname.startsWith(href);
  };

  const handleLogout = () => {
    // Clear all auth data
    localStorage.removeItem(STORAGE_KEYS.adminToken);
    localStorage.removeItem(STORAGE_KEYS.adminRefreshToken);
    localStorage.removeItem(STORAGE_KEYS.adminEmail);
    localStorage.removeItem('admin_id');

    toast.success('Logout effettuato');
    navigate('/admin/login');
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 transform border-r border-border bg-card transition-transform duration-300 ease-in-out lg:translate-x-0",
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between border-b border-border px-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                <span className="font-bold text-primary">SC</span>
              </div>
              <h1 className="text-xl font-bold tracking-tight">StudiocentOS</h1>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);

              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200 group",
                    active
                      ? "bg-primary text-primary-foreground shadow-md shadow-primary/20"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  <Icon className={cn("h-5 w-5", active ? "text-primary-foreground" : "text-muted-foreground group-hover:text-foreground")} />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* User section */}
          <div className="border-t border-border p-4 bg-muted/30">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary border border-primary/20">
                <User className="h-5 w-5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground truncate">
                  Admin User
                </p>
                <p className="text-xs text-muted-foreground truncate">admin@studiocentos.it</p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                onClick={handleLogout}
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
              </Button>
            </div>

            {/* Theme Toggle */}
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-center gap-2"
              onClick={toggleTheme}
            >
              {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              {isDark ? 'Tema Chiaro' : 'Tema Scuro'}
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64 flex flex-col min-h-screen">
        {/* Top bar */}
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-border bg-background/80 backdrop-blur-md px-4 sm:px-6">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden text-muted-foreground"
          >
            <Menu className="h-6 w-6" />
          </Button>

          {/* Search */}
          <div className="flex flex-1 items-center gap-2">
            <div className="relative w-full max-w-md hidden sm:block">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="search"
                placeholder="Cerca in StudiocentOS..."
                className="w-full rounded-lg border border-input bg-muted/50 py-2 pl-9 pr-4 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary placeholder:text-muted-foreground"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <NotificationsDropdown />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 bg-background/50">
          <Outlet />
        </main>
      </div>

      <ChatWidget className="bottom-6 right-6 sm:bottom-8 sm:right-8" />
    </div>
  );
}
