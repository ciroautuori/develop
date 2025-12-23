import React, { Component, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // Aggiorna lo state per mostrare la UI di fallback
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Silenziosamente logga l'errore invece di mostrarlo in console
    console.debug('Error caught by boundary:', error, errorInfo);
    
    // Non lasciare che l'errore si propaghi alla console
    // Questo dovrebbe fermare gli errori {} vuoti
  }

  render() {
    if (this.state.hasError) {
      // Fallback UI semplice o il fallback custom
      return this.props.fallback || (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h2 className="text-xl font-semibold mb-2">Qualcosa è andato storto</h2>
            <p className="text-muted-foreground mb-4">Si è verificato un errore. Ricarica la pagina.</p>
            <button 
              onClick={() => window.location.reload()} 
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md"
            >
              Ricarica
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
