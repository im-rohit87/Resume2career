import React, { useState, useEffect, useCallback } from 'react';
import { History, Briefcase, PlayCircle, ChevronRight, ChevronDown, Loader2 } from 'lucide-react';
import { api } from '../services/api';

interface HistoryPageProps {
  onNavigate: (page: string, params?: unknown) => void;
}

function Spinner() { return <Loader2 className="w-4 h-4 animate-spin" />; }

type Tab = 'interviews' | 'matches';

function MiniScoreBadge({ score }: { score: number }) {
  const rounded = Math.round(score);
  const color = rounded >= 75 ? 'bg-emerald-500/20 text-emerald-400' : rounded >= 50 ? 'bg-amber-500/20 text-amber-400' : 'bg-rose-500/20 text-rose-400';
  return <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${color}`}>{rounded}</span>;
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    in_progress: 'bg-indigo-500/20 text-indigo-400',
    completed: 'bg-emerald-500/20 text-emerald-400',
    abandoned: 'bg-slate-700 text-gray-400',
  };
  const labels: Record<string, string> = {
    in_progress: 'In Progress',
    completed: 'Completed',
    abandoned: 'Abandoned',
  };
  return <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${styles[status] || 'bg-slate-700 text-gray-500'}`}>{labels[status] || status}</span>;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({ onNavigate }) => {
  const [tab, setTab] = useState<Tab>('interviews');
  const [interviews, setInterviews] = useState<unknown[]>([]);
  const [matches, setMatches] = useState<unknown[]>([]);
  const [loadingI, setLoadingI] = useState(true);
  const [loadingM, setLoadingM] = useState(true);
  const [expandedMatch, setExpandedMatch] = useState<number | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const i = await api.getInterviewHistory();
      setInterviews(i);
    } catch (e) { console.error(e); }
    finally { setLoadingI(false); }

    try {
      const m = await api.getMatchHistory();
      setMatches(m);
    } catch (e) { console.error(e); }
    finally { setLoadingM(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  type AnyRecord = Record<string, unknown>;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">History</h1>
        <p className="text-gray-500 text-sm mt-1">Your past interviews and job match analyses.</p>
      </div>

      {/* Tabs */}
      <div className="flex bg-gray-100 rounded-xl p-1 gap-1 w-fit">
        {(['interviews', 'matches'] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all capitalize ${
              tab === t ? 'bg-indigo-600 text-white' : 'text-gray-500 hover:text-gray-800'
            }`}
          >
            {t === 'interviews' ? 'Interviews' : 'Job Matches'}
          </button>
        ))}
      </div>

      {/* Interviews Tab */}
      {tab === 'interviews' && (
        <div className="space-y-3">
          {loadingI ? (
            <div className="flex items-center gap-2 text-gray-400 py-8 justify-center"><Spinner /><span>Loading…</span></div>
          ) : interviews.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <PlayCircle className="w-10 h-10 mx-auto mb-3 opacity-30" />
              <p className="font-semibold text-gray-500">No interviews yet</p>
              <p className="text-sm mt-1">Start your first mock interview to see results here.</p>
              <button
                onClick={() => onNavigate('interview-setup')}
                className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl"
              >
                Start Interview
              </button>
            </div>
          ) : (
            interviews.map((session: unknown) => {
              const s = session as AnyRecord;
              return (
                <div
                  key={s.id as number}
                  className="flex items-center gap-4 px-4 py-3 bg-white border border-gray-200 rounded-xl cursor-pointer hover:border-gray-300 transition-all"
                  onClick={() => onNavigate('report', { sessionId: s.id })}
                >
                  <PlayCircle className="w-5 h-5 text-indigo-400 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-gray-800 font-semibold text-sm truncate">{s.title as string}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <StatusBadge status={s.status as string} />
                      <span className="text-gray-400 text-xs">{new Date(s.created_at as string).toLocaleDateString()}</span>
                    </div>
                  </div>
                  {(s.overall_score != null) && <MiniScoreBadge score={s.overall_score as number} />}
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Matches Tab */}
      {tab === 'matches' && (
        <div className="space-y-3">
          {loadingM ? (
            <div className="flex items-center gap-2 text-gray-400 py-8 justify-center"><Spinner /><span>Loading…</span></div>
          ) : matches.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <Briefcase className="w-10 h-10 mx-auto mb-3 opacity-30" />
              <p className="font-semibold text-gray-500">No job matches yet</p>
              <p className="text-sm mt-1">Analyze a job description to see match history here.</p>
              <button
                onClick={() => onNavigate('matching')}
                className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl"
              >
                Analyze a Job
              </button>
            </div>
          ) : (
            matches.map((match: unknown) => {
              const m = match as AnyRecord;
              return (
                <div key={m.id as number} className="bg-white border border-gray-200 rounded-xl overflow-hidden">
                  <button
                    onClick={() => setExpandedMatch(expandedMatch === m.id ? null : m.id as number)}
                    className="w-full flex items-center gap-4 px-4 py-3 hover:bg-white/40 text-left"
                  >
                    <Briefcase className="w-4 h-4 text-indigo-400 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-gray-800 text-sm font-semibold truncate">
                        {m.role_title as string}{m.company_name ? ` @ ${m.company_name as string}` : ''}
                      </p>
                      <p className="text-gray-400 text-xs">{new Date(m.created_at as string).toLocaleDateString()}</p>
                    </div>
                    <MiniScoreBadge score={m.match_score as number} />
                    {expandedMatch === m.id ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
                  </button>
                  {expandedMatch === m.id && (
                    <div className="px-4 pb-4 pt-2 border-t border-gray-200 text-sm text-gray-500 space-y-2">
                      <div>
                        <span className="text-gray-400 text-xs">Required coverage: </span>
                        <span className="text-gray-800">{Math.round((m.score_breakdown as AnyRecord)?.required_skills_coverage as number)}%</span>
                        <span className="text-gray-400 text-xs ml-3">Preferred: </span>
                        <span className="text-gray-800">{Math.round((m.score_breakdown as AnyRecord)?.preferred_skills_coverage as number)}%</span>
                      </div>
                      {Array.isArray(m.recommendations) && (m.recommendations as string[]).length > 0 && (
                        <ul className="space-y-1">
                          {(m.recommendations as string[]).slice(0, 3).map((rec, i) => (
                            <li key={i} className="flex items-start gap-1.5">
                              <span className="text-indigo-400 font-bold">{i + 1}.</span>{rec}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
};
