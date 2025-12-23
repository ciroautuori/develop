import React, { useState } from 'react';
import { Link } from '@tanstack/react-router';
import { Menu, X, Sun, Moon, Search, User, LogOut } from 'lucide-react';
import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/utils/cn';
import { useAuth } from '@/contexts/AuthContext';

interface HeaderProps {
  className?: string;
}

export const Header: React.FC<HeaderProps> = ({ className }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { theme, setTheme } = useTheme();
  const { user, isAuthenticated, logout } = useAuth();

  const navigation = [
    { name: 'Home', href: '/' },
    { name: 'Bandi', href: '/bandi', badge: 'Hub APS' },
    { name: 'Corsi', href: '/corsi', badge: 'ISS' },
    { name: 'Eventi', href: '/eventi', badge: 'ISS' },
    { name: 'Progetti', href: '/progetti', badge: 'ISS' },
    { name: 'Volontariato', href: '/volontariato', badge: 'ISS' },
  ];

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <header className={cn('sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60', className)}>
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="h-8 w-8">
              <img 
                src="/iss-logo.svg" 
                alt="ISS Logo" 
                className="w-full h-full object-contain"
              />
            </div>
            <div className="hidden sm:block">
              <span className="text-xl font-bold text-gradient">
                Innovazione Sociale Salernitana
              </span>
              <p className="text-xs text-muted-foreground">
                Hub Bandi APS + Formazione Digitale
              </p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className="flex items-center gap-2 text-sm font-medium transition-colors hover:text-primary"
                activeProps={{
                  className: 'text-primary',
                }}
              >
                {item.name}
                {item.badge && (
                  <Badge variant="outline" className="text-xs">
                    {item.badge}
                  </Badge>
                )}
              </Link>
            ))}
          </nav>

          {/* Actions */}
          <div className="flex items-center space-x-2">
            {/* Search Button */}
            <Button variant="ghost" size="icon" className="hidden sm:inline-flex">
              <Search className="h-4 w-4" />
              <span className="sr-only">Cerca</span>
            </Button>

            {/* Theme Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            >
              <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span>
            </Button>

            {/* User Menu */}
            {isAuthenticated ? (
              <div className="flex items-center space-x-2">
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium">{user?.nome} {user?.cognome}</p>
                  <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
                </div>
                <Button variant="ghost" size="icon" onClick={handleLogout}>
                  <LogOut className="h-4 w-4" />
                  <span className="sr-only">Logout</span>
                </Button>
              </div>
            ) : (
              <div className="hidden sm:flex items-center space-x-2">
                <Button variant="ghost" size="sm">
                  <Link to="/login">Accedi</Link>
                </Button>
                <Button variant="iss-primary" size="sm">
                  <Link to="/register">Registrati</Link>
                </Button>
              </div>
            )}

            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
              <span className="sr-only">Toggle menu</span>
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="space-y-1 px-2 pb-3 pt-2">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="flex items-center justify-between rounded-md px-3 py-2 text-base font-medium transition-colors hover:bg-accent hover:text-accent-foreground"
                  onClick={() => setIsMenuOpen(false)}
                  activeProps={{
                    className: 'bg-accent text-accent-foreground',
                  }}
                >
                  <span>{item.name}</span>
                  {item.badge && (
                    <Badge variant="outline" className="text-xs">
                      {item.badge}
                    </Badge>
                  )}
                </Link>
              ))}

              {/* Mobile Auth Buttons */}
              {!isAuthenticated && (
                <div className="space-y-2 pt-4 border-t">
                  <Link
                    to="/login"
                    className="block rounded-md px-3 py-2 text-base font-medium transition-colors hover:bg-accent hover:text-accent-foreground"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Accedi
                  </Link>
                  <Link
                    to="/register"
                    className="block rounded-md bg-primary px-3 py-2 text-base font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Registrati
                  </Link>
                </div>
              )}

              {/* Mobile User Info */}
              {isAuthenticated && user && (
                <div className="space-y-2 pt-4 border-t">
                  <div className="px-3 py-2">
                    <p className="text-base font-medium">{user.nome} {user.cognome}</p>
                    <p className="text-sm text-muted-foreground capitalize">{user.role}</p>
                    {user.organizzazione && (
                      <p className="text-sm text-muted-foreground">{user.organizzazione}</p>
                    )}
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center rounded-md px-3 py-2 text-base font-medium transition-colors hover:bg-accent hover:text-accent-foreground"
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};
