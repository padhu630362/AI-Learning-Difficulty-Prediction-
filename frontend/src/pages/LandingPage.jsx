import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import ThemeToggle from '../components/ThemeToggle';
import {
  Sparkles,
  ArrowRight,
  Brain,
  ShieldCheck,
  TrendingUp,
  Target,
  BookOpen,
  CheckCircle2,
  Users,
  Compass,
  AlertTriangle,
  Award,
  ChevronRight,
  Menu,
  X,
  GraduationCap,
  Layers,
  BarChart3,
  Sliders,
  HelpCircle,
  FileCheck
} from 'lucide-react';

const LandingPage = () => {
  const { isAuthenticated, user } = useAuth();
  const { isDark } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Interactive Hero Preview Simulator State
  const [simQuiz, setSimQuiz] = useState(48);
  const [simAttempts, setSimAttempts] = useState(3);
  const [simErrors, setSimErrors] = useState(5);

  // Compute live simulated struggle severity
  const simMastery = simQuiz * 0.7 + (100 - simErrors * 5) * 0.3;
  const simScore = Math.min(100, Math.max(0, (100 - simMastery) * 0.7 + simErrors * 3.5 + (simAttempts - 1) * 4));
  const simTier = simScore < 28 ? 'Low' : simScore < 50 ? 'Moderate' : 'High';

  const tierColors = {
    Low: 'text-emerald-700 bg-emerald-100/90 dark:text-emerald-300 dark:bg-emerald-950/80 border-emerald-300 dark:border-emerald-800',
    Moderate: 'text-amber-800 bg-amber-100/90 dark:text-amber-300 dark:bg-amber-950/80 border-amber-300 dark:border-amber-800',
    High: 'text-rose-800 bg-rose-100/90 dark:text-rose-300 dark:bg-rose-950/80 border-rose-300 dark:border-rose-800',
  };

  const getDashboardLink = () => {
    if (!user) return '/login';
    if (user.role === 'admin') return '/admin/dashboard';
    if (user.role === 'instructor') return '/instructor/dashboard';
    return '/student/dashboard';
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'bg-forest-980 text-forest-100' : 'bg-ivory-50 text-forest-950'}`}>
      {/* ------------------------------------------------------------------- */}
      {/* TOP NAVIGATION BAR                                                  */}
      {/* ------------------------------------------------------------------- */}
      <nav className={`sticky top-0 z-50 backdrop-blur-md border-b transition-colors duration-300 ${
        isDark ? 'bg-forest-950/85 border-forest-800/80' : 'bg-ivory-50/90 border-forest-200/60'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-emerald-600 to-forest-800 dark:from-emerald-500 dark:to-forest-900 flex items-center justify-center text-white shadow-md shadow-emerald-900/20 group-hover:scale-105 transition-transform duration-300 border border-gold-500/30">
                <Sparkles className="w-5 h-5 text-gold-300" />
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-bold font-serif tracking-tight flex items-center gap-1.5">
                  EduPredict <span className="text-xs px-2 py-0.5 rounded-full font-sans font-semibold bg-gold-500/15 text-gold-600 dark:text-gold-400 border border-gold-500/30">AI</span>
                </span>
                <span className="text-[11px] font-medium tracking-wide text-forest-600 dark:text-forest-400">
                  Learning Difficulty Intelligence
                </span>
              </div>
            </Link>

            {/* Desktop Navigation Links */}
            <div className="hidden md:flex items-center space-x-8 text-sm font-medium">
              <a href="#how-it-works" className="hover:text-gold-600 dark:hover:text-gold-400 transition-colors">
                How It Works
              </a>
              <a href="#features" className="hover:text-gold-600 dark:hover:text-gold-400 transition-colors">
                Features
              </a>
              <a href="#simulator" className="hover:text-gold-600 dark:hover:text-gold-400 transition-colors">
                Live Simulator
              </a>
              <a href="#about" className="hover:text-gold-600 dark:hover:text-gold-400 transition-colors">
                Benefits
              </a>
            </div>

            {/* Action Buttons & Theme Toggle */}
            <div className="hidden md:flex items-center space-x-3.5">
              <ThemeToggle />

              {isAuthenticated ? (
                <Link
                  to={getDashboardLink()}
                  className="inline-flex items-center px-4 py-2 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-emerald-700 to-forest-800 hover:from-emerald-600 hover:to-forest-700 shadow-sm border border-gold-500/30 transition-all duration-200"
                >
                  <span>Go to Dashboard</span>
                  <ArrowRight className="w-4 h-4 ml-1.5" />
                </Link>
              ) : (
                <>
                  <Link
                    to="/login"
                    className={`px-4 py-2 rounded-xl text-sm font-semibold transition-colors ${
                      isDark
                        ? 'text-forest-200 hover:text-white hover:bg-forest-900/60'
                        : 'text-forest-800 hover:text-forest-950 hover:bg-forest-100/70'
                    }`}
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/register"
                    className="inline-flex items-center px-4 py-2 rounded-xl text-sm font-semibold text-forest-950 bg-gradient-to-r from-gold-400 via-gold-300 to-gold-400 hover:from-gold-300 hover:to-gold-200 shadow-xs shadow-gold-500/20 transition-all duration-200"
                  >
                    <span>Get Started</span>
                    <ArrowRight className="w-4 h-4 ml-1 text-forest-950" />
                  </Link>
                </>
              )}
            </div>

            {/* Mobile Hamburger Toggle */}
            <div className="flex md:hidden items-center space-x-2">
              <ThemeToggle size="sm" />
              <button
                type="button"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-xl border border-forest-200 dark:border-forest-800 text-forest-700 dark:text-forest-300 hover:bg-forest-100 dark:hover:bg-forest-900"
                aria-label="Toggle Navigation Menu"
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Dropdown */}
        {mobileMenuOpen && (
          <div className={`md:hidden px-4 pt-3 pb-6 border-t ${isDark ? 'bg-forest-950 border-forest-800' : 'bg-ivory-50 border-forest-200'}`}>
            <div className="flex flex-col space-y-3 text-sm font-medium">
              <a
                href="#how-it-works"
                onClick={() => setMobileMenuOpen(false)}
                className="py-2 px-3 rounded-lg hover:bg-forest-100 dark:hover:bg-forest-900"
              >
                How It Works
              </a>
              <a
                href="#features"
                onClick={() => setMobileMenuOpen(false)}
                className="py-2 px-3 rounded-lg hover:bg-forest-100 dark:hover:bg-forest-900"
              >
                Features
              </a>
              <a
                href="#simulator"
                onClick={() => setMobileMenuOpen(false)}
                className="py-2 px-3 rounded-lg hover:bg-forest-100 dark:hover:bg-forest-900"
              >
                Live Simulator
              </a>
              <a
                href="#about"
                onClick={() => setMobileMenuOpen(false)}
                className="py-2 px-3 rounded-lg hover:bg-forest-100 dark:hover:bg-forest-900"
              >
                Benefits
              </a>
              <div className="pt-3 border-t border-forest-200 dark:border-forest-800 flex flex-col space-y-2">
                {isAuthenticated ? (
                  <Link
                    to={getDashboardLink()}
                    className="w-full text-center py-2.5 px-4 rounded-xl text-sm font-semibold text-white bg-forest-800 dark:bg-forest-700"
                  >
                    Go to Dashboard
                  </Link>
                ) : (
                  <>
                    <Link
                      to="/login"
                      className="w-full text-center py-2.5 px-4 rounded-xl text-sm font-semibold border border-forest-300 dark:border-forest-700"
                    >
                      Sign In
                    </Link>
                    <Link
                      to="/register"
                      className="w-full text-center py-2.5 px-4 rounded-xl text-sm font-semibold text-forest-950 bg-gold-400 hover:bg-gold-300"
                    >
                      Get Started
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* ------------------------------------------------------------------- */}
      {/* HERO SECTION                                                        */}
      {/* ------------------------------------------------------------------- */}
      <section className="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28">
        {/* Subtle Decorative Background Rings */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-gradient-to-tr from-emerald-500/10 to-gold-400/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
            {/* Left Column: Hero Narrative */}
            <div className="lg:col-span-7 text-center lg:text-left">
              <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-emerald-100/80 dark:bg-forest-900/90 text-emerald-800 dark:text-emerald-300 border border-emerald-300/80 dark:border-forest-700 mb-6 shadow-xs">
                <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span>Calibrated Pedagogical Intelligence & Telemetry</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold font-serif tracking-tight leading-[1.12]">
                Predict Learning Difficulties{' '}
                <span className="gold-shimmer">Before Midterm Exams</span>
              </h1>

              <p className="mt-6 text-base sm:text-lg text-forest-700 dark:text-forest-300 max-w-2xl mx-auto lg:mx-0 leading-relaxed font-sans">
                Transform formative LMS quizzes, assignment paces, and repeated error telemetry into explainable difficulty risk forecasts and personalized remediation pathways.
              </p>

              {/* Primary Call to Action buttons */}
              <div className="mt-8 flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
                <Link
                  to={isAuthenticated ? getDashboardLink() : "/register"}
                  className="w-full sm:w-auto inline-flex items-center justify-center px-7 py-3.5 rounded-2xl text-base font-bold text-forest-950 bg-gradient-to-r from-gold-400 via-gold-300 to-gold-400 hover:from-gold-300 hover:to-gold-200 shadow-md shadow-gold-500/25 border border-gold-300/40 transition-all duration-300 hover:-translate-y-0.5"
                >
                  <span>Get Started Free</span>
                  <ArrowRight className="w-5 h-5 ml-2 text-forest-950" />
                </Link>

                <a
                  href="#how-it-works"
                  className={`w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 rounded-2xl text-base font-semibold border transition-all duration-300 hover:-translate-y-0.5 ${
                    isDark
                      ? 'border-forest-700 text-forest-200 bg-forest-900/60 hover:bg-forest-800 hover:text-white'
                      : 'border-forest-300 text-forest-800 bg-white hover:bg-forest-50 hover:text-forest-950 shadow-xs'
                  }`}
                >
                  <span>Explore Features</span>
                  <ChevronRight className="w-4 h-4 ml-1" />
                </a>
              </div>

              {/* Key Trust Signals */}
              <div className="mt-10 pt-8 border-t border-forest-200/80 dark:border-forest-800/80 grid grid-cols-3 gap-4 text-left">
                <div>
                  <div className="text-2xl font-bold font-serif text-emerald-700 dark:text-emerald-400">96.17%</div>
                  <div className="text-xs text-forest-600 dark:text-forest-400 font-medium mt-0.5">Benchmark Accuracy</div>
                </div>
                <div>
                  <div className="text-2xl font-bold font-serif text-gold-600 dark:text-gold-400">100%</div>
                  <div className="text-xs text-forest-600 dark:text-forest-400 font-medium mt-0.5">Zero PII Leakage</div>
                </div>
                <div>
                  <div className="text-2xl font-bold font-serif text-forest-800 dark:text-forest-200">10-Feature</div>
                  <div className="text-xs text-forest-600 dark:text-forest-400 font-medium mt-0.5">Live LMS Telemetry</div>
                </div>
              </div>
            </div>

            {/* Right Column: Live Interactive Simulator / Preview Card */}
            <div id="simulator" className="lg:col-span-5">
              <div className={`p-6 sm:p-7 rounded-3xl border shadow-xl transition-all duration-300 relative overflow-hidden ${
                isDark
                  ? 'bg-forest-950/90 border-forest-800 shadow-forest-950/60'
                  : 'bg-white border-forest-200/80 shadow-card-morning'
              }`}>
                {/* Gold accent corner badge */}
                <div className="flex items-center justify-between pb-4 border-b border-forest-200/60 dark:border-forest-800/80">
                  <div className="flex items-center space-x-2.5">
                    <div className="w-8 h-8 rounded-xl bg-emerald-500/15 flex items-center justify-center text-emerald-600 dark:text-emerald-400 border border-emerald-500/30">
                      <Brain className="w-4 h-4" />
                    </div>
                    <div>
                      <h2 className="text-sm font-bold font-serif leading-tight">Live ML Inference Preview</h2>
                      <span className="text-[11px] text-forest-500 dark:text-forest-400">Real-Time Risk Computation</span>
                    </div>
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-gold-500/10 text-gold-600 dark:text-gold-300 border border-gold-500/30">
                    Interactive
                  </span>
                </div>

                {/* Simulated Topic Context */}
                <div className="mt-4 p-3.5 rounded-2xl bg-forest-50 dark:bg-forest-900/60 border border-forest-200/60 dark:border-forest-800/60">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-forest-700 dark:text-forest-300">Topic: Binary Search Trees</span>
                    <span className="px-2 py-0.5 rounded-md font-medium text-[11px] bg-forest-200/70 dark:bg-forest-800 text-forest-800 dark:text-forest-200">Intermediate</span>
                  </div>
                </div>

                {/* Interactive Sliders */}
                <div className="mt-5 space-y-4">
                  <div>
                    <div className="flex justify-between text-xs font-medium mb-1.5">
                      <span className="text-forest-700 dark:text-forest-300">Quiz Performance</span>
                      <span className="font-bold text-emerald-700 dark:text-emerald-400">{simQuiz}%</span>
                    </div>
                    <input
                      type="range"
                      min="10"
                      max="100"
                      value={simQuiz}
                      onChange={(e) => setSimQuiz(Number(e.target.value))}
                      className="w-full accent-emerald-600 cursor-pointer"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between text-xs font-medium mb-1.5">
                      <span className="text-forest-700 dark:text-forest-300">Formative Re-Attempts</span>
                      <span className="font-bold text-gold-600 dark:text-gold-400">{simAttempts} attempts</span>
                    </div>
                    <input
                      type="range"
                      min="1"
                      max="6"
                      value={simAttempts}
                      onChange={(e) => setSimAttempts(Number(e.target.value))}
                      className="w-full accent-gold-500 cursor-pointer"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between text-xs font-medium mb-1.5">
                      <span className="text-forest-700 dark:text-forest-300">Repeated Misconceptions / Errors</span>
                      <span className="font-bold text-rose-600 dark:text-rose-400">{simErrors} errors</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="15"
                      value={simErrors}
                      onChange={(e) => setSimErrors(Number(e.target.value))}
                      className="w-full accent-rose-500 cursor-pointer"
                    />
                  </div>
                </div>

                {/* Real-Time Outcome Panel */}
                <div className="mt-6 pt-4 border-t border-forest-200/60 dark:border-forest-800/80">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-[11px] font-semibold text-forest-500 dark:text-forest-400 uppercase tracking-wider block">
                        Forecasted Difficulty Risk
                      </span>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`px-3 py-1 rounded-xl text-xs font-bold border ${tierColors[simTier]}`}>
                          {simTier} Difficulty
                        </span>
                        <span className="text-xs font-mono text-forest-600 dark:text-forest-400">
                          (Severity: {(simScore / 100).toFixed(2)})
                        </span>
                      </div>
                    </div>

                    <div className="text-right">
                      <span className="text-[11px] font-semibold text-forest-500 dark:text-forest-400 uppercase tracking-wider block">
                        Intervention Priority
                      </span>
                      <span className="text-xs font-bold text-forest-800 dark:text-forest-200 mt-1 block">
                        {simTier === 'High' ? 'Immediate Support' : simTier === 'Moderate' ? 'Guided Review' : 'On Track'}
                      </span>
                    </div>
                  </div>

                  {/* Recommendation Preview */}
                  <div className="mt-4 p-3 rounded-xl bg-gold-500/10 border border-gold-500/20 text-xs">
                    <span className="font-bold text-gold-700 dark:text-gold-300 block mb-0.5">
                      Automated Action Roadmap:
                    </span>
                    <span className="text-forest-700 dark:text-forest-300">
                      {simTier === 'High'
                        ? 'Generate tree traversal visual worksheets and schedule 1-on-1 instructor mentoring.'
                        : simTier === 'Moderate'
                        ? 'Assign supplemental BST search practice with targeted feedback hints.'
                        : 'Reinforce advanced balanced-tree invariants and self-paced challenge questions.'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------- */}
      {/* HOW IT WORKS SECTION                                                */}
      {/* ------------------------------------------------------------------- */}
      <section id="how-it-works" className={`py-20 border-t transition-colors duration-300 ${
        isDark ? 'bg-forest-950/40 border-forest-800/60' : 'bg-ivory-100/60 border-forest-200/60'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gold-500/15 text-gold-600 dark:text-gold-400 border border-gold-500/30">
              End-to-End Workflow
            </span>
            <h2 className="mt-3 text-3xl sm:text-4xl font-extrabold font-serif tracking-tight">
              From Learning Telemetry to Actionable Mastery
            </h2>
            <p className="mt-3 text-sm sm:text-base text-forest-600 dark:text-forest-400">
              Four cohesive steps bridge day-to-day student interactions with scientifically grounded, explainable pedagogical interventions.
            </p>
          </div>

          <div className="mt-14 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Step 1 */}
            <div className={`p-6 rounded-2xl border transition-all duration-300 relative group ${
              isDark ? 'bg-forest-950 border-forest-800 hover:border-gold-500/40' : 'bg-white border-forest-200/80 hover:border-emerald-600/40 shadow-xs'
            }`}>
              <div className="flex items-center justify-between mb-4">
                <span className="text-3xl font-bold font-serif text-forest-200 dark:text-forest-800 group-hover:text-gold-500 transition-colors">
                  01
                </span>
                <div className="w-10 h-10 rounded-xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 flex items-center justify-center border border-emerald-500/30">
                  <Layers className="w-5 h-5" />
                </div>
              </div>
              <h3 className="text-lg font-bold font-serif mb-2">Learning Data Telemetry</h3>
              <p className="text-xs sm:text-sm text-forest-600 dark:text-forest-400 leading-relaxed">
                Automated ingestion of quiz percentages, assignment submission timeliness, weekly study hours, quiz retakes, and repeated misconceptions.
              </p>
            </div>

            {/* Step 2 */}
            <div className={`p-6 rounded-2xl border transition-all duration-300 relative group ${
              isDark ? 'bg-forest-950 border-forest-800 hover:border-gold-500/40' : 'bg-white border-forest-200/80 hover:border-emerald-600/40 shadow-xs'
            }`}>
              <div className="flex items-center justify-between mb-4">
                <span className="text-3xl font-bold font-serif text-forest-200 dark:text-forest-800 group-hover:text-gold-500 transition-colors">
                  02
                </span>
                <div className="w-10 h-10 rounded-xl bg-gold-500/15 text-gold-600 dark:text-gold-400 flex items-center justify-center border border-gold-500/30">
                  <Brain className="w-5 h-5" />
                </div>
              </div>
              <h3 className="text-lg font-bold font-serif mb-2">Canonical AI Analysis</h3>
              <p className="text-xs sm:text-sm text-forest-600 dark:text-forest-400 leading-relaxed">
                A calibrated 10-feature pipeline calculates learning pace gaps relative to course benchmarks, isolating cognitive struggles without demographic bias.
              </p>
            </div>

            {/* Step 3 */}
            <div className={`p-6 rounded-2xl border transition-all duration-300 relative group ${
              isDark ? 'bg-forest-950 border-forest-800 hover:border-gold-500/40' : 'bg-white border-forest-200/80 hover:border-emerald-600/40 shadow-xs'
            }`}>
              <div className="flex items-center justify-between mb-4">
                <span className="text-3xl font-bold font-serif text-forest-200 dark:text-forest-800 group-hover:text-gold-500 transition-colors">
                  03
                </span>
                <div className="w-10 h-10 rounded-xl bg-forest-500/15 text-forest-600 dark:text-forest-400 flex items-center justify-center border border-forest-500/30">
                  <Target className="w-5 h-5" />
                </div>
              </div>
              <h3 className="text-lg font-bold font-serif mb-2">Difficulty Risk Prediction</h3>
              <p className="text-xs sm:text-sm text-forest-600 dark:text-forest-400 leading-relaxed">
                Multi-class classification stratifies struggle into Low, Moderate, and High difficulty severity tiers with calibrated probability vectors.
              </p>
            </div>

            {/* Step 4 */}
            <div className={`p-6 rounded-2xl border transition-all duration-300 relative group ${
              isDark ? 'bg-forest-950 border-forest-800 hover:border-gold-500/40' : 'bg-white border-forest-200/80 hover:border-emerald-600/40 shadow-xs'
            }`}>
              <div className="flex items-center justify-between mb-4">
                <span className="text-3xl font-bold font-serif text-forest-200 dark:text-forest-800 group-hover:text-gold-500 transition-colors">
                  04
                </span>
                <div className="w-10 h-10 rounded-xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 flex items-center justify-center border border-emerald-500/30">
                  <Compass className="w-5 h-5" />
                </div>
              </div>
              <h3 className="text-lg font-bold font-serif mb-2">Actionable Recommendations</h3>
              <p className="text-xs sm:text-sm text-forest-600 dark:text-forest-400 leading-relaxed">
                Direct distribution of prioritized study actions to students and early intervention alerts to course instructors for timely follow-up.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------- */}
      {/* FEATURES SECTION                                                    */}
      {/* ------------------------------------------------------------------- */}
      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100/90 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
              Core Capabilities
            </span>
            <h2 className="mt-3 text-3xl sm:text-4xl font-extrabold font-serif tracking-tight">
              Built for Academic Rigor and Actionable Transparency
            </h2>
            <p className="mt-3 text-sm sm:text-base text-forest-600 dark:text-forest-400">
              Every feature is engineered to empower student self-regulation and equip educators with formative diagnostics.
            </p>
          </div>

          <div className="mt-14 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <div className={`p-6 sm:p-7 rounded-2xl border transition-all duration-300 ${
              isDark ? 'bg-forest-950/80 border-forest-800' : 'bg-white border-forest-200/80 shadow-xs'
            }`}>
              <div className="w-11 h-11 rounded-xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 flex items-center justify-center border border-emerald-500/30 mb-4">
                <Target className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold font-serif mb-2">Early Difficulty Prediction</h3>
              <p className="text-xs sm:text-sm text-forest-600 dark:text-forest-400 leading-relaxed">
                Detect conceptual friction points weeks in advance, enabling non-punitive interventions before summative exams lock in poor grades.
              </p>
            </div>

            {/* Feature 2 */}
            <div className={`p-6 sm:p-7 rounded-2xl border transition-all duration-300 ${
              isDark ? 'bg-forest-950/80 border-forest-800' : 'bg-white border-forest-200/80 shadow-xs'
            }`}>
              <div className="w-11 h-11 rounded-xl bg-gold-500/15 text-gold-600 dark:text-gold-400 flex items-center justify-center border border-gold-500/30 mb-4">
                <BarChart3 className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold font-serif mb-2">Formative Performance Analysis</h3>
              <p className="text-xs sm:text-sm text-forest-600 dark:text-forest-400 leading-relaxed">
                Multivariate tracking of quiz scores, assignment adherence, and study time distribution across curriculum difficulty tiers.
              </p>
            </div>

            {/* Feature 3 */}
            <div className={`p-6 sm:p-7 rounded-2xl border transition-all duration-300 ${
              isDark ? 'bg-forest-950/80 border-forest-800' : 'bg-white border-forest-200/80 shadow-xs'
            }`}>
              <div className="w-11 h-11 rounded-xl bg-forest-500/15 text-forest-600 dark:text-forest-400 flex items-center justify-center border border-forest-500/30 mb-4">
                <Sliders className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold font-serif mb-2">Learning-Gap Identification</h3>
              <p className="text-xs sm:text-sm text-forest-600 dark:text-forest-400 leading-relaxed">
                Pinpoint root misconceptions and pacing discrepancies, separating foundational prerequisite gaps from topic-specific challenges.
              </p>
            </div>

            {/* Feature 4 */}
            <div className={`p-6 sm:p-7 rounded-2xl border transition-all duration-300 ${
              isDark ? 'bg-forest-950/80 border-forest-800' : 'bg-white border-forest-200/80 shadow-xs'
            }`}>
              <div className="w-11 h-11 rounded-xl bg-gold-500/15 text-gold-600 dark:text-gold-400 flex items-center justify-center border border-gold-500/30 mb-4">
                <Compass className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold font-serif mb-2">Personalized Study Recommendations</h3>
              <p className="text-xs sm:text-sm text-forest-600 dark:text-forest-400 leading-relaxed">
                Automated curriculum-aligned study suggestions, review guides, and peer tutoring prompts with one-click completion checklists.
              </p>
            </div>

            {/* Feature 5 */}
            <div className={`p-6 sm:p-7 rounded-2xl border transition-all duration-300 ${
              isDark ? 'bg-forest-950/80 border-forest-800' : 'bg-white border-forest-200/80 shadow-xs'
            }`}>
              <div className="w-11 h-11 rounded-xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 flex items-center justify-center border border-emerald-500/30 mb-4">
                <TrendingUp className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold font-serif mb-2">Cohort Progress Tracking</h3>
              <p className="text-xs sm:text-sm text-forest-600 dark:text-forest-400 leading-relaxed">
                Instructors gain full visibility into subject-wide mastery curves, struggling subgroups, and post-intervention recovery rates.
              </p>
            </div>

            {/* Feature 6 */}
            <div className={`p-6 sm:p-7 rounded-2xl border transition-all duration-300 ${
              isDark ? 'bg-forest-950/80 border-forest-800' : 'bg-white border-forest-200/80 shadow-xs'
            }`}>
              <div className="w-11 h-11 rounded-xl bg-forest-500/15 text-forest-600 dark:text-forest-400 flex items-center justify-center border border-forest-500/30 mb-4">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold font-serif mb-2">Privacy & Telemetry Auditing</h3>
              <p className="text-xs sm:text-sm text-forest-600 dark:text-forest-400 leading-relaxed">
                Zero exposure of personally identifiable information. Full SHA-256 pseudonymization, model version isolation, and shadow inference safeguards.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------- */}
      {/* BENEFITS SECTION                                                    */}
      {/* ------------------------------------------------------------------- */}
      <section id="about" className={`py-20 border-t transition-colors duration-300 ${
        isDark ? 'bg-forest-950/40 border-forest-800/60' : 'bg-ivory-100/60 border-forest-200/60'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gold-500/15 text-gold-600 dark:text-gold-400 border border-gold-500/30">
              Institutional Impact
            </span>
            <h2 className="mt-3 text-3xl sm:text-4xl font-extrabold font-serif tracking-tight">
              Designed for Both Learners and Academic Leaders
            </h2>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* For Students */}
            <div className={`p-8 rounded-3xl border transition-all duration-300 ${
              isDark ? 'bg-forest-950 border-forest-800' : 'bg-white border-forest-200/80 shadow-xs'
            }`}>
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 flex items-center justify-center border border-emerald-500/30">
                  <GraduationCap className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-xl font-bold font-serif">For Students</h3>
                  <span className="text-xs text-forest-500 dark:text-forest-400">Empowering Autonomous Mastery</span>
                </div>
              </div>

              <ul className="space-y-4 text-sm text-forest-700 dark:text-forest-300">
                <li className="flex items-start space-x-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>Crystal-Clear Progress Visibility:</strong> Understand exactly where conceptual gaps exist in real time without guessing.</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>Non-Punitive Self-Correction:</strong> Predictions serve as formative diagnostics, offering personalized revision actions before tests.</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>Actionable Step-by-Step Study Roadmaps:</strong> Targeted worksheets, remedial practice, and peer assistance tailored to your pace.</span>
                </li>
              </ul>

              <div className="mt-8 pt-6 border-t border-forest-200/60 dark:border-forest-800">
                <Link
                  to="/register"
                  className="inline-flex items-center text-sm font-bold text-emerald-700 dark:text-emerald-400 hover:text-emerald-600 group"
                >
                  <span>Register as a Student</span>
                  <ArrowRight className="w-4 h-4 ml-1.5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>
            </div>

            {/* For Instructors */}
            <div className={`p-8 rounded-3xl border transition-all duration-300 ${
              isDark ? 'bg-forest-950 border-forest-800' : 'bg-white border-forest-200/80 shadow-xs'
            }`}>
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 rounded-2xl bg-gold-500/15 text-gold-600 dark:text-gold-400 flex items-center justify-center border border-gold-500/30">
                  <Users className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-xl font-bold font-serif">For Instructors & Faculty</h3>
                  <span className="text-xs text-forest-500 dark:text-forest-400">Timely Classroom Interventions</span>
                </div>
              </div>

              <ul className="space-y-4 text-sm text-forest-700 dark:text-forest-300">
                <li className="flex items-start space-x-3">
                  <CheckCircle2 className="w-5 h-5 text-gold-600 dark:text-gold-400 shrink-0 mt-0.5" />
                  <span><strong>Proactive Early Warnings:</strong> Receive automated high-risk alerts before struggling students fall irrecoverably behind.</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle2 className="w-5 h-5 text-gold-600 dark:text-gold-400 shrink-0 mt-0.5" />
                  <span><strong>Cohort Analytics & Gap Heatmaps:</strong> Identify curriculum bottlenecks where class-wide repeated mistakes spike.</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle2 className="w-5 h-5 text-gold-600 dark:text-gold-400 shrink-0 mt-0.5" />
                  <span><strong>Instructor-in-the-Loop Verification:</strong> Review and confirm staged ML predictions with full teacher oversight and follow-up logging.</span>
                </li>
              </ul>

              <div className="mt-8 pt-6 border-t border-forest-200/60 dark:border-forest-800">
                <Link
                  to="/register"
                  className="inline-flex items-center text-sm font-bold text-gold-600 dark:text-gold-400 hover:text-gold-500 group"
                >
                  <span>Register as an Instructor</span>
                  <ArrowRight className="w-4 h-4 ml-1.5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------- */}
      {/* PROFESSIONAL FOOTER                                                 */}
      {/* ------------------------------------------------------------------- */}
      <footer className={`py-12 border-t transition-colors duration-300 ${
        isDark ? 'bg-forest-980 border-forest-800 text-forest-400' : 'bg-ivory-100 border-forest-200 text-forest-600'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
            {/* Column 1: Brand */}
            <div className="md:col-span-2">
              <div className="flex items-center space-x-2.5 mb-3">
                <div className="w-8 h-8 rounded-xl bg-emerald-700 flex items-center justify-center text-white border border-gold-400/40">
                  <Sparkles className="w-4 h-4 text-gold-300" />
                </div>
                <span className="text-lg font-bold font-serif text-forest-900 dark:text-white">
                  AI Learning Difficulty Predictor
                </span>
              </div>
              <p className="text-xs leading-relaxed max-w-sm">
                Empowering academic institutions with explainable, formative difficulty prediction and automated pedagogical roadmaps.
              </p>
              <div className="mt-4 flex items-center space-x-2 text-xs text-forest-500">
                <ShieldCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                <span>Active Model: <strong>v1.0.0-production-baseline</strong></span>
              </div>
            </div>

            {/* Column 2: Navigation */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-forest-900 dark:text-forest-200 mb-3 font-serif">
                Navigation
              </h4>
              <ul className="space-y-2 text-xs">
                <li><a href="#how-it-works" className="hover:text-gold-500 transition-colors">How It Works</a></li>
                <li><a href="#features" className="hover:text-gold-500 transition-colors">Core Features</a></li>
                <li><a href="#simulator" className="hover:text-gold-500 transition-colors">Live Simulator</a></li>
                <li><a href="#about" className="hover:text-gold-500 transition-colors">Institutional Impact</a></li>
              </ul>
            </div>

            {/* Column 3: Portals */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-forest-900 dark:text-forest-200 mb-3 font-serif">
                Access Portals
              </h4>
              <ul className="space-y-2 text-xs">
                <li><Link to="/login" className="hover:text-gold-500 transition-colors">Sign In to Dashboard</Link></li>
                <li><Link to="/register" className="hover:text-gold-500 transition-colors">Create Free Account</Link></li>
                <li><a href="#simulator" className="hover:text-gold-500 transition-colors">Interactive Demo</a></li>
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-forest-200/80 dark:border-forest-800/80 flex flex-col sm:flex-row items-center justify-between text-xs">
            <p>© 2026 AI Learning Difficulty Predictor. All rights reserved.</p>
            <p className="mt-2 sm:mt-0 text-[11px] text-forest-500">
              Formative Academic Telemetry & Educational Machine Learning System
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;

