import React, { useState, useEffect, useCallback } from 'react';
import {
  Shield, Loader2, AlertCircle, ToggleLeft, ToggleRight,
  Plus, ChevronDown, ChevronUp, Users, FileText, PlayCircle, Star
} from 'lucide-react';
import { api } from '../services/api';
import { AdminQuestion, AdminStats, User } from '../types';

interface AdminPageProps {
  onNavigate: (page: string, params?: unknown) => void;
  currentUser: User;
}

function Spinner() { return <Loader2 className="w-4 h-4 animate-spin" />; }

function StatCard({ label, value, icon: Icon, color = 'text-indigo-400' }: {
  label: string; value: number | string; icon: React.ElementType; color?: string;
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-5">
      <div className="flex items-center gap-3 mb-2">
        <Icon className={`w-5 h-5 ${color}`} />
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">{label}</p>
      </div>
      <p className="text-2xl font-extrabold text-gray-900">{value}</p>
    </div>
  );
}

const EMPTY_QUESTION = {
  role: '', category: 'technical', difficulty: 'intermediate', skill_tag: '',
  question_text: '', expected_points: [] as string[], sample_good_answer: '',
};

export const AdminPage: React.FC<AdminPageProps> = ({ currentUser }) => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [questions, setQuestions] = useState<AdminQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newQ, setNewQ] = useState({ ...EMPTY_QUESTION });
  const [addingQ, setAddingQ] = useState(false);
  const [togglingId, setTogglingId] = useState<number | null>(null);
  const [expectedPointInput, setExpectedPointInput] = useState('');

  const fetchData = useCallback(async () => {
    try {
      const [s, q] = await Promise.all([api.getAdminStats(), api.getAdminQuestions()]);
      setStats(s);
      setQuestions(q);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load admin data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (currentUser.role !== 'admin') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-rose-400">
        <Shield className="w-12 h-12" />
        <p className="text-lg font-bold">Access Denied</p>
        <p className="text-gray-500 text-sm">This page is only accessible to administrators.</p>
      </div>
    );
  }

  const handleToggle = async (id: number) => {
    setTogglingId(id);
    try {
      await api.toggleAdminQuestion(id);
      setQuestions((prev) => prev.map((q) => q.id === id ? { ...q, is_active: !q.is_active } : q));
    } catch (e) { console.error(e); }
    finally { setTogglingId(null); }
  };

  const handleAddQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddingQ(true);
    try {
      const q = await api.createAdminQuestion(newQ);
      setQuestions((prev) => [q, ...prev]);
      setNewQ({ ...EMPTY_QUESTION });
      setShowAddForm(false);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to add question');
    } finally {
      setAddingQ(false);
    }
  };

  const addExpectedPoint = () => {
    const v = expectedPointInput.trim();
    if (v) { setNewQ({ ...newQ, expected_points: [...newQ.expected_points, v] }); setExpectedPointInput(''); }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-gray-400 gap-3">
        <Spinner /> <p className="text-sm">Loading admin panel…</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="flex items-center gap-3">
        <Shield className="w-6 h-6 text-amber-400" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Admin Hub</h1>
          <p className="text-gray-500 text-sm mt-0.5">System management panel · Restricted access</p>
        </div>
      </div>

      {/* Privacy Notice */}
      <div className="flex items-start gap-3 px-4 py-3 bg-amber-500/10 border border-amber-500/30 rounded-xl">
        <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-amber-300">
          <strong>Data Privacy:</strong> User data is strictly isolated. Admins can view aggregate statistics and manage the question bank only. Individual user profiles and interview content are not accessible here.
        </p>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-rose-400 text-sm">
          <AlertCircle className="w-4 h-4" /> {error}
        </div>
      )}

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          <StatCard label="Registered Users" value={stats.total_registered_users} icon={Users} />
          <StatCard label="Resumes Analyzed" value={stats.total_resumes_analyzed} icon={FileText} color="text-emerald-400" />
          <StatCard label="Interviews Initiated" value={stats.total_interviews_initiated} icon={PlayCircle} color="text-sky-400" />
          <StatCard label="Interviews Completed" value={stats.total_interviews_completed} icon={PlayCircle} color="text-purple-400" />
          <StatCard label="Question Bank" value={stats.curated_question_bank_count} icon={Shield} color="text-amber-400" />
          <StatCard label="System Avg Score" value={`${Math.round(stats.system_average_score)}/100`} icon={Star} color="text-rose-400" />
        </div>
      )}

      {/* Question Bank */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-900">Question Bank</h2>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl"
          >
            {showAddForm ? <ChevronUp className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
            {showAddForm ? 'Cancel' : 'Add Question'}
          </button>
        </div>

        {/* Add Form */}
        {showAddForm && (
          <form onSubmit={handleAddQuestion} className="bg-white border border-gray-200 rounded-2xl p-6 space-y-4">
            <h3 className="font-bold text-gray-900">New Question</h3>
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label htmlFor="q-role" className="block text-xs font-semibold text-gray-500 mb-1">Role</label>
                <input id="q-role" type="text" value={newQ.role} onChange={(e) => setNewQ({ ...newQ, role: e.target.value })} placeholder="Software Engineer" className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2 outline-none" />
              </div>
              <div>
                <label htmlFor="q-skill" className="block text-xs font-semibold text-gray-500 mb-1">Skill Tag</label>
                <input id="q-skill" type="text" value={newQ.skill_tag} onChange={(e) => setNewQ({ ...newQ, skill_tag: e.target.value })} placeholder="React, Python…" className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2 outline-none" />
              </div>
              <div>
                <label htmlFor="q-category" className="block text-xs font-semibold text-gray-500 mb-1">Category</label>
                <select id="q-category" value={newQ.category} onChange={(e) => setNewQ({ ...newQ, category: e.target.value })} className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2 outline-none">
                  <option value="technical">Technical</option>
                  <option value="behavioral">Behavioral</option>
                  <option value="hr">HR</option>
                  <option value="project">Project</option>
                </select>
              </div>
              <div>
                <label htmlFor="q-difficulty" className="block text-xs font-semibold text-gray-500 mb-1">Difficulty</label>
                <select id="q-difficulty" value={newQ.difficulty} onChange={(e) => setNewQ({ ...newQ, difficulty: e.target.value })} className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2 outline-none">
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>
            </div>
            <div>
              <label htmlFor="q-text" className="block text-xs font-semibold text-gray-500 mb-1">Question Text</label>
              <textarea id="q-text" value={newQ.question_text} onChange={(e) => setNewQ({ ...newQ, question_text: e.target.value })} rows={3} className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2 outline-none resize-y" />
            </div>
            <div>
              <label htmlFor="q-answer" className="block text-xs font-semibold text-gray-500 mb-1">Sample Good Answer</label>
              <textarea id="q-answer" value={newQ.sample_good_answer} onChange={(e) => setNewQ({ ...newQ, sample_good_answer: e.target.value })} rows={3} className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2 outline-none resize-y" />
            </div>
            <div>
              <label htmlFor="q-points" className="block text-xs font-semibold text-gray-500 mb-1">Expected Points</label>
              <div className="flex gap-2 mb-2">
                <input id="q-points" type="text" value={expectedPointInput} onChange={(e) => setExpectedPointInput(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addExpectedPoint(); } }} className="flex-1 bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2 outline-none" placeholder="Add a point and press Enter" />
                <button type="button" onClick={addExpectedPoint} className="px-3 py-2 bg-gray-100 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-300"><Plus className="w-4 h-4" /></button>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {newQ.expected_points.map((p, i) => (
                  <span key={i} className="flex items-center gap-1 bg-gray-100 border border-gray-300 text-gray-700 text-xs rounded-lg px-2 py-0.5">
                    {p}
                    <button type="button" onClick={() => setNewQ({ ...newQ, expected_points: newQ.expected_points.filter((_, j) => j !== i) })} className="text-gray-400 hover:text-rose-400"><X className="w-3 h-3" /></button>
                  </span>
                ))}
              </div>
            </div>
            <button type="submit" disabled={addingQ} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl">
              {addingQ ? <Spinner /> : <Plus className="w-4 h-4" />}
              {addingQ ? 'Adding…' : 'Add Question'}
            </button>
          </form>
        )}

        {/* Questions Table */}
        <div className="space-y-2">
          {questions.map((q) => (
            <div key={q.id} className={`flex items-start gap-4 px-4 py-3 bg-white border rounded-xl transition-all ${q.is_active ? 'border-gray-200' : 'border-gray-200/50 opacity-60'}`}>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <span className="text-xs font-semibold text-gray-500 capitalize">{q.category}</span>
                  <span className="text-xs text-gray-400 capitalize">{q.difficulty}</span>
                  {q.skill_tag && <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-500 rounded-full">{q.skill_tag}</span>}
                </div>
                <p className="text-gray-800 text-sm">{q.question_text}</p>
                {q.role && <p className="text-gray-400 text-xs mt-1">For: {q.role}</p>}
              </div>
              <button
                onClick={() => handleToggle(q.id)}
                disabled={togglingId === q.id}
                className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-semibold transition-all disabled:opacity-50"
                title={q.is_active ? 'Deactivate' : 'Activate'}
              >
                {togglingId === q.id ? <Spinner /> : q.is_active ? (
                  <><ToggleRight className="w-4 h-4 text-emerald-400" /> <span className="text-emerald-400">Active</span></>
                ) : (
                  <><ToggleLeft className="w-4 h-4 text-gray-400" /> <span className="text-gray-400">Inactive</span></>
                )}
              </button>
            </div>
          ))}
          {questions.length === 0 && (
            <div className="text-center py-8 text-gray-400">
              <p>No questions in the bank yet.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Fix missing import
function X({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}
