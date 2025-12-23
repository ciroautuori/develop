/**
 * PasswordStrengthMeter - Visual password strength indicator.
 */

import { getPasswordStrength } from '../../lib/validation';

interface PasswordStrengthMeterProps {
  password: string;
}

export function PasswordStrengthMeter({ password }: PasswordStrengthMeterProps) {
  if (!password) return null;

  const { strength, score, feedback } = getPasswordStrength(password);

  const strengthColors = {
    weak: 'bg-gray-500',
    medium: 'bg-gold',
    strong: 'bg-gold',
    'very-strong': 'bg-gold',
  };

  const strengthLabels = {
    weak: 'Weak',
    medium: 'Medium',
    strong: 'Strong',
    'very-strong': 'Very Strong',
  };

  const strengthTextColors = {
    weak: 'text-gray-500 dark:text-gray-400',
    medium: 'text-gold dark:text-gold',
    strong: 'text-gold dark:text-gold',
    'very-strong': 'text-gold dark:text-gold',
  };

  return (
    <div className="space-y-2">
      {/* Strength bar */}
      <div className="flex gap-1">
        {[1, 2, 3, 4].map((level) => (
          <div
            key={level}
            className={`h-2 flex-1 rounded-full transition-all duration-300 ${
              score >= level * 2 ? strengthColors[strength] : 'bg-gray-200 dark:bg-gray-700'
            }`}
          />
        ))}
      </div>

      {/* Strength label */}
      <div className="flex items-center justify-between">
        <span className={`text-sm font-medium ${strengthTextColors[strength]}`}>
          {strengthLabels[strength]}
        </span>
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {score}/8 points
        </span>
      </div>

      {/* Feedback */}
      {feedback.length > 0 && (
        <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
          {feedback.map((item, index) => (
            <li key={index} className="flex items-center gap-2">
              <span className="text-gray-400">•</span>
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
