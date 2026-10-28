import React, { useState, useEffect } from 'react';
import axiosClient from '../../api/axiosClient';
import Modal from '../../components/Modal';
import ConfirmDialog from '../../components/ConfirmDialog';
import { useToast } from '../../context/ToastContext';
import { Database, Upload, Play, Trash2, Eye, CheckCircle2, AlertTriangle, FileSpreadsheet } from 'lucide-react';

const AdminDatasets = () => {
  const toast = useToast();
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);

  // Upload modal
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  // Preview modal
  const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [trainingDatasetId, setTrainingDatasetId] = useState(null);

  // Confirmation dialog
  const [confirmDialog, setConfirmDialog] = useState({
    isOpen: false,
    title: '',
    message: '',
    variant: 'primary',
    confirmText: 'Confirm',
    action: null,
  });

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    setLoading(true);
    try {
      const res = await axiosClient.get('/datasets');
      setDatasets(res.data.datasets || []);
    } catch (err) {
      console.error('Failed to load datasets:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;
    setUploading(true);

    const formData = new FormData();
    formData.append('file', uploadFile);

    try {
      await axiosClient.post('/datasets/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setIsUploadModalOpen(false);
      setUploadFile(null);
      toast.success('Dataset uploaded and validated successfully!');
      fetchDatasets();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Dataset upload and validation failed');
    } finally {
      setUploading(false);
    }
  };

  const handleViewPreview = async (datasetId) => {
    try {
      const res = await axiosClient.get(`/datasets/${datasetId}`);
      setSelectedDataset(res.data.dataset);
      setIsPreviewModalOpen(true);
    } catch (err) {
      toast.error('Failed to load dataset preview');
    }
  };

  const promptTrainDataset = (dataset) => {
    setConfirmDialog({
      isOpen: true,
      title: 'Train ML Pipeline',
      message: `Start machine learning training pipeline on "${dataset.original_name}"? This will evaluate candidate models (Random Forest, Logistic Regression, Decision Tree) with 5-fold cross-validation and activate the best performing version.`,
      variant: 'primary',
      confirmText: 'Train Pipeline',
      action: () => executeTrainDataset(dataset.id),
    });
  };

  const executeTrainDataset = async (datasetId) => {
    setTrainingDatasetId(datasetId);
    setConfirmDialog((prev) => ({ ...prev, isOpen: false }));
    try {
      const res = await axiosClient.post(`/datasets/${datasetId}/train`);
      toast.success(res.data.message || 'Model training completed and activated successfully!');
      fetchDatasets();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Model training failed');
    } finally {
      setTrainingDatasetId(null);
    }
  };

  const promptDeleteDataset = (dataset) => {
    setConfirmDialog({
      isOpen: true,
      title: 'Delete Dataset',
      message: `Are you sure you want to permanently delete "${dataset.original_name}"? This cannot be undone.`,
      variant: 'danger',
      confirmText: 'Delete Dataset',
      action: () => executeDeleteDataset(dataset.id),
    });
  };

  const executeDeleteDataset = async (datasetId) => {
    setConfirmDialog((prev) => ({ ...prev, isOpen: false }));
    try {
      await axiosClient.delete(`/datasets/${datasetId}`);
      toast.success('Dataset deleted successfully');
      fetchDatasets();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to delete dataset');
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Dataset Inventory & Validation</h1>
          <p className="text-sm text-slate-500 mt-1">
            Upload, validate, inspect, and train machine-learning models on structured educational datasets.
          </p>
        </div>

        <button
          onClick={() => setIsUploadModalOpen(true)}
          className="inline-flex items-center space-x-1.5 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors shrink-0"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Dataset CSV</span>
        </button>
      </div>

      {/* Dataset Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/50 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                <th className="px-6 py-4">Filename</th>
                <th className="px-6 py-4">Rows</th>
                <th className="px-6 py-4">Columns</th>
                <th className="px-6 py-4">Validation Status</th>
                <th className="px-6 py-4">Upload Date</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {datasets.map((d) => (
                <tr key={d.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="px-6 py-4 font-semibold text-slate-900 flex items-center space-x-2">
                    <FileSpreadsheet className="w-4 h-4 text-indigo-600 shrink-0" />
                    <span>{d.original_name}</span>
                    {d.is_active_training_set && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                        Active Training
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 font-mono text-xs">{d.row_count}</td>
                  <td className="px-6 py-4 font-mono text-xs">{d.column_count}</td>
                  <td className="px-6 py-4">
                    {d.validation_status === 'valid' ? (
                      <span className="text-emerald-700 text-xs font-semibold flex items-center space-x-1">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Valid Schema</span>
                      </span>
                    ) : (
                      <span className="text-rose-600 text-xs font-semibold flex items-center space-x-1">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        <span>Invalid</span>
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-xs text-slate-500">
                    {new Date(d.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <button
                      onClick={() => handleViewPreview(d.id)}
                      className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors inline-flex items-center space-x-1"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Preview</span>
                    </button>

                    <button
                      onClick={() => promptTrainDataset(d)}
                      disabled={trainingDatasetId === d.id || d.validation_status !== 'valid'}
                      className="px-2.5 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 text-xs font-semibold rounded-lg transition-colors inline-flex items-center space-x-1 disabled:opacity-50"
                      title={d.validation_status !== 'valid' ? 'Cannot train on invalid dataset' : 'Train candidate models'}
                    >
                      <Play className="w-3.5 h-3.5 text-indigo-600" />
                      <span>{trainingDatasetId === d.id ? 'Training ML Pipeline...' : 'Train Model'}</span>
                    </button>

                    <button
                      onClick={() => promptDeleteDataset(d)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                      title="Delete dataset"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Upload Modal */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Upload Structured Dataset"
      >
        <div className="space-y-4">
          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-600 space-y-1">
            <p className="font-semibold text-slate-800">Required Schema Features:</p>
            <p className="font-mono text-[11px] text-slate-500">
              quiz_score, assignment_score, exam_score, study_time_weekly, attendance_rate, attempt_count, repeated_errors_count, previous_topic_score, learning_pace_gap, topic_difficulty_level, difficulty_category
            </p>
          </div>

          <form onSubmit={handleUploadSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
                Select CSV Dataset File
              </label>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setUploadFile(e.target.files[0])}
                required
                className="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setIsUploadModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={uploading || !uploadFile}
                className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700 disabled:opacity-50"
              >
                {uploading ? 'Validating Schema...' : 'Upload & Validate'}
              </button>
            </div>
          </form>
        </div>
      </Modal>

      {/* Preview Modal */}
      <Modal
        isOpen={isPreviewModalOpen}
        onClose={() => setIsPreviewModalOpen(false)}
        title={`Dataset Preview: ${selectedDataset?.original_name}`}
        maxWidth="max-w-4xl"
      >
        {selectedDataset && (
          <div className="space-y-4">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs flex justify-between items-center">
              <div>
                <span className="font-semibold text-slate-800">Total Rows: {selectedDataset.row_count}</span> •{' '}
                <span className="text-slate-500">{selectedDataset.column_count} Features</span>
              </div>
              <span className={`px-2 py-0.5 rounded font-semibold text-[10px] ${
                selectedDataset.validation_status === 'valid' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
              }`}>
                {selectedDataset.validation_status}
              </span>
            </div>

            {/* Preview Table */}
            <div className="overflow-x-auto border border-slate-200 rounded-xl max-h-96">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-100 border-b border-slate-200 sticky top-0">
                  <tr>
                    {selectedDataset.columns_list?.map((col) => (
                      <th key={col} className="px-3 py-2 text-slate-600 whitespace-nowrap">{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 bg-white">
                  {selectedDataset.preview?.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      {selectedDataset.columns_list?.map((col) => (
                        <td key={col} className="px-3 py-1.5 text-slate-800 whitespace-nowrap">
                          {String(row[col])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="text-right pt-2">
              <button
                onClick={() => setIsPreviewModalOpen(false)}
                className="px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold hover:bg-slate-800"
              >
                Close Preview
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Confirmation Dialog for Training and Deletion */}
      <ConfirmDialog
        isOpen={confirmDialog.isOpen}
        title={confirmDialog.title}
        message={confirmDialog.message}
        confirmText={confirmDialog.confirmText}
        cancelText="Cancel"
        variant={confirmDialog.variant}
        onConfirm={confirmDialog.action}
        onCancel={() => setConfirmDialog((prev) => ({ ...prev, isOpen: false }))}
      />
    </div>
  );
};

export default AdminDatasets;

