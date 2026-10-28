import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import ThemeToggle from '../components/ThemeToggle';
import {
  Sparkles,
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Lock,
  Mail,
  User,
  Eye,
  EyeOff,
  ArrowLeft,
  Shield,
  GraduationCap,
  BookOpen
} from 'lucide-react';

const Register = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    username: '',
    email: '',
    password: '',
    confirm_password: '',
    role: 'student',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [termsAccepted, setTermsAccepted] = useState(false);

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const { isDark } = useTheme();
  const navigate = useNavigate();

  // Evaluate password strength dynamically
  const calculatePasswordStrength = (pass) => {
    if (!pass) return { score: 0, label: 'None', color: 'bg-forest-200 dark:bg-forest-800' };
    let score = 0;
    if (pass.length >= 6) score += 1;
    if (pass.length >= 10) score += 1;
    if (/[0-9]/.test(pass)) score += 1;
    if (/[^A-Za-z0-9]/.test(pass)) score += 1;

    if (score <= 1) return { score: 1, label: 'Weak', color: 'bg-rose-500' };
    if (score === 2) return { score: 2, label: 'Fair', color: 'bg-amber-500' };
    if (score === 3) return { score: 3, label: 'Good', color: 'bg-emerald-500' };
    return { score: 4, label: 'Strong', color: 'bg-gold-500' };
  };

  const strength = calculatePasswordStrength(formData.password);
  const passwordsMatch = formData.password && formData.confirm_password && formData.password === formData.confirm_password;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.full_name.trim() || !formData.username.trim() || !formData.email.trim() || !formData.password) {
      setError('Please fill in all required fields.');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must contain at least 6 characters.');
      return;
    }

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match. Please verify both entries.');
      return;
    }

    if (!termsAccepted) {
      setError('Please accept the Terms of Service & Privacy Policy.');
      return;
    }

    // Security: Only student and instructor roles are permitted for public self-registration
    if (formData.role !== 'student' && formData.role !== 'instructor') {
      setError("Invalid registration role. Only 'Student' or 'Instructor' accounts can be self-registered.");
      return;
    }

    setLoading(true);

    try {
      const payload = {
        full_name: formData.full_name.trim(),
        username: formData.username.trim(),
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
        role: formData.role
      };

      await register(payload);
      setSuccess('Registration successful! Your account is ready. Redirecting to sign in...');
      setTimeout(() => {
        navigate('/login');
      }, 1800);
    } catch (err) {
      const errMsg = err.response?.data?.error || 'Registration failed. Please check your information.';
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`min-h-screen flex flex-col justify-center transition-colors duration-300 ${
      isDark ? 'bg-forest-980 text-forest-100' : 'bg-ivory-50 text-forest-950'
    }`}>
      {/* Header Bar */}
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

      <main className="w-full max-w-xl mx-auto px-4 sm:px-6 py-12">
        {/* Brand Crest */}
        <div className="text-center mb-7">
          <div className="inline-flex w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-600 to-forest-800 dark:from-emerald-500 dark:to-forest-900 items-center justify-center text-white shadow-lg shadow-emerald-900/20 mb-3.5 border border-gold-400/30">
            <Sparkles className="w-7 h-7 text-gold-300" />
          </div>
          <h1 className="text-3xl font-extrabold font-serif tracking-tight">
            Create an Account
          </h1>
          <p className="mt-2 text-xs sm:text-sm text-forest-600 dark:text-forest-400 font-sans">
            Join the educational telemetry and difficulty prediction platform
          </p>
        </div>

        {/* Registration Card */}
        <div className={`p-7 sm:p-9 rounded-3xl border shadow-xl transition-all duration-300 ${
          isDark
            ? 'bg-forest-950/90 border-forest-800 shadow-forest-950/80'
            : 'bg-white border-forest-200/80 shadow-card-morning'
        }`}>
          {error && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-800 dark:text-rose-300 text-xs flex items-center space-x-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600 dark:text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="mb-5 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-800 dark:text-emerald-300 text-xs flex items-center space-x-2.5">
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
              <span>{success}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name & Username in 2 columns */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-forest-700 dark:text-forest-300 mb-1.5 font-sans">
                  Full Name
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-forest-400">
                    <User className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    placeholder="e.g. Eleanor Vance"
                    required
                    className={`w-full pl-9 pr-3 py-2.5 rounded-xl border text-sm transition-all focus:outline-none focus:ring-2 focus:ring-gold-500/40 ${
                      isDark
                        ? 'bg-forest-900/60 border-forest-800 text-forest-100 placeholder-forest-500 focus:border-gold-500/60'
                        : 'bg-forest-50/40 border-forest-200 text-forest-900 placeholder-forest-400 focus:border-emerald-600'
                    }`}
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-forest-700 dark:text-forest-300 mb-1.5 font-sans">
                  Username
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="e.g. eleanor_v"
                  required
                  className={`w-full px-3 py-2.5 rounded-xl border text-sm transition-all focus:outline-none focus:ring-2 focus:ring-gold-500/40 ${
                    isDark
                      ? 'bg-forest-900/60 border-forest-800 text-forest-100 placeholder-forest-500 focus:border-gold-500/60'
                      : 'bg-forest-50/40 border-forest-200 text-forest-900 placeholder-forest-400 focus:border-emerald-600'
                  }`}
                />
              </div>
            </div>

            {/* Email Address */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-forest-700 dark:text-forest-300 mb-1.5 font-sans">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-forest-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="eleanor@university.edu"
                  required
                  className={`w-full pl-9 pr-3 py-2.5 rounded-xl border text-sm transition-all focus:outline-none focus:ring-2 focus:ring-gold-500/40 ${
                    isDark
                      ? 'bg-forest-900/60 border-forest-800 text-forest-100 placeholder-forest-500 focus:border-gold-500/60'
                      : 'bg-forest-50/40 border-forest-200 text-forest-900 placeholder-forest-400 focus:border-emerald-600'
                  }`}
                />
              </div>
            </div>

            {/* Role Selection (Student or Instructor ONLY; Admin forbidden) */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-forest-700 dark:text-forest-300 mb-1.5 font-sans">
                Academic Role
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setFormData({ ...formData, role: 'student' })}
                  className={`flex items-center justify-center p-3 rounded-xl border text-sm font-semibold transition-all cursor-pointer ${
                    formData.role === 'student'
                      ? 'border-emerald-600 bg-emerald-500/15 text-emerald-800 dark:text-emerald-300 shadow-xs ring-1 ring-emerald-500'
                      : isDark
                      ? 'border-forest-800 bg-forest-900/40 text-forest-300 hover:border-forest-700'
                      : 'border-forest-200 bg-forest-50/40 text-forest-700 hover:border-forest-300'
                  }`}
                >
                  <GraduationCap className="w-4 h-4 mr-2 text-emerald-600 dark:text-emerald-400" />
                  <span>Student</span>
                </button>

                <button
                  type="button"
                  onClick={() => setFormData({ ...formData, role: 'instructor' })}
                  className={`flex items-center justify-center p-3 rounded-xl border text-sm font-semibold transition-all cursor-pointer ${
                    formData.role === 'instructor'
                      ? 'border-gold-500 bg-gold-500/15 text-gold-800 dark:text-gold-300 shadow-xs ring-1 ring-gold-500'
                      : isDark
                      ? 'border-forest-800 bg-forest-900/40 text-forest-300 hover:border-forest-700'
                      : 'border-forest-200 bg-forest-50/40 text-forest-700 hover:border-forest-300'
                  }`}
                >
                  <BookOpen className="w-4 h-4 mr-2 text-gold-600 dark:text-gold-400" />
                  <span>Instructor</span>
                </button>
              </div>
              <p className="mt-1.5 text-[11px] text-forest-500 dark:text-forest-400">
                Institutional administrator accounts require authorized provisioning and cannot be self-registered.
              </p>
            </div>

            {/* Password & Confirm Password in 2 columns */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-forest-700 dark:text-forest-300 mb-1.5 font-sans">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-forest-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Min 6 characters"
                    minLength={6}
                    required
                    className={`w-full pl-9 pr-9 py-2.5 rounded-xl border text-sm transition-all focus:outline-none focus:ring-2 focus:ring-gold-500/40 ${
                      isDark
                        ? 'bg-forest-900/60 border-forest-800 text-forest-100 placeholder-forest-500 focus:border-gold-500/60'
                        : 'bg-forest-50/40 border-forest-200 text-forest-900 placeholder-forest-400 focus:border-emerald-600'
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-forest-400 hover:text-forest-600 dark:hover:text-forest-200"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-forest-700 dark:text-forest-300 mb-1.5 font-sans">
                  Confirm Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-forest-400">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    name="confirm_password"
                    value={formData.confirm_password}
                    onChange={handleChange}
                    placeholder="Re-enter password"
                    minLength={6}
                    required
                    className={`w-full pl-9 pr-9 py-2.5 rounded-xl border text-sm transition-all focus:outline-none focus:ring-2 focus:ring-gold-500/40 ${
                      isDark
                        ? 'bg-forest-900/60 border-forest-800 text-forest-100 placeholder-forest-500 focus:border-gold-500/60'
                        : 'bg-forest-50/40 border-forest-200 text-forest-900 placeholder-forest-400 focus:border-emerald-600'
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-forest-400 hover:text-forest-600 dark:hover:text-forest-200"
                    aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>

            {/* Dynamic Password Strength Indicator */}
            {formData.password && (
              <div className="pt-1">
                <div className="flex items-center justify-between text-[11px] mb-1">
                  <span className="text-forest-500">Password Strength:</span>
                  <span className="font-semibold text-forest-700 dark:text-forest-300">{strength.label}</span>
                </div>
                <div className="grid grid-cols-4 gap-1.5 h-1.5">
                  <div className={`rounded-full ${strength.score >= 1 ? strength.color : 'bg-forest-200 dark:bg-forest-800'}`} />
                  <div className={`rounded-full ${strength.score >= 2 ? strength.color : 'bg-forest-200 dark:bg-forest-800'}`} />
                  <div className={`rounded-full ${strength.score >= 3 ? strength.color : 'bg-forest-200 dark:bg-forest-800'}`} />
                  <div className={`rounded-full ${strength.score >= 4 ? strength.color : 'bg-forest-200 dark:bg-forest-800'}`} />
                </div>
              </div>
            )}

            {/* Password match indicator */}
            {formData.confirm_password && (
              <p className={`text-[11px] flex items-center gap-1.5 ${passwordsMatch ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                {passwordsMatch ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Passwords match perfectly.</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-3.5 h-3.5" />
                    <span>Passwords do not match yet.</span>
                  </>
                )}
              </p>
            )}

            {/* Terms & Conditions Acceptance */}
            <div className="pt-2">
              <label className="inline-flex items-start space-x-2 text-xs text-forest-600 dark:text-forest-400 cursor-pointer">
                <input
                  type="checkbox"
                  checked={termsAccepted}
                  onChange={(e) => setTermsAccepted(e.target.checked)}
                  required
                  className="rounded border-forest-300 dark:border-forest-700 text-emerald-600 focus:ring-gold-500/40 w-4 h-4 mt-0.5"
                />
                <span>
                  I agree to the <strong>Terms of Service</strong> and acknowledge the <strong>Privacy Policy</strong> regarding institutional learning telemetry.
                </span>
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || (formData.confirm_password && !passwordsMatch)}
              className="w-full mt-4 flex justify-center items-center py-3 px-4 rounded-xl text-sm font-bold text-forest-950 bg-gradient-to-r from-gold-400 via-gold-300 to-gold-400 hover:from-gold-300 hover:to-gold-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gold-500 shadow-md shadow-gold-500/20 disabled:opacity-50 transition-all duration-200 cursor-pointer"
            >
              {loading ? (
                <span className="inline-flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-forest-950" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Creating Account...
                </span>
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight className="w-4 h-4 ml-1.5" />
                </>
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center text-xs text-forest-600 dark:text-forest-400">
            Already have an account?{' '}
            <Link to="/login" className="font-bold text-gold-600 dark:text-gold-400 hover:underline">
              Sign in to platform
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Register;
