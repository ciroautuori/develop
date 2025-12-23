import { createLazyFileRoute, Link } from "@tanstack/react-router";
import {
  Dumbbell,
  Stethoscope,
  Utensils,
  BarChart2,
  Play,
  ChevronRight,
  Bell,
  User,
  Sparkles,
  Trophy,
  MessageSquare,
} from "lucide-react";
import { Suspense, useState } from "react";
import { format } from "date-fns";
import { it } from "date-fns/locale";
import { useQueryClient } from "@tanstack/react-query";
import { PainTrendMiniChart } from "../features/home/PainTrendMiniChart";
import { ComplianceWidget } from "../features/home/ComplianceWidget";
import { GoogleFitWidget } from "../features/home/GoogleFitWidget";
import { CurrentPhaseCard } from "../features/home/CurrentPhaseCard";
import { RedFlagsAlert } from "../features/home/RedFlagsAlert";
import { cn } from "../lib/utils";
import { useDashboardData } from "../features/home/hooks/useDashboardData";
import { DashboardSkeleton } from "../features/home/DashboardSkeleton";
import { motion } from "framer-motion";
import { PullToRefresh } from "../components/ui/mobile/PullToRefresh";
import { GestureWrapper } from "../components/ui/mobile/GestureWrapper";
import { toast } from "../components/ui/Toast";
import { DashboardTour } from "../features/tour";

export const Route = createLazyFileRoute("/")({
  component: DashboardPage,
});

function DashboardPage() {
  return (
    <Suspense fallback={<DashboardSkeleton />}>
      <DashboardContent />
    </Suspense>
  );
}

function DashboardContent() {
  const today = new Date();
  const { userProfile } = useDashboardData();
  const queryClient = useQueryClient();

  // Determine user's primary focus based on profile
  const hasInjury = userProfile?.injury_description || (userProfile?.pain_locations?.length ?? 0) > 0;
  const userName = userProfile?.name?.split(' ')[0] || 'Atleta';
  const greeting = getGreeting();

  function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Buongiorno';
    if (hour < 18) return 'Buon pomeriggio';
    return 'Buonasera';
  }

  // Pull to refresh handler
  const handleRefresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    toast.success("Dashboard aggiornata!");
  };

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <PullToRefresh onRefresh={handleRefresh}>
      {/* Skip to main content - Accessibility */}
      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-lg">
        Vai al contenuto principale
      </a>

      <motion.div
        id="main-content"
        className="flex flex-col h-full overflow-hidden gap-2"
        variants={container}
        initial="hidden"
        animate="show"
        role="main"
        aria-label="Dashboard principale"
      >
        {/* Personalized Header */}
        <motion.header variants={item} className="flex items-center justify-between py-1.5" role="banner">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 bg-gradient-to-br from-primary to-primary/70 rounded-full flex items-center justify-center shadow-lg ring-2 ring-background">
              <span className="font-bold text-primary-foreground text-base" aria-hidden="true">
                {userName.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex flex-col">
              <h1 className="font-bold text-lg leading-tight text-foreground">
                {greeting}, {userName}! 👋
              </h1>
              <time className="text-xs text-muted-foreground capitalize" dateTime={today.toISOString()}>
                {format(today, "EEEE d MMMM", { locale: it })}
              </time>
            </div>
          </div>

          <nav className="flex items-center gap-2" aria-label="Menu utente">
            <button
              className="p-2 rounded-full hover:bg-accent active:bg-accent/80 transition-colors relative touch-manipulation"
              aria-label="Notifiche (1 nuova)"
            >
              <Bell size={22} strokeWidth={2} className="text-foreground" />
              <span className="absolute top-2.5 right-2.5 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-background animate-pulse" aria-hidden="true"></span>
            </button>

            <Link
              to="/profile"
              className="w-9 h-9 bg-secondary rounded-full flex items-center justify-center overflow-hidden border border-border hover:bg-accent transition-colors touch-manipulation"
              aria-label="Profilo utente"
            >
              <User size={20} className="text-muted-foreground" />
            </Link>
          </nav>
        </motion.header>

        {/* Context-aware Welcome */}
        <motion.div variants={item} className="bg-gradient-to-r from-primary/10 via-primary/5 to-transparent rounded-2xl p-3 border border-primary/20">
          <div className="flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-primary mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-medium text-foreground">
                {hasInjury
                  ? "Oggi è un buon giorno per il recupero. I tuoi agenti AI sono pronti ad aiutarti."
                  : "I tuoi 3 agenti AI sono pronti. Allenamento, nutrizione o check-up?"}
              </p>
            </div>
          </div>
        </motion.div>

        {/* 🚨 Critical Alerts */}
        <motion.div variants={item} className="block">
          <RedFlagsAlert />
        </motion.div>

        {/* 🔥 PRIMARY CTA: Start Workout */}
        <motion.div variants={item} data-tour-id="tour-workout-btn">
          <Link
            to="/workout"
            className="group relative flex items-center justify-between p-4 sm:p-5 bg-primary text-primary-foreground rounded-2xl shadow-lg shadow-primary/25 overflow-hidden hover:bg-primary/90 transition-all active:scale-[0.98] touch-manipulation select-none min-h-[72px]"
          >
            <div className="relative z-10 flex items-center gap-4">
              <div className="p-3 sm:p-3 bg-white/20 backdrop-blur-sm rounded-full">
                <Play className="w-6 h-6 sm:w-6 sm:h-6 fill-current" />
              </div>
              <div>
                <h2 className="text-xl sm:text-lg font-bold leading-none">Inizia Workout</h2>
                <p className="text-primary-foreground/80 text-sm sm:text-xs mt-1.5 sm:mt-1 font-medium">
                  Allenamento Personalizzato
                </p>
              </div>
            </div>
            <ChevronRight className="w-7 h-7 sm:w-6 sm:h-6 opacity-50 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />

            {/* Decorative bg pattern */}
            <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-white/10 rounded-full blur-2xl" />
          </Link>
        </motion.div>

        import {GoogleFitWidget} from "../features/home/GoogleFitWidget";

        // ... (existing code)

        {/* 📊 Status Cards */}
        <motion.div variants={item} className="block">
          <CurrentPhaseCard />
        </motion.div>

        {/* 👟 Google Fit Integration */}
        <motion.div variants={item} className="block">
          <GoogleFitWidget />
        </motion.div>

        {/* 📈 KPI Grid */}
        <motion.div variants={item} className="grid grid-cols-2 gap-2">
          <PainTrendMiniChart days={7} />
          <ComplianceWidget />
        </motion.div>

        {/* 🤖 AI Agents - Your Team */}
        <motion.div variants={item} role="region" aria-labelledby="agents-heading" data-tour-id="tour-agents-section">
          <h2 id="agents-heading" className="hidden md:block text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider px-1">
            I Tuoi Agenti AI
          </h2>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 md:grid-cols-1">
            {/* Medical Agent */}
            <div data-tour-id="tour-medical-agent">
              <div className="min-w-0">
                <AgentCard
                  to="/medical"
                  title="Dr. Iron"
                  subtitle="Medico Sportivo AI"
                  description={hasInjury ? "Monitora il tuo recupero" : "Check-up e prevenzione"}
                  icon={<Stethoscope size={28} />}
                  gradient="from-red-500 to-rose-600"
                  recommended={!!hasInjury}
                />
              </div>
            </div>

            {/* Coach Agent */}
            <div className="min-w-0">
              <AgentCard
                to="/coach"
                title="Coach Iron"
                subtitle="Personal Trainer AI"
                description="Allenamenti personalizzati e tecnica"
                icon={<Trophy size={28} />}
                gradient="from-blue-500 to-indigo-600"
                recommended={!hasInjury}
              />
            </div>

            {/* Nutrition Agent */}
            <div className="min-w-0 sm:col-span-2 md:col-span-1">
              <AgentCard
                to="/nutrition"
                title="Chef Iron"
                subtitle="Nutrizionista AI"
                description="Piani alimentari e macro tracking"
                icon={<Utensils size={28} />}
                gradient="from-orange-500 to-amber-600"
              />
            </div>
          </div>
        </motion.div>

        {/* 📊 Quick Stats */}
        <motion.div variants={item} role="region" aria-labelledby="quick-access-heading" data-tour-id="tour-quick-access">
          <h2 id="quick-access-heading" className="hidden md:block text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider px-1">
            Accesso Rapido
          </h2>
          <div className="grid grid-cols-2 gap-2">
            <div className="min-w-0">
              <QuickActionCard
                to="/progress"
                title="Progressi"
                icon={<BarChart2 size={22} />}
                color="text-amber-500"
                bg="bg-amber-500/10"
              />
            </div>
            <div className="min-w-0">
              <QuickActionCard
                to="/exercises"
                title="Esercizi"
                icon={<Dumbbell size={22} />}
                color="text-emerald-500"
                bg="bg-emerald-500/10"
              />
            </div>
          </div>
        </motion.div>

        {/* 🎯 Welcome Tour - Auto-start per nuovi utenti */}
        <div className="hidden lg:block">
          <DashboardTour autoStart={true} />
        </div>
      </motion.div>
    </PullToRefresh>
  );
}

// ============================================================================
// AGENT CARD - Hero component per ogni agente AI
// ============================================================================

function AgentCard({
  to,
  title,
  subtitle,
  description,
  icon,
  gradient,
  recommended = false,
}: {
  to: string;
  title: string;
  subtitle: string;
  description: string;
  icon: React.ReactNode;
  gradient: string;
  recommended?: boolean;
}) {
  const [showQuickAction, setShowQuickAction] = useState(false);

  const handleLongPress = () => {
    setShowQuickAction(true);
    toast.info({
      title: `Azioni rapide ${title}`,
      description: "Presto disponibili azioni contestuali",
      duration: 2000,
    });
  };

  const handleSwipeLeft = () => {
    // Quick action: go directly to chat
    toast.success(`Apertura chat con ${title}...`);
    // In a real app: router.push(`${to}?tab=chat`)
  };

  return (
    <GestureWrapper
      onLongPress={handleLongPress}
      onSwipeLeft={handleSwipeLeft}
      hapticFeedback="medium"
    >
      <Link
        to={to}
        className={cn(
          "group relative flex items-center gap-3 p-3 rounded-2xl border bg-card overflow-hidden",
          "transition-all duration-200 active:scale-[0.98] hover:shadow-xl hover:scale-[1.01] touch-manipulation select-none",
          recommended && "ring-2 ring-primary ring-offset-2"
        )}
      >
        {/* Agent Avatar */}
        <div className={cn(
          "shrink-0 w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center text-white shadow-lg group-hover:shadow-xl transition-shadow",
          gradient
        )}>
          {icon}
        </div>

        {/* Agent Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-sm text-foreground">{title}</h3>
            {recommended && (
              <span className="text-[10px] font-bold uppercase tracking-wide bg-primary text-primary-foreground px-1.5 py-0.5 rounded" aria-label="Consigliato per te">
                Consigliato
              </span>
            )}
          </div>
          <p className="text-xs text-muted-foreground font-medium">{subtitle}</p>
          <p className="text-xs text-foreground/80 mt-0.5 truncate">{description}</p>
        </div>

        {/* Arrow con micro-interaction */}
        <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-foreground group-hover:translate-x-1 transition-all shrink-0" aria-hidden="true" />

        {/* Decorative gradient con pulse su hover */}
        <div className={cn(
          "absolute top-0 right-0 w-24 h-24 opacity-10 rounded-full blur-2xl pointer-events-none bg-gradient-to-br group-hover:opacity-20 transition-opacity",
          gradient
        )} />

        {/* Quick action hint (appears on swipe) */}
        {showQuickAction && (
          <div className="absolute -right-16 top-1/2 -translate-y-1/2 bg-primary text-primary-foreground p-2 rounded-full shadow-lg">
            <MessageSquare size={18} />
          </div>
        )}
      </Link>
    </GestureWrapper>
  );
}

// ============================================================================
// QUICK ACTION CARD
// ============================================================================

function QuickActionCard({
  to,
  title,
  icon,
  color,
  bg,
}: {
  to: string;
  title: string;
  icon: React.ReactNode;
  color: string;
  bg: string;
}) {
  return (
    <Link
      to={to}
      className="flex items-center gap-3 p-3 rounded-xl border bg-card transition-all duration-200 active:scale-[0.97] hover:shadow-md touch-manipulation select-none"
    >
      <div className={cn("p-2 rounded-lg", bg, color)}>
        {icon}
      </div>
      <span className="font-semibold text-sm text-foreground">{title}</span>
      <ChevronRight className="w-4 h-4 text-muted-foreground ml-auto" />
    </Link>
  );
}
