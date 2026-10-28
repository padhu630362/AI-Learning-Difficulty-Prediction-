import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axiosClient from '../../api/axiosClient';
import StatCard from '../../components/StatCard';
import { CardSkeleton } from '../../components/LoadingSkeleton';
import {
  Users,
  Database,
  Cpu,
  Layers,
  Sparkles,
  ShieldCheck,
  ChevronRight,
  TrendingUp,
  Activity
} from 'lucide-react';

const AdminDashboard = () => {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminOverview();
  }, []);

  const fetchAdminOverview = async () => {
    setLoading(true);
    try {
      const res = await axiosClient.get('/admin/overview');
      setOverview(res.data);
    } catch (err) {
      console.error('Failed to load admin overview:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !overview) {
    return (
      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <CardSkeleton /><CardSkeleton /><CardSkeleton /><CardSkeleton />
        </div>
      </div>
    );
  }

  const { users, academics, predictions, alerts, active_model, datasets_count } = overview;

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">System Administration & AI Control</h1>
        <p className="text-sm text-slate-500 mt-1">
          Platform-level metrics, dataset repositories, user authorization, and machine learning model versioning.
        </p>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Users"
          value={users.total}
          subtitle={`${users.students} Students • ${users.instructors} Instructors`}
          icon={Users}
          color="indigo"
        />
        <StatCard
          title="Curriculum Topics"
          value={academics.topics}
          subtitle={`Across ${academics.subjects} active subjects`}
          icon={Layers}
          color="blue"
        />
        <StatCard
          title="AI Predictions Logged"
          value={predictions.total}
          subtitle={`${predictions.high} High • ${predictions.moderate} Moderate • ${predictions.low} Low`}
          icon={Sparkles}
          color="purple"
        />
        <StatCard
          title="Active ML Model"
          value={active_model ? active_model.model_name : 'No Model'}
          subtitle={active_model ? `F1: ${(active_model.f1_macro * 100).toFixed(1)}% • ${active_model.version_tag}` : 'Train a model'}
          icon={Cpu}
          color={active_model ? 'emerald' : 'rose'}
        />
      </div>

      {/* Model & System Health Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Active Model Snapshot (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Cpu className="w-5 h-5 text-indigo-600" />
              <h2 className="text-base font-bold text-slate-900">Current Production ML Model</h2>
            </div>
            <Link to="/admin/models" className="text-xs font-semibold text-indigo-600 hover:underline flex items-center">
              Full Evaluation Report <ChevronRight className="w-3.5 h-3.5 ml-1" />
            </Link>
          </div>

          {active_model ? (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-slate-900 text-base">{active_model.model_name}</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                      Active
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 font-mono mt-0.5">Version: {active_model.version_tag}</p>
                </div>
                <div className="text-xs text-slate-500 text-left sm:text-right">
                  <p>Trained on {active_model.training_sample_count} student samples</p>
                  <p className="text-slate-400 mt-0.5">{new Date(active_model.created_at).toLocaleDateString()}</p>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl border border-slate-200 text-center">
                  <p className="text-[10px] font-bold uppercase text-slate-400">Accuracy</p>
                  <p className="text-xl font-bold text-slate-800 mt-1">
                    {(active_model.accuracy * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="p-3 rounded-xl border border-slate-200 text-center">
                  <p className="text-[10px] font-bold uppercase text-slate-400">F1-Macro</p>
                  <p className="text-xl font-bold text-indigo-600 mt-1">
                    {(active_model.f1_macro * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="p-3 rounded-xl border border-slate-200 text-center">
                  <p className="text-[10px] font-bold uppercase text-slate-400">Precision</p>
                  <p className="text-xl font-bold text-slate-800 mt-1">
                    {(active_model.precision_macro * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="p-3 rounded-xl border border-slate-200 text-center">
                  <p className="text-[10px] font-bold uppercase text-slate-400">Recall</p>
                  <p className="text-xl font-bold text-slate-800 mt-1">
                    {(active_model.recall_macro * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center bg-slate-50 rounded-xl border border-dashed border-slate-200">
              <p className="text-sm font-semibold text-slate-700">No Model Currently Active</p>
              <p className="text-xs text-slate-400 mt-1">Train a baseline model or upload a verified dataset.</p>
              <Link
                to="/admin/models"
                className="mt-3 inline-block px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700"
              >
                Go to Model Training
              </Link>
            </div>
          )}
        </div>

        {/* Quick Admin Actions (1 col) */}
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <h3 className="text-base font-bold text-slate-900 mb-4">Administration Portals</h3>
            <div className="space-y-2.5">
              <Link
                to="/admin/users"
                className="p-3 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 flex items-center justify-between text-xs font-semibold text-slate-800 transition-colors"
              >
                <div className="flex items-center space-x-2.5">
                  <Users className="w-4 h-4 text-indigo-600" />
                  <span>Manage Users & Roles ({users.total})</span>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400" />
              </Link>

              <Link
                to="/admin/datasets"
                className="p-3 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 flex items-center justify-between text-xs font-semibold text-slate-800 transition-colors"
              >
                <div className="flex items-center space-x-2.5">
                  <Database className="w-4 h-4 text-blue-600" />
                  <span>Datasets & Data Validation ({datasets_count})</span>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400" />
              </Link>

              <Link
                to="/admin/models"
                className="p-3 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 flex items-center justify-between text-xs font-semibold text-slate-800 transition-colors"
              >
                <div className="flex items-center space-x-2.5">
                  <Cpu className="w-4 h-4 text-emerald-600" />
                  <span>Model Pipeline & Diagnostics</span>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400" />
              </Link>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <h3 className="text-base font-bold text-slate-900 mb-2">Early Support Status</h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Total Alerts Raised:</span>
                <span className="font-bold text-slate-800">{alerts.total}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Unreviewed Pending:</span>
                <span className="font-bold text-rose-600">{alerts.pending}</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-500">Resolved / Followed-up:</span>
                <span className="font-bold text-emerald-600">{alerts.reviewed}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;

