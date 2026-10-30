import {
  User,
  Resume,
  ResumeProfile,
  JobMatchResponse,
  InterviewSession,
  QuestionEvaluation,
  EvidenceClaim,
  LearningPlan,
  AnalyticsDashboard,
  AdminQuestion,
  AdminStats,
} from '../types';

const API_BASE = '/api';

// Token Management
export const getToken = (): string | null => localStorage.getItem('r2i_token');
export const setToken = (token: string): void => localStorage.setItem('r2i_token', token);
export const clearToken = (): void => {
  localStorage.removeItem('r2i_token');
  localStorage.removeItem('r2i_user');
};

export const getStoredUser = (): User | null => {
  const u = localStorage.getItem('r2i_user');
  return u ? JSON.parse(u) : null;
};

export const setStoredUser = (user: User): void => {
  localStorage.setItem('r2i_user', JSON.stringify(user));
};

const getHeaders = (isJson = true): HeadersInit => {
  const headers: Record<string, string> = {};
  if (isJson) {
    headers['Content-Type'] = 'application/json';
  }
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errMsg = `Request failed with status ${res.status}`;
    try {
      const errData = await res.json();
      if (errData && errData.detail) {
        errMsg = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errMsg);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Auth
  async register(data: { email: string; username: string; password: string; full_name: string }) {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    const result = await handleResponse<{ access_token: string; user: User }>(res);
    setToken(result.access_token);
    setStoredUser(result.user);
    return result;
  },

  async login(data: { username_or_email: string; password: string }) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    const result = await handleResponse<{ access_token: string; user: User }>(res);
    setToken(result.access_token);
    setStoredUser(result.user);
    return result;
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getHeaders(),
    });
    const user = await handleResponse<User>(res);
    setStoredUser(user);
    return user;
  },

  logout() {
    clearToken();
  },

  // Resumes
  async uploadResume(file: File): Promise<Resume> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/resumes/upload`, {
      method: 'POST',
      headers: getHeaders(false),
      body: formData,
    });
    return handleResponse<Resume>(res);
  },

  async getResumes(): Promise<Resume[]> {
    const res = await fetch(`${API_BASE}/resumes`, {
      headers: getHeaders(),
    });
    return handleResponse<Resume[]>(res);
  },

  async getResume(id: number): Promise<Resume> {
    const res = await fetch(`${API_BASE}/resumes/${id}`, {
      headers: getHeaders(),
    });
    return handleResponse<Resume>(res);
  },

  async updateResumeProfile(id: number, profile: ResumeProfile) {
    const res = await fetch(`${API_BASE}/resumes/${id}/profile`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({ profile }),
    });
    return handleResponse<{ id: number; message: string; profile: ResumeProfile; analysis: any }>(res);
  },

  async deleteResume(id: number): Promise<void> {
    const res = await fetch(`${API_BASE}/resumes/${id}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!res.ok) {
      throw new Error(`Failed to delete resume (${res.status})`);
    }
  },

  // Job Matching
  async matchJob(data: { resume_id: number; role_title: string; company_name?: string; job_description_text: string }) {
    const res = await fetch(`${API_BASE}/matching/match`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<JobMatchResponse>(res);
  },

  async getMatchHistory(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/matching/history`, {
      headers: getHeaders(),
    });
    return handleResponse<any[]>(res);
  },

  // Interviews
  async createInterview(data: {
    resume_id?: number;
    job_id?: number;
    target_role: string;
    difficulty_level: string;
    total_questions: number;
  }) {
    const res = await fetch(`${API_BASE}/interviews/create`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<{ session_id: number; title: string; total_questions: number }>(res);
  },

  async getInterviewSession(sessionId: number): Promise<InterviewSession> {
    const res = await fetch(`${API_BASE}/interviews/session/${sessionId}`, {
      headers: getHeaders(),
    });
    return handleResponse<InterviewSession>(res);
  },

  async submitAnswer(data: {
    question_id: number;
    answer_text: string;
    speech_used?: boolean;
    time_taken_seconds?: number;
  }): Promise<QuestionEvaluation & { session_status: string; current_question_index: number }> {
    const res = await fetch(`${API_BASE}/interviews/submit-answer`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<any>(res);
  },

  async finishInterview(sessionId: number) {
    const res = await fetch(`${API_BASE}/interviews/session/${sessionId}/finish`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  async getInterviewHistory(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/interviews/history`, {
      headers: getHeaders(),
    });
    return handleResponse<any[]>(res);
  },

  // Evidence Checker
  async extractClaims(resumeId: number): Promise<EvidenceClaim[]> {
    const res = await fetch(`${API_BASE}/evidence/extract/${resumeId}`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse<EvidenceClaim[]>(res);
  },

  async getClaims(resumeId: number): Promise<EvidenceClaim[]> {
    const res = await fetch(`${API_BASE}/evidence/claims/${resumeId}`, {
      headers: getHeaders(),
    });
    return handleResponse<EvidenceClaim[]>(res);
  },

  async answerClaim(claimId: number, candidateAnswer: string) {
    const res = await fetch(`${API_BASE}/evidence/answer`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ claim_id: claimId, candidate_answer: candidateAnswer }),
    });
    return handleResponse<{ id: number; status: string; guidance: string; disclaimer: string }>(res);
  },

  // Analytics & Learning Plans
  async getDashboardAnalytics(): Promise<AnalyticsDashboard> {
    const res = await fetch(`${API_BASE}/analytics/dashboard`, {
      headers: getHeaders(),
    });
    return handleResponse<AnalyticsDashboard>(res);
  },

  async createLearningPlan(data: { duration_days: number; target_role: string; focus_skills?: string[] }): Promise<LearningPlan> {
    const res = await fetch(`${API_BASE}/analytics/learning-plan`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<LearningPlan>(res);
  },

  async getLearningPlans(): Promise<LearningPlan[]> {
    const res = await fetch(`${API_BASE}/analytics/learning-plans`, {
      headers: getHeaders(),
    });
    return handleResponse<LearningPlan[]>(res);
  },

  // Admin
  async getAdminQuestions(): Promise<AdminQuestion[]> {
    const res = await fetch(`${API_BASE}/admin/questions`, {
      headers: getHeaders(),
    });
    return handleResponse<AdminQuestion[]>(res);
  },

  async createAdminQuestion(data: any): Promise<AdminQuestion> {
    const res = await fetch(`${API_BASE}/admin/questions`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<AdminQuestion>(res);
  },

  async toggleAdminQuestion(questionId: number) {
    const res = await fetch(`${API_BASE}/admin/questions/${questionId}/toggle`, {
      method: 'PUT',
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  async getAdminStats(): Promise<AdminStats> {
    const res = await fetch(`${API_BASE}/admin/stats`, {
      headers: getHeaders(),
    });
    return handleResponse<AdminStats>(res);
  },

  // Reports
  async getSessionReport(sessionId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/reports/session/${sessionId}`, {
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  getPdfReportDownloadUrl(sessionId: number): string {
    return `${API_BASE}/reports/session/${sessionId}/pdf`;
  },
};
