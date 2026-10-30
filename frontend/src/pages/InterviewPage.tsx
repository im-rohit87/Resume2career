import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Loader2, CheckCircle, ChevronDown, ChevronUp, AlertCircle,
  Clock, Flag, ArrowRight, Trophy, BookOpen
} from 'lucide-react';
import { api } from '../services/api';
import { InterviewSession, QuestionItem, QuestionEvaluation } from '../types';
import { ScoreGauge } from '../components/ScoreGauge';
import { AudioRecorder } from '../components/AudioRecorder';
import { VoiceSpeaker } from '../components/VoiceSpeaker';

interface InterviewPageProps {
  onNavigate: (page: string, params?: unknown) => void;
  sessionId: number;
}

function Spinner({ size = 'sm' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sz = size === 'lg' ? 'w-10 h-10' : size === 'md' ? 'w-6 h-6' : 'w-4 h-4';
  return <Loader2 className={`animate-spin ${sz}`} />;
}

const CATEGORY_COLORS: Record<string, string> = {
  technical: 'bg-blue-500/20 text-blue-300 border-blue-500/40',
  behavioral: 'bg-orange-500/20 text-orange-300 border-orange-500/40',
  hr: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
  project: 'bg-purple-500/20 text-purple-300 border-purple-500/40',
};

const DIFF_COLORS: Record<string, string> = {
  beginner: 'bg-emerald-500/20 text-emerald-400',
  intermediate: 'bg-amber-500/20 text-amber-400',
  advanced: 'bg-rose-500/20 text-rose-400',
};

function ScoreCriterionBar({ label, value }: { label: string; value: number }) {
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

function useTimer() {
  const [elapsed, setElapsed] = useState(0);
  const ref = useRef<ReturnType<typeof setInterval> | null>(null);

  const start = useCallback(() => {
    setElapsed(0);
    if (ref.current) clearInterval(ref.current);
    ref.current = setInterval(() => setElapsed((s) => s + 1), 1000);
  }, []);

  const stop = useCallback(() => {
    if (ref.current) { clearInterval(ref.current); ref.current = null; }
  }, []);

  const reset = useCallback(() => {
    stop();
    setElapsed(0);
  }, [stop]);

  useEffect(() => () => { if (ref.current) clearInterval(ref.current); }, []);

  return { elapsed, start, stop, reset };
}

function formatTime(s: number) {
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
}

export const InterviewPage: React.FC<InterviewPageProps> = ({ onNavigate, sessionId }) => {
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answer, setAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [evaluation, setEvaluation] = useState<QuestionEvaluation | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [showModelAnswer, setShowModelAnswer] = useState(false);
  const [finishing, setFinishing] = useState(false);
  const [finished, setFinished] = useState(false);
  const [error, setError] = useState('');
  const { elapsed, start, stop } = useTimer();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const fetchSession = useCallback(async () => {
    try {
      const s = await api.getInterviewSession(sessionId);
      setSession(s);
      if (s.status === 'completed') { setFinished(true); }
      // Find first unanswered
      const firstUnanswered = s.questions.findIndex((q) => !q.is_answered);
      setCurrentIdx(firstUnanswered >= 0 ? firstUnanswered : s.questions.length - 1);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load session');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => { fetchSession(); }, [fetchSession]);
  useEffect(() => {
    if (!submitted) start();
    else stop();
  }, [currentIdx, submitted, start, stop]);

  // Warn on page refresh
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (!finished) {
        e.preventDefault();
        e.returnValue = 'Your interview is in progress. Are you sure you want to leave?';
      }
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [finished]);

  const currentQuestion: QuestionItem | undefined = session?.questions[currentIdx];

  const handleVoiceTranscript = (transcript: string) => {
    setAnswer((prev) => (prev ? prev + ' ' + transcript : transcript));
    textareaRef.current?.focus();
  };

  const handleSubmit = async () => {
    if (!currentQuestion || !answer.trim() || submitted || submitting) return;
    stop();
    setSubmitting(true);
    setError('');
    try {
      const result = await api.submitAnswer({
        question_id: currentQuestion.id,
        answer_text: answer.trim(),
        speech_used: false,
        time_taken_seconds: elapsed,
      });
      setEvaluation(result);
      setSubmitted(true);
      // Update session question
      setSession((prev) => {
        if (!prev) return prev;
        const qs = prev.questions.map((q, i) =>
          i === currentIdx ? { ...q, is_answered: true, answer: { id: 0, answer_text: answer.trim(), speech_used: false, time_taken_seconds: elapsed, submitted_at: new Date().toISOString(), evaluation: result } } : q
        );
        return { ...prev, questions: qs };
      });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  const handleNext = () => {
    if (!session) return;
    const nextIdx = currentIdx + 1;
    if (nextIdx < session.questions.length) {
      setCurrentIdx(nextIdx);
      setAnswer('');
      setEvaluation(null);
      setSubmitted(false);
      setShowModelAnswer(false);
      setError('');
    } else {
      // All answered
    }
  };

  const handleFinish = async () => {
    setFinishing(true);
    try {
      await api.finishInterview(sessionId);
      setFinished(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to finish interview');
    } finally {
      setFinishing(false);
    }
  };

  const goToQuestion = (idx: number) => {
    if (!session) return;
    const q = session.questions[idx];
    setCurrentIdx(idx);
    if (q.is_answered && q.answer?.evaluation) {
      setEvaluation(q.answer.evaluation);
      setAnswer(q.answer.answer_text || '');
      setSubmitted(true);
    } else {
      setEvaluation(null);
      setAnswer('');
      setSubmitted(false);
    }
    setShowModelAnswer(false);
    setError('');
  };

  const allAnswered = session ? session.questions.every((q) => q.is_answered) : false;

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-gray-400">
        <Spinner size="lg" />
        <p className="mt-4 text-sm">Loading interview session…</p>
      </div>
    );
  }

  if (error && !session) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-rose-400">
        <AlertCircle className="w-10 h-10" />
        <p>{error}</p>
      </div>
    );
  }

  if (finished && session) {
    const score = session.overall_score ?? 0;
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center space-y-8">
        <div className="bg-white border border-gray-200 rounded-2xl p-10 space-y-6">
          <Trophy className="w-12 h-12 text-amber-400 mx-auto" />
          <h1 className="text-2xl font-extrabold text-gray-900">Interview Complete!</h1>
          <p className="text-gray-500">{session.title}</p>
          <ScoreGauge score={score} size={180} label="Overall Score" sublabel={`Readiness: ${Math.round(session.readiness_score ?? 0)}/100`} />
          {session.summary_feedback && (
            <p className="text-gray-700 text-sm italic">{session.summary_feedback}</p>
          )}
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={() => onNavigate('report', { sessionId })}
              className="flex items-center justify-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl text-sm"
            >
              <BookOpen className="w-4 h-4" /> View Full Report
            </button>
            <button
              onClick={() => onNavigate('interview-setup')}
              className="px-5 py-2.5 border border-gray-300 text-gray-700 hover:text-gray-900 rounded-xl text-sm"
            >
              New Interview
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!session || !currentQuestion) return null;

  const catColor = CATEGORY_COLORS[currentQuestion.category] || 'bg-slate-700 text-gray-700 border-gray-300';
  const diffColor = DIFF_COLORS[currentQuestion.difficulty] || 'bg-slate-700/50 text-gray-500';

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-lg font-bold text-gray-900 truncate">{session.title}</h1>
          <p className="text-gray-400 text-xs capitalize">{session.difficulty_level} difficulty</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-gray-500 text-sm">
            <Clock className="w-4 h-4" />
            <span className="font-mono">{formatTime(elapsed)}</span>
          </div>
          <span className="text-gray-500 text-sm">Q {currentIdx + 1} / {session.total_questions}</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-indigo-600 rounded-full transition-all duration-500"
          style={{ width: `${((currentIdx + (submitted ? 1 : 0)) / session.total_questions) * 100}%` }}
        />
      </div>

      {/* Question Tabs */}
      <div className="flex gap-1.5 flex-wrap">
        {session.questions.map((q, i) => (
          <button
            key={q.id}
            onClick={() => goToQuestion(i)}
            className={`w-8 h-8 rounded-lg text-xs font-bold transition-all ${
              i === currentIdx ? 'bg-indigo-600 text-white' :
              q.is_answered ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' :
              'bg-gray-100 text-gray-500 hover:bg-gray-300'
            }`}
          >
            {i + 1}
          </button>
        ))}
      </div>

      {/* Question Card */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-bold text-gray-400">#{currentIdx + 1}</span>
            <span className={`px-2 py-0.5 border rounded-lg text-xs font-semibold capitalize ${catColor}`}>
              {currentQuestion.category}
            </span>
            <span className={`px-2 py-0.5 rounded-lg text-xs font-semibold capitalize ${diffColor}`}>
              {currentQuestion.difficulty}
            </span>
          </div>
          <VoiceSpeaker textToSpeak={currentQuestion.question_text} />
        </div>

        <p className="text-gray-900 font-semibold text-base leading-relaxed">{currentQuestion.question_text}</p>

        {currentQuestion.context_grounding && (
          <p className="text-gray-400 text-sm italic">Context: {currentQuestion.context_grounding}</p>
        )}
      </div>

      {/* Answer Area */}
      {!submitted && (
        <div className="space-y-4">
          <div>
            <label htmlFor="answer-text" className="block text-xs font-semibold text-gray-500 mb-2">
              Your Answer
            </label>
            <textarea
              id="answer-text"
              ref={textareaRef}
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              rows={5}
              placeholder="Type your answer here…"
              className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-4 py-3 outline-none resize-y"
            />
            <div className="flex justify-between mt-1">
              <AudioRecorder onTranscript={handleVoiceTranscript} />
              <span className="text-xs text-gray-400">{answer.length} chars</span>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 text-rose-400 text-sm">
              <AlertCircle className="w-4 h-4" /> {error}
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={!answer.trim() || submitting}
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold rounded-xl text-sm"
          >
            {submitting ? <Spinner /> : <CheckCircle className="w-4 h-4" />}
            {submitting ? 'Evaluating…' : 'Submit Answer'}
          </button>
        </div>
      )}

      {/* Evaluation Panel */}
      {submitted && evaluation && (
        <div className="space-y-4">
          <div className="bg-white border border-gray-200 rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-gray-900">Evaluation</h3>
              <span className={`text-lg font-extrabold ${evaluation.overall_score >= 75 ? 'text-emerald-400' : evaluation.overall_score >= 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                {Math.round(evaluation.overall_score)}/100
              </span>
            </div>

            <div className="space-y-2">
              <ScoreCriterionBar label="Relevance" value={evaluation.relevance_score} />
              <ScoreCriterionBar label="Technical Accuracy" value={evaluation.technical_score} />
              <ScoreCriterionBar label="Completeness" value={evaluation.completeness_score} />
              <ScoreCriterionBar label="Clarity" value={evaluation.clarity_score} />
              <ScoreCriterionBar label="Reasoning" value={evaluation.reasoning_score} />
            </div>

            <p className="text-gray-700 text-sm">{evaluation.feedback_critique}</p>

            {evaluation.strengths.length > 0 && (
              <div>
                <p className="text-xs font-bold text-emerald-400 mb-1.5">✓ Strengths</p>
                <ul className="space-y-1">
                  {evaluation.strengths.map((s, i) => (
                    <li key={i} className="text-sm text-gray-700 flex items-start gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-500 mt-0.5 flex-shrink-0" />{s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {evaluation.improvements.length > 0 && (
              <div>
                <p className="text-xs font-bold text-amber-400 mb-1.5">↑ Improvements</p>
                <ul className="space-y-1">
                  {evaluation.improvements.map((s, i) => (
                    <li key={i} className="text-sm text-gray-700 flex items-start gap-1.5">
                      <span className="text-amber-400 mt-0.5">•</span>{s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {evaluation.adaptive_next_difficulty && (
              <p className="text-xs text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 rounded-lg px-3 py-2">
                Next question difficulty: <strong className="capitalize">{evaluation.adaptive_next_difficulty}</strong>
              </p>
            )}

            {/* Model Answer */}
            <div>
              <button
                onClick={() => setShowModelAnswer(!showModelAnswer)}
                className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors"
              >
                {showModelAnswer ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                {showModelAnswer ? 'Hide' : 'Show'} Model Answer
              </button>
              {showModelAnswer && (
                <div className="mt-3 px-4 py-3 bg-gray-100 border border-gray-300 rounded-xl text-gray-700 text-sm whitespace-pre-wrap">
                  {evaluation.model_answer}
                </div>
              )}
            </div>

            {evaluation.disclaimer && (
              <p className="text-xs text-gray-400 italic">{evaluation.disclaimer}</p>
            )}
          </div>

          <div className="flex gap-3">
            {currentIdx + 1 < session.total_questions ? (
              <button
                onClick={handleNext}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl text-sm"
              >
                <ArrowRight className="w-4 h-4" /> Next Question
              </button>
            ) : (
              <button
                onClick={handleFinish}
                disabled={finishing}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl text-sm"
              >
                {finishing ? <Spinner /> : <Trophy className="w-4 h-4" />}
                {finishing ? 'Finishing…' : 'Finish & See Report'}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Finish Button (always visible when all answered) */}
      {allAnswered && !finished && submitted && currentIdx === session.total_questions - 1 && (
        <div className="border-t border-gray-200 pt-4">
          <button
            onClick={handleFinish}
            disabled={finishing}
            className="flex items-center justify-center gap-2 w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl text-sm"
          >
            {finishing ? <Spinner /> : <Flag className="w-4 h-4" />}
            {finishing ? 'Finishing…' : 'Complete Interview'}
          </button>
        </div>
      )}
    </div>
  );
};
