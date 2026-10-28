import React, { useState, useEffect } from 'react';
import axiosClient from '../../api/axiosClient';
import { useToast } from '../../context/ToastContext';
import { Lightbulb, CheckCircle2, Clock, ExternalLink, Filter, Sparkles } from 'lucide-react';

const StudentRecommendations = () => {
  const toast = useToast();
  const [recommendations, setRecommendations] = useState([]);
  const [activeFilter, setActiveFilter] = useState('pending'); // 'all', 'pending', 'completed'
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);

  useEffect(() => {
    fetchRecommendations();
  }, [activeFilter]);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      let endpoint = '/recommendations/my-recommendations';
      if (activeFilter === 'pending') endpoint += '?status=pending';
      else if (activeFilter === 'completed') endpoint += '?status=completed';

      const res = await axiosClient.get(endpoint);
      setRecommendations(res.data.recommendations || []);
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkComplete = async (recId) => {
    setUpdatingId(recId);
    try {
      await axiosClient.put(`/recommendations/${recId}/complete`);
      toast.success('Study action completed! Great work.');
      if (activeFilter === 'pending') {
        setRecommendations((prev) => prev.filter((r) => r.id !== recId));
      } else {
        fetchRecommendations();
      }
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to update recommendation.');
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Personalized Study Guidance</h1>
          <p className="text-sm text-slate-500 mt-1">
            Machine-learning generated actions targeted at resolving specific learning bottlenecks.
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex bg-slate-100 p-1 rounded-xl">
          <button
            onClick={() => setActiveFilter('pending')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeFilter === 'pending'
                ? 'bg-white text-indigo-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Pending Tasks
          </button>
          <button
            onClick={() => setActiveFilter('completed')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeFilter === 'completed'
                ? 'bg-white text-indigo-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Completed
          </button>
          <button
            onClick={() => setActiveFilter('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeFilter === 'all'
                ? 'bg-white text-indigo-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            All Guidance
          </button>
        </div>
      </div>

      {recommendations.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
          <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No recommendations found</h3>
          <p className="text-xs text-slate-400 mt-1">
            {activeFilter === 'pending'
              ? 'Great job! You have cleared all pending study suggestions.'
              : 'No recommendation history available.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendations.map((rec) => (
            <div
              key={rec.id}
              className={`rounded-2xl border p-5 transition-all flex flex-col justify-between ${
                rec.is_completed
                  ? 'bg-slate-50/80 border-slate-200 opacity-75'
                  : 'bg-white border-slate-200 shadow-xs hover:border-indigo-200'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-bold tracking-wider uppercase text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md">
                    {rec.subject_name || 'General'} • {rec.topic_name || 'Topic'}
                  </span>
                  <span
                    className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                      rec.priority === 'high'
                        ? 'bg-rose-100 text-rose-700'
                        : rec.priority === 'medium'
                        ? 'bg-amber-100 text-amber-700'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {rec.priority} Priority
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 mt-1">{rec.suggested_action}</h3>
                <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">{rec.reason}</p>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                {rec.resource_url ? (
                  <a
                    href={rec.resource_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-indigo-600 font-semibold hover:underline flex items-center space-x-1"
                  >
                    <span>Official Resource</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                ) : (
                  <span className="text-slate-400">Curriculum standard material</span>
                )}

                {!rec.is_completed ? (
                  <button
                    onClick={() => handleMarkComplete(rec.id)}
                    disabled={updatingId === rec.id}
                    className="px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-semibold rounded-lg border border-emerald-200 flex items-center space-x-1.5 transition-colors disabled:opacity-50"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>{updatingId === rec.id ? 'Saving...' : 'Mark as Done'}</span>
                  </button>
                ) : (
                  <span className="text-emerald-600 font-semibold flex items-center space-x-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Completed</span>
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default StudentRecommendations;

