import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, Plus, X, Loader2, AlertCircle, ChevronDown, ChevronUp, BookOpen } from 'lucide-react';
import { api } from '../services/api';
import { LearningPlan, DailyMilestone } from '../types';

interface LearningPlanPageProps {
  onNavigate: (page: string, params?: unknown) => void;
}

function Spinner() { return <Loader2 className="w-4 h-4 animate-spin" />; }

const DURATIONS = [
  { value: 7, label: '7 Days', desc: 'Quick sprint' },
  { value: 15, label: '15 Days', desc: 'Focused prep' },
  { value: 30, label: '30 Days', desc: 'Deep dive' },
];

function DayCard({ milestone, isOpen, onToggle }: {
  milestone: DailyMilestone; isOpen: boolean; onToggle: () => void;
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-4 px-4 py-3 text-left hover:bg-white/40"
      >
        <div className="w-8 h-8 rounded-full bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-xs font-bold text-indigo-400 flex-shrink-0">
          {milestone.day}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-gray-800 font-semibold text-sm">{milestone.focus_topic}</p>
          <p className="text-gray-400 text-xs">{milestone.learning_objectives.length} objectives</p>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
      </button>
      {isOpen && (
        <div className="px-4 pb-4 pt-2 space-y-3 border-t border-gray-200">
          {milestone.learning_objectives.length > 0 && (
            <div>
              <p className="text-xs font-bold text-gray-400 mb-2">OBJECTIVES</p>
              <ul className="space-y-1.5">
                {milestone.learning_objectives.map((obj, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="text-indigo-400 font-bold mt-0.5">{i + 1}.</span>{obj}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {milestone.practice_challenge && (
            <div className="bg-amber-500/5 border border-amber-500/20 rounded-xl px-4 py-3">
              <p className="text-xs font-bold text-amber-400 mb-1">PRACTICE CHALLENGE</p>
              <p className="text-gray-700 text-sm">{milestone.practice_challenge}</p>
            </div>
          )}
          {milestone.recommended_resources.length > 0 && (
            <div>
              <p className="text-xs font-bold text-gray-400 mb-2">RESOURCES</p>
              <ul className="space-y-1">
                {milestone.recommended_resources.map((r, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-500">
                    <BookOpen className="w-3.5 h-3.5 text-indigo-400 mt-0.5 flex-shrink-0" />{r}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export const LearningPlanPage: React.FC<LearningPlanPageProps> = () => {
  const [plans, setPlans] = useState<LearningPlan[]>([]);
  const [duration, setDuration] = useState(15);
  const [targetRole, setTargetRole] = useState('');
  const [focusSkills, setFocusSkills] = useState<string[]>([]);
  const [skillInput, setSkillInput] = useState('');
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [activePlan, setActivePlan] = useState<LearningPlan | null>(null);
  const [expandedDay, setExpandedDay] = useState<number | null>(1);
  const [loading, setLoading] = useState(true);

  const fetchPlans = useCallback(async () => {
    try {
      const p = await api.getLearningPlans();
      setPlans(p);
      if (p.length > 0) setActivePlan(p[0]);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchPlans(); }, [fetchPlans]);

  const addSkill = () => {
    const v = skillInput.trim();
    if (v && !focusSkills.includes(v)) setFocusSkills([...focusSkills, v]);
    setSkillInput('');
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetRole.trim()) { setError('Target role is required.'); return; }
    setGenerating(true);
    setError('');
    try {
      const plan = await api.createLearningPlan({
        duration_days: duration,
        target_role: targetRole,
        focus_skills: focusSkills.length > 0 ? focusSkills : undefined,
      });
      setPlans((prev) => [plan, ...prev]);
      setActivePlan(plan);
      setExpandedDay(1);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Learning Plan</h1>
        <p className="text-gray-500 text-sm mt-1">Generate a personalized day-by-day preparation plan.</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Generator Form */}
        <form onSubmit={handleGenerate} className="lg:col-span-1 bg-white border border-gray-200 rounded-2xl p-5 space-y-5 h-fit">
          <h2 className="font-bold text-gray-900 text-sm">Generate New Plan</h2>

          {/* Duration */}
          <div>
            <span className="block text-xs font-semibold text-gray-500 mb-2">Duration</span>
            <div className="grid grid-cols-3 gap-2">
              {DURATIONS.map((d) => (
                <button
                  key={d.value}
                  type="button"
                  onClick={() => setDuration(d.value)}
                  className={`flex flex-col items-center py-2 px-1 border rounded-xl text-center transition-all ${
                    duration === d.value
                      ? 'border-indigo-500 bg-indigo-500/10 text-indigo-300'
                      : 'border-gray-300 text-gray-500 hover:border-gray-300'
                  }`}
                >
                  <span className="text-sm font-bold">{d.label}</span>
                  <span className="text-xs text-gray-400">{d.desc}</span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label htmlFor="lp-role" className="block text-xs font-semibold text-gray-500 mb-1.5">
              Target Role <span className="text-rose-400">*</span>
            </label>
            <input
              id="lp-role"
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              placeholder="e.g. Full Stack Engineer"
              className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2.5 outline-none"
            />
          </div>

          <div>
            <label htmlFor="lp-skills" className="block text-xs font-semibold text-gray-500 mb-1.5">
              Focus Skills <span className="text-gray-400">(optional)</span>
            </label>
            <div className="flex flex-wrap gap-1.5 mb-2">
              {focusSkills.map((s, i) => (
                <span key={i} className="flex items-center gap-1 bg-gray-100 border border-gray-300 text-gray-700 text-xs rounded-lg px-2 py-0.5">
                  {s}
                  <button type="button" onClick={() => setFocusSkills(focusSkills.filter((_, j) => j !== i))} className="text-gray-400 hover:text-rose-400">
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                id="lp-skills"
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addSkill(); } }}
                placeholder="React, System Design…"
                className="flex-1 bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-1.5 outline-none"
              />
              <button type="button" onClick={addSkill} className="px-3 py-1.5 bg-gray-100 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-300">
                <Plus className="w-4 h-4" />
              </button>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 text-rose-400 text-sm">
              <AlertCircle className="w-4 h-4" /> {error}
            </div>
          )}

          <button
            type="submit"
            disabled={generating}
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold rounded-xl text-sm"
          >
            {generating ? <Spinner /> : <Calendar className="w-4 h-4" />}
            {generating ? 'Generating…' : 'Generate Plan'}
          </button>

          {/* Past Plans */}
          {plans.length > 0 && (
            <div className="pt-3 border-t border-gray-200">
              <p className="text-xs font-bold text-gray-400 mb-2">PAST PLANS</p>
              <div className="space-y-1.5 max-h-48 overflow-y-auto">
                {plans.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => { setActivePlan(p); setExpandedDay(1); }}
                    className={`w-full text-left px-3 py-2 rounded-xl text-sm transition-all ${
                      activePlan?.id === p.id ? 'bg-indigo-600/20 border border-indigo-500/40 text-indigo-300' : 'text-gray-500 hover:bg-gray-100'
                    }`}
                  >
                    <p className="font-medium truncate">{p.title}</p>
                    <p className="text-xs text-gray-400">{p.duration_days} days · {new Date(p.created_at).toLocaleDateString()}</p>
                  </button>
                ))}
              </div>
            </div>
          )}
        </form>

        {/* Plan Display */}
        <div className="lg:col-span-2">
          {loading ? (
            <div className="flex items-center justify-center py-12 text-gray-400">
              <Spinner /> <span className="ml-3">Loading plans…</span>
            </div>
          ) : activePlan ? (
            <div className="space-y-4">
              <div>
                <h2 className="text-lg font-bold text-gray-900">{activePlan.title}</h2>
                <p className="text-gray-500 text-sm">{activePlan.duration_days}-day plan for {activePlan.target_role}</p>
              </div>
              <div className="space-y-2.5 max-h-[70vh] overflow-y-auto pr-1">
                {activePlan.daily_schedule.map((milestone) => (
                  <DayCard
                    key={milestone.day}
                    milestone={milestone}
                    isOpen={expandedDay === milestone.day}
                    onToggle={() => setExpandedDay(expandedDay === milestone.day ? null : milestone.day)}
                  />
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-gray-400 text-center">
              <Calendar className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p className="font-semibold text-gray-500">No learning plan yet</p>
              <p className="text-sm mt-1">Fill in the form and click "Generate Plan" to create your personalized study schedule.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
