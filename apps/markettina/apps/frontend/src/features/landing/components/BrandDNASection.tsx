import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Link2,
  Brain,
  Send,
  Instagram,
  Facebook,
  Linkedin,
  Twitter,
  FileText,
  Image,
  Video,
  MessageSquare,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Zap
} from 'lucide-react';

const flowSteps = [
  {
    icon: Link2,
    title: 'Collega i Social',
    description: 'Instagram, Facebook, LinkedIn, Twitter. Un click e siamo connessi.',
    color: 'from-blue-500 to-cyan-500',
    details: ['OAuth sicuro', 'Import automatico bio', 'Analisi post esistenti']
  },
  {
    icon: Brain,
    title: 'L\'AI Impara Chi Sei',
    description: 'Analizziamo i tuoi contenuti con RAG. Estraiamo il tuo DNA.',
    color: 'from-purple-500 to-pink-500',
    details: ['Tone of Voice', 'Valori del brand', 'Stile visivo']
  },
  {
    icon: Send,
    title: 'Genera e Pubblica',
    description: 'Contenuti on-brand, pubblicati automaticamente. Tu approvi, noi facciamo.',
    color: 'from-gold to-amber-500',
    details: ['Post + Immagini AI', 'Scheduling automatico', 'Multi-piattaforma']
  }
];

const socialIcons = [
  { Icon: Instagram, color: 'text-pink-500', delay: 0 },
  { Icon: Facebook, color: 'text-blue-500', delay: 0.1 },
  { Icon: Linkedin, color: 'text-sky-500', delay: 0.2 },
  { Icon: Twitter, color: 'text-gray-400', delay: 0.3 },
];

const contentTypes = [
  { Icon: FileText, label: 'Post', color: 'text-blue-400' },
  { Icon: Image, label: 'Immagini', color: 'text-purple-400' },
  { Icon: Video, label: 'Video', color: 'text-pink-400' },
  { Icon: MessageSquare, label: 'Stories', color: 'text-gold' },
];

export function BrandDNASection() {
  const navigate = useNavigate();

  return (
    <section className="py-24 bg-background relative overflow-hidden" id="brand-dna">
      {/* Background Effects */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-0 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[150px]" />
        <div className="absolute bottom-1/4 right-0 w-[400px] h-[400px] bg-gold/10 rounded-full blur-[120px]" />
      </div>

      <div className="max-w-7xl mx-auto px-6 relative z-10">

        {/* Header */}
        <div className="text-center mb-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/30 mb-6"
          >
            <Brain className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-medium text-purple-400">Brand DNA Technology</span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-4xl lg:text-6xl font-bold mb-6"
          >
            L'AI che <span className="text-gold">impara chi sei</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-xl text-gray-400 max-w-3xl mx-auto"
          >
            Non siamo un chatbot generico. Analizziamo i tuoi contenuti esistenti,
            estraiamo il tuo <span className="text-foreground font-medium">Tone of Voice</span>,
            e generiamo contenuti <span className="text-foreground font-medium">indistinguibili dai tuoi</span>.
          </motion.p>
        </div>

        {/* Main Flow - 3 Steps */}
        <div className="grid lg:grid-cols-3 gap-8 mb-20">
          {flowSteps.map((step, index) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.15 }}
              className="relative"
            >
              {/* Connector Arrow */}
              {index < flowSteps.length - 1 && (
                <div className="hidden lg:flex absolute top-1/2 -right-4 transform -translate-y-1/2 z-20">
                  <ArrowRight className="w-8 h-8 text-gold/50" />
                </div>
              )}

              <div className="h-full p-8 rounded-2xl bg-card border border-border hover:border-gold/30 transition-all group">
                {/* Step Number */}
                <div className="absolute -top-4 left-8 px-3 py-1 rounded-full bg-secondary border border-border text-sm font-bold text-gold">
                  STEP {index + 1}
                </div>

                {/* Icon */}
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg`}>
                  <step.icon className="w-8 h-8 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold mb-3 text-foreground">{step.title}</h3>
                <p className="text-muted-foreground mb-6 leading-relaxed">{step.description}</p>

                {/* Details */}
                <ul className="space-y-2">
                  {step.details.map((detail, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                      <CheckCircle2 className="w-4 h-4 text-gold" />
                      {detail}
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Visual Demo Row */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="p-8 rounded-3xl bg-card border border-border mb-16"
        >
          <div className="grid lg:grid-cols-3 gap-8 items-center">

            {/* Left: Social Icons */}
            <div className="text-center">
              <div className="flex justify-center gap-4 mb-4">
                {socialIcons.map(({ Icon, color, delay }) => (
                  <motion.div
                    key={color}
                    initial={{ scale: 0 }}
                    whileInView={{ scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay, type: 'spring' }}
                    className={`w-14 h-14 rounded-xl bg-muted/20 border border-border flex items-center justify-center ${color}`}
                  >
                    <Icon className="w-7 h-7" />
                  </motion.div>
                ))}
              </div>
              <p className="text-sm text-gray-500">I tuoi social connessi</p>
            </div>

            {/* Center: Brain Processing */}
            <div className="text-center">
              <motion.div
                animate={{
                  boxShadow: ['0 0 20px rgba(168, 85, 247, 0.3)', '0 0 40px rgba(168, 85, 247, 0.5)', '0 0 20px rgba(168, 85, 247, 0.3)']
                }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-4"
              >
                <Brain className="w-12 h-12 text-white" />
              </motion.div>
              <p className="text-sm font-medium text-purple-400">Brand DNA Engine</p>
              <p className="text-xs text-gray-600 mt-1">RAG + AI Analysis</p>
            </div>

            {/* Right: Content Types */}
            <div className="text-center">
              <div className="flex justify-center gap-4 mb-4">
                {contentTypes.map(({ Icon, label, color }) => (
                  <div key={label} className="text-center">
                    <div className={`w-14 h-14 rounded-xl bg-muted/20 border border-border flex items-center justify-center ${color} mb-1`}>
                      <Icon className="w-7 h-7" />
                    </div>
                    <span className="text-xs text-gray-600">{label}</span>
                  </div>
                ))}
              </div>
              <p className="text-sm text-gray-500">Contenuti generati on-brand</p>
            </div>
          </div>
        </motion.div>

        {/* Key Benefits */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="p-6 rounded-xl bg-green-500/5 border border-green-500/20"
          >
            <div className="flex items-center gap-3 mb-3">
              <Zap className="w-6 h-6 text-green-400" />
              <span className="font-bold text-green-400">5 Minuti di Setup</span>
            </div>
            <p className="text-sm text-gray-400">
              Collega i social con OAuth, rispondi a 3 domande, e il Brand DNA è pronto.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="p-6 rounded-xl bg-purple-500/5 border border-purple-500/20"
          >
            <div className="flex items-center gap-3 mb-3">
              <Sparkles className="w-6 h-6 text-purple-400" />
              <span className="font-bold text-purple-400">Contenuti Unici</span>
            </div>
            <p className="text-sm text-gray-400">
              Non template generici. Ogni post, immagine, video riflette il TUO stile.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="p-6 rounded-xl bg-gold/5 border border-gold/20"
          >
            <div className="flex items-center gap-3 mb-3">
              <Send className="w-6 h-6 text-gold" />
              <span className="font-bold text-gold">Autopost Intelligente</span>
            </div>
            <p className="text-sm text-gray-400">
              Scheduling automatico, pubblicazione multi-piattaforma. Tu approvi, noi facciamo.
            </p>
          </motion.div>
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <button
            onClick={() => navigate('/admin/register')}
            className="px-10 py-5 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-lg font-bold rounded-xl hover:opacity-90 transition-all transform hover:scale-105 shadow-[0_0_30px_rgba(168,85,247,0.4)] flex items-center gap-3 mx-auto"
          >
            <Brain className="w-6 h-6" />
            Configura il tuo Brand DNA
            <ArrowRight className="w-5 h-5" />
          </button>
          <p className="mt-4 text-sm text-gray-500">
            Setup in 5 minuti • 150 token gratis • Nessuna carta richiesta
          </p>
        </motion.div>
      </div>
    </section>
  );
}

export default BrandDNASection;
