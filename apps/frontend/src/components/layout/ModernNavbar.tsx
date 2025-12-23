import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Menu,
  X,
  Search,
  User,
  LogOut,
  ChevronDown,
  Target,
  BookOpen,
  Calendar,
  Heart,
  Settings,
  Bell,
  Home,
  Rocket,
  Newspaper,
  Handshake
} from 'lucide-react';

interface ModernNavbarProps {
  className?: string;
}

interface NavigationItem {
  name: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
  badge?: string;
  description?: string;
  isNew?: boolean;
}

export const ModernNavbar: React.FC<ModernNavbarProps> = ({ className = '' }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

  // User state - reads from localStorage after login
  const [user, setUser] = useState<any>(null);
  const isAuthenticated = !!user;

  // Scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Prevent body scroll when menu is open
  useEffect(() => {
    if (isMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isMenuOpen]);

  // Check for existing auth
  useEffect(() => {
    const token = localStorage.getItem('iss_token');
    const userData = localStorage.getItem('iss_user');
    if (token && userData) {
      try {
        setUser(JSON.parse(userData));
      } catch (e) {
        console.error('Error parsing user data:', e);
      }
    }
  }, []);

  const navigation: NavigationItem[] = [
    {
      name: 'Home',
      href: '/',
      icon: Home,
      description: 'Torna alla homepage'
    },
    {
      name: 'Bandi',
      href: '/bandi',
      icon: Target,
      badge: 'Hub APS',
      description: 'Cerca bandi di finanziamento'
    },
    {
      name: 'Corsi',
      href: '/corsi',
      icon: BookOpen,
      badge: 'Gratuiti',
      description: 'Formazione digitale inclusiva',
      isNew: true
    },
    {
      name: 'Eventi',
      href: '/eventi',
      icon: Calendar,
      badge: 'ISS',
      description: 'Workshop e hackathon sociali',
      isNew: true
    },
    {
      name: 'Progetti',
      href: '/progetti',
      icon: Rocket,
      badge: 'Attivi',
      description: 'Portfolio progetti ISS',
      isNew: true
    },
    {
      name: 'Volontariato',
      href: '/volontariato',
      icon: Heart,
      badge: 'Matching',
      description: 'Opportunità volontariato digitale',
      isNew: true
    },
    {
      name: 'News',
      href: '/news',
      icon: Newspaper,
      badge: 'Blog',
      description: 'Notizie e aggiornamenti ISS',
      isNew: true
    },
    {
      name: 'Partners',
      href: '/partners',
      icon: Handshake,
      badge: 'Rete',
      description: 'Collaborazioni e testimonials',
      isNew: true
    }
  ];

  const handleNavigation = (href: string) => {
    window.location.href = href;
    setIsMenuOpen(false);
    setActiveDropdown(null);
  };

  const handleLogout = () => {
    localStorage.removeItem('iss_token');
    localStorage.removeItem('iss_user');
    setUser(null);
    window.location.href = '/';
  };

  const getUserInitials = (user: any) => {
    if (!user) return 'U';
    return `${user.nome?.[0] || ''}${user.cognome?.[0] || ''}`.toUpperCase();
  };

  const getUserRole = (role: string) => {
    const roleMap: Record<string, string> = {
      'admin': 'Amministratore',
      'aps_responsabile': 'Responsabile APS',
      'aps_operatore': 'Operatore APS',
      'cittadino': 'Cittadino',
      'volontario': 'Volontario'
    };
    return roleMap[role] || role;
  };

  return (
    <>
      {/* Fixed Header - z-50 */}
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled
            ? 'bg-white shadow-lg border-b border-gray-100'
            : 'bg-white/95 backdrop-blur-md shadow-sm'
          } ${className}`}
      >
        <div className="container mx-auto px-3 sm:px-4 lg:px-6">
          <div className="flex h-14 sm:h-16 items-center justify-between">
            {/* Logo - Mobile First */}
            <div
              className="flex items-center gap-2 sm:gap-3 cursor-pointer group flex-shrink-0"
              onClick={() => handleNavigation('/')}
            >
              {/* Logo Icon */}
              <div className="h-9 w-9 sm:h-10 sm:w-10 lg:h-12 lg:w-12 relative flex-shrink-0">
                <div className="absolute inset-0 bg-gradient-to-br from-iss-bordeaux-500/10 to-iss-gold-500/10 rounded-full blur-sm group-hover:blur-md transition-all" />
                <div className="relative h-full w-full bg-white rounded-full p-0.5 shadow-sm border border-gray-100 group-hover:shadow-md transition-all">
                  <img
                    src="/iss-logo.svg"
                    alt="ISS"
                    className="w-full h-full object-contain"
                  />
                </div>
              </div>

              {/* Brand Text - Hidden on very small screens */}
              <div className="hidden xs:block sm:block">
                <div className="text-sm sm:text-base lg:text-lg font-bold text-iss-bordeaux-900 leading-tight">
                  ISS
                </div>
                <div className="text-xs text-gray-500 hidden sm:block leading-tight">
                  Hub Bandi APS
                </div>
              </div>
            </div>

            {/* Desktop Navigation - Hidden on mobile */}
            <nav className="hidden lg:flex items-center gap-1">
              {navigation.slice(0, 6).map((item) => (
                <button
                  key={item.name}
                  onClick={() => handleNavigation(item.href)}
                  className="relative flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-iss-bordeaux-900 hover:bg-iss-bordeaux-50 transition-all"
                >
                  {item.icon && <item.icon className="w-4 h-4" />}
                  <span>{item.name}</span>
                  {item.isNew && (
                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                  )}
                </button>
              ))}

              {/* More dropdown */}
              <div className="relative">
                <button
                  onClick={() => setActiveDropdown(activeDropdown === 'more' ? null : 'more')}
                  className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-iss-bordeaux-900 hover:bg-iss-bordeaux-50 transition-all"
                >
                  <span>Altro</span>
                  <ChevronDown className={`w-4 h-4 transition-transform ${activeDropdown === 'more' ? 'rotate-180' : ''}`} />
                </button>

                {activeDropdown === 'more' && (
                  <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-xl shadow-xl border py-1 z-50">
                    {navigation.slice(6).map((item) => (
                      <button
                        key={item.name}
                        onClick={() => handleNavigation(item.href)}
                        className="flex items-center w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        {item.icon && <item.icon className="w-4 h-4 mr-3 text-gray-400" />}
                        <span>{item.name}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </nav>

            {/* Right Actions */}
            <div className="flex items-center gap-2">
              {/* Search - Hidden on mobile */}
              <Button
                variant="ghost"
                size="icon"
                className="hidden md:flex h-9 w-9"
                onClick={() => handleNavigation('/bandi')}
              >
                <Search className="h-4 w-4" />
              </Button>

              {/* Auth Buttons - Desktop */}
              {!isAuthenticated && (
                <div className="hidden sm:flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleNavigation('/auth/login')}
                    className="text-sm"
                  >
                    Accedi
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => handleNavigation('/auth/register')}
                    className="bg-iss-bordeaux-900 hover:bg-iss-bordeaux-800 text-white text-sm"
                  >
                    Registrati
                  </Button>
                </div>
              )}

              {/* User Menu - Desktop */}
              {isAuthenticated && (
                <div className="hidden sm:block relative">
                  <button
                    onClick={() => setActiveDropdown(activeDropdown === 'user' ? null : 'user')}
                    className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-gray-50"
                  >
                    <div className="w-8 h-8 bg-gradient-to-br from-iss-bordeaux-600 to-iss-gold-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                      {getUserInitials(user)}
                    </div>
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  </button>

                  {activeDropdown === 'user' && (
                    <div className="absolute right-0 top-full mt-1 w-56 bg-white rounded-xl shadow-xl border py-1 z-50">
                      <div className="px-4 py-3 border-b">
                        <div className="font-medium text-gray-900 text-sm">{user?.nome} {user?.cognome}</div>
                        <div className="text-xs text-gray-500">{user?.email}</div>
                      </div>
                      <button onClick={() => handleNavigation('/dashboard')} className="flex items-center w-full px-4 py-2.5 text-sm hover:bg-gray-50">
                        <User className="w-4 h-4 mr-3 text-gray-400" />Dashboard
                      </button>
                      <button onClick={() => handleNavigation('/settings')} className="flex items-center w-full px-4 py-2.5 text-sm hover:bg-gray-50">
                        <Settings className="w-4 h-4 mr-3 text-gray-400" />Impostazioni
                      </button>
                      <div className="border-t my-1" />
                      <button onClick={handleLogout} className="flex items-center w-full px-4 py-2.5 text-sm text-red-600 hover:bg-red-50">
                        <LogOut className="w-4 h-4 mr-3" />Logout
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Mobile Menu Toggle */}
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden h-9 w-9"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                aria-label={isMenuOpen ? 'Chiudi menu' : 'Apri menu'}
              >
                {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Menu Overlay - z-40 */}
      {isMenuOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 lg:hidden"
          onClick={() => setIsMenuOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Mobile Slide-out Menu - z-45 (between overlay and header) */}
      <div
        className={`fixed top-14 sm:top-16 left-0 right-0 bottom-0 bg-white z-[45] lg:hidden transform transition-transform duration-300 ease-out overflow-y-auto ${isMenuOpen ? 'translate-x-0' : 'translate-x-full'
          }`}
      >
        <div className="p-4 pb-20">
          {/* Navigation Items */}
          <nav className="space-y-1">
            {navigation.map((item) => (
              <button
                key={item.name}
                onClick={() => handleNavigation(item.href)}
                className="flex items-center justify-between w-full px-4 py-3.5 rounded-xl text-left hover:bg-iss-bordeaux-50 active:bg-iss-bordeaux-100 transition-colors"
              >
                <div className="flex items-center gap-3">
                  {item.icon && <item.icon className="w-5 h-5 text-iss-bordeaux-600" />}
                  <span className="font-medium text-gray-900">{item.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  {item.isNew && (
                    <span className="w-2 h-2 bg-green-500 rounded-full" />
                  )}
                  {item.badge && (
                    <Badge variant="secondary" className="text-xs bg-iss-gold-100 text-iss-gold-800">
                      {item.badge}
                    </Badge>
                  )}
                </div>
              </button>
            ))}
          </nav>

          {/* Auth Section - Mobile */}
          <div className="mt-6 pt-6 border-t border-gray-100">
            {!isAuthenticated ? (
              <div className="space-y-3">
                <Button
                  onClick={() => handleNavigation('/auth/login')}
                  variant="outline"
                  className="w-full h-12 text-base"
                >
                  Accedi
                </Button>
                <Button
                  onClick={() => handleNavigation('/auth/register')}
                  className="w-full h-12 text-base bg-iss-bordeaux-900 hover:bg-iss-bordeaux-800"
                >
                  Registrati Gratuitamente
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center gap-3 p-4 bg-iss-bordeaux-50 rounded-xl">
                  <div className="w-12 h-12 bg-gradient-to-br from-iss-bordeaux-600 to-iss-gold-500 rounded-full flex items-center justify-center text-white font-semibold">
                    {getUserInitials(user)}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{user?.nome} {user?.cognome}</div>
                    <div className="text-sm text-gray-600">{getUserRole(user?.role)}</div>
                  </div>
                </div>
                <div className="space-y-1">
                  <button onClick={() => handleNavigation('/dashboard')} className="flex items-center w-full px-4 py-3 rounded-xl hover:bg-gray-50">
                    <User className="w-5 h-5 mr-3 text-gray-500" />
                    <span className="font-medium">Dashboard</span>
                  </button>
                  <button onClick={() => handleNavigation('/settings')} className="flex items-center w-full px-4 py-3 rounded-xl hover:bg-gray-50">
                    <Settings className="w-5 h-5 mr-3 text-gray-500" />
                    <span className="font-medium">Impostazioni</span>
                  </button>
                  <button onClick={handleLogout} className="flex items-center w-full px-4 py-3 rounded-xl text-red-600 hover:bg-red-50">
                    <LogOut className="w-5 h-5 mr-3" />
                    <span className="font-medium">Logout</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};
