/**
 * Offline Indicator Component
 * Shows connection status when offline/back online
 */

import { WifiOff, Wifi } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useOfflineIndicator, useOfflineQueue } from '../../hooks/useOfflineQueue';
import { cn } from '../../lib/utils';

export function OfflineIndicator() {
  const { isOnline, showIndicator } = useOfflineIndicator();
  const { queue, isSyncing } = useOfflineQueue();

  return (
    <AnimatePresence>
      {showIndicator && (
        <motion.div
          initial={{ y: -100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -100, opacity: 0 }}
          className="fixed top-20 left-1/2 -translate-x-1/2 z-50 safe-top"
        >
          <div
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-full shadow-lg text-sm font-medium',
              isOnline
                ? 'bg-green-500 text-white'
                : 'bg-yellow-500 text-yellow-950'
            )}
          >
            {isOnline ? (
              <>
                <Wifi size={16} />
                <span>Di nuovo online!</span>
                {queue.length > 0 && (
                  <span className="ml-1 opacity-80">
                    {isSyncing ? 'Sincronizzando...' : `(${queue.length} in coda)`}
                  </span>
                )}
              </>
            ) : (
              <>
                <WifiOff size={16} />
                <span>Modalità offline</span>
                <span className="ml-1 opacity-80 text-xs">
                  Le modifiche saranno sincronizzate
                </span>
              </>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
