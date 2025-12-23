/**
 * Service Card Component
 * DINAMICO - Supporta emoji o URL immagine
 */

import type { Service } from '../types/landing.types';

interface ServiceCardProps {
  service: Service;
}

export function ServiceCard({ service }: ServiceCardProps) {
  // Helper per renderizzare icona (emoji o URL immagine)
  const renderIcon = () => {
    const icon = service.icon;
    // Se è un URL (inizia con http o /)
    if (icon?.startsWith('http') || icon?.startsWith('/')) {
      return <img src={icon} alt="" className="w-16 h-16 object-contain mb-4" loading="lazy" />;
    }
    // Altrimenti è emoji
    return <div className="text-4xl mb-4">{icon || '🔧'}</div>;
  };

  return (
    <div className="bg-white/5 light:bg-gray-100 backdrop-blur rounded-2xl p-8 border border-white/10 light:border-gray-200 hover:border-gold/50 transition hover-lift overflow-hidden">
      {/* Immagine thumbnail se presente */}
      {service.thumbnail_url && (
        <div className="-mx-8 -mt-8 mb-6">
          <img
            src={service.thumbnail_url}
            alt={service.title}
            className="w-full h-40 object-cover"
            loading="lazy"
          />
        </div>
      )}

      {!service.thumbnail_url && renderIcon()}

      <h3 className="text-2xl font-light mb-3 text-white light:text-gray-900">{service.title}</h3>
      <p className="text-gray-400 light:text-gray-600 mb-6">{service.description}</p>

      <ul className="space-y-2 text-sm text-gray-400 light:text-gray-600 mb-6">
        {service.features?.map((feature, i) => (
          <li key={i}>• {feature}</li>
        ))}
      </ul>

      {service.value_indicator && (
        <div className="text-xs text-gray-500 mb-4">
          {service.value_indicator}
        </div>
      )}

      <a href={service.cta_url || '#contatti'} className="inline-block px-6 py-3 bg-white/5 light:bg-gray-200 hover:bg-white/10 light:hover:bg-gray-300 rounded-lg transition text-white light:text-gray-900">
        {service.cta_text}
      </a>
    </div>
  );
}
