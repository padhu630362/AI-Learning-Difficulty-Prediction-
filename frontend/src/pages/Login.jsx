import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import ThemeToggle from '../components/ThemeToggle';
import axiosClient from '../api/axiosClient';
import {
  Sparkles,
  AlertCircle,
  ArrowRight,
  Eye,
  EyeOff,
  CheckCircle2,
  Lock,
  Mail,
  UserCheck,
  BookOpenCheck,
  ShieldCheck,
  ArrowLeft,
  X
} from 'lucide-react';

const Login = () => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Forgot Password Modal State
  const [forgotModalOpen, setForgotModalOpen] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotSuccess, setForgotSuccess] = useState('');
  const [forgotError, setForgotError] = useState('');

  const { login } = useAuth();
  const { isDark } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const isExpired = new URLSearchParams(location.search).get('expired') === 'true';

  // Load remembered identifier if previously saved
  useEffect(() => {
    try {
      const savedId = localStorage.getItem('remembered_identifier');
      if (savedId) {
        setIdentifier(savedId);
        setRememberMe(true);
      }
    } catch {
      // Storage unavailable
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!identifier.trim() || !password) {
      setError('Please provide both username/email and password.');
      return;
    }
    setError('');
    setLoading(true);

    try {
      const user = await login(identifier.trim(), password);

      // Save or clear remember me preference
      if (rememberMe) {
        localStorage.setItem('remembered_identifier', identifier.trim());
      } else {
        localStorage.removeItem('remembered_identifier');
      }

      // Role-based redirection
      if (user.role === 'admin') {
        navigate('/admin/dashboard');
      } else if (user.role === 'instructor') {
        navigate('/instructor/dashboard');
      } else {
        navigate('/student/dashboard');
      }
    } catch (err) {
      const errMsg = err.response?.data?.error || 'Invalid credentials. Please verify your login details.';
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPasswordSubmit = async (e) => {
    e.preventDefault();
    if (!forgotEmail.trim()) {
      setForgotError('Please enter your registered email address or username.');
      return;
    }
    setForgotLoading(true);
    setForgotError('');
    setForgotSuccess('');

    try {
      const res = await axiosClient.post('/auth/forgot-password', {
        identifier: forgotEmail.trim()
      });
      setForgotSuccess(res.data.message || 'Recovery instructions processed successfully.');
      setTimeout(() => {
        setForgotModalOpen(false);
        setForgotSuccess('');
        setForgotEmail('');
      }, 3000);
    } catch (err) {
      setForgotError(err.response?.data?.error || 'Unable to process recovery request. Please try again.');
    } finally {
      setForgotLoading(false);
    }
  };

  const handleQuickLogin = (role) => {
    if (role === 'student') {
      setIdentifier('student_alex');
      setPassword('StudentPass123!');
    } else if (role === 'instructor') {
      setIdentifier('dr_smith');
      setPassword('InstructorPass123!');
    } else if (role === 'admin') {
      setIdentifier('admin');
      setPassword('AdminPass123!');
    }
    setError('');
  };

  return (
    <div className={`min-h-screen flex flex-col justify-center transition-colors duration-300 ${
      isDark ? 'bg-forest-980 text-forest-100' : 'bg-ivory-50 text-forest-950'
    }`}>
      {/* Top Header Controls */}
      <header className="absolute top-0 left-0 right-0 p-4 sm:p-6 flex items-center justify-between max-w-7xl mx-auto w-full">
        <Link
          to="/"
          className="inline-flex items-center text-xs font-semibold text-forest-600 dark:text-forest-400 hover:text-gold-600 dark:hover:text-gold-300 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-1.5" />
          <span>Back to Home</span>
        </Link>
        <ThemeToggle />
      </header>

      <main className="w-full max-w-md mx-auto px-4 sm:px-6 py-12">
        {/* Brand Crest */}
        <div className="text-center mb-8">
          <div className="inline-flex w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-600 to-forest-800 dark:from-emerald-500 dark:to-forest-900 items-center justify-center text-white shadow-lg shadow-emerald-900/20 mb-4 border border-gold-400/30">
            <Sparkles className="w-7 h-7 text-gold-300" />
          </div>
          <h1 className="text-3xl font-extrabold font-serif tracking-tight">
            Sign In to EduPredict
          </h1>
          <p className="mt-2 text-xs sm:text-sm text-forest-600 dark:text-forest-400 font-sans">
            Access your calibrated learning analytics and risk forecasts
          </p>
        </div>

        {/* Login Card */}
        <div className={`p-7 sm:p-8 rounded-3xl border shadow-xl transition-all duration-300 ${
          isDark
            ? 'bg-forest-950/90 border-forest-800 shadow-forest-950/80'
            : 'bg-white border-forest-200/80 shadow-card-morning'
        }`}>
          {isExpired && (
            <div className="mb-5 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-800 dark:text-amber-300 text-xs flex items-center space-x-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 text-amber-600 dark:text-amber-400" />
              <span>Your session has expired. Please sign in again.</span>
            </div>
          )}

          {error && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-800 dark:text-rose-300 text-xs flex items-center space-x-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600 dark:text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-forest-700 dark:text-forest-300 mb-1.5 font-sans">
                Username or Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-forest-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="e.g. student_alex or alex@university.edu"
                  required
                  autoComplete="username"
                  className={`w-full pl-10 pr-3.5 py-2.5 rounded-xl border text-sm transition-all focus:outline-none focus:ring-2 focus:ring-gold-500/40 ${
                    isDark
                      ? 'bg-forest-900/60 border-forest-800 text-forest-100 placeholder-forest-500 focus:border-gold-500/60'
                      : 'bg-forest-50/40 border-forest-200 text-forest-900 placeholder-forest-400 focus:border-emerald-600'
                  }`}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-bold uppercase tracking-wider text-forest-700 dark:text-forest-300 font-sans">
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => {
                    setForgotError('');
                    setForgotSuccess('');
                    setForgotModalOpen(true);
                  }}
                  className="text-xs font-medium text-gold-600 dark:text-gold-400 hover:underline focus:outline-none"
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-forest-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  autoComplete="current-password"
                  className={`w-full pl-10 pr-10 py-2.5 rounded-xl border text-sm transition-all focus:outline-none focus:ring-2 focus:ring-gold-500/40 ${
                    isDark
                      ? 'bg-forest-900/60 border-forest-800 text-forest-100 placeholder-forest-500 focus:border-gold-500/60'
                      : 'bg-forest-50/40 border-forest-200 text-forest-900 placeholder-forest-400 focus:border-emerald-600'
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-forest-400 hover:text-forest-600 dark:hover:text-forest-200 transition-colors"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between pt-1">
              <label className="inline-flex items-center space-x-2 text-xs text-forest-600 dark:text-forest-400 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-forest-300 dark:border-forest-700 text-emerald-600 focus:ring-gold-500/40 w-4 h-4"
                />
                <span>Remember identifier</span>
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-3 flex justify-center items-center py-3 px-4 rounded-xl text-sm font-bold text-forest-950 bg-gradient-to-r from-gold-400 via-gold-300 to-gold-400 hover:from-gold-300 hover:to-gold-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gold-500 shadow-md shadow-gold-500/20 disabled:opacity-60 transition-all duration-200 cursor-pointer"
            >
              {loading ? (
                <span className="inline-flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-forest-950" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Authenticating...
                </span>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4 ml-1.5" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Logins with Emerald/Gold Styling */}
          <div className="mt-7 pt-6 border-t border-forest-200/80 dark:border-forest-800/80">
            <p className="text-[11px] font-bold uppercase tracking-wider text-forest-500 text-center mb-3">
              One-Click Demo Profiles
            </p>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin('student')}
                className="flex flex-col items-center justify-center p-2 rounded-xl border border-emerald-500/20 bg-emerald-500/5 hover:bg-emerald-500/10 transition-colors text-center group cursor-pointer"
              >
                <UserCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400 mb-1 group-hover:scale-110 transition-transform" />
                <span className="text-[11px] font-semibold text-emerald-800 dark:text-emerald-300">Student</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('instructor')}
                className="flex flex-col items-center justify-center p-2 rounded-xl border border-gold-500/25 bg-gold-500/5 hover:bg-gold-500/15 transition-colors text-center group cursor-pointer"
              >
                <BookOpenCheck className="w-4 h-4 text-gold-600 dark:text-gold-400 mb-1 group-hover:scale-110 transition-transform" />
                <span className="text-[11px] font-semibold text-gold-800 dark:text-gold-300">Instructor</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('admin')}
                className="flex flex-col items-center justify-center p-2 rounded-xl border border-forest-400/30 bg-forest-500/5 hover:bg-forest-500/15 transition-colors text-center group cursor-pointer"
              >
                <ShieldCheck className="w-4 h-4 text-forest-700 dark:text-forest-300 mb-1 group-hover:scale-110 transition-transform" />
                <span className="text-[11px] font-semibold text-forest-800 dark:text-forest-200">Admin</span>
              </button>
            </div>
          </div>

          {/* Registration Link */}
          <div className="mt-6 text-center text-xs text-forest-600 dark:text-forest-400">
            Don't have an account yet?{' '}
            <Link to="/register" className="font-bold text-gold-600 dark:text-gold-400 hover:underline">
              Create an account
            </Link>
          </div>
        </div>
      </main>

      {/* ------------------------------------------------------------------- */}
      {/* FORGOT PASSWORD MODAL (Connected to actual backend API)             */}
      {/* ------------------------------------------------------------------- */}
      {forgotModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-forest-980/70 backdrop-blur-xs">
          <div className={`w-full max-w-md p-6 rounded-3xl border shadow-2xl transition-all ${
            isDark ? 'bg-forest-950 border-forest-800 text-forest-100' : 'bg-white border-forest-200 text-forest-900'
          }`}>
            <div className="flex items-center justify-between pb-4 border-b border-forest-200/60 dark:border-forest-800">
              <h2 className="text-base font-bold font-serif">Account Recovery</h2>
              <button
                type="button"
                onClick={() => setForgotModalOpen(false)}
                className="p-1 rounded-lg text-forest-400 hover:text-forest-700 dark:hover:text-forest-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="mt-3 text-xs text-forest-600 dark:text-forest-400">
              Enter your registered username or institutional email address to request password recovery guidance.
            </p>

            {forgotSuccess && (
              <div className="mt-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-800 dark:text-emerald-300 text-xs flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
                <span>{forgotSuccess}</span>
              </div>
            )}

            {forgotError && (
              <div className="mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-800 dark:text-rose-300 text-xs flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-600 dark:text-rose-400" />
                <span>{forgotError}</span>
              </div>
            )}

            <form onSubmit={handleForgotPasswordSubmit} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider mb-1">
                  Email or Username
                </label>
                <input
                  type="text"
                  value={forgotEmail}
                  onChange={(e) => setForgotEmail(e.target.value)}
                  placeholder="e.g. alex@university.edu"
                  required
                  className={`w-full px-3.5 py-2.5 rounded-xl border text-sm transition-all focus:outline-none focus:ring-2 focus:ring-gold-500/40 ${
                    isDark
                      ? 'bg-forest-900/60 border-forest-800 text-forest-100 placeholder-forest-500'
                      : 'bg-forest-50/40 border-forest-200 text-forest-900 placeholder-forest-400'
                  }`}
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setForgotModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold border border-forest-300 dark:border-forest-700 hover:bg-forest-100 dark:hover:bg-forest-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={forgotLoading}
                  className="px-5 py-2 rounded-xl text-xs font-bold text-forest-950 bg-gold-400 hover:bg-gold-300 shadow-xs disabled:opacity-50"
                >
                  {forgotLoading ? 'Processing...' : 'Send Recovery Instructions'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;
