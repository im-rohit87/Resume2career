import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldCheck, Loader2, AlertCircle, CheckCircle, Info, ChevronDown, ChevronRight
} from 'lucide-react';
import { api } from '../services/api';
import { Resume, EvidenceClaim } from '../types';

interface EvidenceCheckerPageProps {
  onNavigate: (page: string, params?: unknown) => void;
}

function Spinner() { return <Loader2 className="w-4 h-4 animate-spin" />; }

const CLAIM_TYPE_ICONS: Record<string, string> = {
  project: '🚀',
  metric: '📊',
  technology: '⚙️',
  architecture: '🏗️',
};

const STATUS_STYLES: Record<string, string> = {
  pending: 'bg-slate-700/50 text-gray-500 border-gray-300',
  practiced: 'bg-sky-500/20 text-sky-400 border-sky-500/40',
  verified_strong: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
  needs_preparation: 'bg-amber-500/20 text-amber-400 border-amber-500/40',
};

const STATUS_LABELS: Record<string, string> = {
  pending: 'Pending',
  practiced: 'Practiced',
  verified_strong: 'Verified Strong',
  needs_preparation: 'Needs Preparation',
};

function ClaimCard({ claim, onSubmitDefense }: {
  claim: EvidenceClaim;
  onSubmitDefense: (id: number, answer: string) => Promise<{ status: string; guidance: string; disclaimer: string }>;
}) {
  const [defense, setDefense] = useState(claim.candidate_answer || '');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{ status: string; guidance: string; disclaimer: string } | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [localStatus, setLocalStatus] = useState(claim.status);

  const handleSubmit = async () => {
    if (!defense.trim()) return;
    setSubmitting(true);
    try {
      const res = await onSubmitDefense(claim.id, defense);
      setResult(res);
      setLocalStatus(res.status);
    } catch (e) { console.error(e); }
    finally { setSubmitting(false); }
  };

  const icon = CLAIM_TYPE_ICONS[claim.claim_type] || '📌';
  const statusStyle = STATUS_STYLES[localStatus] || STATUS_STYLES.pending;
  const statusLabel = STATUS_LABELS[localStatus] || localStatus;

  return (
    <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-start gap-3 px-5 py-4 text-left hover:bg-white/40"
      >
        <span className="text-xl flex-shrink-0">{icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="text-xs text-gray-400 capitalize">{claim.claim_type}</span>
            <span className={`px-2 py-0.5 border rounded-full text-xs font-semibold ${statusStyle}`}>
              {statusLabel}
            </span>
          </div>
          <p className="text-gray-800 text-sm">{claim.claim_text}</p>
        </div>
        {expanded ? <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0 mt-1" /> : <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0 mt-1" />}
      </button>

      {expanded && (
        <div className="px-5 pb-5 space-y-4 border-t border-gray-200 pt-4">
          <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl px-4 py-3">
            <p className="text-xs font-bold text-indigo-400 mb-1">Verification Question</p>
            <p className="text-gray-800 text-sm">{claim.verification_question}</p>
          </div>

          {result ? (
            <div className="space-y-2">
              <div className={`px-4 py-3 rounded-xl border text-sm ${STATUS_STYLES[result.status] || STATUS_STYLES.pending}`}>
                <p className="font-bold mb-1">{STATUS_LABELS[result.status]}</p>
                <p>{result.guidance}</p>
              </div>
              <p className="text-xs text-gray-400 italic">{result.disclaimer}</p>
            </div>
          ) : (
            <>
              <div>
                <label htmlFor={`defense-${claim.id}`} className="block text-xs font-semibold text-gray-500 mb-1.5">
                  Your Defense / Explanation
                </label>
                <textarea
                  id={`defense-${claim.id}`}
                  value={defense}
                  onChange={(e) => setDefense(e.target.value)}
                  rows={4}
                  placeholder="Explain how you achieved this, with specifics…"
                  className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2.5 outline-none resize-y"
                />
              </div>
              <button
                onClick={handleSubmit}
                disabled={!defense.trim() || submitting}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl"
              >
                {submitting ? <Spinner /> : <CheckCircle className="w-4 h-4" />}
                {submitting ? 'Evaluating…' : 'Submit Defense'}
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export const EvidenceCheckerPage: React.FC<EvidenceCheckerPageProps> = () => {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<number | ''>('');
  const [claims, setClaims] = useState<EvidenceClaim[]>([]);
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState('');
  const [loadingResumes, setLoadingResumes] = useState(true);

  const fetchResumes = useCallback(async () => {
    try {
      const r = await api.getResumes();
      setResumes(r);
      if (r.length > 0) {
        setSelectedResumeId(r[0].id);
      }
    } catch (e) { console.error(e); }
    finally { setLoadingResumes(false); }
  }, []);

  useEffect(() => { fetchResumes(); }, [fetchResumes]);

  const fetchClaims = useCallback(async (resumeId: number) => {
    setLoading(true);
    try {
      const c = await api.getClaims(resumeId);
      setClaims(c);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  const handleResumeChange = (id: number) => {
    setSelectedResumeId(id);
    setClaims([]);
    if (id) fetchClaims(id);
  };

  const handleExtract = async () => {
    if (!selectedResumeId) return;
    setExtracting(true);
    setError('');
    try {
      const result = await api.extractClaims(selectedResumeId as number);
      setClaims(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Extraction failed');
    } finally {
      setExtracting(false);
    }
  };

  const handleSubmitDefense = async (claimId: number, answer: string) => {
    return api.answerClaim(claimId, answer);
  };

  const updateClaimStatus = (id: number, status: string) => {
    setClaims((prev) => prev.map((c) => c.id === id ? { ...c, status: status as EvidenceClaim['status'] } : c));
  };

  // Summary stats
  const practiced = claims.filter((c) => c.status === 'practiced').length;
  const verified = claims.filter((c) => c.status === 'verified_strong').length;
  const needsPrep = claims.filter((c) => c.status === 'needs_preparation').length;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Evidence Checker</h1>
        <p className="text-gray-500 text-sm mt-1">Practice defending claims on your resume with targeted questions.</p>
      </div>

      {/* Disclaimer */}
      <div className="flex items-start gap-3 px-4 py-3 bg-amber-500/10 border border-amber-500/30 rounded-xl">
        <Info className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-amber-300">
          <strong>Preparation tool only.</strong> This is not a truthfulness verdict or background check — it is designed to help you articulate your experience better.
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-3">
        {loadingResumes ? (
          <div className="flex items-center gap-2 text-gray-400 text-sm"><Spinner /> Loading resumes…</div>
        ) : (
          <select
            value={selectedResumeId}
            onChange={(e) => handleResumeChange(Number(e.target.value))}
            className="flex-1 bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2.5 outline-none"
            aria-label="Select resume for evidence checking"
          >
            <option value="">-- Select Resume --</option>
            {resumes.map((r) => (
              <option key={r.id} value={r.id}>{r.filename}</option>
            ))}
          </select>
        )}
        <button
          onClick={handleExtract}
          disabled={!selectedResumeId || extracting}
          className="flex items-center justify-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl"
        >
          {extracting ? <Spinner /> : <ShieldCheck className="w-4 h-4" />}
          {extracting ? 'Extracting…' : 'Extract Claims'}
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-rose-400 text-sm">
          <AlertCircle className="w-4 h-4" /> {error}
        </div>
      )}

      {/* Summary */}
      {claims.length > 0 && (
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Verified Strong', count: verified, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30' },
            { label: 'Practiced', count: practiced, color: 'text-sky-400', bg: 'bg-sky-500/10 border-sky-500/30' },
            { label: 'Needs Prep', count: needsPrep, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/30' },
          ].map((s) => (
            <div key={s.label} className={`${s.bg} border rounded-xl px-4 py-3 text-center`}>
              <p className={`text-2xl font-extrabold ${s.color}`}>{s.count}</p>
              <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Claims List */}
      {loading ? (
        <div className="flex items-center justify-center py-12 text-gray-400">
          <Spinner /> <span className="ml-3">Loading claims…</span>
        </div>
      ) : claims.length > 0 ? (
        <div className="space-y-3">
          {claims.map((claim) => (
            <ClaimCard
              key={claim.id}
              claim={claim}
              onSubmitDefense={async (id, answer) => {
                const res = await handleSubmitDefense(id, answer);
                updateClaimStatus(id, res.status);
                return res;
              }}
            />
          ))}
        </div>
      ) : selectedResumeId ? (
        <div className="text-center py-12 text-gray-400">
          <ShieldCheck className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p>No claims extracted yet. Click "Extract Claims" to begin.</p>
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          <p>Select a resume to get started.</p>
        </div>
      )}
    </div>
  );
};
