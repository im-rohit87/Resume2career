export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: 'user' | 'admin';
  created_at: string;
}

export interface ContactInfo {
  name?: string;
  email?: string;
  phone?: string;
  linkedin?: string;
  github?: string;
  location?: string;
}

export interface EducationItem {
  degree?: string;
  institution?: string;
  year?: string;
  gpa_or_percentage?: string;
}

export interface ExperienceItem {
  title?: string;
  company?: string;
  duration?: string;
  responsibilities: string[];
}

export interface ProjectItem {
  title?: string;
  technologies: string[];
  description?: string;
  metrics_or_outcomes?: string;
}

export interface SkillsCategorized {
  technical_skills: string[];
  frameworks_libraries: string[];
  tools_platforms: string[];
  soft_skills: string[];
}

export interface ResumeProfile {
  contact: ContactInfo;
  summary?: string;
  skills: SkillsCategorized;
  experience: ExperienceItem[];
  projects: ProjectItem[];
  education: EducationItem[];
  certifications: string[];
}

export interface ResumeAnalysisResult {
  heuristic_score: number;
  score_breakdown: {
    contact_completeness: number;
    skills_breadth: number;
    experience_and_projects: number;
    structure_and_formatting: number;
    quantified_metrics: number;
  };
  strengths: string[];
  missing_sections: string[];
  actionable_suggestions: string[];
  quantified_metrics_found: string[];
  formula_explanation: string;
  disclaimer: string;
}

export interface Resume {
  id: number;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  profile: ResumeProfile;
  analysis?: ResumeAnalysisResult;
  created_at: string;
  updated_at: string;
}

export interface SkillMatchEvidence {
  skill: string;
  found_in_resume: boolean;
  evidence_snippet?: string;
  category: 'required' | 'preferred';
}

export interface RelatedSkillBridge {
  missing_target: string;
  related_candidate_skill: string;
  bridge_rationale: string;
}

export interface JobMatchResponse {
  id: number;
  resume_id: number;
  job_id: number;
  role_title: string;
  company_name?: string;
  match_score: number;
  score_breakdown: {
    required_skills_coverage: number;
    preferred_skills_coverage: number;
    semantic_corpus_similarity: number;
  };
  required_skills_matched: SkillMatchEvidence[];
  required_skills_missing: string[];
  preferred_skills_matched: SkillMatchEvidence[];
  preferred_skills_missing: string[];
  related_skills_present: RelatedSkillBridge[];
  recommendations: string[];
  formula_explanation: string;
  disclaimer: string;
  created_at: string;
}

export interface QuestionEvaluation {
  id?: number;
  relevance_score: number;
  technical_score: number;
  completeness_score: number;
  clarity_score: number;
  reasoning_score: number;
  overall_score: number;
  feedback_critique: string;
  strengths: string[];
  improvements: string[];
  model_answer: string;
  evaluated_by: string;
  adaptive_next_difficulty?: string;
  disclaimer?: string;
}

export interface QuestionItem {
  id: number;
  question_order: number;
  category: 'technical' | 'project' | 'behavioral' | 'hr' | string;
  question_text: string;
  context_grounding?: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | string;
  is_answered?: boolean;
  answer?: {
    id: number;
    answer_text: string;
    speech_used: boolean;
    time_taken_seconds: number;
    submitted_at: string;
    evaluation?: QuestionEvaluation;
  };
}

export interface InterviewSession {
  id: number;
  title: string;
  target_role: string;
  difficulty_level: string;
  status: 'in_progress' | 'completed' | 'abandoned';
  total_questions: number;
  current_question_index: number;
  overall_score?: number;
  readiness_score?: number;
  summary_feedback?: string;
  created_at: string;
  completed_at?: string;
  questions: QuestionItem[];
}

export interface EvidenceClaim {
  id: number;
  resume_id: number;
  claim_type: string;
  claim_text: string;
  verification_question: string;
  candidate_answer?: string;
  status: 'pending' | 'practiced' | 'verified_strong' | 'needs_preparation';
  notes?: string;
  created_at: string;
}

export interface DailyMilestone {
  day: number;
  focus_topic: string;
  learning_objectives: string[];
  practice_challenge: string;
  recommended_resources: string[];
}

export interface LearningPlan {
  id: number;
  title: string;
  duration_days: number;
  target_role: string;
  daily_schedule: DailyMilestone[];
  created_at: string;
}

export interface AnalyticsDashboard {
  total_interviews: number;
  average_score: number;
  readiness_index: number;
  criterion_averages: {
    relevance: number;
    technical: number;
    completeness: number;
    clarity: number;
    reasoning: number;
  };
  history_trend: Array<{
    session_number: number;
    title: string;
    date: string;
    score: number;
    readiness: number;
  }>;
  strong_topics: string[];
  weak_topics: string[];
  readiness_formula: string;
  disclaimer: string;
}

export interface AdminQuestion {
  id: number;
  role: string;
  category: string;
  difficulty: string;
  skill_tag: string;
  question_text: string;
  expected_points: string[];
  sample_good_answer: string;
  is_active: boolean;
  created_at: string;
}

export interface AdminStats {
  total_registered_users: number;
  total_resumes_analyzed: number;
  total_interviews_initiated: number;
  total_interviews_completed: number;
  curated_question_bank_count: number;
  system_average_score: number;
  note: string;
}
