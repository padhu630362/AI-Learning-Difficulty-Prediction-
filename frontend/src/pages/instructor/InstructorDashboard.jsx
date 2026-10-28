import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axiosClient from '../../api/axiosClient';
import StatCard from '../../components/StatCard';
import { CardSkeleton } from '../../components/LoadingSkeleton';
import { useToast } from '../../context/ToastContext';
import {
  Users,
  BookOpen,
  AlertTriangle,
  ClipboardCheck,
  ChevronRight,
  ShieldAlert,
  ArrowRight,
  Sparkles,
  RefreshCw
} from 'lucide-react';

const InstructorDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [students, setStudents] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [scanning, setScanning] = useState(false);

  useEffect(() => {
    fetchInstructorData();
  }, []);

  const fetchInstructorData = async () => {
    setLoading(true);
    try {
      const [studentsRes, subjectsRes, alertsRes] = await Promise.all([
        axiosClient.get('/users/students'),
        axiosClient.get('/subjects?only_mine=true'),
        axiosClient.get('/alerts?is_reviewed=false'),
      ]);

      setStudents(studentsRes.data.students || []);
      setSubjects(subjectsRes.data.subjects || []);
      setAlerts(alertsRes.data.alerts || []);
    } catch (err) {
      console.error('Failed to load instructor dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAlertScan = async () => {
    if (subjects.length === 0) return;
    setScanning(true);
    try {
      let count = 0;
      for (const sub of subjects) {
        const res = await axiosClient.post('/alerts/scan', { subject_id: sub.id });
        count += res.data.new_alerts_count || 0;
      }
      toast.success(`Early support scan completed! ${count} new alerts generated.`);
      fetchInstructorData();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Scan failed.');
    } finally {
      setScanning(false);
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

  const criticalAlertsCount = alerts.filter((a) => a.severity === 'critical' || a.severity === 'high').length;

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-8">
      {/* Header with trigger button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Instructor Command Center</h1>
          <p className="text-sm text-slate-500 mt-1">
            Student cohort monitoring, curriculum management, and machine learning difficulty forecasting.
          </p>
        </div>

        <button
          onClick={handleRunAlertScan}
          disabled={scanning}
          className="inline-flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2.5 rounded-xl font-semibold text-xs shadow-xs transition-colors disabled:opacity-50 shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${scanning ? 'animate-spin' : ''}`} />
          <span>{scanning ? 'Scanning Cohort...' : 'Scan Early Support Alerts'}</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Active Students"
          value={students.length}
          subtitle="Enrolled in class cohorts"
          icon={Users}
          color="indigo"
        />
        <StatCard
          title="Managed Subjects"
          value={subjects.length}
          subtitle="Active curriculum modules"
          icon={BookOpen}
          color="blue"
        />
        <StatCard
          title="Pending Support Alerts"
          value={alerts.length}
          subtitle={`${criticalAlertsCount} high / critical priority`}
          icon={AlertTriangle}
          color={alerts.length > 0 ? 'rose' : 'emerald'}
        />
        <StatCard
          title="Early Interventions"
          value={alerts.filter(a => a.follow_ups_count > 0).length}
          subtitle="Support actions logged"
          icon={ClipboardCheck}
          color="amber"
        />
      </div>

      {/* 2-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Authorized Students Table (2 cols) */}
        <div className="lg:col-span-2 space-y-8">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="text-base font-bold text-slate-900">Enrolled Student Cohort</h2>
                <p className="text-xs text-slate-500">Click a student to view their performance analysis</p>
              </div>
              <span className="text-xs font-semibold text-slate-400">{students.length} Total</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    <th className="pb-3">Student Name</th>
                    <th className="pb-3">Username</th>
                    <th className="pb-3">Email</th>
                    <th className="pb-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {students.map((student) => (
                    <tr key={student.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="py-3.5 font-semibold text-slate-800 flex items-center space-x-3">
                        <div className="h-8 w-8 rounded-full bg-indigo-50 text-indigo-700 font-bold text-xs flex items-center justify-center border border-indigo-100">
                          {student.full_name.charAt(0)}
                        </div>
                        <span>{student.full_name}</span>
                      </td>
                      <td className="py-3.5 text-xs text-slate-500 font-mono">@{student.username}</td>
                      <td className="py-3.5 text-xs text-slate-500">{student.email}</td>
                      <td className="py-3.5 text-right">
                        <Link
                          to={`/instructor/students/${student.id}`}
                          className="inline-flex items-center text-xs font-semibold text-indigo-600 hover:text-indigo-800 hover:underline"
                        >
                          <span>Full Profile</span>
                          <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Subjects Overview */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-bold text-slate-900">Your Assigned Subjects</h2>
              <Link to="/instructor/subjects" className="text-xs font-semibold text-indigo-600 hover:underline">
                Manage Topics
              </Link>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {subjects.map((sub) => (
                <div key={sub.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
                  <span className="text-xs font-bold text-indigo-600 bg-white border border-indigo-100 px-2 py-0.5 rounded">
                    {sub.code}
                  </span>
                  <h3 className="font-bold text-slate-900 text-sm mt-2">{sub.name}</h3>
                  <p className="text-xs text-slate-500 mt-1 line-clamp-2">{sub.description}</p>
                  <div className="mt-3 pt-2 border-t border-slate-200/60 flex items-center justify-between text-xs text-slate-500">
                    <span>{sub.topic_count} Topics</span>
                    <Link to="/instructor/assessments" className="text-indigo-600 font-semibold hover:underline">
                      Assessments →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Early Support Alerts (1 col) */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-rose-500" />
                <h2 className="text-base font-bold text-slate-900">Unreviewed Early Alerts</h2>
              </div>
              <Link to="/instructor/alerts" className="text-xs font-semibold text-indigo-600 hover:underline">
                All Alerts
              </Link>
            </div>

            {alerts.length === 0 ? (
              <div className="p-6 text-center bg-emerald-50 rounded-xl border border-emerald-100">
                <Sparkles className="w-6 h-6 text-emerald-600 mx-auto mb-1" />
                <p className="text-xs font-bold text-emerald-900">No Pending Alerts</p>
                <p className="text-[11px] text-emerald-700 mt-0.5">
                  All early support warnings have been reviewed or no current student risk detected.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {alerts.slice(0, 5).map((a) => (
                  <div
                    key={a.id}
                    className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors"
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-semibold text-xs text-slate-900">{a.student_name}</span>
                      <span
                        className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${
                          a.severity === 'critical' || a.severity === 'high'
                            ? 'bg-rose-100 text-rose-700'
                            : 'bg-amber-100 text-amber-700'
                        }`}
                      >
                        {a.severity}
                      </span>
                    </div>
                    <p className="text-xs font-semibold text-slate-800">{a.title}</p>
                    <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-2">{a.description}</p>
                    <div className="mt-3 pt-2 border-t border-slate-200/60 flex justify-between items-center text-xs">
                      <span className="text-[10px] text-slate-400">{new Date(a.created_at).toLocaleDateString()}</span>
                      <Link
                        to="/instructor/alerts"
                        className="text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                      >
                        Review & Follow-up →
                      </Link>
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

export default InstructorDashboard;

