/**
 * Terms of Service Page - Multi-language
 */
import { motion } from 'framer-motion';
import { ArrowLeft, FileText, Mail } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLanguage, LanguageSelector, LanguageProvider } from '../i18n';

function TermsOfServiceContent() {
  const { t } = useLanguage();
  const terms = t.terms;

  const sectionOrder = [
    'acceptance',
    'services',
    'account',
    'payment',
    'intellectual',
    'warranties',
    'limitations',
    'termination',
    'modifications',
    'law',
    'contact',
  ] as const;

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-900 to-black light:from-white light:via-gray-50 light:to-white text-white light:text-gray-900">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-[#0A0A0A]/80 light:bg-white/80 backdrop-blur-lg border-b border-white/10 light:border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link
            to="/"
            className="flex items-center gap-2 text-white/70 light:text-gray-600 hover:text-white light:hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Torna alla home</span>
          </Link>
          <LanguageSelector />
        </div>
      </header>

      {/* Content */}
      <main className="pt-24 pb-16 px-4">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Title */}
            <div className="text-center mb-12">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gold/20 mb-6">
                <FileText className="w-8 h-8 text-gold" />
              </div>
              <h1 className="text-4xl md:text-5xl font-bold mb-4">{terms.title}</h1>
              <p className="text-white/60 light:text-gray-500">
                {terms.lastUpdate}: 29 Novembre 2025
              </p>
            </div>

            {/* Intro */}
            <div className="bg-white/5 light:bg-gray-50 rounded-2xl p-6 md:p-8 mb-8 border border-white/10 light:border-gray-200">
              <p className="text-lg text-white/80 light:text-gray-700 leading-relaxed">{terms.intro}</p>
            </div>

            {/* Sections */}
            <div className="space-y-6">
              {sectionOrder.map((key, index) => {
                const section = terms.sections[key];
                return (
                  <motion.section
                    key={key}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.05 }}
                    className="bg-white/5 light:bg-gray-50 rounded-2xl p-6 md:p-8 border border-white/10 light:border-gray-200 hover:border-gold/30 transition-colors"
                  >
                    <h2 className="text-xl md:text-2xl font-semibold mb-4 text-gold">
                      {section.title}
                    </h2>
                    <p className="text-white/70 light:text-gray-600 leading-relaxed mb-4">{section.content}</p>

                    {'items' in section && section.items && (
                      <ul className="space-y-2 ml-4">
                        {section.items.map((item: string, i: number) => (
                          <li key={i} className="flex items-start gap-3 text-white/70 light:text-gray-600">
                            <span className="text-gold mt-1">•</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </motion.section>
                );
              })}
            </div>

            {/* Contact CTA */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              className="mt-12 text-center"
            >
              <div className="bg-gradient-to-r from-gold/20 to-transparent rounded-2xl p-8 border border-gold/30">
                <Mail className="w-12 h-12 text-gold mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">Hai domande sui termini?</h3>
                <p className="text-white/60 light:text-gray-500 mb-4">Il nostro team legale è a disposizione</p>
                <a
                  href="mailto:legal@studiocentos.it"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gold text-black font-medium rounded-xl hover:bg-[#B8963A] transition-colors"
                >
                  <Mail className="w-5 h-5" />
                  legal@studiocentos.it
                </a>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 light:border-gray-200 py-8 text-center text-white/40 light:text-gray-500">
        <p>© {new Date().getFullYear()} StudioCentOS. {t.footer.rights}</p>
      </footer>
    </div>
  );
}

export function TermsOfService() {
  return (
    <LanguageProvider>
      <TermsOfServiceContent />
    </LanguageProvider>
  );
}

export default TermsOfService;
