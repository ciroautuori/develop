/**
 * Language Context for Landing Page i18n
 */
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { translations, Language } from './translations';

type TranslationType = typeof translations.it | typeof translations.en | typeof translations.es;

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: TranslationType;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const STORAGE_KEY = 'studiocentos-language';

// Detect browser language
function detectBrowserLanguage(): Language {
  const browserLang = navigator.language.split('-')[0];
  if (browserLang === 'es') return 'es';
  if (browserLang === 'en') return 'en';
  return 'it'; // Default Italian
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>('it');

  // Load language from URL, localStorage or detect from browser
  useEffect(() => {
    // 1. Check URL path
    const path = window.location.pathname;
    const pathLang = path.split('/')[1] as Language; // e.g. /en/services -> en

    if (pathLang && ['it', 'en', 'es'].includes(pathLang)) {
      setLanguageState(pathLang);
      localStorage.setItem(STORAGE_KEY, pathLang);
      document.documentElement.lang = pathLang;
      return;
    }

    // 2. Check localStorage
    const saved = localStorage.getItem(STORAGE_KEY) as Language;
    if (saved && ['it', 'en', 'es'].includes(saved)) {
      setLanguageState(saved);
      document.documentElement.lang = saved;
    } else {
      // 3. Fallback to Browser
      const detected = detectBrowserLanguage();
      setLanguageState(detected);
      document.documentElement.lang = detected;
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem(STORAGE_KEY, lang);
    // Update HTML lang attribute
    document.documentElement.lang = lang;
  };

  const t = translations[language];

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
}

// Language selector component - Simple toggle (like theme toggle)
export function LanguageSelector() {
  const { language, setLanguage } = useLanguage();

  const languages: { code: Language; flag: string }[] = [
    { code: 'it', flag: '🇮🇹' },
    { code: 'en', flag: '🇬🇧' },
    { code: 'es', flag: '🇪🇸' },
  ];

  // Cycle to next language on click
  const cycleLanguage = () => {
    const currentIndex = languages.findIndex(l => l.code === language);
    const nextIndex = (currentIndex + 1) % languages.length;
    setLanguage(languages[nextIndex].code);
  };

  const currentLang = languages.find(l => l.code === language) || languages[0];

  return (
    <button
      onClick={cycleLanguage}
      className="p-2 rounded-lg bg-white/5 light:bg-gray-100 hover:bg-white/10 light:hover:bg-gray-200 transition-colors border border-white/10 light:border-gray-200"
      aria-label="Change language"
      title={`${language.toUpperCase()} → Click to change`}
    >
      <span className="text-xl">{currentLang.flag}</span>
    </button>
  );
}
