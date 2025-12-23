/**
 * GDPR Compliant Cookie Banner - Multi-language
 * Uses CSS animations instead of framer-motion to avoid hydration errors
 */
import { useState, useEffect } from 'react';
import { Cookie, X, Settings, Shield, BarChart3, Megaphone } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../i18n';

interface CookiePreferences {
  necessary: boolean;
  analytics: boolean;
  marketing: boolean;
}

const COOKIE_CONSENT_KEY = 'studiocentos-cookie-consent';
const COOKIE_PREFERENCES_KEY = 'studiocentos-cookie-preferences';

export function CookieBanner() {
  const { t } = useLanguage();
  const c = t.cookies;

  const [showBanner, setShowBanner] = useState(false);
  const [showCustomize, setShowCustomize] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [preferences, setPreferences] = useState<CookiePreferences>({
    necessary: true,
    analytics: false,
    marketing: false,
  });

  useEffect(() => {
    const consent = localStorage.getItem(COOKIE_CONSENT_KEY);
    if (!consent) {
      const timer = setTimeout(() => {
        setShowBanner(true);
        setTimeout(() => setIsVisible(true), 50);
      }, 1500);
      return () => clearTimeout(timer);
    } else {
      const savedPrefs = localStorage.getItem(COOKIE_PREFERENCES_KEY);
      if (savedPrefs) {
        setPreferences(JSON.parse(savedPrefs));
      }
    }
  }, []);

  const saveConsent = (prefs: CookiePreferences) => {
    localStorage.setItem(COOKIE_CONSENT_KEY, 'true');
    localStorage.setItem(COOKIE_PREFERENCES_KEY, JSON.stringify(prefs));
    setPreferences(prefs);

    // Update Google Consent Mode v2
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('consent', 'update', {
        'ad_storage': prefs.marketing ? 'granted' : 'denied',
        'ad_user_data': prefs.marketing ? 'granted' : 'denied',
        'ad_personalization': prefs.marketing ? 'granted' : 'denied',
        'analytics_storage': prefs.analytics ? 'granted' : 'denied'
      });
    }

    setIsVisible(false);
    setTimeout(() => {
      setShowBanner(false);
      setShowCustomize(false);
    }, 300);
    window.dispatchEvent(new CustomEvent('cookieConsentUpdated', { detail: prefs }));
  };

  const acceptAll = () => saveConsent({ necessary: true, analytics: true, marketing: true });
  const acceptNecessary = () => saveConsent({ necessary: true, analytics: false, marketing: false });
  const saveCustom = () => saveConsent(preferences);

  if (!showBanner) return null;

  return (
    <div
      className={`fixed bottom-0 left-0 right-0 z-[9999] p-3 md:p-6 transition-all duration-300 ease-out ${
        isVisible ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'
      }`}
    >
      <div
        className="w-full max-w-4xl mx-auto bg-black/95 light:bg-white/95 backdrop-blur-xl rounded-2xl border border-white/10 light:border-gray-200 shadow-2xl flex flex-col"
        style={{ maxHeight: '70vh' }}
      >
        {!showCustomize ? (
          <div className="p-4 md:p-6 overflow-y-auto">
            <div className="flex flex-col md:flex-row items-start gap-4">
              <div className="flex items-center gap-3 md:block">
                <div className="p-2 md:p-3 rounded-xl bg-gold/20 shrink-0">
                  <Cookie className="w-5 h-5 md:w-6 md:h-6 text-gold" />
                </div>
                <h3 className="text-base font-bold text-white light:text-gray-900 md:hidden">{c.title}</h3>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="hidden md:block text-lg font-semibold text-white light:text-gray-900 mb-2">{c.title}</h3>
                <p className="text-xs md:text-sm text-white/70 light:text-gray-600 leading-relaxed mb-3 md:mb-4">
                  {c.description}
                </p>
                <p className="text-[10px] md:text-xs text-white/50 light:text-gray-500">
                  {c.moreInfo}{' '}
                  <Link to="/privacy" className="text-gold hover:underline">{c.privacyLink}</Link>
                </p>
              </div>
            </div>
            <div className="grid grid-cols-2 sm:flex sm:flex-row gap-3 mt-4 md:mt-6">
              <button onClick={acceptAll} className="col-span-2 sm:flex-1 px-6 py-3 bg-gold text-black font-bold rounded-xl hover:bg-gold-dark transition-all text-sm sm:text-base shadow-[0_0_20px_-5px_rgba(212,175,55,0.3)]">
                {c.acceptAll}
              </button>
              <button onClick={acceptNecessary} className="col-span-1 sm:flex-1 px-3 sm:px-6 py-3 bg-white/10 light:bg-gray-100 text-white light:text-gray-700 font-medium rounded-xl hover:bg-white/20 light:hover:bg-gray-200 transition-all text-xs sm:text-base whitespace-nowrap">
                {c.acceptNecessary}
              </button>
              <button onClick={() => setShowCustomize(true)} className="col-span-1 flex items-center justify-center gap-2 px-3 sm:px-6 py-3 border border-white/20 light:border-gray-300 text-white light:text-gray-700 rounded-xl hover:bg-white/5 light:hover:bg-gray-50 transition-all text-xs sm:text-base">
                <Settings className="w-4 h-4" />
                {c.customize}
              </button>
            </div>
          </div>
        ) : (
          <div className="p-4 md:p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-white light:text-gray-900 flex items-center gap-2">
                <Settings className="w-5 h-5 text-gold" />
                {c.customize}
              </h3>
              <button onClick={() => setShowCustomize(false)} className="p-2 hover:bg-white/10 light:hover:bg-gray-100 rounded-lg transition-colors">
                <X className="w-5 h-5 text-white/60 light:text-gray-500" />
              </button>
            </div>
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-white/5 light:bg-gray-50 border border-white/10 light:border-gray-200">
                <div className="flex items-start md:items-center justify-between gap-4">
                  <div className="flex items-start md:items-center gap-3">
                    <Shield className="w-5 h-5 text-gold shrink-0 mt-1 md:mt-0" />
                    <div>
                      <p className="font-medium text-white light:text-gray-900">{c.necessary}</p>
                      <p className="text-xs text-white/50 light:text-gray-500">{c.necessaryDesc}</p>
                    </div>
                  </div>
                  <div className="px-3 py-1 bg-gold/20 text-gold light:text-gold text-xs rounded-full shrink-0">{c.alwaysActive}</div>
                </div>
              </div>
              <div className="p-4 rounded-xl bg-white/5 light:bg-gray-50 border border-white/10 light:border-gray-200">
                <div className="flex items-start md:items-center justify-between gap-4">
                  <div className="flex items-start md:items-center gap-3">
                    <BarChart3 className="w-5 h-5 text-gold shrink-0 mt-1 md:mt-0" />
                    <div>
                      <p className="font-medium text-white light:text-gray-900">{c.analytics}</p>
                      <p className="text-xs text-white/50 light:text-gray-500">{c.analyticsDesc}</p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer shrink-0">
                    <input type="checkbox" checked={preferences.analytics} onChange={(e) => setPreferences(p => ({ ...p, analytics: e.target.checked }))} className="sr-only peer" />
                    <div className="w-11 h-6 bg-white/20 light:bg-gray-300 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-gold rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gold"></div>
                  </label>
                </div>
              </div>
              <div className="p-4 rounded-xl bg-white/5 light:bg-gray-50 border border-white/10 light:border-gray-200">
                <div className="flex items-start md:items-center justify-between gap-4">
                  <div className="flex items-start md:items-center gap-3">
                    <Megaphone className="w-5 h-5 text-gold shrink-0 mt-1 md:mt-0" />
                    <div>
                      <p className="font-medium text-white light:text-gray-900">{c.marketing}</p>
                      <p className="text-xs text-white/50 light:text-gray-500">{c.marketingDesc}</p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer shrink-0">
                    <input type="checkbox" checked={preferences.marketing} onChange={(e) => setPreferences(p => ({ ...p, marketing: e.target.checked }))} className="sr-only peer" />
                    <div className="w-11 h-6 bg-white/20 light:bg-gray-300 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-gold rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gold"></div>
                  </label>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 sm:flex sm:flex-row gap-3 mt-5">
              <button onClick={saveCustom} className="col-span-2 sm:flex-1 px-6 py-3 bg-gold text-black font-bold rounded-xl hover:bg-gold-dark transition-all text-sm sm:text-base shadow-[0_0_20px_-5px_rgba(212,175,55,0.3)]">
                {c.save}
              </button>
              <button onClick={() => setShowCustomize(false)} className="col-span-2 sm:w-auto flex items-center justify-center gap-2 px-6 py-3 border border-white/20 light:border-gray-300 text-white light:text-gray-700 rounded-xl hover:bg-white/5 light:hover:bg-gray-50 transition-all text-sm sm:text-base">
                <X className="w-5 h-5" />
                {c.close}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export function useCookieConsent() {
  const [consent, setConsent] = useState<CookiePreferences | null>(null);

  useEffect(() => {
    const savedPrefs = localStorage.getItem(COOKIE_PREFERENCES_KEY);
    if (savedPrefs) {
      setConsent(JSON.parse(savedPrefs));
    }
    const handleUpdate = (e: CustomEvent<CookiePreferences>) => {
      setConsent(e.detail);
    };
    window.addEventListener('cookieConsentUpdated', handleUpdate as EventListener);
    return () => window.removeEventListener('cookieConsentUpdated', handleUpdate as EventListener);
  }, []);

  return consent;
}

export default CookieBanner;
