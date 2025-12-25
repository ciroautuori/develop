
import { useState, useEffect } from "react";
import { Loader2, Sparkles, BrainCircuit, Activity, Heart, Ruler, SearchCheck } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const LOADING_MESSAGES = [
    { icon: SearchCheck, text: "Analisi dati biometrici in corso...", color: "text-blue-500" },
    { icon: Ruler, text: "Calcolo parametri antropometrici...", color: "text-indigo-500" },
    { icon: Activity, text: "Valutazione livello esperienza...", color: "text-violet-500" },
    { icon: Heart, text: "Configurazione protocolli medici...", color: "text-rose-500" },
    { icon: BrainCircuit, text: "L'AI sta strutturando il tuo piano...", color: "text-amber-500" },
    { icon: Sparkles, text: "Ottimizzazione finale in corso...", color: "text-emerald-500" },
];

export function SmartLoader() {
    const [currentIndex, setCurrentIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentIndex((prev) => (prev + 1) % LOADING_MESSAGES.length);
        }, 1200); // Change message every 1.2s

        return () => clearInterval(interval);
    }, []);

    const CurrentMessage = LOADING_MESSAGES[currentIndex];
    const Icon = CurrentMessage.icon;

    return (
        <div className="flex flex-col items-center justify-center min-h-[100dvh] bg-background px-4 text-center">
            {/* Animated Icon Container */}
            <div className="relative w-24 h-24 mb-8 flex items-center justify-center">
                {/* Background Rings */}
                <div className="absolute inset-0 border-4 border-primary/10 rounded-full animate-[spin_3s_linear_infinite]" />
                <div className="absolute inset-2 border-4 border-t-primary/30 border-r-primary/30 border-b-transparent border-l-transparent rounded-full animate-[spin_2s_linear_infinite]" />

                {/* Central Icon - Changing */}
                <div className="relative z-10 bg-background/50 backdrop-blur-sm rounded-full p-4">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={currentIndex}
                            initial={{ opacity: 0, scale: 0.5 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.5 }}
                            transition={{ duration: 0.3 }}
                        >
                            <Icon className={`w-10 h-10 ${CurrentMessage.color}`} />
                        </motion.div>
                    </AnimatePresence>
                </div>
            </div>

            {/* Main Heading */}
            <h2 className="text-2xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/60">
                Creazione Profilo AI
            </h2>

            {/* Rotating Message */}
            <div className="h-8 relative w-full max-w-md">
                <AnimatePresence mode="wait">
                    <motion.p
                        key={currentIndex}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="text-muted-foreground font-medium absolute inset-0 flex items-center justify-center"
                    >
                        {CurrentMessage.text}
                    </motion.p>
                </AnimatePresence>
            </div>

            {/* Progress Bar (Fake but satisfying) */}
            <div className="w-full max-w-xs h-1.5 bg-secondary/30 rounded-full mt-8 overflow-hidden">
                <motion.div
                    className="h-full bg-primary"
                    initial={{ width: "0%" }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 8, ease: "linear" }} // 8s matches roughly total loop
                />
            </div>
        </div>
    );
}
