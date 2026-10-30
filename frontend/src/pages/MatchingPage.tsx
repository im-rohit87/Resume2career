import React, { useState, useEffect, useCallback } from 'react';
import { Briefcase, Loader2, AlertCircle, ChevronDown, ChevronRight, Info } from 'lucide-react';
import { api } from '../services/api';
import { Resume, JobMatchResponse } from '../types';
import { ScoreGauge } from '../components/ScoreGauge';

interface MatchingPageProps {
  onNavigate: (page: string, params?: unknown) => void;
}

function Spinner() {
  return <Loader2 className="w-4 h-4 animate-spin" />;
}

function ScoreBreakdownRow({ label, value, color }: { label: string; value: number; color: string }) {
  const pct = Math.round(value);
  return (
    <div className="flex items-center gap-3">
      <span className="text-gray-500 text-xs w-40 flex-shrink-0">{label}</span>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-gray-800 text-xs font-semibold w-10 text-right">{pct}%</span>
    </div>
  );
}

function SkillChip({
  skill, matched, category, evidence,
}: {
  skill: string; matched: boolean; category: 'required' | 'preferred'; evidence?: string;
}) {
  const [showTooltip, setShowTooltip] = useState(false);
  const base = matched
    ? category === 'required' ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300' : 'bg-sky-500/15 border-sky-500/40 text-sky-300'
    : category === 'required' ? 'bg-rose-500/15 border-rose-500/40 text-rose-300' : 'bg-amber-500/15 border-amber-500/40 text-amber-300';
  return (
    <div className="relative inline-block">
      <span
        className={`inline-flex items-center gap-1 px-2 py-1 border rounded-lg text-xs font-medium cursor-default ${base}`}
        onMouseEnter={() => evidence && setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        {matched ? '✓' : '✗'} {skill}
        {evidence && <Info className="w-3 h-3 opacity-60" />}
      </span>
      {showTooltip && evidence && (
        <div className="absolute bottom-full left-0 mb-2 z-10 w-56 bg-gray-100 border border-gray-300 text-gray-700 text-xs rounded-xl p-3 shadow-xl">
          <p className="font-semibold text-gray-800 mb-1">Evidence:</p>
          <p className="italic">{evidence}</p>
        </div>
      )}
    </div>
  );
}

export const MatchingPage: React.FC<MatchingPageProps> = () => {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<number | ''>('');
  const [roleTitle, setRoleTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [jobDesc, setJobDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<JobMatchResponse | null>(null);
  const [history, setHistory] = useState<JobMatchResponse[]>([]);
  const [expandedHistory, setExpandedHistory] = useState<number | null>(null);
  const [loadingResumes, setLoadingResumes] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [r, h] = await Promise.all([api.getResumes(), api.getMatchHistory()]);
      setResumes(r);
      setHistory(h);
      if (r.length > 0) setSelectedResumeId(r[0].id);
    } catch (e) { console.error(e); }
    finally { setLoadingResumes(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedResumeId) { setError('Please select a resume.'); return; }
    if (!roleTitle.trim()) { setError('Role title is required.'); return; }
    if (!jobDesc.trim()) { setError('Job description is required.'); return; }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await api.matchJob({
        resume_id: selectedResumeId as number,
        role_title: roleTitle,
        company_name: companyName || undefined,
        job_description_text: jobDesc,
      });
      setResult(res);
      setHistory((prev) => [res, ...prev.filter((h) => h.id !== res.id)]);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Job Match Analysis</h1>
        <p className="text-gray-500 text-sm mt-1">Paste a job description to see how your resume matches up.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <form onSubmit={handleAnalyze} className="bg-white border border-gray-200 rounded-2xl p-6 space-y-5">
          <h2 className="font-bold text-gray-900">Match Settings</h2>

          <div>
            <label htmlFor="match-resume" className="block text-xs font-semibold text-gray-500 mb-1.5">Select Resume</label>
            {loadingResumes ? (
              <div className="flex items-center gap-2 text-gray-400 text-sm"><Spinner /> Loading…</div>
            ) : (
              <select
                id="match-resume"
                value={selectedResumeId}
                onChange={(e) => setSelectedResumeId(Number(e.target.value))}
                className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2.5 outline-none"
              >
                <option value="">-- Select Resume --</option>
                {resumes.map((r) => (
                  <option key={r.id} value={r.id}>{r.filename}</option>
                ))}
              </select>
            )}
          </div>

          <div>
            <label htmlFor="role-title" className="block text-xs font-semibold text-gray-500 mb-1.5">Role Title <span className="text-rose-400">*</span></label>
            <input
              id="role-title"
              type="text"
              value={roleTitle}
              onChange={(e) => setRoleTitle(e.target.value)}
              placeholder="Senior Software Engineer"
              className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2.5 outline-none"
            />
          </div>

          <div>
            <label htmlFor="company-name" className="block text-xs font-semibold text-gray-500 mb-1.5">Company Name <span className="text-gray-400">(optional)</span></label>
            <input
              id="company-name"
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="Acme Corp"
              className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2.5 outline-none"
            />
          </div>

          <div>
            <label htmlFor="job-desc" className="block text-xs font-semibold text-gray-500 mb-1.5">Job Description <span className="text-rose-400">*</span></label>
            <textarea
              id="job-desc"
              value={jobDesc}
              onChange={(e) => setJobDesc(e.target.value)}
              rows={10}
              placeholder="Paste the full job description here…"
              className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2.5 outline-none resize-y"
            />
          </div>

          {error && (
            <div className="flex items-center gap-2 text-rose-400 text-sm">
              <AlertCircle className="w-4 h-4" /> {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold rounded-xl text-sm"
          >
            {loading ? <Spinner /> : <Briefcase className="w-4 h-4" />}
            {loading ? 'Analyzing…' : 'Analyze Match'}
          </button>
        </form>

        {/* Results Panel */}
        <div className="space-y-5">
          {loading && (
            <div className="bg-white border border-gray-200 rounded-2xl p-12 flex flex-col items-center gap-4 text-gray-400">
              <Loader2 className="w-10 h-10 animate-spin text-indigo-500" />
              <p className="text-sm">Analyzing match…</p>
            </div>
          )}

          {result && !loading && (
            <>
              <div className="bg-white border border-gray-200 rounded-2xl p-6 flex flex-col items-center">
                <ScoreGauge score={result.match_score} size={180} label={`Match Score — ${result.role_title}`} sublabel={result.company_name} />
              </div>

              <div className="bg-white border border-gray-200 rounded-2xl p-5 space-y-3">
                <h3 className="font-bold text-gray-900 text-sm">Score Breakdown</h3>
                <ScoreBreakdownRow label="Required Skills Coverage" value={result.score_breakdown.required_skills_coverage} color="bg-indigo-500" />
                <ScoreBreakdownRow label="Preferred Skills Coverage" value={result.score_breakdown.preferred_skills_coverage} color="bg-sky-500" />
                <ScoreBreakdownRow label="Semantic Similarity" value={result.score_breakdown.semantic_corpus_similarity} color="bg-purple-500" />
              </div>

              <div className="bg-white border border-gray-200 rounded-2xl p-5 space-y-3">
                <h3 className="font-bold text-gray-900 text-sm">Required Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {result.required_skills_matched.map((s) => (
                    <SkillChip key={s.skill} skill={s.skill} matched category="required" evidence={s.evidence_snippet} />
                  ))}
                  {result.required_skills_missing.map((s) => (
                    <SkillChip key={s} skill={s} matched={false} category="required" />
                  ))}
                </div>
              </div>

              {(result.preferred_skills_matched.length > 0 || result.preferred_skills_missing.length > 0) && (
                <div className="bg-white border border-gray-200 rounded-2xl p-5 space-y-3">
                  <h3 className="font-bold text-gray-900 text-sm">Preferred Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {result.preferred_skills_matched.map((s) => (
                      <SkillChip key={s.skill} skill={s.skill} matched category="preferred" evidence={s.evidence_snippet} />
                    ))}
                    {result.preferred_skills_missing.map((s) => (
                      <SkillChip key={s} skill={s} matched={false} category="preferred" />
                    ))}
                  </div>
                </div>
              )}

              {result.related_skills_present.length > 0 && (
                <div className="bg-white border border-gray-200 rounded-2xl p-5 space-y-3">
                  <h3 className="font-bold text-gray-900 text-sm">Related Skill Bridges</h3>
                  {result.related_skills_present.map((b, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-gray-500">
                      <span className="text-indigo-400 font-semibold">{b.related_candidate_skill}</span>
                      <ChevronRight className="w-4 h-4" />
                      <span className="text-amber-400 font-semibold">{b.missing_target}</span>
                      <span className="text-gray-400 text-xs">– {b.bridge_rationale}</span>
                    </div>
                  ))}
                </div>
              )}

              {result.recommendations.length > 0 && (
                <div className="bg-white border border-gray-200 rounded-2xl p-5">
                  <h3 className="font-bold text-gray-900 text-sm mb-3">Recommendations</h3>
                  <ul className="space-y-2">
                    {result.recommendations.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                        <span className="text-indigo-400 font-bold mt-0.5">{i + 1}.</span>{r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="px-2">
                <p className="text-xs text-gray-400 italic">{result.formula_explanation}</p>
                <p className="text-xs text-gray-400 italic mt-1">{result.disclaimer}</p>
              </div>
            </>
          )}

          {!result && !loading && (
            <div className="bg-white border border-gray-200 rounded-2xl p-12 text-center text-gray-400">
              <Briefcase className="w-10 h-10 mx-auto mb-3 opacity-30" />
              <p>Fill in the form and click "Analyze Match" to see results.</p>
            </div>
          )}
        </div>
      </div>

      {/* History */}
      {history.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-bold text-gray-900">Match History</h2>
          {history.map((h) => (
            <div key={h.id} className="bg-white border border-gray-200 rounded-xl overflow-hidden">
              <button
                onClick={() => setExpandedHistory(expandedHistory === h.id ? null : h.id)}
                className="w-full flex items-center gap-4 px-4 py-3 hover:bg-white/40 text-left"
              >
                <Briefcase className="w-4 h-4 text-indigo-400 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-gray-800 text-sm font-semibold truncate">{h.role_title}{h.company_name ? ` @ ${h.company_name}` : ''}</p>
                  <p className="text-gray-400 text-xs">{new Date(h.created_at).toLocaleDateString()}</p>
                </div>
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                  h.match_score >= 70 ? 'bg-emerald-500/20 text-emerald-400' :
                  h.match_score >= 50 ? 'bg-amber-500/20 text-amber-400' :
                  'bg-rose-500/20 text-rose-400'
                }`}>{Math.round(h.match_score)}%</span>
                {expandedHistory === h.id ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
              </button>
              {expandedHistory === h.id && (
                <div className="px-4 pb-4 space-y-3 border-t border-gray-200 pt-3">
                  <div className="flex flex-wrap gap-2">
                    {h.required_skills_matched.map((s) => <SkillChip key={s.skill} skill={s.skill} matched category="required" />)}
                    {h.required_skills_missing.map((s) => <SkillChip key={s} skill={s} matched={false} category="required" />)}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
