import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axiosClient from '../../api/axiosClient';
import { useToast } from '../../context/ToastContext';
import { User, Sparkles, Clock, CheckCircle2, ChevronLeft, Layers, AlertCircle } from 'lucide-react';

const InstructorStudentDetail = () => {
  const toast = useToast();
  const { studentId } = useParams();
  const [student, setStudent] = useState(null);
  const [results, setResults] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);

  // Prediction trigger on topic
  const [selectedTopicId, setSelectedTopicId] = useState('');
  const [predicting, setPredicting] = useState(false);

  useEffect(() => {
    fetchStudentProfile();
  }, [studentId]);

  const fetchStudentProfile = async () => {
    setLoading(true);
    try {
      const [studRes, resRes, predRes, recRes, subsRes] = await Promise.all([
        axiosClient.get('/users/students'),
        axiosClient.get(`/assessments/student/${studentId}`),
        axiosClient.get(`/predictions/student/${studentId}`),
        axiosClient.get(`/recommendations/student/${studentId}`),
        axiosClient.get('/subjects'),
      ]);

      const found = (studRes.data.students || []).find((s) => s.id === parseInt(studentId));
      setStudent(found);
      setResults(resRes.data.results || []);
      setPredictions(predRes.data.predictions || []);
      setRecommendations(recRes.data.recommendations || []);
      setSubjects(subsRes.data.subjects || []);
    } catch (err) {
      console.error('Failed to load student details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunPredict = async () => {
    if (!selectedTopicId) return;
    setPredicting(true);
    try {
      await axiosClient.post('/predictions/predict', {
        student_id: parseInt(studentId),
        topic_id: parseInt(selectedTopicId),
      });
      toast.success('Prediction generated successfully!');
      fetchStudentProfile();
    } catch (err) {
      if (err.response?.status === 422) {
        toast.warning(err.response?.data?.error || 'Student has insufficient assessment data in this topic.');
      } else {
        toast.error(err.response?.data?.error || 'Failed to generate prediction');
      }
    } finally {
      setPredicting(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading student records...</div>;
  }

  if (!student) {
    return <div className="p-8 text-center text-slate-500">Student not found.</div>;
  }

  const avgScore = results.length > 0
    ? Math.round(results.reduce((a, b) => a + b.percentage, 0) / results.length)
    : 0;

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      <Link to="/instructor/dashboard" className="text-xs font-semibold text-indigo-600 hover:underline flex items-center">
        <ChevronLeft className="w-4 h-4 mr-0.5" /> Back to Dashboard
      </Link>

      {/* Profile banner */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
        <div className="flex items-center space-x-4">
          <div className="h-14 w-14 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-xl">
            {student.full_name.charAt(0)}
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">{student.full_name}</h1>
            <p className="text-xs text-slate-500 font-mono">@{student.username} • {student.email}</p>
          </div>
        </div>

        <div className="flex space-x-6 text-xs text-slate-600 border-t md:border-t-0 pt-3 md:pt-0 w-full md:w-auto">
          <div>
            <p className="text-slate-400 uppercase font-semibold">Average Grade</p>
            <p className="text-lg font-bold text-slate-900">{avgScore}%</p>
          </div>
          <div>
            <p className="text-slate-400 uppercase font-semibold">Submissions</p>
            <p className="text-lg font-bold text-slate-900">{results.length}</p>
          </div>
          <div>
            <p className="text-slate-400 uppercase font-semibold">Predictions</p>
            <p className="text-lg font-bold text-slate-900">{predictions.length}</p>
          </div>
        </div>
      </div>

      {/* Manual Predict Trigger */}
      <div className="bg-indigo-50/60 rounded-2xl border border-indigo-100 p-5 flex flex-col sm:flex-row items-center justify-between space-y-3 sm:space-y-0">
        <div className="flex items-center space-x-2.5">
          <Sparkles className="w-5 h-5 text-indigo-600 shrink-0" />
          <div>
            <h3 className="text-sm font-bold text-indigo-950">Run Targeted AI Difficulty Evaluation</h3>
            <p className="text-xs text-indigo-700">Evaluate student's projected difficulty for a specific topic</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <select
            value={selectedTopicId}
            onChange={(e) => setSelectedTopicId(e.target.value)}
            className="px-3 py-2 rounded-xl border border-indigo-200 text-xs bg-white focus:outline-none w-full sm:w-64"
          >
            <option value="">Select Curriculum Topic...</option>
            {subjects.map((sub) => (
              <optgroup key={sub.id} label={sub.name}>
                {sub.topics?.map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </optgroup>
            ))}
          </select>
          <button
            onClick={handleRunPredict}
            disabled={!selectedTopicId || predicting}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-xl shadow-xs transition-colors disabled:opacity-50 whitespace-nowrap"
          >
            {predicting ? 'Evaluating...' : 'Evaluate'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Assessment Marks */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <h3 className="text-base font-bold text-slate-900 mb-4">Academic Results Log</h3>
          {results.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No assessment submissions logged.</p>
          ) : (
            <div className="space-y-3">
              {results.map((r) => (
                <div key={r.id} className="p-3.5 rounded-xl border border-slate-100 bg-slate-50/50 flex justify-between items-center text-xs">
                  <div>
                    <p className="font-bold text-slate-900">{r.assessment_title}</p>
                    <p className="text-slate-500 mt-0.5">{r.subject_name} • {r.topic_name}</p>
                  </div>
                  <div className="text-right">
                    <span className={`font-bold ${r.percentage >= 70 ? 'text-emerald-600' : r.percentage >= 50 ? 'text-amber-600' : 'text-rose-600'}`}>
                      {r.percentage}% ({r.marks_obtained}/{r.max_marks})
                    </span>
                    <p className="text-[10px] text-slate-400">{r.study_time_minutes} min study</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Prediction Records */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <h3 className="text-base font-bold text-slate-900 mb-4">AI Difficulty Predictions</h3>
          {predictions.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No AI predictions generated yet.</p>
          ) : (
            <div className="space-y-3">
              {predictions.map((p) => (
                <div key={p.id} className="p-3.5 rounded-xl border border-slate-100 bg-slate-50/50 flex justify-between items-center text-xs">
                  <div>
                    <p className="font-bold text-slate-900">{p.topic_name}</p>
                    <p className="text-slate-500 mt-0.5">{p.subject_name} • Model {p.model_version}</p>
                  </div>
                  <div className="text-right">
                    <span
                      className={`px-2.5 py-0.5 rounded-full font-semibold text-[10px] ${
                        p.predicted_difficulty === 'High'
                          ? 'bg-rose-100 text-rose-700'
                          : p.predicted_difficulty === 'Moderate'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-emerald-100 text-emerald-700'
                      }`}
                    >
                      {p.predicted_difficulty} Risk
                    </span>
                    <p className="text-[10px] text-slate-400 mt-0.5">Severity: {Math.round(p.difficulty_score * 100)}%</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InstructorStudentDetail;

