/**
 * PWA Install Prompt Hook
 * Gestisce l'installazione della PWA con prompt personalizzato
 */

import { useState, useEffect } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

interface UsePWAInstallReturn {
  isInstallable: boolean;
  isInstalled: boolean;
  showPrompt: () => Promise<boolean>;
  dismissPrompt: () => void;
  installPromptEvent: BeforeInstallPromptEvent | null;
}

/**
 * Hook per gestire l'installazione PWA
 */
export function usePWAInstall(): UsePWAInstallReturn {
  const [installPromptEvent, setInstallPromptEvent] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if already installed
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    // @ts-ignore - Safari specific
    const isSafariStandalone = window.navigator.standalone === true;

    setIsInstalled(isStandalone || isSafariStandalone);

    // Listen for install prompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setInstallPromptEvent(e as BeforeInstallPromptEvent);
    };

    // Listen for successful install
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setInstallPromptEvent(null);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const showPrompt = async (): Promise<boolean> => {
    if (!installPromptEvent) {
      return false;
    }

    try {
      await installPromptEvent.prompt();
      const { outcome } = await installPromptEvent.userChoice;

      if (outcome === 'accepted') {
        setInstallPromptEvent(null);
        return true;
      }

      return false;
    } catch (error) {
      console.error('Error showing install prompt:', error);
      return false;
    }
  };

  const dismissPrompt = () => {
    setInstallPromptEvent(null);
    localStorage.setItem('pwa-install-dismissed', Date.now().toString());
  };

  return {
    isInstallable: !!installPromptEvent && !isInstalled,
    isInstalled,
    showPrompt,
    dismissPrompt,
    installPromptEvent,
  };
}

/**
 * Hook per mostrare prompt dopo N sessioni
 */
export function usePWAInstallPrompt(sessionsBeforePrompt: number = 3) {
  const { isInstallable, showPrompt, dismissPrompt } = usePWAInstall();
  const [shouldShowPrompt, setShouldShowPrompt] = useState(false);

  useEffect(() => {
    if (!isInstallable) return;

    // Check if already dismissed
    const dismissed = localStorage.getItem('pwa-install-dismissed');
    if (dismissed) {
      const dismissedTime = parseInt(dismissed);
      const daysSinceDismissed = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24);

      // Don't show again for 7 days after dismissal
      if (daysSinceDismissed < 7) {
        return;
      }
    }

    // Track sessions
    const sessionsKey = 'pwa-sessions-count';
    const currentSessions = parseInt(localStorage.getItem(sessionsKey) || '0');

    if (currentSessions < sessionsBeforePrompt) {
      localStorage.setItem(sessionsKey, (currentSessions + 1).toString());
      return;
    }

    // Show prompt after N sessions
    setShouldShowPrompt(true);
  }, [isInstallable, sessionsBeforePrompt]);

  const handleInstall = async () => {
    const accepted = await showPrompt();
    if (accepted) {
      localStorage.setItem('pwa-sessions-count', '0');
    }
    setShouldShowPrompt(false);
  };

  const handleDismiss = () => {
    dismissPrompt();
    setShouldShowPrompt(false);
  };

  return {
    shouldShowPrompt,
    handleInstall,
    handleDismiss,
  };
}
