import React, { useState, useEffect } from 'react';
import axiosClient from '../../api/axiosClient';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { Cpu, RefreshCw, CheckCircle2, Award, Zap, Layers, AlertCircle, Sparkles } from 'lucide-react';
import { useToast } from '../../context/ToastContext';
import ConfirmDialog from '../../components/ConfirmDialog';

const AdminModelEvaluation = () => {
  const toast = useToast();
  const [activeModel, setActiveModel] = useState(null);
  const [candidateComparison, setCandidateComparison] = useState(null);
  const [modelHistory, setModelHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [isTrainConfirmOpen, setIsTrainConfirmOpen] = useState(false);

  useEffect(() => {
    fetchModelData();
  }, []);

  const fetchModelData = async () => {
    setLoading(true);
    try {
      const [activeRes, histRes] = await Promise.all([
        axiosClient.get('/models/active'),
        axiosClient.get('/models/history'),
      ]);
      setActiveModel(activeRes.data.active_model);
      setCandidateComparison(activeRes.data.candidate_comparison || null);
      setModelHistory(histRes.data.models || []);
    } catch (err) {
      console.error('Failed to load model diagnostics:', err);
    } finally {
      setLoading(false);
    }
  };

  const executeTrainBaseline = async () => {
    setIsTrainConfirmOpen(false);
    setTraining(true);
    try {
      const res = await axiosClient.post('/models/train-default');
      toast.success(`Candidate models evaluated! Winner algorithm: ${res.data.model.algorithm}`);
      fetchModelData();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Training failed');
    } finally {
      setTraining(false);
    }
  };

  const handleActivateModel = async (modelId) => {
    try {
      await axiosClient.put(`/models/${modelId}/activate`);
      toast.success('Model activated and weights loaded in memory!');
      fetchModelData();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Activation failed');
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading model evaluation analytics...</div>;
  }

  // Feature importances formatting
  const featureData = activeModel?.feature_importances
    ? Object.entries(activeModel.feature_importances).map(([name, val]) => ({
        name: name.replace(/_/g, ' '),
        importance: Math.round(val * 1000) / 10,
      })).slice(0, 8)
    : [];

  const cm = activeModel?.confusion_matrix;
  const cr = activeModel?.classification_report;

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Machine Learning Model Diagnostics</h1>
          <p className="text-sm text-slate-500 mt-1">
            Real evaluation metrics on held-out test data, cross-validation, and confusion matrices.
          </p>
        </div>

        <button
          onClick={() => setIsTrainConfirmOpen(true)}
          disabled={training}
          className="inline-flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2.5 rounded-xl font-semibold text-xs shadow-xs transition-colors disabled:opacity-50 shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${training ? 'animate-spin' : ''}`} />
          <span>{training ? 'Training Candidate Models...' : 'Retrain Pipeline'}</span>
        </button>
      </div>

      {activeModel ? (
        <>
          {/* Active Model Header & KPI Cards */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-2 sm:space-y-0">
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h2 className="text-lg font-bold text-slate-900">{activeModel.model_name}</h2>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                      Active In Production
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 font-mono mt-0.5">Tag: {activeModel.version_tag}</p>
                </div>
              </div>

              <div className="text-xs text-slate-500 text-left sm:text-right">
                <p>Trained with {activeModel.training_sample_count} samples</p>
                <p className="text-slate-400 mt-0.5">{new Date(activeModel.created_at).toLocaleString()}</p>
              </div>
            </div>

            {/* Metric Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-3 border-t border-slate-100">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Test Accuracy</p>
                <p className="text-2xl font-bold text-slate-900 mt-1">{(activeModel.accuracy * 100).toFixed(1)}%</p>
              </div>

              <div className="p-4 rounded-xl bg-indigo-50 border border-indigo-100 text-center">
                <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wider">F1-Score (Macro)</p>
                <p className="text-2xl font-bold text-indigo-700 mt-1">{(activeModel.f1_macro * 100).toFixed(1)}%</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Precision (Macro)</p>
                <p className="text-2xl font-bold text-slate-900 mt-1">{(activeModel.precision_macro * 100).toFixed(1)}%</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Recall (Macro)</p>
                <p className="text-2xl font-bold text-slate-900 mt-1">{(activeModel.recall_macro * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>

          {/* Candidate Models Benchmark Comparison */}
          {candidateComparison && Object.keys(candidateComparison).length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
              <div className="flex items-center space-x-2">
                <Award className="w-5 h-5 text-indigo-600" />
                <h3 className="text-base font-bold text-slate-900">Candidate Algorithms Benchmark (5-Fold Stratified CV)</h3>
              </div>
              <p className="text-xs text-slate-500">
                Evaluation results across candidate models evaluated on identical cross-validation splits. The model with the highest cross-validation Macro F1 is automatically selected for production inference.
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-400 font-semibold uppercase">
                      <th className="py-2.5">Algorithm</th>
                      <th className="py-2.5">5-Fold CV F1</th>
                      <th className="py-2.5">Test Accuracy</th>
                      <th className="py-2.5">Macro F1</th>
                      <th className="py-2.5">High-Risk Recall</th>
                      <th className="py-2.5">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {Object.entries(candidateComparison).map(([algoName, metrics]) => {
                      const isWinner = algoName === activeModel.algorithm;
                      return (
                        <tr key={algoName} className={isWinner ? 'bg-indigo-50/50 font-semibold' : ''}>
                          <td className="py-3 font-medium text-slate-800 flex items-center space-x-1.5">
                            <span>{algoName}</span>
                            {isWinner && <span className="text-[10px] bg-indigo-100 text-indigo-800 px-1.5 py-0.5 rounded font-bold">Selected</span>}
                          </td>
                          <td className="py-3 font-mono">{metrics.cv_mean_f1 ? `${(metrics.cv_mean_f1 * 100).toFixed(1)}% ± ${(metrics.cv_std_f1 * 100).toFixed(1)}%` : 'N/A'}</td>
                          <td className="py-3 font-mono">{(metrics.accuracy * 100).toFixed(1)}%</td>
                          <td className="py-3 font-mono text-indigo-600 font-bold">{(metrics.f1_macro * 100).toFixed(1)}%</td>
                          <td className="py-3 font-mono">{metrics.high_difficulty_recall ? `${(metrics.high_difficulty_recall * 100).toFixed(1)}%` : 'N/A'}</td>
                          <td className="py-3">
                            {isWinner ? (
                              <span className="inline-flex items-center text-emerald-600 font-medium">
                                <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Active
                              </span>
                            ) : (
                              <span className="text-slate-400">Candidate</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Deep Diagnostics: Confusion Matrix & Classification Report */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Visual Confusion Matrix */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
              <h3 className="text-base font-bold text-slate-900 mb-1">Confusion Matrix (Held-out Test Set)</h3>
              <p className="text-xs text-slate-500 mb-6">True labels (rows) vs. Model Predicted labels (columns)</p>

              {cm && cm.matrix ? (
                <div className="space-y-4">
                  <div className="flex justify-center">
                    <div className="inline-block">
                      <div className="grid grid-cols-4 gap-2 text-center text-xs font-semibold text-slate-600 mb-2">
                        <div></div>
                        <div>Pred Low</div>
                        <div>Pred Mod</div>
                        <div>Pred High</div>
                      </div>

                      {cm.labels.map((rowLabel, rowIdx) => (
                        <div key={rowIdx} className="grid grid-cols-4 gap-2 items-center mb-2">
                          <div className="text-xs font-semibold text-slate-700 text-right pr-2">
                            True {rowLabel}
                          </div>
                          {cm.matrix[rowIdx].map((val, colIdx) => {
                            const isDiagonal = rowIdx === colIdx;
                            return (
                              <div
                                key={colIdx}
                                className={`w-16 h-12 flex items-center justify-center rounded-xl text-sm font-bold border transition-colors ${
                                  isDiagonal
                                    ? 'bg-emerald-100 text-emerald-900 border-emerald-300'
                                    : val > 0
                                    ? 'bg-rose-50 text-rose-800 border-rose-200'
                                    : 'bg-slate-50 text-slate-400 border-slate-200'
                                }`}
                              >
                                {val}
                              </div>
                            );
                          })}
                        </div>
                      ))}
                    </div>
                  </div>
                  <p className="text-[11px] text-slate-400 text-center">
                    Green cells represent correct classifications along the principal diagonal.
                  </p>
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">Confusion matrix not available.</p>
              )}
            </div>

            {/* Classification Report Table */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
              <h3 className="text-base font-bold text-slate-900 mb-1">Classification Report</h3>
              <p className="text-xs text-slate-500 mb-4">Precision, recall, and F1-score breakdown per class</p>

              {cr ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead>
                      <tr className="border-b border-slate-200 text-slate-500 uppercase tracking-wider">
                        <th className="pb-2">Class</th>
                        <th className="pb-2">Precision</th>
                        <th className="pb-2">Recall</th>
                        <th className="pb-2">F1-Score</th>
                        <th className="pb-2">Support</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {['Low', 'Moderate', 'High'].map((cls) => {
                        const item = cr[cls] || {};
                        return (
                          <tr key={cls}>
                            <td className="py-2.5 font-bold font-sans text-slate-900">{cls}</td>
                            <td className="py-2.5">{(item.precision * 100 || 0).toFixed(1)}%</td>
                            <td className="py-2.5">{(item.recall * 100 || 0).toFixed(1)}%</td>
                            <td className="py-2.5 font-bold text-indigo-600">{(item['f1-score'] * 100 || 0).toFixed(1)}%</td>
                            <td className="py-2.5">{item.support || 0}</td>
                          </tr>
                        );
                      })}
                      <tr className="bg-slate-50 font-bold border-t border-slate-200 text-slate-900">
                        <td className="py-2.5 font-sans">Macro Avg</td>
                        <td className="py-2.5">{(cr['macro avg']?.precision * 100 || 0).toFixed(1)}%</td>
                        <td className="py-2.5">{(cr['macro avg']?.recall * 100 || 0).toFixed(1)}%</td>
                        <td className="py-2.5 text-indigo-600">{(cr['macro avg']?.['f1-score'] * 100 || 0).toFixed(1)}%</td>
                        <td className="py-2.5">{cr['macro avg']?.support || 0}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">Classification report not available.</p>
              )}
            </div>
          </div>

          {/* Feature Importances */}
          {featureData.length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
              <h3 className="text-base font-bold text-slate-900 mb-1">Feature Importances (Model Sensitivity)</h3>
              <p className="text-xs text-slate-500 mb-6">Relative weight of educational features in predicting difficulty</p>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={featureData}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                    <XAxis type="number" tick={{ fontSize: 10, fill: '#64748b' }} unit="%" />
                    <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: '#475569' }} />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const d = payload[0].payload;
                          return (
                            <div className="bg-slate-900 text-white text-xs p-2.5 rounded-xl shadow-lg">
                              <p className="font-bold">{d.name}</p>
                              <p className="text-indigo-300 font-bold mt-1">Weight: {d.importance}%</p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Bar dataKey="importance" fill="#4f46e5" radius={[0, 6, 6, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
          <Cpu className="w-10 h-10 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No Model Trained Yet</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Click 'Retrain Pipeline' to run an automated multi-model training benchmark.
          </p>
        </div>
      )}

      {/* Version History Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <h3 className="text-base font-bold text-slate-900 mb-4">Model Version History & Comparison</h3>

        {modelHistory.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No model versions saved yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  <th className="pb-3">Version Tag</th>
                  <th className="pb-3">Algorithm</th>
                  <th className="pb-3">Accuracy</th>
                  <th className="pb-3">F1-Macro</th>
                  <th className="pb-3">Precision</th>
                  <th className="pb-3">Recall</th>
                  <th className="pb-3">Trained Date</th>
                  <th className="pb-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700 text-xs">
                {modelHistory.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-50/60">
                    <td className="py-3 font-semibold text-slate-900 flex items-center space-x-1.5">
                      <span>{m.version_tag}</span>
                      {m.is_active && (
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
                          Active
                        </span>
                      )}
                    </td>
                    <td className="py-3 font-mono">{m.algorithm}</td>
                    <td className="py-3 font-mono font-bold">{(m.accuracy * 100).toFixed(1)}%</td>
                    <td className="py-3 font-mono font-bold text-indigo-600">{(m.f1_macro * 100).toFixed(1)}%</td>
                    <td className="py-3 font-mono">{(m.precision_macro * 100).toFixed(1)}%</td>
                    <td className="py-3 font-mono">{(m.recall_macro * 100).toFixed(1)}%</td>
                    <td className="py-3 text-slate-500">{new Date(m.created_at).toLocaleDateString()}</td>
                    <td className="py-3 text-right">
                      {!m.is_active ? (
                        <button
                          onClick={() => handleActivateModel(m.id)}
                          className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg transition-colors"
                        >
                          Activate
                        </button>
                      ) : (
                        <span className="text-emerald-600 font-semibold">Active</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Retrain Pipeline Confirmation Dialog */}
      <ConfirmDialog
        isOpen={isTrainConfirmOpen}
        title="Retrain Candidate Models"
        message="Run the complete training pipeline across candidate models (Random Forest, Logistic Regression, Decision Tree) with 5-fold cross-validation on synthetic student interaction records? The winning model will be dynamically activated in memory."
        confirmText="Start Training"
        cancelText="Cancel"
        variant="primary"
        isLoading={training}
        onConfirm={executeTrainBaseline}
        onCancel={() => setIsTrainConfirmOpen(false)}
      />
    </div>
  );
};

export default AdminModelEvaluation;

