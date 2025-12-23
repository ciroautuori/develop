/**
 * CustomerLayout Component
 * Main layout wrapper for customer area with sidebar and header
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useLocation, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  Wand2,
  FileText,
  Settings,
  LogOut,
  Menu,
  X,
  Coins,
  ChevronDown,
  Bell,
  User,
  Palette,
} from 'lucide-react';
import { cn } from '../../../shared/lib/utils';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { TokenBalance } from '../components/TokenBalance';

interface NavItem {
  id: string;
  label: string;
  icon: React.ElementType;
  href: string;
  badge?: number;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, href: '/customer' },
  { id: 'ai-marketing', label: 'AI Marketing', icon: Wand2, href: '/customer/ai-marketing' },
  { id: 'content', label: 'I Miei Contenuti', icon: FileText, href: '/customer/content' },
  { id: 'brand', label: 'Brand DNA', icon: Palette, href: '/customer/brand' },
  { id: 'settings', label: 'Impostazioni', icon: Settings, href: '/customer/settings' },
];

export function CustomerLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const location = useLocation();
  const { theme, setTheme } = useTheme();
  const isDark = theme === 'dark';

  // Mock user data - replace with real auth
  const user = {
    name: 'Mario Rossi',
    email: 'mario@azienda.it',
    company: 'Azienda Srl',
    avatar: null,
  };

  // Mock token data - replace with real API
  const tokenData = {
    balance: 1247,
    used: 753,
    total: 2000,
    planName: 'Growth',
  };

  const isActive = (href: string) => {
    if (href === '/customer') {
      return location.pathname === '/customer';
    }
    return location.pathname.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Header */}
      <header className="lg:hidden sticky top-0 z-50 bg-card border-b border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-lg hover:bg-muted transition-colors"
          >
            <Menu className="h-5 w-5" />
          </button>

          <Link to="/customer" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">M</span>
            </div>
            <span className="font-bold text-foreground">MARKETTINA</span>
          </Link>

          <TokenBalance
            balance={tokenData.balance}
            used={tokenData.used}
            total={tokenData.total}
            compact
          />
        </div>
      </header>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden fixed inset-0 bg-black/50 z-50"
            />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="lg:hidden fixed left-0 top-0 bottom-0 w-[280px] bg-card border-r border-border z-50 overflow-y-auto"
            >
              <SidebarContent
                user={user}
                tokenData={tokenData}
                navItems={NAV_ITEMS}
                isActive={isActive}
                onClose={() => setSidebarOpen(false)}
              />
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Desktop Sidebar */}
      <aside className="hidden lg:block fixed left-0 top-0 bottom-0 w-[280px] bg-card border-r border-border overflow-y-auto">
        <SidebarContent
          user={user}
          tokenData={tokenData}
          navItems={NAV_ITEMS}
          isActive={isActive}
        />
      </aside>

      {/* Main Content */}
      <main className="lg:ml-[280px] min-h-screen">
        <Outlet />
      </main>
    </div>
  );
}

// Sidebar Content Component
function SidebarContent({
  user,
  tokenData,
  navItems,
  isActive,
  onClose,
}: {
  user: any;
  tokenData: any;
  navItems: NavItem[];
  isActive: (href: string) => boolean;
  onClose?: () => void;
}) {
  return (
    <div className="flex flex-col h-full">
      {/* Logo & Close */}
      <div className="p-4 flex items-center justify-between border-b border-border">
        <Link to="/customer" className="flex items-center gap-2" onClick={onClose}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-lg">M</span>
          </div>
          <div>
            <span className="font-bold text-foreground block">MARKETTINA</span>
            <span className="text-xs text-muted-foreground">Customer Portal</span>
          </div>
        </Link>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-muted transition-colors lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* User Info */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
            <User className="h-5 w-5 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium text-foreground truncate">{user.name}</p>
            <p className="text-sm text-muted-foreground truncate">{user.company}</p>
          </div>
        </div>
      </div>

      {/* Token Balance Mini */}
      <div className="p-4 border-b border-border">
        <div className="p-3 rounded-xl bg-muted/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">Token</span>
            <span className="font-bold text-foreground">{tokenData.balance.toLocaleString()}</span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div
              className="h-full bg-primary rounded-full"
              style={{ width: `${((tokenData.total - tokenData.used) / tokenData.total) * 100}%` }}
            />
          </div>
          <Link
            to="/customer/tokens"
            onClick={onClose}
            className="block text-center text-xs text-primary font-medium mt-2 hover:underline"
          >
            Acquista Token
          </Link>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <Link
              key={item.id}
              to={item.href}
              onClick={onClose}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all',
                active
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted'
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="font-medium">{item.label}</span>
              {item.badge && (
                <span className="ml-auto px-2 py-0.5 text-xs font-bold rounded-full bg-red-500 text-white">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <button
          onClick={() => {
            // Handle logout
            localStorage.removeItem('customer_token');
            window.location.href = '/login';
          }}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-muted-foreground hover:text-foreground hover:bg-muted transition-all"
        >
          <LogOut className="h-5 w-5" />
          <span className="font-medium">Esci</span>
        </button>
      </div>
    </div>
  );
}
