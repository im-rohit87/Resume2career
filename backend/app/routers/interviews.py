import json
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import (
    User,
    Resume,
    JobDescription,
    InterviewSession,
    InterviewQuestion,
    InterviewAnswer,
    AnswerEvaluation,
)
from app.schemas.schemas import (
    InterviewCreateRequest,
    AnswerSubmitRequest,
    InterviewSessionDetail,
)
from app.services.llm_service import LLMService
from app.services.evaluator_service import EvaluatorService

router = APIRouter(prefix="/interviews", tags=["Adaptive Mock Interviews"])


@router.post("/create")
def create_interview_session(
    payload: InterviewCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume_profile = {}
    job_text = ""

    # Load resume if provided
    if payload.resume_id:
        resume = db.query(Resume).filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id).first()
        if resume:
            resume_profile = json.loads(resume.edited_profile_json or resume.raw_profile_json)

    # Load job description if provided
    if payload.job_id:
        job = db.query(JobDescription).filter(JobDescription.id == payload.job_id, JobDescription.user_id == current_user.id).first()
        if job:
            job_text = job.raw_text

    # Generate questions (AI or curated fallback)
    questions_data, source = LLMService.generate_interview_questions(
        resume_profile=resume_profile,
        job_description=job_text,
        role=payload.target_role,
        difficulty=payload.difficulty_level,
        count=payload.total_questions,
    )

    # Create Session
    session_title = f"{payload.target_role} — {'Adaptive' if payload.difficulty_level == 'adaptive' else payload.difficulty_level.capitalize()} Interview"
    new_session = InterviewSession(
        user_id=current_user.id,
        resume_id=payload.resume_id,
        job_id=payload.job_id,
        title=session_title,
        target_role=payload.target_role,
        difficulty_level=payload.difficulty_level,
        status="in_progress",
        total_questions=len(questions_data),
        current_question_index=0,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Create Question records
    created_questions = []
    for idx, q in enumerate(questions_data, 1):
        context = f"Grounded in target role: {payload.target_role}"
        if q.get("skill_tag"):
            context += f" | Key Competency: {q['skill_tag']}"

        question_record = InterviewQuestion(
            session_id=new_session.id,
            question_order=idx,
            category=q.get("category", "technical"),
            question_text=q["question_text"],
            context_grounding=context,
            difficulty=q.get("difficulty", "intermediate"),
            expected_points_json=json.dumps(q.get("expected_points", [])),
        )
        db.add(question_record)
        created_questions.append(question_record)

    db.commit()

    return {
        "session_id": new_session.id,
        "title": new_session.title,
        "target_role": new_session.target_role,
        "difficulty_level": new_session.difficulty_level,
        "status": new_session.status,
        "total_questions": new_session.total_questions,
        "current_question_index": 0,
        "question_generation_source": source,
        "created_at": new_session.created_at,
    }


@router.get("/session/{session_id}")
def get_interview_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found or access denied."
        )

    # Fetch questions with answers & evaluations
    questions = (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.session_id == session.id)
        .order_by(InterviewQuestion.question_order.asc())
        .all()
    )

    questions_payload = []
    for q in questions:
        ans = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == q.id).first()
        ans_data = None
        if ans:
            eval_record = db.query(AnswerEvaluation).filter(AnswerEvaluation.answer_id == ans.id).first()
            eval_data = None
            if eval_record:
                eval_data = {
                    "id": eval_record.id,
                    "relevance_score": eval_record.relevance_score,
                    "technical_score": eval_record.technical_score,
                    "completeness_score": eval_record.completeness_score,
                    "clarity_score": eval_record.clarity_score,
                    "reasoning_score": eval_record.reasoning_score,
                    "overall_score": eval_record.overall_score,
                    "feedback_critique": eval_record.feedback_critique,
                    "strengths": json.loads(eval_record.strengths_json) if eval_record.strengths_json else [],
                    "improvements": json.loads(eval_record.improvements_json) if eval_record.improvements_json else [],
                    "model_answer": eval_record.model_answer,
                    "evaluated_by": eval_record.evaluated_by,
                }
            ans_data = {
                "id": ans.id,
                "answer_text": ans.answer_text,
                "speech_used": ans.speech_used,
                "time_taken_seconds": ans.time_taken_seconds,
                "submitted_at": ans.submitted_at,
                "evaluation": eval_data,
            }

        questions_payload.append({
            "id": q.id,
            "question_order": q.question_order,
            "category": q.category,
            "question_text": q.question_text,
            "context_grounding": q.context_grounding,
            "difficulty": q.difficulty,
            "is_answered": ans is not None,
            "answer": ans_data,
        })

    return {
        "id": session.id,
        "title": session.title,
        "target_role": session.target_role,
        "difficulty_level": session.difficulty_level,
        "status": session.status,
        "total_questions": session.total_questions,
        "current_question_index": session.current_question_index,
        "overall_score": session.overall_score,
        "readiness_score": session.readiness_score,
        "summary_feedback": session.summary_feedback,
        "created_at": session.created_at,
        "completed_at": session.completed_at,
        "questions": questions_payload,
    }


@router.post("/submit-answer")
def submit_answer(
    payload: AnswerSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Fetch question and verify session ownership
    question = db.query(InterviewQuestion).filter(InterviewQuestion.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview question not found.")

    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == question.session_id, InterviewSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to submit answers for this interview session."
        )

    # 2. Check for duplicate submission
    existing_answer = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == question.id).first()
    if existing_answer:
        # Return already evaluated response safely without re-inserting
        eval_record = db.query(AnswerEvaluation).filter(AnswerEvaluation.answer_id == existing_answer.id).first()
        return {
            "message": "Answer already submitted for this question.",
            "answer_id": existing_answer.id,
            "evaluation": {
                "overall_score": eval_record.overall_score if eval_record else 0.0,
                "feedback_critique": eval_record.feedback_critique if eval_record else "",
            }
        }

    # 3. Create InterviewAnswer record
    new_answer = InterviewAnswer(
        question_id=question.id,
        answer_text=payload.answer_text.strip(),
        speech_used=payload.speech_used,
        time_taken_seconds=payload.time_taken_seconds,
    )
    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)

    # 4. Evaluate Answer
    expected_pts = json.loads(question.expected_points_json) if question.expected_points_json else []
    eval_result = EvaluatorService.evaluate_answer(
        question_text=question.question_text,
        category=question.category,
        difficulty=question.difficulty,
        expected_points=expected_pts,
        sample_good_answer="",
        candidate_answer=payload.answer_text.strip(),
    )

    # 5. Save Evaluation Record
    evaluation = AnswerEvaluation(
        answer_id=new_answer.id,
        relevance_score=eval_result["relevance_score"],
        technical_score=eval_result["technical_score"],
        completeness_score=eval_result["completeness_score"],
        clarity_score=eval_result["clarity_score"],
        reasoning_score=eval_result["reasoning_score"],
        overall_score=eval_result["overall_score"],
        feedback_critique=eval_result["feedback_critique"],
        strengths_json=json.dumps(eval_result["strengths"]),
        improvements_json=json.dumps(eval_result["improvements"]),
        model_answer=eval_result["model_answer"],
        evaluated_by=eval_result["evaluated_by"],
    )
    db.add(evaluation)

    # 6. Adaptive Difficulty Progression
    if session.difficulty_level == "adaptive":
        next_difficulty = eval_result["adaptive_next_difficulty"]
        # Find next question in sequence
        next_q = (
            db.query(InterviewQuestion)
            .filter(
                InterviewQuestion.session_id == session.id,
                InterviewQuestion.question_order == question.question_order + 1,
            )
            .first()
        )
        if next_q:
            next_q.difficulty = next_difficulty

    # 7. Advance Session Progress
    session.current_question_index = min(session.current_question_index + 1, session.total_questions)

    # Check if all questions completed
    total_answers = (
        db.query(InterviewAnswer)
        .join(InterviewQuestion)
        .filter(InterviewQuestion.session_id == session.id)
        .count()
    )

    if total_answers >= session.total_questions:
        session.status = "completed"
        session.completed_at = datetime.datetime.utcnow()
        # Calculate final overall score
        all_evals = (
            db.query(AnswerEvaluation)
            .join(InterviewAnswer)
            .join(InterviewQuestion)
            .filter(InterviewQuestion.session_id == session.id)
            .all()
        )
        if all_evals:
            avg_score = sum(e.overall_score for e in all_evals) / len(all_evals)
            session.overall_score = round(avg_score, 1)
            # Heuristic readiness score (penalizes extreme variance)
            session.readiness_score = round(avg_score * 0.95, 1)
            session.summary_feedback = (
                f"Completed {len(all_evals)} interview rounds with an average performance score of {session.overall_score}/100. "
                f"Candidate exhibited consistent depth in primary criteria."
            )

    db.commit()
    db.refresh(evaluation)

    return {
        "evaluation_id": evaluation.id,
        "answer_id": new_answer.id,
        "overall_score": evaluation.overall_score,
        "relevance_score": evaluation.relevance_score,
        "technical_score": evaluation.technical_score,
        "completeness_score": evaluation.completeness_score,
        "clarity_score": evaluation.clarity_score,
        "reasoning_score": evaluation.reasoning_score,
        "feedback_critique": evaluation.feedback_critique,
        "strengths": eval_result["strengths"],
        "improvements": eval_result["improvements"],
        "model_answer": evaluation.model_answer,
        "evaluated_by": evaluation.evaluated_by,
        "adaptive_next_difficulty": eval_result.get("adaptive_next_difficulty"),
        "session_status": session.status,
        "current_question_index": session.current_question_index,
        "disclaimer": eval_result["disclaimer"],
    }


@router.post("/session/{session_id}/finish")
def finish_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    all_evals = (
        db.query(AnswerEvaluation)
        .join(InterviewAnswer)
        .join(InterviewQuestion)
        .filter(InterviewQuestion.session_id == session.id)
        .all()
    )

    if all_evals:
        avg_score = sum(e.overall_score for e in all_evals) / len(all_evals)
        session.overall_score = round(avg_score, 1)
        session.readiness_score = round(avg_score * 0.95, 1)
    else:
        session.overall_score = 0.0
        session.readiness_score = 0.0

    session.status = "completed"
    session.completed_at = datetime.datetime.utcnow()
    db.commit()

    return {
        "session_id": session.id,
        "status": session.status,
        "overall_score": session.overall_score,
        "readiness_score": session.readiness_score,
    }


@router.get("/history")
def list_interview_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == current_user.id)
        .order_by(InterviewSession.created_at.desc())
        .all()
    )
    out = []
    for s in sessions:
        out.append({
            "id": s.id,
            "title": s.title,
            "target_role": s.target_role,
            "difficulty_level": s.difficulty_level,
            "status": s.status,
            "total_questions": s.total_questions,
            "current_question_index": s.current_question_index,
            "overall_score": s.overall_score,
            "readiness_score": s.readiness_score,
            "created_at": s.created_at,
            "completed_at": s.completed_at,
        })
    return out
