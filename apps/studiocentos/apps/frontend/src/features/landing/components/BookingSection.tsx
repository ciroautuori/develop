/**
 * Booking Section Component
 * Sezione prenotazione consulenza con integrazione calendario
 * Con supporto multilingua IT/EN/ES
 */

import { useEffect } from 'react';
import { useLanguage } from '../i18n';

export function BookingSection() {
  const { t } = useLanguage();

  useEffect(() => {
    // Carica script Calendly dinamicamente
    const script = document.createElement('script');
    script.src = 'https://assets.calendly.com/assets/external/widget.js';
    script.async = true;
    document.body.appendChild(script);

    return () => {
      // Cleanup
      document.body.removeChild(script);
    };
  }, []);

  return (
    <section id="prenota" className="max-w-4xl mx-auto px-6 py-32">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-light mb-4">
          {t.booking.title} <span className="text-gold">{t.booking.titleHighlight}</span>
        </h2>
        <p className="text-xl text-gray-400 mb-8">
          {t.booking.subtitle}
        </p>
      </div>

      {/* Calendario Prenotazione */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur rounded-3xl p-8 border border-white/10">
        {/*
          INTEGRAZIONE CALENDARIO:
          Sostituisci questo blocco con il tuo sistema di prenotazione:

          Opzione 1: Calendly
          <div className="calendly-inline-widget" data-url="https://calendly.com/studiocentos/consulenza" style={{minWidth:'320px',height:'700px'}}></div>

          Opzione 2: Cal.com
          <div id="my-cal-inline" style={{width:'100%',height:'100%',overflow:'scroll'}}></div>

          Opzione 3: Google Calendar Appointment
          <iframe src="YOUR_GOOGLE_CALENDAR_BOOKING_URL" style={{border:0}} width="100%" height="600" frameBorder="0"></iframe>
        */}

        <div className="text-center py-20">
          <div className="text-6xl mb-6">📅</div>
          <h3 className="text-2xl font-light mb-4">{t.booking.title} {t.booking.titleHighlight}</h3>
          <p className="text-gray-400 mb-8">
            {t.booking.subtitle}
          </p>

          {/* CTA */}
          <div className="space-y-4">
            <a href="https://calendly.com/studiocentos" target="_blank" rel="noopener noreferrer" className="inline-block px-8 py-4 bg-gold text-black rounded-lg hover:bg-[#F4E5B8] transition font-medium">
              {t.booking.submit}
            </a>
            <p className="text-sm text-gray-500">
              📧 ciro@studiocentos.it
            </p>
          </div>
        </div>
      </div>

      {/* Info Consulenza */}
      <div className="mt-12 grid md:grid-cols-3 gap-6 text-center">
        <div className="bg-white/5 rounded-2xl p-6">
          <div className="text-3xl mb-3">⏱️</div>
          <div className="font-medium mb-2">{t.booking.duration}</div>
          <div className="text-sm text-gray-400">{t.booking.infoMeet}</div>
        </div>
        <div className="bg-white/5 rounded-2xl p-6">
          <div className="text-3xl mb-3">💰</div>
          <div className="font-medium mb-2">{t.booking.titleHighlight.split(' ')[0]}</div>
          <div className="text-sm text-gray-400">{t.booking.infoCancel}</div>
        </div>
        <div className="bg-white/5 rounded-2xl p-6">
          <div className="text-3xl mb-3">🎯</div>
          <div className="font-medium mb-2">{t.booking.infoEmail}</div>
          <div className="text-sm text-gray-400">✉️</div>
        </div>
      </div>
    </section>
  );
}
