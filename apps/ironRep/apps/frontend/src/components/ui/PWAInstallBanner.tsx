/**
 * PWA Install Banner Component
 * Banner personalizzato per installazione PWA
 */

import { X, Download, Smartphone } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePWAInstallPrompt } from '../../hooks/usePWAInstall';
import { cn } from '../../lib/utils';
import { hapticFeedback } from '../../lib/haptics';

export function PWAInstallBanner() {
  const { shouldShowPrompt, handleInstall, handleDismiss } = usePWAInstallPrompt(3);

  return (
    <AnimatePresence>
      {shouldShowPrompt && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className="fixed bottom-20 left-4 right-4 lg:bottom-4 lg:left-auto lg:right-4 lg:max-w-md z-50"
        >
          <div className="bg-gradient-to-r from-primary to-primary/90 text-primary-foreground rounded-2xl shadow-2xl p-4 border-2 border-primary-foreground/20">
            <button
              onClick={() => {
                hapticFeedback.selection();
                handleDismiss();
              }}
              className="absolute top-2 right-2 p-2 hover:bg-primary-foreground/20 rounded-full transition-colors"
              aria-label="Chiudi"
            >
              <X size={20} />
            </button>

            <div className="flex items-start gap-4 pr-8">
              <div className="flex-shrink-0 p-3 bg-primary-foreground/10 rounded-xl">
                <Smartphone size={28} />
              </div>

              <div className="flex-1">
                <h3 className="font-bold text-lg mb-1">
                  Installa IronRep
                </h3>
                <p className="text-sm opacity-90 mb-3">
                  Accesso rapido, notifiche e funzionalità offline. Usa l'app come una nativa!
                </p>

                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      hapticFeedback.impact("medium");
                      handleInstall();
                    }}
                    className={cn(
                      "flex-1 bg-primary-foreground text-primary font-bold py-2.5 px-4 rounded-xl",
                      "flex items-center justify-center gap-2",
                      "hover:scale-105 active:scale-95 transition-transform",
                      "shadow-md"
                    )}
                  >
                    <Download size={18} />
                    Installa
                  </button>

                  <button
                    onClick={() => {
                      hapticFeedback.selection();
                      handleDismiss();
                    }}
                    className="px-4 py-2.5 rounded-xl font-medium opacity-90 hover:opacity-100 hover:bg-primary-foreground/10 transition-all"
                  >
                    Dopo
                  </button>
                </div>
              </div>
            </div>

            {/* Decorative gradient */}
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary-foreground/5 to-transparent pointer-events-none" />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
