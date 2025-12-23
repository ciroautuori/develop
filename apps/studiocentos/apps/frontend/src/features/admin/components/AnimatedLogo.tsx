/**
 * Logo Animato StudioCentOS
 * Identico al logo nella Landing page
 */

import { useTheme } from '../../../shared/contexts/ThemeContext';

interface AnimatedLogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
}

export function AnimatedLogo({ size = 'md', showText = true }: AnimatedLogoProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-10 h-10',
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-lg',
    lg: 'text-xl',
  };

  return (
    <a href="/admin" className="flex items-center gap-2 group relative z-50">
      <div className={`relative ${sizeClasses[size]} flex items-center justify-center`}>
        {/* Glow pulsante */}
        <div className="absolute inset-[-8px] rounded-full bg-[radial-gradient(circle,rgba(212,175,55,0.3)_0%,transparent_70%)] animate-pulse" />

        {/* Logo SVG con animazioni */}
        <svg viewBox="0 0 100 100" className="w-full h-full relative z-10">
          <style>
            {`
              @keyframes rotateRays {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
              }
              @keyframes brightness {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
              }
              .rays-group {
                animation: rotateRays 20s linear infinite;
                transform-origin: 50% 50%;
              }
              .bulb-glow {
                animation: brightness 2s ease-in-out infinite;
              }
            `}
          </style>

          {/* Raggi rotanti */}
          <g className="rays-group">
            <line x1="50" y1="20" x2="50" y2="10" stroke="#D4AF37" strokeWidth="2"/>
            <line x1="65" y1="25" x2="72" y2="18" stroke="#D4AF37" strokeWidth="2"/>
            <line x1="70" y1="50" x2="80" y2="50" stroke="#D4AF37" strokeWidth="2"/>
            <line x1="65" y1="75" x2="72" y2="82" stroke="#D4AF37" strokeWidth="2"/>
            <line x1="50" y1="80" x2="50" y2="90" stroke="#D4AF37" strokeWidth="2"/>
            <line x1="35" y1="75" x2="28" y2="82" stroke="#D4AF37" strokeWidth="2"/>
            <line x1="30" y1="50" x2="20" y2="50" stroke="#D4AF37" strokeWidth="2"/>
            <line x1="35" y1="25" x2="28" y2="18" stroke="#D4AF37" strokeWidth="2"/>
          </g>

          {/* Lampadina centrale con brightness */}
          <circle
            cx="50" cy="50" r="20"
            fill="none"
            stroke="#D4AF37"
            strokeWidth="2"
            className="bulb-glow"
          />
          <path
            d="M 45 55 L 48 60 L 52 60 L 55 55"
            fill="none"
            stroke="#D4AF37"
            strokeWidth="2"
            className="bulb-glow"
          />
        </svg>
      </div>

      {showText && (
        <div className={`font-bold tracking-tight ${textSizeClasses[size]}`}>
          <span className="text-gold">STUDIO</span>
          <span className={isDark ? "text-white" : "text-gray-900"}>CENTOS</span>
        </div>
      )}
    </a>
  );
}
