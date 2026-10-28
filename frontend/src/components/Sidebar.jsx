import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import {
  LayoutDashboard,
  BookOpen,
  LineChart,
  Lightbulb,
  TrendingUp,
  ClipboardCheck,
  AlertTriangle,
  Users,
  Database,
  Cpu,
  Sparkles,
  X
} from 'lucide-react';

const Sidebar = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const { isDark } = useTheme();
  if (!user) return null;

  const role = user.role;

  const studentLinks = [
    { to: '/student/dashboard', label: 'My Dashboard', icon: LayoutDashboard },
    { to: '/student/subjects', label: 'Subjects & Topics', icon: BookOpen },
    { to: '/student/analysis', label: 'Difficulty Analysis', icon: LineChart },
    { to: '/student/recommendations', label: 'Study Recommendations', icon: Lightbulb },
    { to: '/student/progress', label: 'Progress Tracking', icon: TrendingUp },
  ];

  const instructorLinks = [
    { to: '/instructor/dashboard', label: 'Instructor Overview', icon: LayoutDashboard },
    { to: '/instructor/subjects', label: 'Subjects & Topics', icon: BookOpen },
    { to: '/instructor/assessments', label: 'Assessments & Scores', icon: ClipboardCheck },
    { to: '/instructor/alerts', label: 'Early Support Alerts', icon: AlertTriangle },
  ];

  const adminLinks = [
    { to: '/admin/dashboard', label: 'Admin Overview', icon: LayoutDashboard },
    { to: '/admin/users', label: 'User Directory', icon: Users },
    { to: '/admin/datasets', label: 'Dataset Management', icon: Database },
    { to: '/admin/models', label: 'Model Evaluation & ML', icon: Cpu },
  ];

  const links = role === 'admin' ? adminLinks : role === 'instructor' ? instructorLinks : studentLinks;

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-forest-980/60 backdrop-blur-xs lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 flex flex-col transition-all duration-300 ease-in-out lg:translate-x-0 border-r ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } ${
          isDark
            ? 'bg-forest-950 text-forest-200 border-forest-800'
            : 'bg-white text-forest-800 border-forest-200 shadow-sm'
        }`}
      >
        {/* Brand header */}
        <div className={`flex items-center justify-between h-16 px-6 border-b ${
          isDark ? 'border-forest-800' : 'border-forest-200'
        }`}>
          <div className="flex items-center space-x-2.5">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-emerald-600 to-forest-800 flex items-center justify-center text-white border border-gold-400/30">
              <Sparkles className="w-4 h-4 text-gold-300" />
            </div>
            <span className="font-bold font-serif tracking-tight text-forest-950 dark:text-white">
              EduPredict Hub
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-forest-400 hover:text-forest-700 dark:hover:text-white lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation list */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-1">
          <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-forest-500 dark:text-forest-400 font-sans">
            Navigation Menu
          </div>
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? isDark
                        ? 'bg-forest-900 text-gold-300 border border-gold-500/30 shadow-xs'
                        : 'bg-emerald-50 text-emerald-900 border border-emerald-300/80 font-semibold shadow-xs'
                      : isDark
                      ? 'text-forest-300 hover:bg-forest-900/60 hover:text-white'
                      : 'text-forest-700 hover:bg-forest-50 hover:text-forest-950'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{link.label}</span>
              </NavLink>
            );
          })}
        </div>

        {/* User preview footer in sidebar */}
        <div className={`p-4 border-t ${isDark ? 'border-forest-800' : 'border-forest-200'}`}>
          <div className={`rounded-2xl p-3 flex items-center space-x-3 border ${
            isDark
              ? 'bg-forest-900/50 border-forest-800'
              : 'bg-forest-50/60 border-forest-200'
          }`}>
            <div className="h-9 w-9 rounded-xl bg-forest-200 dark:bg-forest-800 flex items-center justify-center text-forest-900 dark:text-white font-bold text-sm border border-forest-300 dark:border-forest-700">
              {user.username.charAt(0).toUpperCase()}
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-bold truncate text-forest-900 dark:text-white">{user.full_name}</p>
              <p className="text-[11px] text-forest-500 dark:text-forest-400 capitalize">{user.role} Account</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
