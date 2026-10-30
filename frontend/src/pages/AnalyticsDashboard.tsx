import React, { useState, useEffect, useCallback } from 'react';
import { Loader2, PlayCircle, AlertCircle, TrendingUp } from 'lucide-react';
import { api } from '../services/api';
import { AnalyticsDashboard as AnalyticsData } from '../types';
import { ScoreGauge } from '../components/ScoreGauge';
import { TrendChart } from '../components/TrendChart';
import { RadarChart } from '../components/RadarChart';

interface AnalyticsDashboardProps {
  onNavigate: (page: string, params?: unknown) => void;
}

function Spinner() { return <Loader2 className="w-5 h-5 animate-spin" />; }

function StatCard({ label, value, sub, color = 'text-gray-900' }: { label: string; value: string | number; sub?: string; color?: string }) {
  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-5">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">{label}</p>
      <p className={`text-3xl font-extrabold ${color}`}>{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  );
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ onNavigate }) => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchData = useCallback(async () => {
    try {
      const d = await api.getDashboardAnalytics();
      setData(d);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-gray-400 gap-3">
        <Spinner />
        <p className="text-sm">Loading dashboard…</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-rose-400">
        <AlertCircle className="w-10 h-10" />
        <p>{error}</p>
      </div>
    );
  }

  if (data.total_interviews === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-6">
        <TrendingUp className="w-16 h-16 text-indigo-400 mx-auto opacity-50" />
        <h1 className="text-2xl font-bold text-gray-900">Your Dashboard</h1>
        <p className="text-gray-500">No interview data yet. Complete your first mock interview to see analytics here.</p>
        <button
          onClick={() => onNavigate('interview-setup')}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl"
        >
          <PlayCircle className="w-5 h-5" /> Start First Interview
        </button>
      </div>
    );
  }

  const radarData = {
    relevance: data.criterion_averages.relevance,
    technical: data.criterion_averages.technical,
    completeness: data.criterion_averages.completeness,
    clarity: data.criterion_averages.clarity,
    reasoning: data.criterion_averages.reasoning,
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Performance Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Your interview performance analytics and readiness trends.</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Interviews" value={data.total_interviews} />
        <StatCard
          label="Average Score"
          value={`${Math.round(data.average_score)}/100`}
          color={data.average_score >= 75 ? 'text-emerald-400' : data.average_score >= 50 ? 'text-amber-400' : 'text-rose-400'}
        />
        <StatCard
          label="Readiness Index"
          value={`${Math.round(data.readiness_index)}/100`}
          sub="Estimated interview readiness"
          color={data.readiness_index >= 75 ? 'text-emerald-400' : data.readiness_index >= 50 ? 'text-amber-400' : 'text-rose-400'}
        />
        <StatCard
          label="Last Session"
          value={data.history_trend.length > 0 ? `${Math.round(data.history_trend[data.history_trend.length - 1].score)}/100` : 'N/A'}
        />
      </div>

      {/* Gauge + Radar */}
      <div className="grid sm:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-2xl p-6 flex flex-col items-center">
          <ScoreGauge
            score={data.readiness_index}
            size={180}
            label="Overall Readiness"
            sublabel={data.readiness_formula}
          />
        </div>
        <div className="bg-white border border-gray-200 rounded-2xl p-6">
          <h3 className="font-bold text-gray-900 text-sm mb-4">Criterion Averages</h3>
          <RadarChart data={{
            relevance: data.criterion_averages.relevance,
            technical: data.criterion_averages.technical,
            completeness: data.criterion_averages.completeness,
            clarity: data.criterion_averages.clarity,
            reasoning: data.criterion_averages.reasoning,
          }} size={220} />
        </div>
      </div>

      {/* Trend Chart */}
      {data.history_trend.length > 1 && (
        <div className="bg-white border border-gray-200 rounded-2xl p-6">
          <h3 className="font-bold text-gray-900 text-sm mb-4">Score Trend</h3>
          <TrendChart
            data={data.history_trend.map((h) => ({ session_number: h.session_number, title: h.title, date: h.date, score: h.score, readiness: h.readiness }))}
          />
        </div>
      )}

      {/* Strong / Weak Topics */}
      <div className="grid sm:grid-cols-2 gap-6">
        {data.strong_topics.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-2xl p-5">
            <h3 className="font-bold text-emerald-400 text-sm mb-3">✓ Strong Topics</h3>
            <div className="flex flex-wrap gap-2">
              {data.strong_topics.map((t, i) => (
                <span key={i} className="px-2 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 rounded-lg text-xs">{t}</span>
              ))}
            </div>
          </div>
        )}
        {data.weak_topics.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-2xl p-5">
            <h3 className="font-bold text-amber-400 text-sm mb-3">↑ Topics to Improve</h3>
            <div className="flex flex-wrap gap-2">
              {data.weak_topics.map((t, i) => (
                <span key={i} className="px-2 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-300 rounded-lg text-xs">{t}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="px-2">
        <p className="text-xs text-gray-400 italic">{data.disclaimer}</p>
      </div>

      <div className="text-center">
        <button
          onClick={() => onNavigate('interview-setup')}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl"
        >
          <PlayCircle className="w-4 h-4" /> New Interview
        </button>
      </div>
    </div>
  );
};
