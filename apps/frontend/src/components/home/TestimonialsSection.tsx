import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Quote, 
  Star, 
  Heart, 
  Users, 
  Award,
  MapPin,
  Calendar
} from 'lucide-react';

const testimonials = [
  {
    id: 1,
    name: 'Maria Rossi',
    role: 'Presidente APS "Nuove Rotte"',
    location: 'Salerno',
    avatar: '👩‍💼',
    rating: 5,
    quote: 'Grazie a ISS abbiamo trovato 3 bandi perfetti per i nostri progetti di inclusione sociale. La piattaforma è incredibilmente intuitiva e il supporto per l\'accessibilità è eccezionale.',
    highlight: 'Trovati 3 bandi in una settimana',
    category: 'APS Responsabile',
    date: '2025-09-15'
  },
  {
    id: 2,
    name: 'Giuseppe Verdi',
    role: 'Coordinatore Volontariato',
    location: 'Napoli',
    avatar: '👨‍🏫',
    rating: 5,
    quote: 'La formazione digitale gratuita di ISS ha trasformato la nostra APS. Ora gestiamo tutto digitalmente e abbiamo accesso a molte più opportunità di finanziamento.',
    highlight: '100% digitali in 2 mesi',
    category: 'Volontario',
    date: '2025-09-10'
  },
  {
    id: 3,
    name: 'Anna Bianchi',
    role: 'Operatrice APS "Campania Solidale"',
    location: 'Caserta',
    avatar: '👩‍💻',
    rating: 5,
    quote: 'Il sistema di notifiche automatiche ci ha fatto risparmiare ore di ricerca. Riceviamo solo bandi rilevanti per il nostro settore e non perdiamo mai una scadenza.',
    highlight: 'Risparmiati 10 ore/settimana',
    category: 'APS Operatore',
    date: '2025-09-05'
  },
  {
    id: 4,
    name: 'Francesco Neri',
    role: 'Cittadino in Formazione',
    location: 'Avellino',
    avatar: '👨‍🎓',
    rating: 5,
    quote: 'I corsi di alfabetizzazione digitale sono fantastici! Gratuiti, accessibili e con certificazione riconosciuta. Ora posso aiutare la mia APS con la tecnologia.',
    highlight: 'Certificazione ottenuta',
    category: 'Cittadino',
    date: '2025-08-28'
  },
  {
    id: 5,
    name: 'Lucia Gialli',
    role: 'Presidente APS "Insieme per Tutti"',
    location: 'Benevento',
    avatar: '👩‍🦽',
    rating: 5,
    quote: 'Come persona con disabilità visiva, apprezzo enormemente l\'accessibilità totale della piattaforma. Finalmente posso navigare autonomamente e trovare finanziamenti per la mia APS.',
    highlight: 'Accessibilità perfetta',
    category: 'APS Responsabile',
    date: '2025-08-20'
  },
  {
    id: 6,
    name: 'Marco Blu',
    role: 'Coordinatore Progetti',
    location: 'Salerno',
    avatar: '👨‍💼',
    rating: 5,
    quote: 'L\'export automatico dei bandi in PDF ci ha semplificato enormemente il lavoro di candidatura. La qualità dei documenti è professionale e pronta per la submissione.',
    highlight: 'Candidature più veloci',
    category: 'APS Operatore',
    date: '2025-08-15'
  }
];

const stats = [
  { value: '4.9/5', label: 'Rating Medio', icon: Star },
  { value: '500+', label: 'APS Soddisfatte', icon: Users },
  { value: '98%', label: 'Raccomanderebbero ISS', icon: Heart },
  { value: '2000+', label: 'Utenti Attivi', icon: Award }
];

export function TestimonialsSection() {
  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-iss-bordeaux-100 text-iss-bordeaux-800 px-4 py-2 rounded-full text-sm font-semibold mb-4">
            <Heart className="w-4 h-4" />
            Testimonianze Reali
          </div>
          <h2 className="text-3xl lg:text-5xl font-bold text-iss-bordeaux-900 mb-6">
            Cosa dicono le APS
            <span className="text-iss-gold-600 block">
              che usano ISS
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Storie vere di APS campane che hanno trasformato il loro accesso ai finanziamenti 
            grazie alla piattaforma ISS.
          </p>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {stats.map((stat, index) => (
            <Card key={index} className="text-center border-2 border-iss-gold-100 hover:border-iss-gold-300 transition-all duration-300">
              <CardContent className="p-6">
                <stat.icon className="w-8 h-8 text-iss-gold-600 mx-auto mb-3" />
                <div className="text-2xl font-bold text-iss-bordeaux-900 mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-600 font-medium">
                  {stat.label}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Testimonials Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {testimonials.map((testimonial) => (
            <Card 
              key={testimonial.id}
              className="group hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border-2 border-gray-100 hover:border-iss-gold-200"
            >
              <CardContent className="p-8">
                {/* Quote Icon */}
                <div className="flex justify-between items-start mb-6">
                  <Quote className="w-8 h-8 text-iss-gold-400" />
                  <div className="flex gap-1">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 fill-iss-gold-400 text-iss-gold-400" />
                    ))}
                  </div>
                </div>

                {/* Testimonial Content */}
                <blockquote className="text-gray-700 leading-relaxed mb-6 italic">
                  "{testimonial.quote}"
                </blockquote>

                {/* Highlight */}
                <Badge className="bg-iss-gold-100 text-iss-gold-800 hover:bg-iss-gold-200 mb-6">
                  ✨ {testimonial.highlight}
                </Badge>

                {/* Author Info */}
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-iss-bordeaux-100 to-iss-gold-100 rounded-full flex items-center justify-center text-2xl">
                    {testimonial.avatar}
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-iss-bordeaux-900">
                      {testimonial.name}
                    </div>
                    <div className="text-sm text-gray-600">
                      {testimonial.role}
                    </div>
                    <div className="flex items-center gap-4 text-xs text-gray-500 mt-1">
                      <div className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {testimonial.location}
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(testimonial.date).toLocaleDateString('it-IT', { 
                          month: 'short', 
                          year: 'numeric' 
                        })}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Category Badge */}
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <Badge variant="outline" className="text-xs">
                    {testimonial.category}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center">
          <div className="bg-gradient-to-r from-iss-bordeaux-900 to-iss-bordeaux-800 rounded-3xl p-8 lg:p-12 text-white">
            <h3 className="text-2xl lg:text-3xl font-bold mb-4">
              Unisciti alle 500+ APS che hanno già scelto ISS
            </h3>
            <p className="text-lg text-iss-bordeaux-100 mb-8 max-w-2xl mx-auto">
              Inizia subito a esplorare le opportunità di finanziamento per la tua APS. 
              È gratuito, accessibile e sempre disponibile.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-iss-gold-500 hover:bg-iss-gold-400 text-iss-bordeaux-900 px-8 py-4 rounded-lg font-semibold transition-all duration-300 hover:scale-105 shadow-lg">
                Registra la tua APS
              </button>
              <button className="border-2 border-white text-white hover:bg-white hover:text-iss-bordeaux-900 px-8 py-4 rounded-lg font-semibold transition-all duration-300 hover:scale-105">
                Esplora i Bandi
              </button>
            </div>
            
            <div className="flex items-center justify-center gap-6 mt-8 pt-8 border-t border-iss-bordeaux-700 text-iss-bordeaux-200 text-sm">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4" />
                500+ APS attive
              </div>
              <div className="flex items-center gap-2">
                <Star className="w-4 h-4" />
                4.9/5 rating medio
              </div>
              <div className="flex items-center gap-2">
                <Heart className="w-4 h-4" />
                100% gratuito
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
