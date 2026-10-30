import React, { useState, useEffect, useCallback } from 'react';
import { PlayCircle, Loader2, AlertCircle, ChevronDown } from 'lucide-react';
import { api } from '../services/api';
import { Resume, JobMatchResponse } from '../types';

interface InterviewSetupPageProps {
  onNavigate: (page: string, params?: unknown) => void;
}

function Spinner() {
  return <Loader2 className="w-4 h-4 animate-spin" />;
}

const DIFFICULTIES = [
  { value: 'beginner', label: 'Beginner', desc: 'Fundamentals & basics' },
  { value: 'intermediate', label: 'Intermediate', desc: 'Applied concepts' },
  { value: 'advanced', label: 'Advanced', desc: 'Expert-level depth' },
  { value: 'adaptive', label: 'Adaptive', desc: 'AI adjusts in real-time' },
];

export const InterviewSetupPage: React.FC<InterviewSetupPageProps> = ({ onNavigate }) => {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [matches, setMatches] = useState<JobMatchResponse[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<number | ''>('');
  const [selectedMatchId, setSelectedMatchId] = useState<number | ''>('');
  const [targetRole, setTargetRole] = useState('');
  const [difficulty, setDifficulty] = useState('adaptive');
  const [numQuestions, setNumQuestions] = useState(5);
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(true);
  const [error, setError] = useState('');

  const fetchData = useCallback(async () => {
    try {
      const [r, h] = await Promise.all([api.getResumes(), api.getMatchHistory()]);
      setResumes(r);
      setMatches(h);
      if (r.length > 0) setSelectedResumeId(r[0].id);
    } catch (e) { console.error(e); }
    finally { setLoadingData(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetRole.trim()) { setError('Target role is required.'); return; }
    setLoading(true);
    setError('');
    try {
      const result = await api.createInterview({
        resume_id: selectedResumeId ? (selectedResumeId as number) : undefined,
        job_id: selectedMatchId ? (selectedMatchId as number) : undefined,
        target_role: targetRole,
        difficulty_level: difficulty,
        total_questions: numQuestions,
      });
      onNavigate('interview', { sessionId: result.session_id });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to create interview session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Setup Mock Interview</h1>
        <p className="text-gray-500 text-sm mt-1">Configure your adaptive interview session.</p>
      </div>

      <form onSubmit={handleStart} className="bg-white border border-gray-200 rounded-2xl p-6 space-y-6">
        {/* Resume */}
        <div>
          <label htmlFor="setup-resume" className="block text-xs font-semibold text-gray-500 mb-1.5">
            Resume <span className="text-gray-400 font-normal">(optional — personalizes questions)</span>
          </label>
          {loadingData ? (
            <div className="flex items-center gap-2 text-gray-400 text-sm"><Spinner /> Loading…</div>
          ) : (
            <div className="relative">
              <select
                id="setup-resume"
                value={selectedResumeId}
                onChange={(e) => setSelectedResumeId(e.target.value ? Number(e.target.value) : '')}
                className="w-full appearance-none bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2.5 outline-none pr-8"
              >
                <option value="">No resume</option>
                {resumes.map((r) => (
                  <option key={r.id} value={r.id}>{r.filename}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          )}
        </div>

        {/* Job Match */}
        <div>
          <label htmlFor="setup-match" className="block text-xs font-semibold text-gray-500 mb-1.5">
            Job Match <span className="text-gray-400 font-normal">(optional — targets job-specific questions)</span>
          </label>
          <div className="relative">
            <select
              id="setup-match"
              value={selectedMatchId}
              onChange={(e) => setSelectedMatchId(e.target.value ? Number(e.target.value) : '')}
              className="w-full appearance-none bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2.5 outline-none pr-8"
            >
              <option value="">No job match</option>
              {matches.map((m) => (
                <option key={m.id} value={m.id}>{m.role_title}{m.company_name ? ` @ ${m.company_name}` : ''}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
        </div>

        {/* Target Role */}
        <div>
          <label htmlFor="target-role" className="block text-xs font-semibold text-gray-500 mb-1.5">
            Target Role <span className="text-rose-400">*</span>
          </label>
          <input
            id="target-role"
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. Senior Software Engineer"
            className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2.5 outline-none"
          />
        </div>

        {/* Difficulty */}
        <div>
          <span className="block text-xs font-semibold text-gray-500 mb-2">Difficulty Level</span>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {DIFFICULTIES.map((d) => (
              <button
                key={d.value}
                type="button"
                onClick={() => setDifficulty(d.value)}
                className={`flex flex-col items-center gap-1 p-3 border rounded-xl text-center transition-all ${
                  difficulty === d.value
                    ? 'border-indigo-500 bg-indigo-500/10 text-indigo-300'
                    : 'border-gray-300 text-gray-500 hover:border-gray-300'
                }`}
              >
                <span className="text-sm font-semibold">{d.label}</span>
                <span className="text-xs text-gray-400">{d.desc}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Number of Questions */}
        <div>
          <label htmlFor="num-questions" className="block text-xs font-semibold text-gray-500 mb-2">
            Questions: <span className="text-indigo-400 font-bold">{numQuestions}</span>
          </label>
          <input
            id="num-questions"
            type="range"
            min={3}
            max={10}
            step={1}
            value={numQuestions}
            onChange={(e) => setNumQuestions(Number(e.target.value))}
            className="w-full accent-indigo-500"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>3 (Quick)</span>
            <span>10 (Full)</span>
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 text-rose-400 text-sm">
            <AlertCircle className="w-4 h-4" /> {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold rounded-xl text-sm transition-all shadow-lg shadow-indigo-600/20"
        >
          {loading ? <Spinner /> : <PlayCircle className="w-5 h-5" />}
          {loading ? 'Starting session…' : 'Start Interview'}
        </button>
      </form>

      <p className="text-center text-xs text-gray-400">
        Questions are generated using your resume and job match context. Results are for practice only.
      </p>
    </div>
  );
};
