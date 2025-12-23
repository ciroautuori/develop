import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Bot,
  Zap,
  BarChart3,
  Users,
  ArrowRight,
  Play,
  Brain,
  Sparkles,
  Calendar
} from 'lucide-react';
import { LandingHeader } from './components/LandingHeader';
import { LandingFooter } from './components/LandingFooter';
import { TokenCalculator } from './components/TokenCalculator';
import { BrandDNASection } from './components/BrandDNASection';

export function MarkettinaLanding() {
  const navigate = useNavigate();
  const [isVideoOpen, setIsVideoOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden">
      <LandingHeader />

      {/* HERO SECTION - Con metriche di impatto */}
      <section className="relative pt-32 pb-20 lg:pt-44 lg:pb-28 overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-20 left-1/4 w-[500px] h-[500px] bg-gold/15 rounded-full blur-[120px]" />
          <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-purple-500/10 rounded-full blur-[100px]" />
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">

            {/* Left: Copy */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gold/10 border border-gold/30 mb-8">
                <Brain className="w-4 h-4 text-gold" />
                <span className="text-sm font-medium text-gold">Marketing AI che impara chi sei</span>
              </div>

              <h1 className="text-5xl lg:text-6xl font-bold tracking-tight mb-6 leading-tight">
                Collega i Social.
                <br />
                <span className="text-gold">L'AI fa il resto.</span>
              </h1>

              <p className="text-xl text-muted-foreground mb-8 leading-relaxed">
                MARKETTINA analizza i tuoi contenuti, impara il tuo stile,
                e <span className="text-foreground font-medium">genera + pubblica automaticamente</span> su
                Instagram, Facebook, LinkedIn e TikTok.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <button
                  onClick={() => navigate('/admin/register')}
                  className="px-8 py-4 bg-gold text-black font-bold rounded-xl hover:bg-gold-light transition-all transform hover:scale-105 shadow-[0_0_25px_rgba(212,175,55,0.4)] flex items-center justify-center gap-2"
                >
                  Inizia Gratis - 150 Token
                  <ArrowRight className="w-5 h-5" />
                </button>

                <button
                  onClick={() => setIsVideoOpen(true)}
                  className="px-8 py-4 bg-muted/50 text-foreground font-medium rounded-xl hover:bg-muted border border-border transition-all flex items-center justify-center gap-2"
                >
                  <Play className="w-5 h-5 fill-current" />
                  Guarda Demo
                </button>
              </div>

              <div className="flex items-center gap-6 text-sm text-gray-500">
                <span className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-gold" />
                  Setup 5 minuti
                </span>
                <span className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-purple-400" />
                  No carta richiesta
                </span>
              </div>
            </motion.div>

            {/* Right: Impact Metrics Panel */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative"
            >
              <div className="p-8 rounded-3xl bg-card border border-border shadow-2xl">

                {/* Header */}
                <div className="text-center mb-8">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/30 mb-4">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-xs font-medium text-green-400">Risparmio vs Agenzia</span>
                  </div>
                  <h3 className="text-2xl font-bold text-foreground">Il tuo marketing in numeri</h3>
                </div>

                {/* Big Savings Number */}
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.4, type: 'spring' }}
                  className="text-center mb-8 p-6 rounded-2xl bg-gradient-to-br from-green-500/10 to-transparent border border-green-500/20"
                >
                  <div className="text-5xl lg:text-6xl font-bold text-green-400 mb-2">-90%</div>
                  <div className="text-muted-foreground">rispetto ad un'agenzia tradizionale</div>
                  <div className="mt-3 flex items-center justify-center gap-4 text-sm">
                    <span className="text-red-400 line-through">€500/mese</span>
                    <span className="text-foreground">→</span>
                    <span className="text-green-400 font-bold">€50/mese</span>
                  </div>
                </motion.div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="p-4 rounded-xl bg-muted/30 border border-border text-center"
                  >
                    <div className="text-3xl font-bold text-gold mb-1">30+</div>
                    <div className="text-xs text-gray-500">Post generati/mese</div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="p-4 rounded-xl bg-muted/30 border border-border text-center"
                  >
                    <div className="text-3xl font-bold text-purple-400 mb-1">20h</div>
                    <div className="text-xs text-gray-500">Risparmiate/mese</div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.7 }}
                    className="p-4 rounded-xl bg-white/5 border border-white/10 text-center"
                  >
                    <div className="text-3xl font-bold text-blue-400 mb-1">4</div>
                    <div className="text-xs text-gray-500">Social gestiti</div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8 }}
                    className="p-4 rounded-xl bg-white/5 border border-white/10 text-center"
                  >
                    <div className="text-3xl font-bold text-pink-400 mb-1">100%</div>
                    <div className="text-xs text-gray-500">On-brand</div>
                  </motion.div>
                </div>

                {/* Bottom CTA hint */}
                <div className="text-center text-sm text-gray-500">
                  <span className="text-gold">↓</span> Scopri come funziona <span className="text-gold">↓</span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* BRAND DNA SECTION - Il cuore del valore */}
      <BrandDNASection />

      {/* FEATURES GRID - 4 card chiave */}
      <section className="py-24 bg-muted/30" id="features">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">
              Tutto il marketing in <span className="text-gold">una piattaforma</span>
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Non solo generazione contenuti. Lead finding, analytics, scheduling. Tutto incluso.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FeatureCard
              icon={<Bot className="w-7 h-7 text-gold" />}
              title="Agenti AI Specializzati"
              description="Content Creator, SEO Specialist, Social Manager. Team AI che collaborano per te."
            />
            <FeatureCard
              icon={<Users className="w-7 h-7 text-gold" />}
              title="Lead Finder"
              description="Trova clienti ideali nella tua zona. Email verificate, profili social, dati aziendali."
            />
            <FeatureCard
              icon={<Calendar className="w-7 h-7 text-gold" />}
              title="Calendario Editoriale"
              description="Pianifica 30 giorni di contenuti in 5 minuti. Scheduling automatico multi-piattaforma."
            />
            <FeatureCard
              icon={<BarChart3 className="w-7 h-7 text-gold" />}
              title="Analytics & ROI"
              description="Traccia performance di ogni post. Scopri cosa funziona e ottimizza automaticamente."
            />
          </div>
        </div>
      </section>

      {/* TOKEN CALCULATOR */}
      <TokenCalculator />

      {/* CTA FINAL */}
      <section className="py-32 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-gold/10 to-transparent" />
        <div className="relative z-10 max-w-4xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl lg:text-5xl font-bold mb-6">
              Pronto a mettere il marketing in <span className="text-gold">autopilota</span>?
            </h2>
            <p className="text-xl text-muted-foreground mb-10">
              5 minuti di setup. Zero competenze tecniche.
              L'AI impara, genera, pubblica. Tu cresci.
            </p>
            <button
              onClick={() => navigate('/admin/register')}
              className="px-12 py-6 bg-gold text-black text-xl font-bold rounded-xl hover:bg-gold-light transition-all transform hover:scale-105 shadow-[0_0_40px_rgba(212,175,55,0.5)]"
            >
              Inizia Ora - 150 Token Gratis
            </button>
            <p className="mt-6 text-sm text-muted-foreground">
              Nessuna carta di credito • Cancella quando vuoi
            </p>
          </motion.div>
        </div>
      </section>

      <LandingFooter />
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="p-6 rounded-2xl bg-card border border-border hover:border-gold/50 transition-all group"
    >
      <div className="mb-5 p-3 rounded-xl bg-secondary w-fit group-hover:scale-110 transition-transform border border-border">
        {icon}
      </div>
      <h3 className="text-lg font-bold mb-2 text-foreground">{title}</h3>
      <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
    </motion.div>
  );
}
