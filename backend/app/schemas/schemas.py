from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# ==========================================
# AUTH SCHEMAS
# ==========================================
class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)


class UserLogin(BaseModel):
    username_or_email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==========================================
# RESUME SCHEMAS
# ==========================================
class ContactInfo(BaseModel):
    name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    location: Optional[str] = ""


class EducationItem(BaseModel):
    degree: Optional[str] = ""
    institution: Optional[str] = ""
    year: Optional[str] = ""
    gpa_or_percentage: Optional[str] = ""


class ExperienceItem(BaseModel):
    title: Optional[str] = ""
    company: Optional[str] = ""
    duration: Optional[str] = ""
    responsibilities: List[str] = []


class ProjectItem(BaseModel):
    title: Optional[str] = ""
    technologies: List[str] = []
    description: Optional[str] = ""
    metrics_or_outcomes: Optional[str] = ""


class SkillsCategorized(BaseModel):
    technical_skills: List[str] = []
    frameworks_libraries: List[str] = []
    tools_platforms: List[str] = []
    soft_skills: List[str] = []


class ResumeProfile(BaseModel):
    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = ""
    skills: SkillsCategorized = Field(default_factory=SkillsCategorized)
    experience: List[ExperienceItem] = []
    projects: List[ProjectItem] = []
    education: List[EducationItem] = []
    certifications: List[str] = []


class ResumeAnalysisResult(BaseModel):
    heuristic_score: float
    score_breakdown: Dict[str, float]
    strengths: List[str]
    missing_sections: List[str]
    actionable_suggestions: List[str]
    quantified_metrics_found: List[str]
    formula_explanation: str
    disclaimer: str


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    file_type: str
    file_size_bytes: int
    profile: ResumeProfile
    analysis: Optional[ResumeAnalysisResult] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeUpdateProfileRequest(BaseModel):
    profile: ResumeProfile


# ==========================================
# JOB DESCRIPTION & MATCHING SCHEMAS
# ==========================================
class JobMatchRequest(BaseModel):
    resume_id: int
    role_title: str = Field(..., min_length=2, max_length=150)
    company_name: Optional[str] = ""
    job_description_text: str = Field(..., min_length=20)


class SkillMatchEvidence(BaseModel):
    skill: str
    found_in_resume: bool
    evidence_snippet: Optional[str] = ""
    category: str = "required"  # "required" or "preferred"


class JobMatchResponse(BaseModel):
    id: int
    match_score: float
    score_breakdown: Dict[str, float]
    role_title: str
    required_skills_matched: List[SkillMatchEvidence]
    required_skills_missing: List[str]
    preferred_skills_matched: List[SkillMatchEvidence]
    preferred_skills_missing: List[str]
    related_skills_present: List[Dict[str, str]]
    recommendations: List[str]
    formula_explanation: str
    disclaimer: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# INTERVIEW & EVALUATION SCHEMAS
# ==========================================
class InterviewCreateRequest(BaseModel):
    resume_id: Optional[int] = None
    job_id: Optional[int] = None
    target_role: str = Field(default="Full Stack Developer", min_length=2)
    difficulty_level: str = Field(default="adaptive")  # beginner, intermediate, advanced, adaptive
    total_questions: int = Field(default=5, ge=3, le=10)


class QuestionResponse(BaseModel):
    id: int
    session_id: int
    question_order: int
    category: str
    question_text: str
    context_grounding: Optional[str] = ""
    difficulty: str

    model_config = ConfigDict(from_attributes=True)


class AnswerSubmitRequest(BaseModel):
    question_id: int
    answer_text: str = Field(..., min_length=5)
    speech_used: bool = False
    time_taken_seconds: int = 0


class EvaluationResponse(BaseModel):
    id: int
    answer_id: int
    relevance_score: float
    technical_score: float
    completeness_score: float
    clarity_score: float
    reasoning_score: float
    overall_score: float
    feedback_critique: str
    strengths: List[str]
    improvements: List[str]
    model_answer: str
    evaluated_by: str
    adaptive_next_difficulty: Optional[str] = None
    disclaimer: str

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionDetail(BaseModel):
    id: int
    title: str
    target_role: str
    difficulty_level: str
    status: str
    total_questions: int
    current_question_index: int
    overall_score: Optional[float] = None
    readiness_score: Optional[float] = None
    summary_feedback: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    questions: List[QuestionResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# EVIDENCE CHECKER SCHEMAS
# ==========================================
class EvidenceClaimResponse(BaseModel):
    id: int
    resume_id: int
    claim_type: str
    claim_text: str
    verification_question: str
    candidate_answer: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvidenceAnswerRequest(BaseModel):
    claim_id: int
    candidate_answer: str = Field(..., min_length=10)


# ==========================================
# LEARNING PLAN SCHEMAS
# ==========================================
class LearningPlanRequest(BaseModel):
    duration_days: int = Field(default=15, ge=7, le=30)
    target_role: str = Field(default="Full Stack Developer")
    focus_skills: Optional[List[str]] = []


class DailyMilestone(BaseModel):
    day: int
    focus_topic: str
    learning_objectives: List[str]
    practice_challenge: str
    recommended_resources: List[str]


class LearningPlanResponse(BaseModel):
    id: int
    title: str
    duration_days: int
    target_role: str
    daily_schedule: List[DailyMilestone]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ADMIN & QUESTION BANK SCHEMAS
# ==========================================
class QuestionBankCreate(BaseModel):
    role: str
    category: str
    difficulty: str
    skill_tag: str
    question_text: str
    expected_points: List[str] = []
    sample_good_answer: str


class QuestionBankResponse(BaseModel):
    id: int
    role: str
    category: str
    difficulty: str
    skill_tag: str
    question_text: str
    expected_points: List[str]
    sample_good_answer: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
