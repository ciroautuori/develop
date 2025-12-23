/**
 * LeadCardSkeleton Component
 * Loading skeleton for lead search results
 */

import { useTheme } from '../../contexts/ThemeContext';

export function LeadCardSkeleton() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <div
      className={`p-4 rounded-xl animate-pulse ${
        isDark ? 'bg-white/5 border border-white/10' : 'bg-gray-50 border border-gray-200'
      }`}
    >
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <div className={`w-5 h-5 rounded mt-1 ${isDark ? 'bg-white/20' : 'bg-gray-300'}`} />

        {/* Content */}
        <div className="flex-1 space-y-3">
          {/* Title & Badge */}
          <div className="flex items-center gap-2">
            <div className={`h-6 w-48 rounded ${isDark ? 'bg-white/20' : 'bg-gray-300'}`} />
            <div className={`h-5 w-16 rounded-full ${isDark ? 'bg-white/10' : 'bg-gray-200'}`} />
          </div>

          {/* Address */}
          <div className={`h-4 w-64 rounded ${isDark ? 'bg-white/10' : 'bg-gray-200'}`} />

          {/* Contact Info */}
          <div className="flex gap-4">
            <div className={`h-4 w-32 rounded ${isDark ? 'bg-white/10' : 'bg-gray-200'}`} />
            <div className={`h-4 w-28 rounded ${isDark ? 'bg-white/10' : 'bg-gray-200'}`} />
            <div className={`h-4 w-36 rounded ${isDark ? 'bg-white/10' : 'bg-gray-200'}`} />
          </div>

          {/* Tags */}
          <div className="flex gap-2">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className={`h-6 w-20 rounded ${isDark ? 'bg-white/10' : 'bg-gray-200'}`}
              />
            ))}
          </div>
        </div>

        {/* Score */}
        <div className="text-center space-y-1">
          <div className={`h-8 w-12 rounded ${isDark ? 'bg-white/20' : 'bg-gray-300'}`} />
          <div className={`h-3 w-12 rounded ${isDark ? 'bg-white/10' : 'bg-gray-200'}`} />
        </div>
      </div>
    </div>
  );
}
