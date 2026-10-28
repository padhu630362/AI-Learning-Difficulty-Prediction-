import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const ThemeToggle = ({ className = '', size = 'md' }) => {
  const { theme, toggleTheme, isDark } = useTheme();

  const sizeClasses = {
    sm: 'p-1.5 text-xs',
    md: 'p-2 text-sm',
    lg: 'p-2.5 text-base',
  };

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={`Switch to ${isDark ? 'morning' : 'night'} theme`}
      title={`Switch to ${isDark ? 'Morning (Warm Ivory)' : 'Night (Deep Forest)'} theme`}
      className={`inline-flex items-center justify-center rounded-xl transition-all duration-300 border focus:outline-none focus:ring-2 focus:ring-gold-500/50 ${
        isDark
          ? 'bg-forest-900/90 text-gold-400 border-forest-700/80 hover:bg-forest-800 hover:text-gold-300 hover:border-gold-500/50 shadow-inner'
          : 'bg-white/90 text-forest-800 border-forest-200/80 hover:bg-ivory-100 hover:text-forest-950 hover:border-gold-500/60 shadow-xs'
      } ${sizeClasses[size] || sizeClasses.md} ${className}`}
    >
      {isDark ? (
        <Sun className={`${iconSizes[size] || iconSizes.md} transition-transform duration-300 rotate-0 hover:rotate-45 text-gold-400`} />
      ) : (
        <Moon className={`${iconSizes[size] || iconSizes.md} transition-transform duration-300 -rotate-12 hover:rotate-0 text-forest-800`} />
      )}
      <span className="sr-only">Toggle theme</span>
    </button>
  );
};

export default ThemeToggle;

