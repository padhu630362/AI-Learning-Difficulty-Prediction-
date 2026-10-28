import React, { useState, useEffect } from 'react';
import axiosClient from '../../api/axiosClient';
import Modal from '../../components/Modal';
import ConfirmDialog from '../../components/ConfirmDialog';
import { useToast } from '../../context/ToastContext';
import { Plus, BookOpen, Layers, Edit, Trash2, Sparkles, ExternalLink } from 'lucide-react';

const InstructorSubjects = () => {
  const toast = useToast();
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modals state
  const [isSubjectModalOpen, setIsSubjectModalOpen] = useState(false);
  const [isTopicModalOpen, setIsTopicModalOpen] = useState(false);
  const [topicToDelete, setTopicToDelete] = useState(null);
  const [isDeletingTopic, setIsDeletingTopic] = useState(false);
  const [subjectForm, setSubjectForm] = useState({ code: '', name: '', description: '' });
  const [topicForm, setTopicForm] = useState({
    name: '',
    description: '',
    learning_objectives: '',
    difficulty_level: 'intermediate',
    order_index: 1,
    resources: '',
  });
  const [editingTopicId, setEditingTopicId] = useState(null);
  const [batchPredictingId, setBatchPredictingId] = useState(null);

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

  const selectSubject = async (subId) => {
    try {
      const res = await axiosClient.get(`/subjects/${subId}`);
      setSelectedSubject(res.data.subject);
      setTopics(res.data.subject.topics || []);
    } catch (err) {
      console.error('Error loading subject details:', err);
    }
  };

  const handleCreateSubject = async (e) => {
    e.preventDefault();
    try {
      const res = await axiosClient.post('/subjects', subjectForm);
      setIsSubjectModalOpen(false);
      setSubjectForm({ code: '', name: '', description: '' });
      toast.success('Subject created successfully!');
      fetchSubjects();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to create subject');
    }
  };

  const handleSaveTopic = async (e) => {
    e.preventDefault();
    try {
      if (editingTopicId) {
        await axiosClient.put(`/subjects/topics/${editingTopicId}`, topicForm);
        toast.success('Topic updated successfully!');
      } else {
        await axiosClient.post(`/subjects/${selectedSubject.id}/topics`, topicForm);
        toast.success('Topic added successfully!');
      }
      setIsTopicModalOpen(false);
      setEditingTopicId(null);
      setTopicForm({
        name: '',
        description: '',
        learning_objectives: '',
        difficulty_level: 'intermediate',
        order_index: 1,
        resources: '',
      });
      selectSubject(selectedSubject.id);
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to save topic');
    }
  };

  const handleEditTopic = (topic) => {
    setEditingTopicId(topic.id);
    setTopicForm({
      name: topic.name,
      description: topic.description || '',
      learning_objectives: topic.learning_objectives || '',
      difficulty_level: topic.difficulty_level || 'intermediate',
      order_index: topic.order_index || 1,
      resources: topic.resources || '',
    });
    setIsTopicModalOpen(true);
  };

  const confirmDeleteTopic = async () => {
    if (!topicToDelete) return;
    setIsDeletingTopic(true);
    try {
      await axiosClient.delete(`/subjects/topics/${topicToDelete.id}`);
      toast.success('Topic deleted successfully');
      setTopicToDelete(null);
      selectSubject(selectedSubject.id);
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to delete topic');
    } finally {
      setIsDeletingTopic(false);
    }
  };

  const handleBatchPredict = async (topicId) => {
    setBatchPredictingId(topicId);
    try {
      const res = await axiosClient.post(`/predictions/batch-predict-topic/${topicId}`);
      toast.success(res.data.message || 'Batch predictions generated successfully for all enrolled students!');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Batch prediction failed.');
    } finally {
      setBatchPredictingId(null);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Subject & Topic Management</h1>
          <p className="text-sm text-slate-500 mt-1">
            Configure learning objectives, syllabus hierarchy, and trigger cohort-wide AI difficulty evaluations.
          </p>
        </div>

        <button
          onClick={() => setIsSubjectModalOpen(true)}
          className="inline-flex items-center space-x-1.5 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>New Subject</span>
        </button>
      </div>

      {/* Subject Tabs */}
      <div className="flex space-x-2 border-b border-slate-200 overflow-x-auto pb-2">
        {subjects.map((sub) => (
          <button
            key={sub.id}
            onClick={() => selectSubject(sub.id)}
            className={`px-4 py-2.5 rounded-xl text-sm font-semibold whitespace-nowrap transition-all ${
              selectedSubject?.id === sub.id
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {sub.code} - {sub.name}
          </button>
        ))}
      </div>

      {selectedSubject && (
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
            <div>
              <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                {selectedSubject.code}
              </span>
              <h2 className="text-xl font-bold text-slate-900 mt-2">{selectedSubject.name}</h2>
              <p className="text-xs text-slate-600 mt-1 max-w-xl">{selectedSubject.description}</p>
            </div>

            <button
              onClick={() => {
                setEditingTopicId(null);
                setTopicForm({
                  name: '',
                  description: '',
                  learning_objectives: '',
                  difficulty_level: 'intermediate',
                  order_index: topics.length + 1,
                  resources: '',
                });
                setIsTopicModalOpen(true);
              }}
              className="inline-flex items-center space-x-1.5 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors shrink-0"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Topic</span>
            </button>
          </div>

          {/* Topics Table / List */}
          <div className="space-y-3">
            <h3 className="text-base font-bold text-slate-900">Topics & Curriculum Modules ({topics.length})</h3>

            {topics.length === 0 ? (
              <div className="p-8 bg-white rounded-2xl border border-dashed border-slate-200 text-center">
                <Layers className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                <p className="text-sm font-semibold text-slate-700">No topics created yet</p>
                <p className="text-xs text-slate-400 mt-1">Add syllabus topics to attach assessments and run predictions.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-3">
                {topics.map((t) => (
                  <div
                    key={t.id}
                    className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0 hover:border-slate-300 transition-colors"
                  >
                    <div className="space-y-1 max-w-2xl">
                      <div className="flex items-center space-x-2">
                        <span className="h-6 w-6 rounded-full bg-slate-100 text-slate-700 font-bold text-xs flex items-center justify-center">
                          {t.order_index}
                        </span>
                        <h4 className="text-base font-bold text-slate-900">{t.name}</h4>
                        <span className="capitalize text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                          {t.difficulty_level}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600">{t.description}</p>
                      {t.learning_objectives && (
                        <p className="text-xs text-slate-400">Objectives: {t.learning_objectives}</p>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 shrink-0">
                      <button
                        onClick={() => handleBatchPredict(t.id)}
                        disabled={batchPredictingId === t.id}
                        className="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded-lg text-xs font-semibold flex items-center space-x-1"
                      >
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>{batchPredictingId === t.id ? 'Evaluating...' : 'Cohort AI Evaluation'}</span>
                      </button>

                      <button
                        onClick={() => handleEditTopic(t)}
                        className="p-1.5 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg"
                      >
                        <Edit className="w-4 h-4" />
                      </button>

                      <button
                        onClick={() => setTopicToDelete(t)}
                        className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg"
                        title="Delete Topic"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Subject Modal */}
      <Modal
        isOpen={isSubjectModalOpen}
        onClose={() => setIsSubjectModalOpen(false)}
        title="Create New Subject"
      >
        <form onSubmit={handleCreateSubject} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Subject Code
            </label>
            <input
              type="text"
              value={subjectForm.code}
              onChange={(e) => setSubjectForm({ ...subjectForm, code: e.target.value })}
              placeholder="e.g. CS102"
              required
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Subject Name
            </label>
            <input
              type="text"
              value={subjectForm.name}
              onChange={(e) => setSubjectForm({ ...subjectForm, name: e.target.value })}
              placeholder="e.g. Database Systems & SQL"
              required
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Description
            </label>
            <textarea
              value={subjectForm.description}
              onChange={(e) => setSubjectForm({ ...subjectForm, description: e.target.value })}
              placeholder="Brief course overview..."
              rows={3}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="flex justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={() => setIsSubjectModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700"
            >
              Create Subject
            </button>
          </div>
        </form>
      </Modal>

      {/* Topic Modal */}
      <Modal
        isOpen={isTopicModalOpen}
        onClose={() => setIsTopicModalOpen(false)}
        title={editingTopicId ? 'Edit Topic' : 'Add New Topic'}
      >
        <form onSubmit={handleSaveTopic} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Topic Name
            </label>
            <input
              type="text"
              value={topicForm.name}
              onChange={(e) => setTopicForm({ ...topicForm, name: e.target.value })}
              placeholder="e.g. Relational Normalization (3NF & BCNF)"
              required
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
                Difficulty Level
              </label>
              <select
                value={topicForm.difficulty_level}
                onChange={(e) => setTopicForm({ ...topicForm, difficulty_level: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
                Curriculum Order Index
              </label>
              <input
                type="number"
                value={topicForm.order_index}
                onChange={(e) => setTopicForm({ ...topicForm, order_index: parseInt(e.target.value) || 1 })}
                min={1}
                required
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Description
            </label>
            <textarea
              value={topicForm.description}
              onChange={(e) => setTopicForm({ ...topicForm, description: e.target.value })}
              placeholder="Topic description..."
              rows={2}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Learning Objectives
            </label>
            <textarea
              value={topicForm.learning_objectives}
              onChange={(e) => setTopicForm({ ...topicForm, learning_objectives: e.target.value })}
              placeholder="What students should be able to do..."
              rows={2}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Learning Resource Link (URL)
            </label>
            <input
              type="url"
              value={topicForm.resources}
              onChange={(e) => setTopicForm({ ...topicForm, resources: e.target.value })}
              placeholder="https://en.wikipedia.org/wiki/..."
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="flex justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={() => setIsTopicModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700"
            >
              Save Topic
            </button>
          </div>
        </form>
      </Modal>

      {/* Confirmation Dialog for Topic Deletion */}
      <ConfirmDialog
        isOpen={Boolean(topicToDelete)}
        title="Delete Topic"
        message={`Are you sure you want to delete "${topicToDelete?.name}"? All associated assessments and recorded results will be permanently removed.`}
        confirmText="Delete Topic"
        cancelText="Cancel"
        variant="danger"
        isLoading={isDeletingTopic}
        onConfirm={confirmDeleteTopic}
        onCancel={() => setTopicToDelete(null)}
      />
    </div>
  );
};

export default InstructorSubjects;

