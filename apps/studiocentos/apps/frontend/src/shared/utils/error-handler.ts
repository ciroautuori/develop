/**
 * Error Handler Utility
 * Centralized error handling and user-friendly messages
 */

import { toast } from 'sonner';

export interface ApiError {
  status: number;
  message: string;
  detail?: string;
  code?: string;
}

export class AppError extends Error {
  constructor(
    message: string,
    public code?: string,
    public status?: number,
    public detail?: string
  ) {
    super(message);
    this.name = 'AppError';
  }
}

/**
 * Extract error message from various error types
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof AppError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === 'string') {
    return error;
  }

  if (error && typeof error === 'object' && 'message' in error) {
    return String(error.message);
  }

  return 'Si è verificato un errore sconosciuto';
}

/**
 * Handle API response errors
 */
export async function handleApiError(response: Response, context?: string): Promise<never> {
  let errorMessage = 'Errore nella richiesta';
  let errorDetail: string | undefined;

  try {
    const data = await response.json();
    errorMessage = data.message || data.detail || errorMessage;
    errorDetail = data.detail;
  } catch {
    errorMessage = response.statusText || errorMessage;
  }

  // Status-specific messages
  const statusMessages: Record<number, string> = {
    400: 'Richiesta non valida',
    401: 'Sessione scaduta. Effettua nuovamente il login',
    403: 'Non hai i permessi per questa operazione',
    404: 'Risorsa non trovata',
    409: 'Conflitto: questa operazione è già stata eseguita',
    422: 'Dati non validi',
    429: 'Troppe richieste. Riprova tra qualche minuto',
    500: 'Errore del server. Riprova più tardi',
    502: 'Servizio temporaneamente non disponibile',
    503: 'Servizio in manutenzione',
  };

  const userMessage = statusMessages[response.status] || errorMessage;
  const fullMessage = context ? `${context}: ${userMessage}` : userMessage;

  // Show toast notification
  if (response.status === 401) {
    toast.error('Sessione scaduta', {
      description: 'Effettua nuovamente il login',
      duration: 5000,
    });
    // Redirect to login after delay
    setTimeout(() => {
      window.location.href = '/login';
    }, 2000);
  } else {
    toast.error(fullMessage, {
      description: errorDetail,
      duration: 4000,
    });
  }

  // Log error in development
  if (import.meta.env.DEV) {
    console.error('[API Error]', {
      status: response.status,
      message: errorMessage,
      detail: errorDetail,
      context,
      url: response.url,
    });
  }

  throw new AppError(fullMessage, `HTTP_${response.status}`, response.status, errorDetail);
}

/**
 * Handle generic errors with user-friendly messages
 */
export function handleError(error: unknown, context?: string): void {
  const message = getErrorMessage(error);
  const fullMessage = context ? `${context}: ${message}` : message;

  toast.error(fullMessage, { duration: 4000 });

  if (import.meta.env.DEV) {
    console.error('[Error]', { error, context });
  }
}

/**
 * Retry function with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: unknown;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      if (i < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, i);
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}

/**
 * Validate API response and throw if not ok
 */
export async function validateResponse(response: Response, context?: string): Promise<Response> {
  if (!response.ok) {
    await handleApiError(response, context);
  }
  return response;
}

/**
 * Safe JSON parse with error handling
 */
export async function safeJsonParse<T>(response: Response): Promise<T> {
  try {
    return await response.json();
  } catch (error) {
    console.error('[JSON Parse Error]', error);
    throw new AppError('Risposta del server non valida');
  }
}

/**
 * Network error handler
 */
export function handleNetworkError(context?: string): void {
  const message = 'Errore di connessione. Verifica la tua connessione internet';
  toast.error(context ? `${context}: ${message}` : message, {
    duration: 5000,
  });
}
