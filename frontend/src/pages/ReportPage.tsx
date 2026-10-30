import React, { useState, useEffect, useCallback } from 'react';
import { Loader2, Download, BookOpen, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { api, getToken } from '../services/api';
import { ScoreGauge } from '../components/ScoreGauge';

interface ReportPageProps {
  onNavigate: (page: string, params?: unknown) => void;
  sessionId: number;
}

function Spinner() { return <Loader2 className="w-4 h-4 animate-spin" />; }

function ScoreBar({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value);
  const color = pct >= 75 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-500' : 'bg-rose-500';
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-500">{label}</span>
        <span className="text-gray-800 font-semibold">{pct}/100</span>
      </div>
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all duration-700`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function ReadinessBadge({ score }: { score: number }) {
  const s = Math.round(score);
  const label = s >= 80 ? 'Interview Ready' : s >= 60 ? 'Nearly Ready' : s >= 40 ? 'Developing' : 'Needs Work';
  const color = s >= 80 ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40' :
    s >= 60 ? 'bg-sky-500/20 text-sky-400 border-sky-500/40' :
    s >= 40 ? 'bg-amber-500/20 text-amber-400 border-amber-500/40' :
    'bg-rose-500/20 text-rose-400 border-rose-500/40';
  return <span className={`px-3 py-1 border rounded-full text-sm font-semibold ${color}`}>{label}</span>;
}

type AnyRecord = Record<string, unknown>;

export const ReportPage: React.FC<ReportPageProps> = ({ onNavigate, sessionId }) => {
  const [report, setReport] = useState<AnyRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedQ, setExpandedQ] = useState<number | null>(0);

  const fetchReport = useCallback(async () => {
    try {
      const r = await api.getSessionReport(sessionId);
      setReport(r);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load report');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => { fetchReport(); }, [fetchReport]);

  const handleDownloadPdf = () => {
    const url = api.getPdfReportDownloadUrl(sessionId);
    const token = getToken();
    // Open in new tab with auth header via fetch
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.blob())
      .then((blob) => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `interview-report-${sessionId}.pdf`;
        a.click();
      })
      .catch(() => window.open(url, '_blank'));
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-gray-400">
        <Spinner /> <span className="ml-3 mt-2">Loading report…</span>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-rose-400">
        <AlertCircle className="w-10 h-10" />
        <p>{error || 'Report not found'}</p>
        <button onClick={() => onNavigate('history')} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-xl text-sm">
          Back to History
        </button>
      </div>
    );
  }

  const session = report.session as AnyRecord;
  const questions = (report.questions as AnyRecord[]) || [];
  const overallScore = session.overall_score as number ?? 0;
  const readinessScore = session.readiness_score as number ?? 0;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{session.title as string}</h1>
          <p className="text-gray-500 text-sm mt-1">
            {new Date(session.created_at as string).toLocaleDateString()} ·{' '}
            <span className="capitalize">{session.difficulty_level as string}</span> ·{' '}
            {session.total_questions as number} questions
          </p>
        </div>
        <div className="flex items-center gap-3">
          <ReadinessBadge score={readinessScore} />
          <button
            onClick={handleDownloadPdf}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 border border-gray-300 text-gray-700 hover:text-gray-900 rounded-xl text-sm font-semibold"
          >
            <Download className="w-4 h-4" /> PDF
          </button>
        </div>
      </div>

      {/* Score Summary */}
      <div className="grid sm:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-2xl p-6 flex flex-col items-center">
          <ScoreGauge score={overallScore} size={180} label="Overall Score" />
        </div>
        <div className="bg-white border border-gray-200 rounded-2xl p-6 flex flex-col items-center">
          <ScoreGauge score={readinessScore} size={180} label="Readiness Index" sublabel="Estimated interview readiness" />
        </div>
      </div>

      {/* Summary Feedback */}
      {session.summary_feedback && (
        <div className="bg-white border border-gray-200 rounded-2xl p-5">
          <h2 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-indigo-400" /> Overall Summary
          </h2>
          <p className="text-gray-700 text-sm leading-relaxed">{session.summary_feedback as string}</p>
        </div>
      )}

      {/* Question Breakdowns */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-gray-900">Question-by-Question Breakdown</h2>
        {questions.map((q: AnyRecord, idx: number) => {
          const evaluation = q.evaluation as AnyRecord | undefined;
          const answer = q.answer as AnyRecord | undefined;
          const isExpanded = expandedQ === idx;
          return (
            <div key={q.id as number} className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
              <button
                onClick={() => setExpandedQ(isExpanded ? null : idx)}
                className="w-full flex items-start gap-4 px-5 py-4 text-left hover:bg-white/40"
              >
                <div className="flex-shrink-0 w-7 h-7 rounded-full bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-xs font-bold text-indigo-400">
                  {idx + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <span className="text-xs text-gray-400 capitalize">{q.category as string}</span>
                    <span className="text-xs text-gray-400 capitalize">{q.difficulty as string}</span>
                  </div>
                  <p className="text-gray-800 text-sm font-medium">{q.question_text as string}</p>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0">
                  {evaluation && (
                    <span className={`text-sm font-bold ${(evaluation.overall_score as number) >= 75 ? 'text-emerald-400' : (evaluation.overall_score as number) >= 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                      {Math.round(evaluation.overall_score as number)}/100
                    </span>
                  )}
                  {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                </div>
              </button>

              {isExpanded && (
                <div className="px-5 pb-5 space-y-5 border-t border-gray-200 pt-4">
                  {/* Answer */}
                  {answer && (
                    <div>
                      <p className="text-xs font-bold text-gray-400 mb-2">YOUR ANSWER</p>
                      <div className="bg-gray-100 rounded-xl px-4 py-3 text-gray-700 text-sm whitespace-pre-wrap">
                        {answer.answer_text as string}
                      </div>
                    </div>
                  )}

                  {/* Evaluation */}
                  {evaluation && (
                    <>
                      <div>
                        <p className="text-xs font-bold text-gray-400 mb-3">RUBRIC BREAKDOWN</p>
                        <div className="space-y-2">
                          <ScoreBar label="Relevance" value={evaluation.relevance_score as number} />
                          <ScoreBar label="Technical Accuracy" value={evaluation.technical_score as number} />
                          <ScoreBar label="Completeness" value={evaluation.completeness_score as number} />
                          <ScoreBar label="Clarity" value={evaluation.clarity_score as number} />
                          <ScoreBar label="Reasoning" value={evaluation.reasoning_score as number} />
                        </div>
                      </div>

                      <div>
                        <p className="text-xs font-bold text-gray-400 mb-2">FEEDBACK</p>
                        <p className="text-gray-700 text-sm">{evaluation.feedback_critique as string}</p>
                      </div>

                      {Array.isArray(evaluation.strengths) && (evaluation.strengths as string[]).length > 0 && (
                        <div>
                          <p className="text-xs font-bold text-emerald-500 mb-2">✓ STRENGTHS</p>
                          <ul className="space-y-1">
                            {(evaluation.strengths as string[]).map((s, i) => (
                              <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                                <span className="text-emerald-500 mt-0.5">•</span>{s}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {Array.isArray(evaluation.improvements) && (evaluation.improvements as string[]).length > 0 && (
                        <div>
                          <p className="text-xs font-bold text-amber-500 mb-2">↑ IMPROVEMENTS</p>
                          <ul className="space-y-1">
                            {(evaluation.improvements as string[]).map((s, i) => (
                              <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                                <span className="text-amber-400 mt-0.5">•</span>{s}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      <div>
                        <p className="text-xs font-bold text-gray-400 mb-2">MODEL ANSWER</p>
                        <div className="bg-indigo-500/5 border border-indigo-500/20 rounded-xl px-4 py-3 text-gray-700 text-sm whitespace-pre-wrap">
                          {evaluation.model_answer as string}
                        </div>
                      </div>

                      {evaluation.disclaimer && (
                        <p className="text-xs text-gray-400 italic">{evaluation.disclaimer as string}</p>
                      )}
                    </>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="text-center">
        <button
          onClick={() => onNavigate('interview-setup')}
          className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl text-sm"
        >
          Start New Interview
        </button>
      </div>
    </div>
  );
};
