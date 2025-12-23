/**
 * Landing Footer Component
 */
import { Link } from 'react-router-dom';
import { useLanguage } from '../i18n';
import { BuyMeCoffeeButton } from '../../../shared/components/ui/BuyMeCoffeeButton';

export function LandingFooter() {
  const currentYear = new Date().getFullYear();
  const { t } = useLanguage();

  return (
    <footer className="border-t border-white/5 light:border-gray-200 py-12">
      <div className="max-w-6xl mx-auto px-6 text-center text-gray-500 text-sm">
        <div className="flex items-center justify-center gap-2 mb-4">
          <div className="w-6 h-6">
            <svg viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="20" fill="none" stroke="#D4AF37" strokeWidth="2" />
              <line x1="50" y1="20" x2="50" y2="10" stroke="#D4AF37" strokeWidth="2" />
            </svg>
          </div>
          <span className="text-white light:text-gray-900">
            STUDIO<span className="text-gold">CENTOS</span>
          </span>
        </div>
        <p className="text-gray-400 light:text-gray-600">{t.footer.tagline}</p>
        <p className="mt-2 text-gray-400 light:text-gray-600">{t.footer.location}</p>

        {/* Legal Links */}
        <div className="mt-6 flex items-center justify-center gap-4 flex-wrap">
          <Link
            to="/privacy"
            className="text-gray-400 hover:text-gold transition-colors"
          >
            {t.footer.privacy}
          </Link>
          <span className="text-gray-600">•</span>
          <Link
            to="/terms"
            className="text-gray-400 hover:text-gold transition-colors"
          >
            {t.footer.terms}
          </Link>
          <span className="text-gray-600">•</span>
          <BuyMeCoffeeButton variant="compact" />
        </div>

        <p className="mt-4 text-xs text-gray-500">
          © {currentYear} StudiocentOS. {t.footer.rights}
        </p>
      </div>
    </footer>
  );
}
