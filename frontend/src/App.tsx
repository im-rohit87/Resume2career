import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { AuthPage } from './pages/AuthPage';
import { ResumesPage } from './pages/ResumesPage';
import { MatchingPage } from './pages/MatchingPage';
import { InterviewSetupPage } from './pages/InterviewSetupPage';
import { InterviewPage } from './pages/InterviewPage';
import { EvidenceCheckerPage } from './pages/EvidenceCheckerPage';
import { HistoryPage } from './pages/HistoryPage';
import { ReportPage } from './pages/ReportPage';
import { AnalyticsDashboard } from './pages/AnalyticsDashboard';
import { LearningPlanPage } from './pages/LearningPlanPage';
import { AdminPage } from './pages/AdminPage';
import { api, getToken, getStoredUser, clearToken } from './services/api';
import { User } from './types';

export default function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [authLoading, setAuthLoading] = useState(true);

  // Validate token on mount
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setAuthLoading(false);
      return;
    }
    const stored = getStoredUser();
    if (stored) {
      setCurrentUser(stored);
      setAuthLoading(false);
    }
    // Re-validate with server in background
    api.getMe()
      .then((user) => setCurrentUser(user))
      .catch(() => {
        clearToken();
        setCurrentUser(null);
      })
      .finally(() => setAuthLoading(false));
  }, []);

  const handleLogin = (user: User) => {
    setCurrentUser(user);
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    clearToken();
    setCurrentUser(null);
    setCurrentPage('dashboard');
    setCurrentSessionId(null);
  };

  const handleNavigate = (page: string, params?: unknown) => {
    const p = params as Record<string, unknown> | undefined;
    if (page === 'interview' && p?.sessionId) {
      setCurrentSessionId(p.sessionId as number);
    }
    if (page === 'report' && p?.sessionId) {
      setCurrentSessionId(p.sessionId as number);
    }
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-gray-400">
          <svg className="w-8 h-8 animate-spin text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
          <p className="text-sm">Loading Resume2Interview AI…</p>
        </div>
      </div>
    );
  }

  if (!currentUser) {
    return <AuthPage onLogin={handleLogin} />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <AnalyticsDashboard onNavigate={handleNavigate} />;
      case 'resumes':
        return <ResumesPage onNavigate={handleNavigate} />;
      case 'matching':
        return <MatchingPage onNavigate={handleNavigate} />;
      case 'interview-setup':
        return <InterviewSetupPage onNavigate={handleNavigate} />;
      case 'interview':
        return currentSessionId
          ? <InterviewPage onNavigate={handleNavigate} sessionId={currentSessionId} />
          : <InterviewSetupPage onNavigate={handleNavigate} />;
      case 'evidence':
        return <EvidenceCheckerPage onNavigate={handleNavigate} />;
      case 'history':
        return <HistoryPage onNavigate={handleNavigate} />;
      case 'report':
        return currentSessionId
          ? <ReportPage onNavigate={handleNavigate} sessionId={currentSessionId} />
          : <HistoryPage onNavigate={handleNavigate} />;
      case 'learning-plan':
        return <LearningPlanPage onNavigate={handleNavigate} />;
      case 'admin':
        return currentUser.role === 'admin'
          ? <AdminPage onNavigate={handleNavigate} currentUser={currentUser} />
          : <AnalyticsDashboard onNavigate={handleNavigate} />;
      default:
        return <AnalyticsDashboard onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar
        currentUser={currentUser}
        currentPage={currentPage}
        onNavigate={handleNavigate}
        onLogout={handleLogout}
      />
      <main className="min-h-[calc(100vh-4rem)]">
        {renderPage()}
      </main>
    </div>
  );
}
