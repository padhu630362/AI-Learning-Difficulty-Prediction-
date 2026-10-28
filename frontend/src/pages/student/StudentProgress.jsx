import React, { useState, useEffect } from 'react';
import axiosClient from '../../api/axiosClient';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { TrendingUp, Award, CheckCircle2, History } from 'lucide-react';

const StudentProgress = () => {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    setLoading(true);
    try {
      const res = await axiosClient.get('/progress/my-progress');
      setProgress(res.data.progress);
    } catch (err) {
      console.error('Failed to fetch student progress:', err);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#10b981', '#f59e0b', '#f43f5e'];

  if (loading || !progress) {
    return (
      <div className="p-8 text-center text-slate-500">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
        <p className="text-xs">Compiling longitudinal learning progress...</p>
      </div>
    );
  }

  const pieData = [
    { name: 'Low Difficulty', value: progress.difficulty_breakdown.Low },
    { name: 'Moderate Difficulty', value: progress.difficulty_breakdown.Moderate },
    { name: 'High Difficulty', value: progress.difficulty_breakdown.High },
  ].filter((d) => d.value > 0);

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Learning Progress & History</h1>
        <p className="text-sm text-slate-500 mt-1">
          Longitudinal tracking of assessment performance, recommendation completion, and difficulty trajectory.
        </p>
      </div>

      {/* Top Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Recommendations Completed
          </p>
          <p className="text-2xl font-bold text-slate-900 mt-1">
            {progress.recommendation_progress.completed} / {progress.recommendation_progress.total}
          </p>
          <div className="w-full bg-slate-100 rounded-full h-2 mt-3">
            <div
              className="bg-indigo-600 h-2 rounded-full"
              style={{ width: `${progress.recommendation_progress.completion_rate}%` }}
            />
          </div>
          <p className="text-xs text-slate-500 mt-2">
            {progress.recommendation_progress.completion_rate}% completion rate
          </p>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Total Assessments Completed
          </p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{progress.timeline.length}</p>
          <p className="text-xs text-slate-500 mt-3">Quizzes, assignments & examinations</p>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Curriculum Mastery Status
          </p>
          <p className="text-2xl font-bold text-emerald-600 mt-1">
            {progress.difficulty_breakdown.Low} Modules
          </p>
          <p className="text-xs text-slate-500 mt-3">Operating at low learning friction</p>
        </div>
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Score Timeline */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <h3 className="text-base font-bold text-slate-900 mb-1">Assessment Performance Trajectory</h3>
          <p className="text-xs text-slate-500 mb-6">Percentage marks across chronological submissions</p>

          <div className="h-64 w-full">
            {progress.timeline.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={progress.timeline} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#64748b' }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#64748b' }} />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const d = payload[0].payload;
                        return (
                          <div className="bg-slate-900 text-white text-xs p-2.5 rounded-xl shadow-lg border border-slate-800">
                            <p className="font-bold">{d.assessment_title}</p>
                            <p className="text-slate-300">{d.subject_name}</p>
                            <p className="text-emerald-400 font-bold mt-1">Score: {d.percentage}%</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="percentage"
                    stroke="#4f46e5"
                    strokeWidth={2.5}
                    dot={{ fill: '#4f46e5', r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No chronological assessment records
              </div>
            )}
          </div>
        </div>

        {/* Subject Averages */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <h3 className="text-base font-bold text-slate-900 mb-1">Subject Performance Comparison</h3>
          <p className="text-xs text-slate-500 mb-6">Mean assessment percentages across subjects</p>

          <div className="h-64 w-full">
            {progress.subject_summary.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={progress.subject_summary} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="subject_name" tick={{ fontSize: 10, fill: '#64748b' }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#64748b' }} />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const d = payload[0].payload;
                        return (
                          <div className="bg-slate-900 text-white text-xs p-2.5 rounded-xl shadow-lg">
                            <p className="font-bold">{d.subject_name}</p>
                            <p className="text-indigo-400 font-bold mt-1">Average: {d.average_score}%</p>
                            <p className="text-slate-300">Latest: {d.latest_score}%</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="average_score" fill="#6366f1" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No subject records available
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Historical Prediction Log */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <div className="flex items-center space-x-2 mb-4">
          <History className="w-5 h-5 text-indigo-600" />
          <h3 className="text-base font-bold text-slate-900">Historical AI Model Prediction Log</h3>
        </div>

        {progress.prediction_timeline.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No historical prediction logs recorded.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  <th className="pb-3">Date</th>
                  <th className="pb-3">Subject</th>
                  <th className="pb-3">Topic</th>
                  <th className="pb-3">Difficulty Outcome</th>
                  <th className="pb-3">Severity Score</th>
                  <th className="pb-3">High Risk Prob</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700 text-xs">
                {progress.prediction_timeline.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/60">
                    <td className="py-3 text-slate-500">{item.date}</td>
                    <td className="py-3 font-semibold text-slate-800">{item.subject_name}</td>
                    <td className="py-3">{item.topic_name}</td>
                    <td className="py-3">
                      <span
                        className={`px-2 py-0.5 rounded font-semibold text-[10px] ${
                          item.predicted_difficulty === 'High'
                            ? 'bg-rose-100 text-rose-700'
                            : item.predicted_difficulty === 'Moderate'
                            ? 'bg-amber-100 text-amber-700'
                            : 'bg-emerald-100 text-emerald-700'
                        }`}
                      >
                        {item.predicted_difficulty}
                      </span>
                    </td>
                    <td className="py-3 font-mono">{item.difficulty_score}%</td>
                    <td className="py-3 font-mono">{item.probability_high}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentProgress;

