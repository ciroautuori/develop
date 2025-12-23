/**
 * Dashboard Tour - Step definitions
 * Stile Google: guida l'utente attraverso le funzionalità principali
 */

import type { TourStep } from '../hooks/useTour';

export const DASHBOARD_TOUR_ID = 'dashboard-welcome';

export const dashboardTourSteps: TourStep[] = [
  {
    id: 'welcome',
    targetId: null, // Fullscreen welcome
    title: 'Benvenuto in IronRep! 🎉',
    description: 'Hai a disposizione 3 agenti AI specializzati: Coach per gli allenamenti, Nutrizionista per i pasti, e Medico Sportivo per il recupero. Vediamoli insieme!',
    position: 'center',
  },
  {
    id: 'workout-cta',
    targetId: 'tour-workout-btn',
    title: 'Inizia il tuo Workout 💪',
    description: 'Questo è il tuo pulsante principale. Clicca qui per iniziare un allenamento personalizzato generato dall\'AI in base al tuo profilo.',
    position: 'bottom',
  },
  {
    id: 'agents-section',
    targetId: 'tour-agents-section',
    title: 'I Tuoi Agenti AI 🤖',
    description: 'Dr. Iron ti segue nel recupero, Coach Iron crea i tuoi workout, Chef Iron pianifica i pasti. Ognuno impara dalle tue preferenze!',
    position: 'top',
  },
  {
    id: 'medical-agent',
    targetId: 'tour-medical-agent',
    title: 'Dr. Iron - Medico Sportivo 🩺',
    description: 'Monitora infortuni, traccia il dolore, ricevi protocolli di riabilitazione personalizzati. Perfetto se hai fastidi o vuoi prevenirli.',
    position: 'bottom',
  },
  {
    id: 'progress',
    targetId: 'tour-quick-access',
    title: 'Monitora i Progressi 📊',
    description: 'Visualizza grafici dettagliati del tuo percorso: peso, misure, forza, compliance. I dati guidano l\'AI nelle sue raccomandazioni.',
    position: 'top',
  },
  {
    id: 'complete',
    targetId: null, // Fullscreen finale
    title: 'Sei pronto! 🚀',
    description: 'Inizia esplorando la dashboard o parla con uno degli agenti. IronRep impara ogni giorno dalle tue interazioni. In bocca al lupo!',
    position: 'center',
  },
];
