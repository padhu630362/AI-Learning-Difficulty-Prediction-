import React, { useState, useEffect } from 'react';
import axiosClient from '../../api/axiosClient';
import Modal from '../../components/Modal';
import { useToast } from '../../context/ToastContext';
import { BookOpen, Sparkles, AlertTriangle, CheckCircle2, ChevronRight, Layers, FileText } from 'lucide-react';

const StudentSubjects = () => {
  const toast = useToast();
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [predictingTopicId, setPredictingTopicId] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    setLoading(true);
    try {
      const res = await axiosClient.get('/subjects');
      const data = res.data.subjects || [];
      setSubjects(data);
      if (data.length > 0) {
        selectSubject(data[0].id);
      }
    } catch (err) {
      console.error('Error fetching subjects:', err);
    } finally {
      setLoading(false);
    }
  };

  const selectSubject = async (subjectId) => {
    try {
      const res = await axiosClient.get(`/subjects/${subjectId}`);
      setSelectedSubject(res.data.subject);
      setTopics(res.data.subject.topics || []);
    } catch (err) {
      console.error('Error fetching subject details:', err);
    }
  };

  const handleRunPrediction = async (topicId) => {
    setPredictingTopicId(topicId);
    try {
      const res = await axiosClient.post('/predictions/predict', { topic_id: topicId });
      setPredictionResult(res.data.prediction);
      setIsModalOpen(true);
      toast.success('AI difficulty evaluation generated!');
    } catch (err) {
      if (err.response?.status === 422) {
        toast.warning(err.response?.data?.error || 'Insufficient assessment data recorded for this topic yet.');
      } else {
        toast.error(err.response?.data?.error || 'Failed to generate prediction. Check if ML model is trained.');
      }
    } finally {
      setPredictingTopicId(null);
    }
  };

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

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Curriculum & Topics</h1>
        <p className="text-sm text-slate-500 mt-1">
          Explore syllabus modules and assess your real-time machine-learning difficulty rating.
        </p>
      </div>

      {/* Subject Tabs */}
      <div className="flex space-x-2 border-b border-slate-200 overflow-x-auto pb-2">
        {subjects.map((sub) => (
          <button
            key={sub.id}
            onClick={() => selectSubject(sub.id)}
            className={`px-4 py-2.5 rounded-xl text-sm font-semibold whitespace-nowrap transition-all flex items-center space-x-2 ${
              selectedSubject?.id === sub.id
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            <span className="font-mono text-xs opacity-80">{sub.code}:</span>
            <span>{sub.name}</span>
          </button>
        ))}
      </div>

      {selectedSubject && (
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-md">
                  {selectedSubject.code}
                </span>
                <h2 className="text-xl font-bold text-slate-900 mt-2">{selectedSubject.name}</h2>
                <p className="text-sm text-slate-600 mt-1 max-w-2xl">{selectedSubject.description}</p>
              </div>
              <div className="text-right text-xs text-slate-500">
                <p className="font-semibold text-slate-700">{selectedSubject.instructor_name || 'Department Faculty'}</p>
                <p className="mt-0.5">{topics.length} Syllabus Modules</p>
              </div>
            </div>
          </div>

          {/* Topics List */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-slate-800 flex items-center space-x-2">
              <Layers className="w-5 h-5 text-indigo-600" />
              <span>Syllabus Topics & Difficulty Forecast</span>
            </h3>

            <div className="grid grid-cols-1 gap-4">
              {topics.map((t, idx) => (
                <div
                  key={t.id}
                  className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:border-indigo-200 transition-all flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0"
                >
                  <div className="space-y-1.5 max-w-2xl">
                    <div className="flex items-center space-x-2">
                      <span className="h-6 w-6 rounded-full bg-slate-100 text-slate-600 font-bold text-xs flex items-center justify-center">
                        {idx + 1}
                      </span>
                      <h4 className="text-base font-bold text-slate-900">{t.name}</h4>
                      <span className="capitalize text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                        {t.difficulty_level}
                      </span>
                    </div>

                    <p className="text-xs text-slate-600">{t.description}</p>

                    {t.learning_objectives && (
                      <div className="text-xs text-slate-500 flex items-start space-x-1.5 mt-1">
                        <FileText className="w-3.5 h-3.5 mt-0.5 text-slate-400 shrink-0" />
                        <span>Objectives: {t.learning_objectives}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center space-x-3 shrink-0">
                    <button
                      onClick={() => handleRunPrediction(t.id)}
                      disabled={predictingTopicId === t.id}
                      className="px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-semibold rounded-xl border border-indigo-200 flex items-center space-x-1.5 transition-colors disabled:opacity-50"
                    >
                      <Sparkles className="w-4 h-4 text-indigo-600" />
                      <span>{predictingTopicId === t.id ? 'Running AI Model...' : 'Predict Difficulty'}</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Prediction Result Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="AI Difficulty Prediction Result"
        maxWidth="max-w-2xl"
      >
        {predictionResult && (
          <div className="space-y-6">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-500 uppercase font-semibold">Evaluated Topic</p>
                <h4 className="text-base font-bold text-slate-900">{predictionResult.topic_name}</h4>
                <p className="text-xs text-slate-500">{predictionResult.subject_name}</p>
              </div>

              <div className="text-right">
                <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getDifficultyBadge(predictionResult.predicted_difficulty)}`}>
                  {predictionResult.predicted_difficulty} Predicted Difficulty
                </span>
                <p className="text-xs text-slate-500 mt-1">
                  Severity Score: {Math.round(predictionResult.difficulty_score * 100)}%
                </p>
              </div>
            </div>

            {/* Model Probabilities Bar */}
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                Calibrated Class Probabilities
              </p>
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-100 text-center">
                  <p className="text-xs font-semibold text-emerald-800">Low</p>
                  <p className="text-lg font-bold text-emerald-700">
                    {Math.round(predictionResult.probability_low * 100)}%
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-amber-50 border border-amber-100 text-center">
                  <p className="text-xs font-semibold text-amber-800">Moderate</p>
                  <p className="text-lg font-bold text-amber-700">
                    {Math.round(predictionResult.probability_moderate * 100)}%
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-100 text-center">
                  <p className="text-xs font-semibold text-rose-800">High</p>
                  <p className="text-lg font-bold text-rose-700">
                    {Math.round(predictionResult.probability_high * 100)}%
                  </p>
                </div>
              </div>
            </div>

            {/* Contributing Factors */}
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                Why this was predicted (Contributing Factors)
              </p>
              <div className="space-y-2">
                {predictionResult.contributing_factors?.map((f, i) => (
                  <div key={i} className="p-3 rounded-xl border border-slate-200 bg-white text-xs flex items-start space-x-2">
                    <span className={`px-2 py-0.5 rounded font-semibold text-[10px] shrink-0 ${
                      f.impact === 'High Risk' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'
                    }`}>
                      {f.impact}
                    </span>
                    <span className="text-slate-700">{f.description}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            {predictionResult.recommendations && predictionResult.recommendations.length > 0 && (
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                  Generated Recommendations
                </p>
                <div className="space-y-2">
                  {predictionResult.recommendations.map((r, i) => (
                    <div key={i} className="p-3 rounded-xl bg-indigo-50 border border-indigo-100 text-xs">
                      <p className="font-semibold text-indigo-900">{r.suggested_action}</p>
                      <p className="text-indigo-700 mt-0.5">{r.reason}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="text-right pt-3 border-t border-slate-100">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700"
              >
                Close Window
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default StudentSubjects;

