import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="user", nullable=False)  # "user" or "admin"
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("JobDescription", back_populates="user", cascade="all, delete-orphan")
    interviews = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    learning_plans = relationship("LearningPlan", back_populates="user", cascade="all, delete-orphan")
    evidence_claims = relationship("ResumeEvidenceClaim", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=False)  # "pdf" or "docx"
    file_size_bytes = Column(Integer, nullable=False)
    extracted_text = Column(Text, nullable=False)
    raw_profile_json = Column(Text, nullable=False)  # Parsed JSON string
    edited_profile_json = Column(Text, nullable=True)  # User-edited JSON string
    analysis_json = Column(Text, nullable=True)  # Resume analysis results JSON
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="resumes")
    matches = relationship("JobMatchResult", back_populates="resume", cascade="all, delete-orphan")
    evidence_claims = relationship("ResumeEvidenceClaim", back_populates="resume", cascade="all, delete-orphan")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True, default="")
    raw_text = Column(Text, nullable=False)
    extracted_skills_json = Column(Text, nullable=False)  # {required_skills: [], preferred_skills: []}
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="jobs")
    matches = relationship("JobMatchResult", back_populates="job", cascade="all, delete-orphan")


class JobMatchResult(Base):
    __tablename__ = "job_match_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Float, nullable=False)  # 0 to 100
    score_breakdown_json = Column(Text, nullable=False)
    matched_skills_json = Column(Text, nullable=False)
    missing_skills_json = Column(Text, nullable=False)
    related_skills_json = Column(Text, nullable=False)
    recommendations_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    resume = relationship("Resume", back_populates="matches")
    job = relationship("JobDescription", back_populates="matches")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    target_role = Column(String(255), nullable=False)
    difficulty_level = Column(String(50), default="intermediate", nullable=False)  # beginner, intermediate, advanced, adaptive
    status = Column(String(50), default="in_progress", nullable=False)  # in_progress, completed, abandoned
    total_questions = Column(Integer, default=5, nullable=False)
    current_question_index = Column(Integer, default=0, nullable=False)
    overall_score = Column(Float, nullable=True)
    readiness_score = Column(Float, nullable=True)
    summary_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="interviews")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan", order_by="InterviewQuestion.question_order")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_order = Column(Integer, nullable=False)  # 1, 2, 3...
    category = Column(String(50), nullable=False)  # technical, project, behavioral, hr, evidence_check
    question_text = Column(Text, nullable=False)
    context_grounding = Column(Text, nullable=True, default="")  # How this relates to resume/job
    difficulty = Column(String(50), default="intermediate", nullable=False)  # beginner, intermediate, advanced
    expected_points_json = Column(Text, nullable=False, default="[]")
    follow_up_to_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=True)

    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    answer_text = Column(Text, nullable=False)
    speech_used = Column(Boolean, default=False, nullable=False)
    time_taken_seconds = Column(Integer, default=0, nullable=False)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    question = relationship("InterviewQuestion", back_populates="answer")
    evaluation = relationship("AnswerEvaluation", back_populates="answer", uselist=False, cascade="all, delete-orphan")


class AnswerEvaluation(Base):
    __tablename__ = "answer_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("interview_answers.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    relevance_score = Column(Float, nullable=False)  # 0 to 100
    technical_score = Column(Float, nullable=False)  # 0 to 100
    completeness_score = Column(Float, nullable=False)  # 0 to 100
    clarity_score = Column(Float, nullable=False)  # 0 to 100
    reasoning_score = Column(Float, nullable=False)  # 0 to 100
    overall_score = Column(Float, nullable=False)  # Weighted average
    feedback_critique = Column(Text, nullable=False)
    strengths_json = Column(Text, nullable=False, default="[]")
    improvements_json = Column(Text, nullable=False, default="[]")
    model_answer = Column(Text, nullable=False)
    evaluated_by = Column(String(50), default="heuristic_engine", nullable=False)  # "ai_llm" or "heuristic_engine"
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    answer = relationship("InterviewAnswer", back_populates="evaluation")


class ResumeEvidenceClaim(Base):
    __tablename__ = "resume_evidence_claims"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_type = Column(String(50), nullable=False)  # project, metric, architecture, technology
    claim_text = Column(Text, nullable=False)
    verification_question = Column(Text, nullable=False)
    candidate_answer = Column(Text, nullable=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, practiced, needs_preparation, verified_strong
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="evidence_claims")
    resume = relationship("Resume", back_populates="evidence_claims")


class LearningPlan(Base):
    __tablename__ = "learning_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    duration_days = Column(Integer, nullable=False)  # 7, 15, or 30
    target_role = Column(String(255), nullable=False)
    plan_json = Column(Text, nullable=False)  # Daily study & practice schedule
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="learning_plans")


class SystemQuestionBank(Base):
    __tablename__ = "system_question_bank"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(100), nullable=False, index=True)  # e.g., "Full Stack Developer", "Backend Engineer", "General"
    category = Column(String(50), nullable=False)  # technical, project, behavioral, hr
    difficulty = Column(String(50), nullable=False)  # beginner, intermediate, advanced
    skill_tag = Column(String(100), nullable=False, index=True)  # e.g., "Python", "React", "System Design", "SQL"
    question_text = Column(Text, nullable=False)
    expected_points_json = Column(Text, nullable=False, default="[]")
    sample_good_answer = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
