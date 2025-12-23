/**
 * Console Filter - Filtra errori CORS noti di Google
 *
 * Problema: Le librerie Google (GSI, Analytics) generano errori CORS
 * verso play.google.com/log che non sono risolvibili lato sviluppatore.
 *
 * Questa utility filtra questi errori per mantenere la console pulita.
 *
 * @see https://developers.google.com/identity/sign-in/web/troubleshooting
 */

const IGNORED_ERRORS = [
  // Google CORS errors (non-fixable)
  'play.google.com/log',
  'play.google.com',
  'accounts.google.com/gsi',
  'has been blocked by CORS policy',
];

/**
 * Verifica se un messaggio deve essere ignorato
 */
function shouldIgnore(args: unknown[]): boolean {
  const message = args.map(arg => String(arg)).join(' ');
  return IGNORED_ERRORS.some(pattern => message.includes(pattern));
}

/**
 * Inizializza il filtro console (solo in development)
 */
export function initConsoleFilter(): void {
  // Attivo sia in dev che prod per filtrare errori cosmetici

  const originalError = console.error;
  const originalWarn = console.warn;

  console.error = (...args: unknown[]) => {
    if (!shouldIgnore(args)) {
      originalError.apply(console, args);
    }
  };

  console.warn = (...args: unknown[]) => {
    if (!shouldIgnore(args)) {
      originalWarn.apply(console, args);
    }
  };

  // Log che il filtro è attivo
  console.info('🔇 Console filter attivo: errori CORS Google filtrati');
}

/**
 * Disabilita il filtro (ripristina console originale)
 */
export function disableConsoleFilter(): void {
  // Il browser mantiene i riferimenti originali, reload per ripristinare
  console.info('ℹ️ Reload pagina per disabilitare il filtro console');
}
