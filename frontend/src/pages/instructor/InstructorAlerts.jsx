import React, { useState, useEffect } from 'react';
import axiosClient from '../../api/axiosClient';
import Modal from '../../components/Modal';
import { useToast } from '../../context/ToastContext';
import { AlertTriangle, CheckCircle2, MessageSquare, Plus, Clock, ShieldAlert, Sparkles } from 'lucide-react';

const InstructorAlerts = () => {
  const toast = useToast();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isReviewedFilter, setIsReviewedFilter] = useState('false'); // 'false', 'true', 'all'
  const [severityFilter, setSeverityFilter] = useState('');

  // Follow-up modal
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [isFollowUpModalOpen, setIsFollowUpModalOpen] = useState(false);
  const [followUpForm, setFollowUpForm] = useState({
    action_taken: '1-on-1 Mentoring Session',
    notes: '',
    outcome: 'pending',
  });

  useEffect(() => {
    fetchAlerts();
  }, [isReviewedFilter, severityFilter]);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      let endpoint = '/alerts';
      const params = [];
      if (isReviewedFilter !== 'all') {
        params.push(`is_reviewed=${isReviewedFilter}`);
      }
      if (severityFilter) {
        params.push(`severity=${severityFilter}`);
      }
      if (params.length > 0) {
        endpoint += '?' + params.join('&');
      }

      const res = await axiosClient.get(endpoint);
      setAlerts(res.data.alerts || []);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkReviewed = async (alertId) => {
    try {
      await axiosClient.put(`/alerts/${alertId}/review`);
      toast.success('Alert marked as reviewed');
      fetchAlerts();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to update alert');
    }
  };

  const handleSaveFollowUp = async (e) => {
    e.preventDefault();
    if (!selectedAlert) return;
    try {
      await axiosClient.post(`/alerts/${selectedAlert.id}/follow-ups`, followUpForm);
      setIsFollowUpModalOpen(false);
      setFollowUpForm({
        action_taken: '1-on-1 Mentoring Session',
        notes: '',
        outcome: 'pending',
      });
      toast.success('Support follow-up logged successfully!');
      fetchAlerts();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to save follow-up');
    }
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return 'bg-rose-100 text-rose-700 border-rose-200';
      case 'medium':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      default:
        return 'bg-blue-100 text-blue-700 border-blue-200';
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Early Support Alerts</h1>
          <p className="text-sm text-slate-500 mt-1">
            Automated alerts for students experiencing learning friction, repeated errors, or sharp performance drops.
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-2">
          <select
            value={isReviewedFilter}
            onChange={(e) => setIsReviewedFilter(e.target.value)}
            className="px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold bg-white text-slate-700 focus:outline-none"
          >
            <option value="false">Unreviewed (Pending)</option>
            <option value="true">Reviewed & Resolved</option>
            <option value="all">All Alerts</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold bg-white text-slate-700 focus:outline-none"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
          </select>
        </div>
      </div>

      {alerts.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
          <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900">No alerts found</h3>
          <p className="text-xs text-slate-400 mt-1">
            There are no student alerts matching your selected status filter.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((a) => (
            <div
              key={a.id}
              className={`rounded-2xl border p-5 shadow-xs transition-all ${
                a.is_reviewed ? 'bg-slate-50/70 border-slate-200' : 'bg-white border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-100 space-y-2 sm:space-y-0">
                <div className="flex items-center space-x-3">
                  <div className="h-9 w-9 rounded-xl bg-slate-100 flex items-center justify-center text-slate-700 font-bold text-xs">
                    {a.student_name ? a.student_name.charAt(0) : 'S'}
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">{a.student_name}</h3>
                    <p className="text-xs text-slate-500">{a.subject_name} {a.topic_name ? `• ${a.topic_name}` : ''}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${getSeverityBadge(a.severity)}`}>
                    {a.severity}
                  </span>
                  {a.is_reviewed ? (
                    <span className="text-emerald-700 bg-emerald-50 text-[11px] font-semibold px-2 py-0.5 rounded-md flex items-center space-x-1">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Reviewed</span>
                    </span>
                  ) : (
                    <span className="text-rose-700 bg-rose-50 text-[11px] font-semibold px-2 py-0.5 rounded-md flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>Action Required</span>
                    </span>
                  )}
                </div>
              </div>

              <div className="py-3">
                <p className="text-sm font-bold text-slate-800">{a.title}</p>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">{a.description}</p>
              </div>

              {/* Follow-ups log */}
              {a.follow_ups && a.follow_ups.length > 0 && (
                <div className="mt-2 mb-3 p-3 bg-slate-50 rounded-xl border border-slate-100 space-y-2">
                  <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                    Logged Support Follow-ups ({a.follow_ups.length})
                  </p>
                  {a.follow_ups.map((f, idx) => (
                    <div key={idx} className="text-xs text-slate-700 flex justify-between items-start">
                      <div>
                        <span className="font-semibold text-slate-900">• {f.action_taken}:</span>{' '}
                        <span>{f.notes}</span>
                      </div>
                      <span className="text-[10px] text-slate-500 uppercase font-mono ml-2">
                        {f.outcome}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="text-[11px] text-slate-400">
                  Triggered on: {new Date(a.created_at).toLocaleDateString()}
                </span>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => {
                      setSelectedAlert(a);
                      setIsFollowUpModalOpen(true);
                    }}
                    className="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold rounded-lg border border-indigo-200 flex items-center space-x-1 transition-colors"
                  >
                    <Plus className="w-3 h-3" />
                    <span>Log Follow-Up Action</span>
                  </button>

                  {!a.is_reviewed && (
                    <button
                      onClick={() => handleMarkReviewed(a.id)}
                      className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg transition-colors"
                    >
                      Mark Reviewed
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Follow-up modal */}
      <Modal
        isOpen={isFollowUpModalOpen}
        onClose={() => setIsFollowUpModalOpen(false)}
        title={`Log Academic Support Follow-Up: ${selectedAlert?.student_name}`}
      >
        <form onSubmit={handleSaveFollowUp} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Action Taken
            </label>
            <select
              value={followUpForm.action_taken}
              onChange={(e) => setFollowUpForm({ ...followUpForm, action_taken: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
            >
              <option value="1-on-1 Mentoring Session">1-on-1 Mentoring Session</option>
              <option value="Custom Practice Worksheet Assigned">Custom Practice Worksheet Assigned</option>
              <option value="Office Hours Concept Walkthrough">Office Hours Concept Walkthrough</option>
              <option value="Peer Tutoring Assistance Arranged">Peer Tutoring Assistance Arranged</option>
              <option value="Quiz Retake & Formative Feedback">Quiz Retake & Formative Feedback</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Follow-Up Notes & Observations
            </label>
            <textarea
              value={followUpForm.notes}
              onChange={(e) => setFollowUpForm({ ...followUpForm, notes: e.target.value })}
              placeholder="e.g. Worked through binary tree pointer manipulations. Student expressed clearer understanding."
              rows={3}
              required
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Observed Outcome
            </label>
            <select
              value={followUpForm.outcome}
              onChange={(e) => setFollowUpForm({ ...followUpForm, outcome: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
            >
              <option value="improved">Improved / Concept Mastered</option>
              <option value="pending">Pending Follow-up Assessment</option>
              <option value="stable">Stable / Continuing Support</option>
              <option value="escalated">Escalated to Academic Advisor</option>
            </select>
          </div>

          <div className="flex justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={() => setIsFollowUpModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700"
            >
              Save & Mark Alert Reviewed
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default InstructorAlerts;

