import React, { useState, useEffect } from 'react';
import axiosClient from '../../api/axiosClient';
import Modal from '../../components/Modal';
import { useToast } from '../../context/ToastContext';
import { Plus, Upload, CheckCircle2, AlertCircle, FileSpreadsheet, Clock, User, Download } from 'lucide-react';

const InstructorAssessments = () => {
  const toast = useToast();
  const [assessments, setAssessments] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [students, setStudents] = useState([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState('');
  const [loading, setLoading] = useState(true);

  // Create assessment modal
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newAssessment, setNewAssessment] = useState({
    subject_id: '',
    topic_id: '',
    title: '',
    assessment_type: 'quiz',
    max_marks: 100,
    passing_marks: 40,
    weightage: 1.0,
    assessment_date: new Date().toISOString().split('T')[0],
  });
  const [availableTopics, setAvailableTopics] = useState([]);

  // Manual result entry modal
  const [isResultModalOpen, setIsResultModalOpen] = useState(false);
  const [selectedAssessment, setSelectedAssessment] = useState(null);
  const [resultForm, setResultForm] = useState({
    student_id: '',
    marks_obtained: '',
    study_time_minutes: 60,
    attempt_count: 1,
    repeated_errors_count: 0,
    completion_status: 'completed',
    remarks: '',
  });

  // CSV Import Modal
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [csvFile, setCsvFile] = useState(null);
  const [importSummary, setImportSummary] = useState(null);
  const [importing, setImporting] = useState(false);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      const [subsRes, studRes, assRes] = await Promise.all([
        axiosClient.get('/subjects'),
        axiosClient.get('/users/students'),
        axiosClient.get('/assessments'),
      ]);

      setSubjects(subsRes.data.subjects || []);
      setStudents(studRes.data.students || []);
      setAssessments(assRes.data.assessments || []);
    } catch (err) {
      console.error('Error fetching assessment data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubjectChange = async (subId) => {
    setNewAssessment((prev) => ({ ...prev, subject_id: subId, topic_id: '' }));
    if (!subId) {
      setAvailableTopics([]);
      return;
    }
    try {
      const res = await axiosClient.get(`/subjects/${subId}/topics`);
      setAvailableTopics(res.data.topics || []);
    } catch (err) {
      console.error('Error fetching topics:', err);
    }
  };

  const handleCreateAssessment = async (e) => {
    e.preventDefault();
    try {
      await axiosClient.post('/assessments', newAssessment);
      setIsCreateModalOpen(false);
      setNewAssessment({
        subject_id: '',
        topic_id: '',
        title: '',
        assessment_type: 'quiz',
        max_marks: 100,
        passing_marks: 40,
        weightage: 1.0,
        assessment_date: new Date().toISOString().split('T')[0],
      });
      toast.success('Assessment created successfully!');
      const res = await axiosClient.get('/assessments');
      setAssessments(res.data.assessments || []);
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to create assessment');
    }
  };

  const handleRecordResult = async (e) => {
    e.preventDefault();
    try {
      await axiosClient.post(`/assessments/${selectedAssessment.id}/results`, resultForm);
      setIsResultModalOpen(false);
      toast.success('Student score saved successfully!');
      fetchInitialData();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to record student result');
    }
  };

  const handleCsvImport = async (e) => {
    e.preventDefault();
    if (!csvFile || !selectedAssessment) return;
    setImporting(true);
    setImportSummary(null);

    const formData = new FormData();
    formData.append('file', csvFile);

    try {
      const res = await axiosClient.post(`/assessments/${selectedAssessment.id}/import-results`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setImportSummary(res.data);
      toast.success(`Import complete: ${res.data.imported_count} scores recorded!`);
      fetchInitialData();
    } catch (err) {
      toast.error(err.response?.data?.error || 'CSV import failed');
    } finally {
      setImporting(false);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await axiosClient.get('/assessments/template.csv', {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'gradebook_template.csv');
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      toast.success('Gradebook CSV template downloaded');
    } catch (err) {
      toast.error('Failed to download CSV template');
    }
  };

  const filteredAssessments = selectedSubjectId
    ? assessments.filter((a) => a.subject_id === parseInt(selectedSubjectId))
    : assessments;

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Assessments & Gradebook</h1>
          <p className="text-sm text-slate-500 mt-1">
            Publish quizzes, record marks, and import batch student performance data via CSV.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleDownloadTemplate}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-xl text-xs font-semibold shadow-xs transition-colors shrink-0"
            title="Download CSV Gradebook Template"
          >
            <Download className="w-4 h-4 text-slate-500" />
            <span>CSV Template</span>
          </button>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="inline-flex items-center space-x-1.5 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors shrink-0"
          >
            <Plus className="w-4 h-4" />
            <span>New Assessment</span>
          </button>
        </div>
      </div>

      {/* Filter bar */}
      <div className="flex items-center space-x-3 bg-white p-3 rounded-2xl border border-slate-200">
        <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider pl-2">Filter by Subject:</label>
        <select
          value={selectedSubjectId}
          onChange={(e) => setSelectedSubjectId(e.target.value)}
          className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium text-slate-700 bg-slate-50 focus:outline-none"
        >
          <option value="">All Subjects</option>
          {subjects.map((s) => (
            <option key={s.id} value={s.id}>{s.code} - {s.name}</option>
          ))}
        </select>
      </div>

      {/* Assessment Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/50 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                <th className="px-6 py-4">Title & Subject</th>
                <th className="px-6 py-4">Type</th>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Max Marks</th>
                <th className="px-6 py-4">Submissions</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {filteredAssessments.map((a) => (
                <tr key={a.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="px-6 py-4">
                    <p className="font-semibold text-slate-900">{a.title}</p>
                    <p className="text-xs text-slate-500">{a.subject_name} • {a.topic_name}</p>
                  </td>
                  <td className="px-6 py-4">
                    <span className="capitalize text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-700">
                      {a.assessment_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-xs text-slate-500">{a.assessment_date}</td>
                  <td className="px-6 py-4 font-mono text-xs">{a.max_marks} pts</td>
                  <td className="px-6 py-4">
                    <span className="text-xs font-semibold text-slate-700 bg-indigo-50 border border-indigo-100 text-indigo-700 px-2 py-0.5 rounded-md">
                      {a.submissions_count} submitted
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <button
                      onClick={() => {
                        setSelectedAssessment(a);
                        setResultForm({
                          student_id: students.length > 0 ? students[0].id : '',
                          marks_obtained: '',
                          study_time_minutes: 60,
                          attempt_count: 1,
                          repeated_errors_count: 0,
                          completion_status: 'completed',
                          remarks: '',
                        });
                        setIsResultModalOpen(true);
                      }}
                      className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors"
                    >
                      Record Grade
                    </button>
                    <button
                      onClick={() => {
                        setSelectedAssessment(a);
                        setCsvFile(null);
                        setImportSummary(null);
                        setIsImportModalOpen(true);
                      }}
                      className="px-2.5 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 text-xs font-semibold rounded-lg transition-colors inline-flex items-center space-x-1"
                    >
                      <Upload className="w-3 h-3" />
                      <span>CSV Import</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Assessment Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Assessment"
      >
        <form onSubmit={handleCreateAssessment} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Subject
            </label>
            <select
              value={newAssessment.subject_id}
              onChange={(e) => handleSubjectChange(e.target.value)}
              required
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
            >
              <option value="">Select subject...</option>
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>{s.code} - {s.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Curriculum Topic
            </label>
            <select
              value={newAssessment.topic_id}
              onChange={(e) => setNewAssessment({ ...newAssessment, topic_id: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
            >
              <option value="">General Subject Assessment (or select topic)</option>
              {availableTopics.map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Assessment Title
            </label>
            <input
              type="text"
              value={newAssessment.title}
              onChange={(e) => setNewAssessment({ ...newAssessment, title: e.target.value })}
              placeholder="e.g. Quiz 3: Binary Tree Rotations"
              required
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
                Assessment Type
              </label>
              <select
                value={newAssessment.assessment_type}
                onChange={(e) => setNewAssessment({ ...newAssessment, assessment_type: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
              >
                <option value="quiz">Quiz</option>
                <option value="assignment">Assignment</option>
                <option value="exam">Examination</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
                Assessment Date
              </label>
              <input
                type="date"
                value={newAssessment.assessment_date}
                onChange={(e) => setNewAssessment({ ...newAssessment, assessment_date: e.target.value })}
                required
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
                Max Marks
              </label>
              <input
                type="number"
                value={newAssessment.max_marks}
                onChange={(e) => setNewAssessment({ ...newAssessment, max_marks: parseFloat(e.target.value) || 100 })}
                min={1}
                required
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
                Passing Marks
              </label>
              <input
                type="number"
                value={newAssessment.passing_marks}
                onChange={(e) => setNewAssessment({ ...newAssessment, passing_marks: parseFloat(e.target.value) || 40 })}
                min={0}
                required
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={() => setIsCreateModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700"
            >
              Create Assessment
            </button>
          </div>
        </form>
      </Modal>

      {/* Record Result Modal */}
      <Modal
        isOpen={isResultModalOpen}
        onClose={() => setIsResultModalOpen(false)}
        title={`Record Student Result: ${selectedAssessment?.title}`}
      >
        <form onSubmit={handleRecordResult} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Select Student
            </label>
            <select
              value={resultForm.student_id}
              onChange={(e) => setResultForm({ ...resultForm, student_id: parseInt(e.target.value) })}
              required
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
            >
              <option value="">Select student...</option>
              {students.map((s) => (
                <option key={s.id} value={s.id}>{s.full_name} ({s.username})</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
                Marks Obtained (Max: {selectedAssessment?.max_marks})
              </label>
              <input
                type="number"
                step="0.5"
                value={resultForm.marks_obtained}
                onChange={(e) => setResultForm({ ...resultForm, marks_obtained: e.target.value })}
                min={0}
                max={selectedAssessment?.max_marks}
                required
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
                Study Time (Minutes)
              </label>
              <input
                type="number"
                value={resultForm.study_time_minutes}
                onChange={(e) => setResultForm({ ...resultForm, study_time_minutes: parseFloat(e.target.value) || 60 })}
                min={0}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
                Attempt Count
              </label>
              <input
                type="number"
                value={resultForm.attempt_count}
                onChange={(e) => setResultForm({ ...resultForm, attempt_count: parseInt(e.target.value) || 1 })}
                min={1}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
                Repeated Error Count
              </label>
              <input
                type="number"
                value={resultForm.repeated_errors_count}
                onChange={(e) => setResultForm({ ...resultForm, repeated_errors_count: parseInt(e.target.value) || 0 })}
                min={0}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Instructor Remarks
            </label>
            <input
              type="text"
              value={resultForm.remarks}
              onChange={(e) => setResultForm({ ...resultForm, remarks: e.target.value })}
              placeholder="e.g. Struggled with base cases, good effort"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="flex justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={() => setIsResultModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700"
            >
              Save Result
            </button>
          </div>
        </form>
      </Modal>

      {/* CSV Import Modal */}
      <Modal
        isOpen={isImportModalOpen}
        onClose={() => setIsImportModalOpen(false)}
        title={`Bulk CSV Import: ${selectedAssessment?.title}`}
      >
        <div className="space-y-4">
          <div className="p-3.5 bg-indigo-50 border border-indigo-100 rounded-xl text-xs text-indigo-900">
            <p className="font-semibold mb-1">Expected CSV Column Headers:</p>
            <p className="font-mono text-[11px] text-indigo-700">
              student_email, marks_obtained, study_time_minutes, attempt_count, repeated_errors_count, completion_status, remarks
            </p>
          </div>

          <form onSubmit={handleCsvImport} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
                Choose CSV File
              </label>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setCsvFile(e.target.files[0])}
                required
                className="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setIsImportModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={importing || !csvFile}
                className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700 disabled:opacity-50"
              >
                {importing ? 'Processing CSV...' : 'Start Import'}
              </button>
            </div>
          </form>

          {importSummary && (
            <div className="mt-4 p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2 text-xs">
              <p className="font-bold text-slate-800">{importSummary.message}</p>
              <div className="flex space-x-4">
                <span className="text-emerald-600 font-semibold">Success: {importSummary.success_count}</span>
                <span className="text-rose-600 font-semibold">Errors: {importSummary.rejected_count}</span>
              </div>
              {importSummary.errors && importSummary.errors.length > 0 && (
                <div className="mt-2 text-[11px] text-rose-700 space-y-1 max-h-32 overflow-y-auto">
                  {importSummary.errors.map((err, i) => (
                    <p key={i}>• {err}</p>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default InstructorAssessments;

