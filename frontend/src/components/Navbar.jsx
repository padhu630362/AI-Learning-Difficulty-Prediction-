import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import ThemeToggle from './ThemeToggle';
import { Menu, LogOut, Sparkles, Shield, GraduationCap, BookOpen } from 'lucide-react';

const Navbar = ({ onToggleSidebar }) => {
  const { user, logout } = useAuth();
  const { isDark } = useTheme();

  const getRoleBadge = (role) => {
    switch (role) {
      case 'admin':
        return {
          label: 'Admin',
          icon: Shield,
          style: 'bg-gold-500/10 text-gold-700 dark:text-gold-300 border-gold-500/30'
        };
      case 'instructor':
        return {
          label: 'Instructor',
          icon: BookOpen,
          style: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-500/30'
        };
      case 'student':
      default:
        return {
          label: 'Student',
          icon: GraduationCap,
          style: 'bg-forest-100 dark:bg-forest-900 text-forest-800 dark:text-forest-200 border-forest-300 dark:border-forest-700'
        };
    }
  };

  const badge = getRoleBadge(user?.role);
  const BadgeIcon = badge.icon;

  return (
    <header className={`sticky top-0 z-40 backdrop-blur-md border-b transition-colors duration-300 ${
      isDark
        ? 'bg-forest-950/90 border-forest-800/80 text-forest-100'
        : 'bg-white/95 border-forest-200/80 text-forest-950 shadow-xs'
    }`}>
      <div className="flex items-center justify-between px-4 sm:px-6 lg:px-8 h-16">
        <div className="flex items-center space-x-3">
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-xl text-forest-600 dark:text-forest-400 hover:bg-forest-100 dark:hover:bg-forest-900 lg:hidden focus:outline-none"
            aria-label="Toggle Navigation"
          >
            <Menu className="w-5 h-5" />
          </button>

          <Link to="/" className="flex items-center space-x-2.5 group">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-emerald-600 to-forest-800 dark:from-emerald-500 dark:to-forest-900 flex items-center justify-center text-white shadow-sm shadow-emerald-900/20 border border-gold-400/30">
              <Sparkles className="w-5 h-5 text-gold-300" />
            </div>
            <div>
              <span className="font-bold font-serif tracking-tight text-base sm:text-lg">
                EduPredict <span className="text-xs px-1.5 py-0.5 rounded font-sans font-semibold bg-gold-500/15 text-gold-600 dark:text-gold-400 border border-gold-500/30">AI</span>
              </span>
              <span className="hidden sm:inline-block ml-2 text-[11px] font-medium text-forest-600 dark:text-forest-400">
                Difficulty Engine
              </span>
            </div>
          </Link>
        </div>

        <div className="flex items-center space-x-3.5">
          {/* Global Theme Toggle */}
          <ThemeToggle size="sm" />

          {user && (
            <div className="flex items-center space-x-3.5 pl-2 border-l border-forest-200 dark:border-forest-800">
              <div className={`hidden sm:flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badge.style}`}>
                <BadgeIcon className="w-3.5 h-3.5" />
                <span>{badge.label}</span>
              </div>

              <div className="hidden md:block text-right">
                <p className="text-xs font-bold leading-tight">{user.full_name}</p>
                <p className="text-[11px] text-forest-500 dark:text-forest-400">{user.email}</p>
              </div>

              <div className="h-9 w-9 rounded-xl bg-forest-100 dark:bg-forest-900 border border-forest-300 dark:border-forest-700 flex items-center justify-center font-bold text-xs text-forest-800 dark:text-forest-200 shadow-xs">
                {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
              </div>

              <button
                onClick={logout}
                title="Log out"
                className="p-2 rounded-xl text-forest-600 dark:text-forest-400 hover:text-rose-600 hover:bg-rose-500/10 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
