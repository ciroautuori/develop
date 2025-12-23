import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
}

export function LoadingSpinner({
  message = 'Caricamento...',
  size = 'md',
  fullScreen = false
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  const Container = fullScreen ? 'div' : 'div';
  const containerClasses = fullScreen
    ? 'flex flex-col items-center justify-center min-h-screen'
    : 'flex flex-col items-center justify-center p-8';

  return (
    <Container className={containerClasses}>
      <Loader2 className={`${sizeClasses[size]} animate-spin text-primary mb-2`} />
      {message && (
        <p className="text-sm text-muted-foreground">{message}</p>
      )}
    </Container>
  );
}
