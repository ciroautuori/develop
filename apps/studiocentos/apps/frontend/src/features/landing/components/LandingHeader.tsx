/**
 * Landing Header Component - Con Theme Toggle + Language Selector + Mobile Menu
 */
import { useState, useEffect } from 'react';
import { Sun, Moon, Menu, X } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useLanguage, LanguageSelector } from '../i18n';
import { Button } from '../../../shared/components/ui/button';
import { BuyMeCoffeeButton } from '../../../shared/components/ui/BuyMeCoffeeButton';

export function LandingHeader() {
  const { t } = useLanguage();
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const isHome = location.pathname === '/';

  // Load theme from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('studiocentos-theme') as 'dark' | 'light';
    if (saved) {
      setTheme(saved);
      document.documentElement.classList.remove('dark', 'light');
      document.documentElement.classList.add(saved);
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    document.documentElement.classList.remove('dark', 'light');
    document.documentElement.classList.add(newTheme);
    localStorage.setItem('studiocentos-theme', newTheme);
  };

  const handleNavClick = (e: React.MouseEvent<HTMLElement>, id: string) => {
    e.preventDefault();
    setMobileMenuOpen(false);

    if (isHome) {
      document.querySelector(id)?.scrollIntoView({ behavior: 'smooth' });
    } else {
      // Navigate to home with hash
      navigate(`/${id}`);
      // Optional: wait for nav and scroll
      setTimeout(() => {
        document.querySelector(id)?.scrollIntoView({ behavior: 'smooth' });
      }, 500);
    }
  };

  return (
    <header className="fixed top-0 w-full z-50 bg-background/90 backdrop-blur-xl border-b border-border transition-colors duration-300">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 py-3 sm:py-4 flex justify-between items-center">
        {/* Logo - Click torna alla home */}
        <a href="/" className="flex items-center gap-2 sm:gap-3 group relative z-50">
          <div className="relative w-8 h-8 sm:w-10 sm:h-10 flex items-center justify-center">
            {/* Glow pulsante */}
            <div className="absolute inset-[-8px] rounded-full bg-[radial-gradient(circle,rgba(212,175,55,0.4)_0%,transparent_70%)] animate-pulse-glow" />

            {/* Logo SVG con animazioni */}
            <svg viewBox="0 0 100 100" className="w-full h-full relative z-10 animate-float">
              {/* Raggi rotanti */}
              <g className="animate-rotate-rays" style={{ transformOrigin: '50% 50%' }}>
                <line x1="50" y1="20" x2="50" y2="10" stroke="#D4AF37" strokeWidth="2" />
                <line x1="65" y1="25" x2="72" y2="18" stroke="#D4AF37" strokeWidth="2" />
                <line x1="70" y1="50" x2="80" y2="50" stroke="#D4AF37" strokeWidth="2" />
                <line x1="65" y1="75" x2="72" y2="82" stroke="#D4AF37" strokeWidth="2" />
                <line x1="50" y1="80" x2="50" y2="90" stroke="#D4AF37" strokeWidth="2" />
                <line x1="35" y1="75" x2="28" y2="82" stroke="#D4AF37" strokeWidth="2" />
                <line x1="30" y1="50" x2="20" y2="50" stroke="#D4AF37" strokeWidth="2" />
                <line x1="35" y1="25" x2="28" y2="18" stroke="#D4AF37" strokeWidth="2" />
              </g>

              {/* Lampadina centrale con brightness */}
              <circle cx="50" cy="50" r="20" fill="none" stroke="#D4AF37" strokeWidth="2" className="animate-brightness" />
              <path d="M 45 55 L 48 60 L 52 60 L 55 55" fill="none" stroke="#D4AF37" strokeWidth="2" className="animate-brightness" />
            </svg>
          </div>
          <div>
            <div className="text-base sm:text-xl font-bold tracking-tight text-foreground">
              <span className="text-primary">STUDIO</span><span className="group-hover:text-primary transition-colors duration-300">CENTOS</span>
            </div>
          </div>
        </a>

        {/* Mobile Controls - Sempre visibili */}
        <div className="flex md:hidden items-center gap-2 relative z-50">
          {/* Language Toggle - Sempre visibile */}
          <LanguageSelector />

          {/* Menu Button */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? (
              <X className="h-6 w-6 text-primary" />
            ) : (
              <Menu className="h-6 w-6 text-primary" />
            )}
          </Button>
        </div>
        {/* Desktop Menu */}
        <div className="hidden md:flex items-center gap-1.5 lg:gap-6 text-xs lg:text-sm tracking-tight text-nowrap">
          <a
            href="#chi-siamo"
            className="text-muted-foreground hover:text-primary transition font-medium px-1 lg:px-0"
            onClick={(e) => handleNavClick(e, '#chi-siamo')}
          >
            {t.nav.chiSiamo}
          </a>
          <a
            href="#servizi"
            className="text-muted-foreground hover:text-primary transition font-medium px-1 lg:px-0"
            onClick={(e) => handleNavClick(e, '#servizi')}
          >
            {t.nav.servizi}
          </a>
          <a
            href="#progetti"
            className="text-muted-foreground hover:text-primary transition font-medium px-1 lg:px-0"
            onClick={(e) => handleNavClick(e, '#progetti')}
          >
            {t.nav.progetti}
          </a>
          <a
            href="#corsi"
            className="text-muted-foreground hover:text-primary transition font-medium px-1 lg:px-0"
            onClick={(e) => handleNavClick(e, '#corsi')}
          >
            {t.nav.academy}
          </a>
          <a
            href="#toolai"
            className="text-muted-foreground hover:text-primary transition font-medium px-1 lg:px-0"
            onClick={(e) => handleNavClick(e, '#toolai')}
          >
            {t.nav.toolai}
          </a>
          <a
            href="#contatti"
            className="text-muted-foreground hover:text-primary transition font-medium px-1 lg:px-0"
            onClick={(e) => handleNavClick(e, '#contatti')}
          >
            {t.nav.contatti}
          </a>

          {/* Language Selector */}
          <div className="scale-90 lg:scale-100">
            <LanguageSelector />
          </div>

          {/* Buy Me a Coffee - Visible on MD and LG */}
          <div className="scale-90 lg:scale-100">
            <BuyMeCoffeeButton variant="compact" />
          </div>

          {/* Theme Toggle */}
          <Button
            variant="outline"
            size="icon"
            onClick={toggleTheme}
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? (
              <Sun className="h-5 w-5 text-primary" />
            ) : (
              <Moon className="h-5 w-5 text-primary" />
            )}
          </Button>

          <Button
            asChild
            className="px-4 lg:px-6 font-medium shadow-lg hover:shadow-xl"
            onClick={(e) => handleNavClick(e, '#contatti')}
          >
            <a href="#contatti">
              {t.nav.contattaci}
            </a>
          </Button>
        </div>

        {/* Mobile Menu Overlay */}
        {mobileMenuOpen && (
          <div
            className="fixed inset-0 bg-background/60 backdrop-blur-sm z-40 md:hidden"
            onClick={() => setMobileMenuOpen(false)}
          />
        )}

        {/* Mobile Menu Panel */}
        <div
          className={`
            fixed top-[60px] right-0 bottom-0 w-72 max-w-[80vw] z-40
            bg-background border-l border-border shadow-2xl
            transform transition-transform duration-300 ease-out
            md:hidden
            ${mobileMenuOpen
              ? 'translate-x-0'
              : 'translate-x-full'
            }
          `}
        >
          <div className="flex flex-col h-full p-6 space-y-6">
            {/* Mobile Nav Links */}
            <div className="flex flex-col space-y-4">
              <a
                href="#chi-siamo"
                className="text-lg text-muted-foreground hover:text-primary transition font-medium py-2"
                onClick={(e) => handleNavClick(e, '#chi-siamo')}
              >
                {t.nav.chiSiamo}
              </a>
              <a
                href="#servizi"
                className="text-lg text-muted-foreground hover:text-primary transition font-medium py-2"
                onClick={(e) => handleNavClick(e, '#servizi')}
              >
                {t.nav.servizi}
              </a>
              <a
                href="#progetti"
                className="text-lg text-muted-foreground hover:text-primary transition font-medium py-2"
                onClick={(e) => handleNavClick(e, '#progetti')}
              >
                {t.nav.progetti}
              </a>
              <a
                href="#toolai"
                className="text-lg text-muted-foreground hover:text-primary transition font-medium py-2"
                onClick={(e) => handleNavClick(e, '#toolai')}
              >
                {t.nav.toolai}
              </a>
              <a
                href="#contatti"
                className="text-lg text-muted-foreground hover:text-primary transition font-medium py-2"
                onClick={(e) => handleNavClick(e, '#contatti')}
              >
                {t.nav.contatti}
              </a>
            </div>

            {/* Divider */}
            <div className="border-t border-border" />

            {/* Theme Toggle Mobile */}
            <Button
              variant="outline"
              className="flex items-center justify-between w-full p-3 h-auto"
              onClick={toggleTheme}
            >
              <span className="text-foreground font-medium">
                {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
              </span>
              {theme === 'dark' ? (
                <Sun className="h-5 w-5 text-primary" />
              ) : (
                <Moon className="h-5 w-5 text-primary" />
              )}
            </Button>

            {/* CTA Button Mobile */}
            <Button
              asChild
              className="w-full text-center font-medium shadow-lg hover:shadow-xl"
              onClick={(e) => handleNavClick(e, '#contatti')}
            >
              <a href="#contatti">
                {t.nav.contattaci}
              </a>
            </Button>
          </div>
        </div>
      </nav>
    </header>
  );
}
