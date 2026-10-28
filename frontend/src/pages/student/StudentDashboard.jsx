import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import axiosClient from '../../api/axiosClient';
import StatCard from '../../components/StatCard';
import { CardSkeleton } from '../../components/LoadingSkeleton';
import {
  GraduationCap,
  BookOpen,
  AlertTriangle,
  Lightbulb,
  ArrowRight,
  CheckCircle2,
  Clock,
  Sparkles,
  ChevronRight
} from 'lucide-react';

const StudentDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [subjects, setSubjects] = useState([]);
  const [results, setResults] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [completingId, setCompletingId] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [subsRes, resRes, predsRes, recsRes] = await Promise.all([
        axiosClient.get('/subjects'),
        axiosClient.get('/assessments/my-results'),
        axiosClient.get('/predictions/my-predictions'),
        axiosClient.get('/recommendations/my-recommendations?status=pending'),
      ]);

      setSubjects(subsRes.data.subjects || []);
      setResults(resRes.data.results || []);
      setPredictions(predsRes.data.predictions || []);
      setRecommendations(recsRes.data.recommendations || []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkCompleted = async (recId) => {
    setCompletingId(recId);
    try {
      await axiosClient.put(`/recommendations/${recId}/complete`);
      setRecommendations((prev) => prev.filter((r) => r.id !== recId));
    } catch (err) {
      console.error('Failed to mark recommendation completed:', err);
    } finally {
      setCompletingId(null);
    }
  };

  // Calculations
  const avgScore = results.length > 0
    ? Math.round(results.reduce((acc, r) => acc + r.percentage, 0) / results.length)
    : 0;

  const highDifficultyCount = predictions.filter((p) => p.predicted_difficulty === 'High').length;

  const getDifficultyBadge = (difficulty) => {
    switch (difficulty) {
      case 'High':
        return 'bg-rose-100 text-rose-700 border-rose-200';
      case 'Moderate':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'Low':
      default:
        return 'bg-emerald-100 text-emerald-700 border-emerald-200';
    }
  };

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <CardSkeleton /><CardSkeleton /><CardSkeleton /><CardSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-8">
      {/* Welcome banner */}
      <div className="bg-gradient-to-r from-indigo-700 via-indigo-600 to-indigo-800 rounded-2xl p-6 sm:p-8 text-white shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
        <div>
          <div className="flex items-center space-x-2 text-indigo-200 text-xs font-semibold uppercase tracking-wider mb-1">
            <Sparkles className="w-4 h-4" />
            <span>AI Learning Analytics</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
            Welcome back, {user?.full_name}!
          </h1>
          <p className="text-indigo-100 text-sm mt-1 max-w-xl">
            Here is your personalized academic status and machine-learning difficulty predictions.
          </p>
        </div>
        <Link
          to="/student/analysis"
          className="inline-flex items-center space-x-2 bg-white text-indigo-700 px-4 py-2.5 rounded-xl font-semibold text-sm hover:bg-indigo-50 shadow-xs transition-colors shrink-0"
        >
          <span>Run Topic Analysis</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Average Score"
          value={`${avgScore}%`}
          subtitle={`Across ${results.length} assessment records`}
          icon={GraduationCap}
          color="indigo"
        />
        <StatCard
          title="Tracked Subjects"
          value={subjects.length}
          subtitle="Enrolled curriculum subjects"
          icon={BookOpen}
          color="blue"
        />
        <StatCard
          title="High Difficulty Gaps"
          value={highDifficultyCount}
          subtitle="Topics flagged for immediate revision"
          icon={AlertTriangle}
          color={highDifficultyCount > 0 ? 'rose' : 'emerald'}
        />
        <StatCard
          title="Pending Study Tasks"
          value={recommendations.length}
          subtitle="Personalized recommendations"
          icon={Lightbulb}
          color="amber"
        />
      </div>

      {/* Main 2-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Subjects & Recent Predictions (2 cols) */}
        <div className="lg:col-span-2 space-y-8">
          {/* Subjects Overview */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Enrolled Subjects</h2>
                <p className="text-xs text-slate-500">Curriculum subjects and current topic counts</p>
              </div>
              <Link to="/student/subjects" className="text-xs font-semibold text-indigo-600 hover:text-indigo-500 flex items-center">
                View All Subjects <ChevronRight className="w-3.5 h-3.5 ml-1" />
              </Link>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {subjects.map((sub) => {
                const subResults = results.filter((r) => r.subject_id === sub.id);
                const subAvg = subResults.length > 0
                  ? Math.round(subResults.reduce((a, b) => a + b.percentage, 0) / subResults.length)
                  : null;

                return (
                  <div key={sub.id} className="border border-slate-200 rounded-xl p-4 hover:border-indigo-200 transition-all bg-slate-50/50">
                    <div className="flex justify-between items-start">
                      <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md">
                        {sub.code}
                      </span>
                      {subAvg !== null && (
                        <span className="text-xs font-semibold text-slate-700">
                          Avg: {subAvg}%
                        </span>
                      )}
                    </div>
                    <h3 className="font-semibold text-slate-800 text-sm mt-2">{sub.name}</h3>
                    <p className="text-xs text-slate-500 line-clamp-2 mt-1">{sub.description}</p>
                    <div className="mt-4 pt-3 border-t border-slate-200/60 flex items-center justify-between text-xs text-slate-500">
                      <span>{sub.topic_count} Topics</span>
                      <Link to={`/student/subjects`} className="text-indigo-600 font-medium hover:underline flex items-center">
                        Topics <ChevronRight className="w-3 h-3 ml-0.5" />
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recent AI Predictions */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Recent ML Difficulty Predictions</h2>
                <p className="text-xs text-slate-500">Trained model predictions based on performance metrics</p>
              </div>
              <Link to="/student/analysis" className="text-xs font-semibold text-indigo-600 hover:text-indigo-500 flex items-center">
                Deep Analysis <ChevronRight className="w-3.5 h-3.5 ml-1" />
              </Link>
            </div>

            {predictions.length === 0 ? (
              <div className="text-center py-8 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                <Sparkles className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm font-medium text-slate-600">No predictions recorded yet</p>
                <p className="text-xs text-slate-400 mt-1">Run an analysis on your topics to evaluate difficulty.</p>
                <Link
                  to="/student/analysis"
                  className="mt-3 inline-block text-xs font-semibold text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-lg hover:bg-indigo-100"
                >
                  Generate First Prediction
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {predictions.slice(0, 4).map((p) => (
                  <div key={p.id} className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between space-y-2 sm:space-y-0">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-semibold text-slate-800">{p.topic_name}</span>
                        <span className="text-xs text-slate-400">({p.subject_name})</span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Severity Index: {Math.round(p.difficulty_score * 100)}% • Model: {p.model_version}
                      </p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${getDifficultyBadge(p.predicted_difficulty)}`}>
                        {p.predicted_difficulty} Difficulty
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Assessment Results */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <h2 className="text-lg font-bold text-slate-900 mb-1">Recent Assessment Marks</h2>
            <p className="text-xs text-slate-500 mb-4">Latest quizzes, assignments, and exam results</p>

            {results.length === 0 ? (
              <p className="text-sm text-slate-500 italic">No assessment scores logged yet.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      <th className="pb-3">Assessment</th>
                      <th className="pb-3">Type</th>
                      <th className="pb-3">Score</th>
                      <th className="pb-3">Percentage</th>
                      <th className="pb-3">Study Time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-700">
                    {results.slice(0, 5).map((r) => (
                      <tr key={r.id} className="hover:bg-slate-50/60">
                        <td className="py-3 font-medium text-slate-800">{r.assessment_title}</td>
                        <td className="py-3">
                          <span className="capitalize text-xs font-medium px-2 py-0.5 rounded-md bg-slate-100 text-slate-600">
                            {r.assessment_type}
                          </span>
                        </td>
                        <td className="py-3">{r.marks_obtained} / {r.max_marks}</td>
                        <td className="py-3">
                          <span className={`font-semibold ${r.percentage >= 70 ? 'text-emerald-600' : r.percentage >= 50 ? 'text-amber-600' : 'text-rose-600'}`}>
                            {r.percentage}%
                          </span>
                        </td>
                        <td className="py-3 text-xs text-slate-500 flex items-center">
                          <Clock className="w-3.5 h-3.5 mr-1" />
                          {r.study_time_minutes} min
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Recommendations & Action Checklist (1 col) */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Lightbulb className="w-5 h-5 text-amber-500" />
                <h2 className="text-base font-bold text-slate-900">Study Recommendations</h2>
              </div>
              <Link to="/student/recommendations" className="text-xs font-semibold text-indigo-600 hover:text-indigo-500">
                View All
              </Link>
            </div>

            {recommendations.length === 0 ? (
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-100 text-center">
                <CheckCircle2 className="w-6 h-6 text-emerald-600 mx-auto mb-1" />
                <p className="text-xs font-semibold text-emerald-800">You are all caught up!</p>
                <p className="text-[11px] text-emerald-600 mt-0.5">No pending recommendations at this time.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {recommendations.slice(0, 5).map((rec) => (
                  <div
                    key={rec.id}
                    className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-600">
                          {rec.topic_name || rec.subject_name}
                        </span>
                        <span className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${
                          rec.priority === 'high' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'
                        }`}>
                          {rec.priority}
                        </span>
                      </div>
                      <p className="text-xs font-semibold text-slate-800 mt-1">{rec.suggested_action}</p>
                      <p className="text-[11px] text-slate-500 mt-1">{rec.reason}</p>
                    </div>

                    <div className="mt-3 pt-2 border-t border-slate-200/60 flex items-center justify-between">
                      {rec.resource_url ? (
                        <a
                          href={rec.resource_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[11px] font-medium text-indigo-600 hover:underline"
                        >
                          View Resource ↗
                        </a>
                      ) : <span />}

                      <button
                        onClick={() => handleMarkCompleted(rec.id)}
                        disabled={completingId === rec.id}
                        className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 flex items-center space-x-1"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>{completingId === rec.id ? 'Marking...' : 'Done'}</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;

