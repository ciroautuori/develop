import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Calculator,
  FileText,
  Image,
  Video,
  Search,
  Sparkles,
  Check,
  Zap,
  TrendingDown,
  Crown,
  Rocket,
  Building2
} from 'lucide-react';

// 3 Tiers pricing structure
type TierType = 'low' | 'medium' | 'high';

interface TierInfo {
  name: string;
  label: string;
  icon: React.ReactNode;
  description: string;
  color: string;
}

const TIERS: Record<TierType, TierInfo> = {
  low: {
    name: 'Economico',
    label: 'LOW',
    icon: <TrendingDown className="w-5 h-5" />,
    description: 'Modelli veloci e economici (Groq, FLUX, SDXL)',
    color: 'text-green-400 border-green-500/30 bg-green-500/10'
  },
  medium: {
    name: 'Professionale',
    label: 'MEDIUM',
    icon: <Rocket className="w-5 h-5" />,
    description: 'Qualità bilanciata (GPT-4o-mini, Imagen 4, Claude Haiku)',
    color: 'text-gold border-gold/30 bg-gold/10'
  },
  high: {
    name: 'Premium',
    label: 'HIGH',
    icon: <Crown className="w-5 h-5" />,
    description: 'Massima qualità (GPT-4o, DALL-E 3 HD, Claude Sonnet)',
    color: 'text-purple-400 border-purple-500/30 bg-purple-500/10'
  }
};

// Token costs per tier (calibrated for €50-€150/month targets)
const TOKEN_COSTS: Record<TierType, {
  post: number;
  blog: number;
  image: number;
  video: number;
  lead: number;
}> = {
  low: {
    post: 5,
    blog: 15,
    image: 15,
    video: 80,
    lead: 30
  },
  medium: {
    post: 15,
    blog: 40,
    image: 40,
    video: 200,
    lead: 80
  },
  high: {
    post: 30,
    blog: 80,
    image: 80,
    video: 400,
    lead: 150
  }
};

// Token packages (1 TOKEN = €0.02)
const PACKAGES = [
  { name: 'Trial', tokens: 150, price: 0, label: 'GRATIS', icon: <Sparkles className="w-5 h-5" /> },
  { name: 'Starter', tokens: 2500, price: 49.99, popular: false, icon: <Zap className="w-5 h-5" /> },
  { name: 'Growth', tokens: 5000, price: 99.99, popular: true, icon: <Rocket className="w-5 h-5" /> },
  { name: 'Pro', tokens: 7500, price: 149.99, popular: false, icon: <Crown className="w-5 h-5" /> },
  { name: 'Agency', tokens: 15000, price: 249.99, popular: false, icon: <Building2 className="w-5 h-5" /> },
];

interface CalculatorState {
  posts: number;
  blogs: number;
  images: number;
  videos: number;
  leadSearches: number;
}

export function TokenCalculator() {
  const navigate = useNavigate();
  const [tier, setTier] = useState<TierType>('medium');
  const [state, setState] = useState<CalculatorState>({
    posts: 30,
    blogs: 4,
    images: 50,
    videos: 0,
    leadSearches: 0,
  });

  const costs = TOKEN_COSTS[tier];

  const totalTokens = useMemo(() => {
    return (
      state.posts * costs.post +
      state.blogs * costs.blog +
      state.images * costs.image +
      state.videos * costs.video +
      state.leadSearches * costs.lead
    );
  }, [state, costs]);

  const estimatedCost = useMemo(() => {
    return (totalTokens * 0.02).toFixed(2);
  }, [totalTokens]);

  const recommendedPackage = useMemo(() => {
    return PACKAGES.find(pkg => pkg.tokens >= totalTokens) || PACKAGES[PACKAGES.length - 1];
  }, [totalTokens]);

  const agencyCost = useMemo(() => {
    // Traditional agency cost estimate (10-15x our price, minimum €500)
    return Math.max(500, totalTokens * 0.15);
  }, [totalTokens]);

  const savings = useMemo(() => {
    return (agencyCost - parseFloat(estimatedCost)).toFixed(0);
  }, [agencyCost, estimatedCost]);

  const savingsPercent = useMemo(() => {
    return Math.round((1 - parseFloat(estimatedCost) / agencyCost) * 100);
  }, [estimatedCost, agencyCost]);

  return (
    <section className="py-24 bg-card relative overflow-hidden" id="pricing">
      {/* Background Effects */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gold/5 rounded-full blur-[150px] pointer-events-none" />

      <div className="max-w-6xl mx-auto px-6 relative z-10">

        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gold/10 border border-gold/30 mb-6">
            <Calculator className="w-4 h-4 text-gold" />
            <span className="text-sm font-medium text-gold">Paga solo ciò che consumi</span>
          </div>
          <h2 className="text-3xl lg:text-5xl font-bold mb-4">
            Calcola il tuo <span className="text-gold">investimento</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
            Configura le tue esigenze mensili e scopri quanto risparmi rispetto ad un'agenzia tradizionale.
          </p>
        </div>

        {/* Tier Selector */}
        <div className="mb-12">
          <div className="flex flex-col sm:flex-row gap-4 max-w-3xl mx-auto">
            {(Object.entries(TIERS) as [TierType, TierInfo][]).map(([key, tierInfo]) => (
              <button
                key={key}
                onClick={() => setTier(key)}
                className={`
                  flex-1 p-4 rounded-xl border-2 transition-all duration-300
                  ${tier === key
                    ? tierInfo.color + ' scale-105 shadow-lg'
                    : 'border-border bg-card hover:bg-muted hover:border-border/80'
                  }
                `}
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className={tier === key ? tierInfo.color.split(' ')[0] : 'text-gray-400'}>
                    {tierInfo.icon}
                  </div>
                  <span className="font-bold text-lg">{tierInfo.name}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${tier === key ? 'bg-white/20' : 'bg-white/5'}`}>
                    {tierInfo.label}
                  </span>
                </div>
                <p className="text-sm text-gray-400 text-left">{tierInfo.description}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-12">

          {/* Sliders */}
          <div className="space-y-6 p-8 rounded-2xl bg-card border border-border">
            <h3 className="font-bold text-xl mb-6 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-gold" />
              Le tue esigenze mensili
            </h3>

            <SliderInput
              icon={<FileText className="w-5 h-5" />}
              label="Post Social"
              sublabel={`${costs.post} token/post`}
              value={state.posts}
              max={100}
              onChange={(val) => setState(s => ({ ...s, posts: val }))}
            />

            <SliderInput
              icon={<FileText className="w-5 h-5" />}
              label="Articoli Blog"
              sublabel={`${costs.blog} token/articolo`}
              value={state.blogs}
              max={20}
              onChange={(val) => setState(s => ({ ...s, blogs: val }))}
            />

            <SliderInput
              icon={<Image className="w-5 h-5" />}
              label="Immagini AI"
              sublabel={`${costs.image} token/immagine`}
              value={state.images}
              max={150}
              onChange={(val) => setState(s => ({ ...s, images: val }))}
            />

            <SliderInput
              icon={<Video className="w-5 h-5" />}
              label="Video AI (5 sec)"
              sublabel={`${costs.video} token/video`}
              value={state.videos}
              max={20}
              onChange={(val) => setState(s => ({ ...s, videos: val }))}
            />

            <SliderInput
              icon={<Search className="w-5 h-5" />}
              label="Ricerche Lead (10 lead)"
              sublabel={`${costs.lead} token/ricerca`}
              value={state.leadSearches}
              max={30}
              onChange={(val) => setState(s => ({ ...s, leadSearches: val }))}
            />
          </div>

          {/* Results */}
          <div className="space-y-6">

            {/* Token Summary */}
            <motion.div
              className="p-8 rounded-2xl bg-gradient-to-br from-gold/10 to-transparent border border-gold/20"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              key={totalTokens}
            >
              <div className="text-center mb-8">
                <div className="text-6xl font-bold text-gold mb-2">
                  {totalTokens.toLocaleString()}
                </div>
                <div className="text-gray-400 text-lg">token/mese necessari</div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-center mb-6">
                <div className="p-5 rounded-xl bg-black/50 border border-white/10">
                  <div className="text-3xl font-bold text-foreground">€{estimatedCost}</div>
                  <div className="text-sm text-gray-400 mt-1">con MARKETTINA</div>
                </div>
                <div className="p-5 rounded-xl bg-red-950/30 border border-red-500/20">
                  <div className="text-3xl font-bold text-red-400 line-through">€{Math.round(agencyCost)}</div>
                  <div className="text-sm text-red-400/70 mt-1">agenzia tradizionale</div>
                </div>
              </div>

              <div className="p-5 rounded-xl bg-green-950/30 border border-green-500/20 text-center">
                <div className="text-xl text-green-400">
                  Risparmi <span className="font-bold text-3xl">€{savings}</span>/mese
                  <span className="ml-2 text-sm bg-green-500/20 px-2 py-1 rounded-full">
                    -{savingsPercent}%
                  </span>
                </div>
              </div>
            </motion.div>

            {/* Recommended Package */}
            <motion.div
              className="p-6 rounded-2xl bg-card border border-border"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <div className="flex items-center gap-3 mb-4">
                <Zap className="w-5 h-5 text-gold fill-gold" />
                <span className="font-medium text-lg">Pacchetto consigliato</span>
              </div>

              <div className="flex items-center justify-between p-5 rounded-xl bg-gold/10 border border-gold/30">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-lg bg-gold/20 text-gold">
                    {recommendedPackage.icon}
                  </div>
                  <div>
                    <div className="font-bold text-2xl text-gold">{recommendedPackage.name}</div>
                    <div className="text-sm text-gray-400">
                      {recommendedPackage.tokens.toLocaleString()} token
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-foreground">
                    {recommendedPackage.price === 0 ? 'GRATIS' : `€${recommendedPackage.price}`}
                  </div>
                  {recommendedPackage.tokens >= totalTokens && totalTokens > 0 && (
                    <div className="text-sm text-green-400 mt-1">
                      Copre ~{Math.floor(recommendedPackage.tokens / totalTokens)} mesi
                    </div>
                  )}
                </div>
              </div>
            </motion.div>

            {/* All Packages Quick View */}
            <div className="grid grid-cols-5 gap-2">
              {PACKAGES.map((pkg) => (
                <div
                  key={pkg.name}
                  className={`p-3 rounded-lg text-center transition-all ${
                    pkg.name === recommendedPackage.name
                      ? 'bg-gold/20 border border-gold/50'
                      : 'bg-muted/20 border border-border'
                  }`}
                >
                  <div className="text-xs text-gray-400">{pkg.name}</div>
                  <div className={`font-bold ${pkg.name === recommendedPackage.name ? 'text-gold' : 'text-foreground'}`}>
                    {pkg.price === 0 ? 'Free' : `€${pkg.price}`}
                  </div>
                </div>
              ))}
            </div>

            {/* CTA */}
            <button
              onClick={() => navigate('/admin/register')}
              className="w-full py-5 bg-gold text-black font-bold text-lg rounded-xl hover:bg-gold-light transition-all transform hover:scale-105 shadow-[0_0_30px_rgba(212,175,55,0.3)] flex items-center justify-center gap-3"
            >
              <Check className="w-6 h-6" />
              Inizia con 150 Token Gratis
            </button>

            <p className="text-center text-sm text-gray-500">
              Nessuna carta di credito richiesta • Accesso immediato
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

interface SliderInputProps {
  icon: React.ReactNode;
  label: string;
  sublabel: string;
  value: number;
  max: number;
  onChange: (value: number) => void;
}

function SliderInput({ icon, label, sublabel, value, max, onChange }: SliderInputProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-gold/10 text-gold">
            {icon}
          </div>
          <div>
            <div className="font-medium text-foreground">{label}</div>
            <div className="text-xs text-gray-500">{sublabel}</div>
          </div>
        </div>
        <div className="text-2xl font-bold text-gold min-w-[60px] text-right">
          {value}
        </div>
      </div>

      <input
        type="range"
        min={0}
        max={max}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer
                   [&::-webkit-slider-thumb]:appearance-none
                   [&::-webkit-slider-thumb]:w-5
                   [&::-webkit-slider-thumb]:h-5
                   [&::-webkit-slider-thumb]:rounded-full
                   [&::-webkit-slider-thumb]:bg-gold
                   [&::-webkit-slider-thumb]:cursor-pointer
                   [&::-webkit-slider-thumb]:shadow-[0_0_10px_rgba(212,175,55,0.5)]
                   [&::-moz-range-thumb]:w-5
                   [&::-moz-range-thumb]:h-5
                   [&::-moz-range-thumb]:rounded-full
                   [&::-moz-range-thumb]:bg-gold
                   [&::-moz-range-thumb]:border-0
                   [&::-moz-range-thumb]:cursor-pointer"
      />

      <div className="flex justify-between text-xs text-gray-600">
        <span>0</span>
        <span>{max}</span>
      </div>
    </div>
  );
}

export default TokenCalculator;
