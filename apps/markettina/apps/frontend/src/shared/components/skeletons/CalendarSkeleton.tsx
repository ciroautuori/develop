/**
 * CalendarSkeleton Component
 * Loading skeleton for calendar view
 */

import { useTheme } from '../../contexts/ThemeContext';

export function CalendarSkeleton() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <div className="space-y-6 animate-pulse">
      {/* Header Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={`p-4 rounded-xl ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}
          >
            <div className={`h-8 w-16 mb-2 rounded ${isDark ? 'bg-white/20' : 'bg-gray-300'}`} />
            <div className={`h-4 w-24 rounded ${isDark ? 'bg-white/10' : 'bg-gray-200'}`} />
          </div>
        ))}
      </div>

      {/* Posts List */}
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className={`p-4 flex items-start gap-4 rounded-xl ${
              isDark ? 'bg-white/5 border border-white/10' : 'bg-gray-50 border border-gray-200'
            }`}
          >
            <div className={`w-3 h-3 rounded-full mt-2 ${isDark ? 'bg-white/20' : 'bg-gray-300'}`} />
            <div className="w-32 space-y-2">
              <div className={`h-5 rounded ${isDark ? 'bg-white/20' : 'bg-gray-300'}`} />
              <div className={`h-4 w-20 rounded ${isDark ? 'bg-white/10' : 'bg-gray-200'}`} />
            </div>
            <div className="flex-1 space-y-2">
              <div className={`h-4 rounded ${isDark ? 'bg-white/20' : 'bg-gray-300'}`} />
              <div className={`h-4 w-3/4 rounded ${isDark ? 'bg-white/10' : 'bg-gray-200'}`} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
