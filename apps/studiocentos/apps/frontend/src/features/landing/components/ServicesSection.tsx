/**
 * Services Section Component - BENTO GRID MODERNO
 * Layout asimmetrico con hover glow effects + 3D Tilt + FRAMER MOTION
 */

import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import type { Service } from '../types/landing.types';
import { useLanguage } from '../i18n';

interface ServicesSectionProps {
  services: Service[];
}

export function ServicesSection({ services }: ServicesSectionProps) {
  const { t } = useLanguage();
  const cardRefs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    // 3D Tilt effect per ogni card
    cardRefs.current.forEach((card) => {
      if (!card) return;

      const handleMouseMove = (e: MouseEvent) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateX = (y - centerY) / 10;
        const rotateY = (centerX - x) / 10;

        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
      };

      const handleMouseLeave = () => {
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
      };

      card.addEventListener('mousemove', handleMouseMove);
      card.addEventListener('mouseleave', handleMouseLeave);

      return () => {
        card.removeEventListener('mousemove', handleMouseMove);
        card.removeEventListener('mouseleave', handleMouseLeave);
      };
    });
  }, []);

  if (!services || services.length === 0) {
    return null;
  }

  // Filtra solo servizi attivi e ordina
  const activeServices = services
    .filter(s => s.is_active)
    .sort((a, b) => a.order - b.order)
    .slice(0, 5); // Max 5 servizi per bento grid

  if (activeServices.length === 0) {
    return null;
  }

  // Primo servizio è featured (grande)
  const featuredService = activeServices[0];
  const otherServices = activeServices.slice(1);

  // Helper per renderizzare icona (emoji o URL immagine)
  const renderIcon = (icon: string, size: 'sm' | 'md' | 'lg' = 'md') => {
    const sizeClass = size === 'lg' ? 'text-6xl' : size === 'md' ? 'text-4xl' : 'text-2xl';
    const imgSize = size === 'lg' ? 'w-24 h-24' : size === 'md' ? 'w-16 h-16' : 'w-12 h-12';

    // Se è un URL (inizia con http o /)
    if (icon?.startsWith('http') || icon?.startsWith('/')) {
      return <img src={icon} alt="" className={`${imgSize} object-contain`} loading="lazy" />;
    }
    // Altrimenti è emoji
    return <span className={sizeClass}>{icon || '🔧'}</span>;
  };

  return (
    <section id="servizi" className="max-w-6xl mx-auto px-4 md:px-6 py-12 md:py-24">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="mb-20 text-center"
      >
        <h2 className="text-3xl md:text-5xl font-light mb-4 text-white light:text-gray-900">
          {t.services.title} <span className="text-gold">{t.services.titleHighlight}</span>
        </h2>
        <p className="text-lg md:text-xl text-gray-400 light:text-gray-600">{t.services.subtitle}</p>
      </motion.div>

      <div className="bento-grid">
        {/* Servizio principale - GRANDE */}
        <div
          ref={(el) => (cardRefs.current[0] = el)}
          className="bento-item-1 bg-gradient-to-br from-white/10 to-white/5 light:bg-gray-100 rounded-3xl p-8 border border-white/10 light:border-gray-200 hover-glow group transition-colors duration-300 overflow-hidden"
        >
          {/* Immagine thumbnail se presente */}
          {featuredService.thumbnail_url && (
            <div className="-mx-8 -mt-8 mb-6">
              <img
                src={featuredService.thumbnail_url}
                alt={featuredService.title}
                className="w-full h-48 object-cover"
                loading="lazy"
              />
            </div>
          )}

          <div className="flex justify-between items-start mb-6">
            <div>
              <div className="text-sm text-gold mb-2">{t.services.featured}</div>
              <h3 className="text-2xl md:text-4xl font-bold mb-3 group-hover:text-gold transition text-white light:text-gray-900">
                {featuredService.title}
              </h3>
              <p className="text-gray-400 light:text-gray-600 text-lg">{featuredService.description}</p>
            </div>
            {!featuredService.thumbnail_url && renderIcon(featuredService.icon, 'lg')}
          </div>

          <ul className="space-y-2 text-sm text-gray-400 light:text-gray-600 mb-6">
            {featuredService.features?.map((feature, i) => (
              <li key={i}>• {feature}</li>
            ))}
          </ul>

          <a href={featuredService.cta_url || '#prenota'} className="inline-flex items-center gap-2 text-gold hover:underline">
            {featuredService.cta_text} <span>→</span>
          </a>
        </div>

        {/* Altri servizi - PICCOLI */}
        {otherServices.map((service, index) => {
          const itemClass = `bento-item-${index + 2}`;
          return (
            <div
              key={service.id}
              ref={(el) => (cardRefs.current[index + 1] = el)}
              className={`${itemClass} bg-gradient-to-br from-white/10 to-white/5 light:bg-gray-100 rounded-3xl p-6 border border-white/10 light:border-gray-200 hover-glow group transition-colors duration-300 overflow-hidden`}
            >
              {/* Immagine thumbnail se presente */}
              {service.thumbnail_url && (
                <div className="-mx-6 -mt-6 mb-4">
                  <img
                    src={service.thumbnail_url}
                    alt={service.title}
                    className="w-full h-32 object-cover"
                    loading="lazy"
                  />
                </div>
              )}

              {!service.thumbnail_url && (
                <div className="mb-4">{renderIcon(service.icon, 'md')}</div>
              )}

              <h3 className="text-2xl font-bold mb-2 group-hover:text-gold transition text-white light:text-gray-900">
                {service.title}
              </h3>
              <p className="text-sm text-gray-400 light:text-gray-600 mb-4">{service.description}</p>

              {service.features && service.features.length > 0 && (
                <div className="flex gap-2 flex-wrap">
                  {service.features.slice(0, 2).map((feature, i) => (
                    <span key={i} className="px-3 py-1 bg-white/5 light:bg-gray-200 rounded-full text-xs text-gray-300 light:text-gray-700">
                      {feature}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
