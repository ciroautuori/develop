import React, { createContext, useContext, useState, useEffect } from 'react';
import { translations } from './translations';

type Language = 'it' | 'en';
type Translations = typeof translations.it;

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: Translations;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Language>('it');

  useEffect(() => {
    const savedLang = localStorage.getItem('markettina-lang') as Language;
    if (savedLang && (savedLang === 'it' || savedLang === 'en')) {
      setLanguage(savedLang);
    }
  }, []);

  const handleSetLanguage = (lang: Language) => {
    setLanguage(lang);
    localStorage.setItem('markettina-lang', lang);
  };

  const value = {
    language,
    setLanguage: handleSetLanguage,
    t: translations[language],
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}

export function LanguageSelector() {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => setLanguage('it')}
        className={`px-2 py-1 rounded text-sm font-medium transition-colors ${language === 'it'
            ? 'text-gold bg-white/10'
            : 'text-gray-400 hover:text-white'
          }`}
      >
        IT
      </button>
      <span className="text-gray-600">|</span>
      <button
        onClick={() => setLanguage('en')}
        className={`px-2 py-1 rounded text-sm font-medium transition-colors ${language === 'en'
            ? 'text-gold bg-white/10'
            : 'text-gray-400 hover:text-white'
          }`}
      >
        EN
      </button>
    </div>
  );
}
