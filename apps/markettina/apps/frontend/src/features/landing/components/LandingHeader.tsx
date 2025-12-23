import { useState } from 'react';
import { Sun, Moon, Menu, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useLanguage, LanguageSelector } from '../../../shared/i18n';
import { useTheme } from '../../../shared/contexts/ThemeContext';

export function LandingHeader() {
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const isDark = theme === 'dark';

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
      setMobileMenuOpen(false);
    }
  };

  return (
    <header className="fixed top-0 w-full z-50 bg-background/90 backdrop-blur-xl border-b border-border">
      <nav className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        {/* Logo */}
        {/* Logo */}
        <div className="flex items-center gap-3 cursor-pointer h-10" onClick={() => window.scrollTo(0, 0)}>
          <img
            src="/markettina-icon.png"
            alt="Markettina"
            className="h-full w-auto object-contain"
          />
          <span className="text-xl font-bold tracking-tight text-foreground">MARKETTINA</span>
        </div>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-6">
          <button onClick={() => scrollToSection('features')} className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
            Features
          </button>
          <button onClick={() => scrollToSection('how-it-works')} className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
            Come Funziona
          </button>

          <div className="h-6 w-px bg-border mx-2" />

          {/* Toggles */}
          <LanguageSelector />
          <button
            onClick={toggleTheme}
            className="p-2 rounded-full hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Toggle Theme"
          >
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>

          <div className="h-6 w-px bg-border mx-2" />

          <button onClick={() => navigate('/admin/login')} className="text-sm font-medium text-foreground hover:text-primary transition-colors">
            Login
          </button>
          <button
            onClick={() => navigate('/admin/login')}
            className="px-5 py-2 bg-primary text-primary-foreground text-sm font-bold rounded-lg hover:brightness-110 transition-all shadow-lg shadow-primary/20"
          >
            Inizia Gratis
          </button>
        </div>

        {/* Mobile Menu Toggle */}
        <div className="flex items-center gap-4 md:hidden">
          <LanguageSelector />
          <button
            onClick={toggleTheme}
            className="p-2 text-foreground"
          >
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
          <button
            className="text-foreground ml-2"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="absolute top-full left-0 w-full bg-background border-b border-border p-6 flex flex-col gap-4 md:hidden shadow-2xl">
          <button onClick={() => scrollToSection('features')} className="text-left text-lg font-medium text-muted-foreground">
            Features
          </button>
          <button onClick={() => scrollToSection('how-it-works')} className="text-left text-lg font-medium text-muted-foreground">
            Come Funziona
          </button>
          <div className="h-px bg-border my-2" />
          <button onClick={() => navigate('/admin/login')} className="text-left text-lg font-medium text-foreground">
            Login
          </button>
          <button
            onClick={() => navigate('/admin/login')}
            className="w-full py-3 bg-primary text-primary-foreground font-bold rounded-lg text-center shadow-lg shadow-primary/20"
          >
            Inizia Gratis
          </button>
        </div>
      )}
    </header>
  );
}
