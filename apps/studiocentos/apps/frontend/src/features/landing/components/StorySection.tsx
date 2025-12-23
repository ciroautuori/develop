/**
 * Story Section Component - La mia storia
 * CEO: Ciro Autuori - Founder StudioCentOS (2023)
 */

import { useLanguage } from '../i18n';

export function StorySection() {
  const { t } = useLanguage();

  return (
    <section id="storia" className="max-w-4xl mx-auto px-6 py-32">
      <h2 className="text-4xl font-light mb-12 text-white light:text-gray-900">
        {t.story.title} <span className="text-gold">{t.story.titleHighlight}</span>
      </h2>
      <div className="space-y-8 text-lg text-gray-400 light:text-gray-600 leading-relaxed">
        <p>{t.story.p1}</p>
        <p>
          {t.story.p2Start} <span className="text-white light:text-gray-900 font-medium">StudioCentOS</span> {t.story.p2End}
        </p>
        <p>
          {t.story.p3Start} <span className="text-white light:text-gray-900 font-medium">{t.story.p3Role}</span>{' '}
          <a
            href="https://innovazionesocialesalernitana.it/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gold hover:text-[#F4E5B8] underline underline-offset-4 transition-colors"
          >
            Innovazione Sociale Salernitana
          </a>{t.story.p3End}
        </p>
        <p>{t.story.p4}</p>
        <div className="p-8 bg-white/5 light:bg-gray-100 rounded-2xl border-l-4 border-gold">
          <p className="text-white light:text-gray-900 text-xl font-light italic">
            {t.story.quote}
          </p>
        </div>
      </div>
    </section>
  );
}
