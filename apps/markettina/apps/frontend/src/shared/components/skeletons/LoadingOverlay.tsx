/**
 * LoadingOverlay Component
 * Full-screen loading overlay with message
 */

import { Loader2 } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

interface LoadingOverlayProps {
  message?: string;
  transparent?: boolean;
}

export function LoadingOverlay({ message = 'Caricamento...', transparent = false }: LoadingOverlayProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center ${
        transparent
          ? 'bg-black/30'
          : isDark
          ? 'bg-[#0A0A0A]/90'
          : 'bg-white/90'
      } backdrop-blur-sm`}
    >
      <div className="flex flex-col items-center gap-4">
        <Loader2
          className={`w-12 h-12 animate-spin ${
            isDark ? 'text-gold' : 'text-gold'
          }`}
        />
        {message && (
          <p
            className={`text-lg font-medium ${
              isDark ? 'text-white' : 'text-gray-900'
            }`}
          >
            {message}
          </p>
        )}
      </div>
    </div>
  );
}
