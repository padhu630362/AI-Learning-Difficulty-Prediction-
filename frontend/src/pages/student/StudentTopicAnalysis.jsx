import React, { useState, useEffect } from 'react';
import axiosClient from '../../api/axiosClient';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { Sparkles, AlertCircle, Info, ExternalLink, ShieldAlert, CheckCircle } from 'lucide-react';

const StudentTopicAnalysis = () => {
  const [predictions, setPredictions] = useState([]);
  const [selectedPrediction, setSelectedPrediction] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    setLoading(true);
    try {
      const res = await axiosClient.get('/predictions/my-predictions');
      const data = res.data.predictions || [];
      setPredictions(data);
      if (data.length > 0) {
        setSelectedPrediction(data[0]);
      }
    } catch (err) {
      console.error('Failed to fetch predictions:', err);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (diff) => {
    if (diff === 'High') return '#f43f5e'; // rose-500
    if (diff === 'Moderate') return '#f59e0b'; // amber-500
    return '#10b981'; // emerald-500
  };

  const chartData = predictions.map((p) => ({
    name: p.topic_name ? (p.topic_name.length > 14 ? p.topic_name.substring(0, 14) + '...' : p.topic_name) : 'Topic',
    fullName: p.topic_name,
    difficultyScore: Math.round(p.difficulty_score * 100),
    category: p.predicted_difficulty,
    raw: p,
  }));

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Topic Difficulty & Knowledge Gaps Analysis
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Interpretable AI explanations highlighting potential concept misconceptions and risk factors.
        </p>
      </div>

      {predictions.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
          <Sparkles className="w-10 h-10 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-700">No predictions recorded yet</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Head to Curriculum & Topics to run a machine learning prediction on your study modules.
          </p>
        </div>
      ) : (
        <>
          {/* Chart Section */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <h2 className="text-base font-bold text-slate-900 mb-1">
              Topic-wise Predicted Difficulty Index (0 - 100%)
            </h2>
            <p className="text-xs text-slate-500 mb-6">
              Higher score indicates greater predicted learning friction. Click on a bar to inspect details.
            </p>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} interval={0} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748b' }} />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const d = payload[0].payload;
                        return (
                          <div className="bg-slate-900 text-white text-xs p-3 rounded-xl shadow-lg border border-slate-800">
                            <p className="font-bold">{d.fullName}</p>
                            <p className="text-slate-300 mt-0.5">
                              Severity Score: <span className="font-semibold text-white">{d.difficultyScore}%</span>
                            </p>
                            <p className="text-slate-300">
                              Difficulty: <span className="font-semibold text-white">{d.category}</span>
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar
                    dataKey="difficultyScore"
                    radius={[6, 6, 0, 0]}
                    onClick={(entry) => setSelectedPrediction(entry.raw)}
                    className="cursor-pointer"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getDifficultyColor(entry.category)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="flex items-center justify-center space-x-6 mt-4 pt-4 border-t border-slate-100 text-xs">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-emerald-500" />
                <span className="text-slate-600 font-medium">Low Difficulty (&lt; 28%)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-amber-500" />
                <span className="text-slate-600 font-medium">Moderate Difficulty (28 - 46%)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-rose-500" />
                <span className="text-slate-600 font-medium">High Difficulty (&gt; 46%)</span>
              </div>
            </div>
          </div>

          {/* Deep Dive Breakdown */}
          {selectedPrediction && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left 2 Cols: Contributing Factors */}
              <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 space-y-2 sm:space-y-0">
                  <div>
                    <span className="text-xs font-semibold text-indigo-600">{selectedPrediction.subject_name}</span>
                    <h3 className="text-xl font-bold text-slate-900 mt-0.5">{selectedPrediction.topic_name}</h3>
                    <p className="text-xs text-slate-400">
                      Evaluated on: {new Date(selectedPrediction.created_at).toLocaleDateString()} • Model: {selectedPrediction.model_version}
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1.5 rounded-full text-xs font-bold border inline-block ${
                      selectedPrediction.predicted_difficulty === 'High'
                        ? 'bg-rose-50 text-rose-700 border-rose-200'
                        : selectedPrediction.predicted_difficulty === 'Moderate'
                        ? 'bg-amber-50 text-amber-700 border-amber-200'
                        : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    }`}
                  >
                    {selectedPrediction.predicted_difficulty} Difficulty Level
                  </span>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-3">
                    Identified Contributing Performance Indicators
                  </h4>
                  <div className="space-y-3">
                    {selectedPrediction.contributing_factors?.map((f, i) => (
                      <div
                        key={i}
                        className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 flex items-start space-x-3"
                      >
                        {f.impact === 'High Risk' ? (
                          <ShieldAlert className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
                        ) : f.impact === 'Moderate Risk' ? (
                          <AlertCircle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                        ) : (
                          <CheckCircle className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                        )}
                        <div>
                          <p className="text-xs font-bold uppercase tracking-wider text-slate-700">
                            {f.feature.replace('_', ' ')} • <span className={f.impact === 'High Risk' ? 'text-rose-600' : 'text-amber-600'}>{f.impact}</span>
                          </p>
                          <p className="text-xs text-slate-600 mt-1">{f.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-indigo-50/60 border border-indigo-100 text-xs text-indigo-900 flex items-start space-x-2">
                  <Info className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                  <p>
                    <strong>Pedagogical Context:</strong> This prediction identifies statistical associations between formative quiz errors, repeated submissions, and difficulty outcomes to support your study planning. It is not an assessment of intrinsic intelligence or ability.
                  </p>
                </div>
              </div>

              {/* Right Col: Calibrated Probabilities & Actions */}
              <div className="space-y-6">
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
                  <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4">
                    Calibrated Outcome Probabilities
                  </h4>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-xs font-semibold mb-1">
                        <span className="text-emerald-700">Low Difficulty</span>
                        <span>{Math.round(selectedPrediction.probability_low * 100)}%</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2">
                        <div
                          className="bg-emerald-500 h-2 rounded-full"
                          style={{ width: `${Math.round(selectedPrediction.probability_low * 100)}%` }}
                        />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs font-semibold mb-1">
                        <span className="text-amber-700">Moderate Difficulty</span>
                        <span>{Math.round(selectedPrediction.probability_moderate * 100)}%</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2">
                        <div
                          className="bg-amber-500 h-2 rounded-full"
                          style={{ width: `${Math.round(selectedPrediction.probability_moderate * 100)}%` }}
                        />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs font-semibold mb-1">
                        <span className="text-rose-700">High Difficulty</span>
                        <span>{Math.round(selectedPrediction.probability_high * 100)}%</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2">
                        <div
                          className="bg-rose-500 h-2 rounded-full"
                          style={{ width: `${Math.round(selectedPrediction.probability_high * 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
                  <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-3">
                    Suggested Next Steps
                  </h4>
                  <ul className="text-xs text-slate-600 space-y-2 list-disc pl-4">
                    <li>Review lecture slides and prerequisite notes for this module.</li>
                    <li>Attempt chapter practice questions before taking the next quiz.</li>
                    <li>Utilize instructor office hours for difficult concepts.</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default StudentTopicAnalysis;

