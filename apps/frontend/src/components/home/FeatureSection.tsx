import { Card, CardContent } from '@/components/ui/card';
import {
  Target,
  Accessibility,
  Heart,
  Zap,
  BookOpen,
  TrendingUp,
  Shield,
  Users,
  Globe,
  Award
} from 'lucide-react';

const features = [
  {
    icon: Target,
    title: 'Ricerca Intelligente',
    description: 'Trova bandi rilevanti in <2 secondi con filtri avanzati, autocomplete e matching intelligente per la tua APS.',
    highlight: '<2 secondi',
    color: 'text-iss-gold-600'
  },
  {
    icon: Accessibility,
    title: '100% Accessibile',
    description: 'Conformità WCAG 2.1 AA completa. Usabile da persone con disabilità attraverso screen reader, navigazione tastiera e supporto completo.',
    highlight: 'WCAG 2.1 AA',
    color: 'text-iss-gold-600'
  },
  {
    icon: Heart,
    title: 'Completamente Gratuito',
    description: 'Zero costi per sempre. Nessun abbonamento, nessuna commissione. Democratizziamo l\'accesso ai finanziamenti per tutte le APS.',
    highlight: 'Zero costi',
    color: 'text-iss-gold-600'
  },
  {
    icon: Zap,
    title: 'Performance Enterprise',
    description: '110+ richieste/secondo con latenza <10ms. Architettura scalabile per migliaia di APS simultanee.',
    highlight: '110+ richieste/secondo',
    color: 'text-iss-gold-600'
  },
  {
    icon: BookOpen,
    title: 'Formazione Digitale',
    description: 'Corsi 100% gratuiti per alfabetizzazione digitale, certificazioni riconosciute e supporto continuo.',
    highlight: '100% gratuiti',
    color: 'text-iss-gold-600'
  },
  {
    icon: TrendingUp,
    title: 'Monitoraggio 24/7',
    description: 'Sistema automatico che monitora 100+ fonti continuamente. Notifiche immediate per nuovi bandi rilevanti.',
    highlight: '100+ fonti',
    color: 'text-iss-gold-600'
  }
];

const additionalFeatures = [
  {
    icon: Shield,
    title: 'Sicurezza Enterprise',
    description: 'Crittografia end-to-end, backup automatici e conformità GDPR per proteggere i dati delle APS.',
    highlight: 'GDPR compliant',
    color: 'text-blue-600'
  },
  {
    icon: Users,
    title: 'Community APS',
    description: 'Network di APS campane per condividere esperienze, best practice e collaborazioni.',
    highlight: 'APS campane',
    color: 'text-green-600'
  },
  {
    icon: Globe,
    title: 'Open Source',
    description: 'Codice aperto, trasparente e verificabile. Contribuisci allo sviluppo della piattaforma.',
    highlight: 'Open Source',
    color: 'text-purple-600'
  }
];

export function FeatureSection() {
  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-iss-gold-100 text-iss-gold-800 px-4 py-2 rounded-full text-sm font-semibold mb-4">
            <Award className="w-4 h-4" />
            Perché scegliere ISS
          </div>
          <h2 className="text-3xl lg:text-5xl font-bold text-iss-bordeaux-900 mb-6">
            La piattaforma che abbatte
            <span className="text-iss-gold-600 block">
              tutte le barriere
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
            La prima piattaforma regionale che democratizza l'accesso ai finanziamenti
            per costruire un futuro più inclusivo e sostenibile per la Campania.
          </p>
        </div>

        {/* Main Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="group border-2 border-gray-100 hover:border-iss-gold-300 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 bg-white"
            >
              <CardContent className="p-8 text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-iss-gold-100 to-iss-gold-200 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                  <feature.icon className={`w-8 h-8 ${feature.color}`} />
                </div>
                <h3 className="text-xl font-semibold text-iss-bordeaux-900 mb-4 group-hover:text-iss-gold-700 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description.split(feature.highlight).map((part, i, arr) => (
                    <span key={i}>
                      {part}
                      {i < arr.length - 1 && (
                        <strong className="text-iss-gold-700 font-bold">
                          {feature.highlight}
                        </strong>
                      )}
                    </span>
                  ))}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Additional Features */}
        <div className="bg-gradient-to-r from-iss-bordeaux-50 to-iss-gold-50 rounded-3xl p-8 lg:p-12">
          <div className="text-center mb-12">
            <h3 className="text-2xl lg:text-3xl font-bold text-iss-bordeaux-900 mb-4">
              E non è tutto...
            </h3>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Scopri tutte le funzionalità avanzate che rendono ISS la scelta preferita
              dalle APS campane più innovative.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {additionalFeatures.map((feature, index) => (
              <div key={index} className="text-center group">
                <div className="w-14 h-14 bg-white rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110">
                  <feature.icon className={`w-7 h-7 ${feature.color}`} />
                </div>
                <h4 className="text-lg font-semibold text-iss-bordeaux-900 mb-3">
                  {feature.title}
                </h4>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {feature.description.split(feature.highlight).map((part, i, arr) => (
                    <span key={i}>
                      {part}
                      {i < arr.length - 1 && (
                        <strong className={`font-bold ${feature.color}`}>
                          {feature.highlight}
                        </strong>
                      )}
                    </span>
                  ))}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <p className="text-lg text-gray-600 mb-6">
            Pronto a rivoluzionare l'accesso ai finanziamenti per la tua APS?
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-iss-bordeaux-900 hover:bg-iss-bordeaux-800 text-white px-8 py-4 rounded-lg font-semibold transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl">
              Inizia Subito - È Gratis
            </button>
            <button className="border-2 border-iss-bordeaux-900 text-iss-bordeaux-900 hover:bg-iss-bordeaux-900 hover:text-white px-8 py-4 rounded-lg font-semibold transition-all duration-300 hover:scale-105">
              Scopri di Più
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
