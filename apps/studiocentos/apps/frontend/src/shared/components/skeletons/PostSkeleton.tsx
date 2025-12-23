/**
 * PostSkeleton Component
 * Loading skeleton for scheduled posts
 */

import { useTheme } from '../../contexts/ThemeContext';

export function PostSkeleton() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <div className={`p-4 flex items-start gap-4 animate-pulse ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
      {/* Status Dot */}
      <div className={`w-3 h-3 rounded-full mt-2 ${isDark ? 'bg-white/20' : 'bg-gray-300'}`} />

      {/* Date */}
      <div className="w-32 space-y-2">
        <div className={`h-5 rounded ${isDark ? 'bg-white/20' : 'bg-gray-300'}`} />
        <div className={`h-4 w-20 rounded ${isDark ? 'bg-white/10' : 'bg-gray-200'}`} />
      </div>

      {/* Platforms */}
      <div className="flex gap-2">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className={`w-8 h-8 rounded-lg ${isDark ? 'bg-white/10' : 'bg-gray-200'}`}
          />
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 space-y-2">
        <div className={`h-4 rounded ${isDark ? 'bg-white/20' : 'bg-gray-300'}`} />
        <div className={`h-4 w-3/4 rounded ${isDark ? 'bg-white/10' : 'bg-gray-200'}`} />
      </div>

      {/* Status Badge */}
      <div className={`w-24 h-6 rounded-full ${isDark ? 'bg-white/10' : 'bg-gray-200'}`} />

      {/* Actions */}
      <div className="flex gap-1">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className={`w-8 h-8 rounded ${isDark ? 'bg-white/10' : 'bg-gray-200'}`}
          />
        ))}
      </div>
    </div>
  );
}
