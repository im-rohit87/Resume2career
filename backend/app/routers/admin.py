import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.models import User, SystemQuestionBank, InterviewSession, Resume
from app.schemas.schemas import QuestionBankCreate, QuestionBankResponse

router = APIRouter(prefix="/admin", tags=["Admin System Management"])


@router.get("/questions", response_model=List[QuestionBankResponse])
def list_system_questions(
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    questions = db.query(SystemQuestionBank).order_by(SystemQuestionBank.created_at.desc()).all()
    out = []
    for q in questions:
        out.append(
            QuestionBankResponse(
                id=q.id,
                role=q.role,
                category=q.category,
                difficulty=q.difficulty,
                skill_tag=q.skill_tag,
                question_text=q.question_text,
                expected_points=json.loads(q.expected_points_json) if q.expected_points_json else [],
                sample_good_answer=q.sample_good_answer,
                is_active=q.is_active,
                created_at=q.created_at,
            )
        )
    return out


@router.post("/questions", response_model=QuestionBankResponse, status_code=status.HTTP_201_CREATED)
def create_system_question(
    payload: QuestionBankCreate,
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    new_q = SystemQuestionBank(
        role=payload.role.strip(),
        category=payload.category.strip().lower(),
        difficulty=payload.difficulty.strip().lower(),
        skill_tag=payload.skill_tag.strip(),
        question_text=payload.question_text.strip(),
        expected_points_json=json.dumps(payload.expected_points),
        sample_good_answer=payload.sample_good_answer.strip(),
        is_active=True,
    )
    db.add(new_q)
    db.commit()
    db.refresh(new_q)

    return QuestionBankResponse(
        id=new_q.id,
        role=new_q.role,
        category=new_q.category,
        difficulty=new_q.difficulty,
        skill_tag=new_q.skill_tag,
        question_text=new_q.question_text,
        expected_points=payload.expected_points,
        sample_good_answer=new_q.sample_good_answer,
        is_active=new_q.is_active,
        created_at=new_q.created_at,
    )


@router.put("/questions/{question_id}/toggle")
def toggle_question_status(
    question_id: int,
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    q = db.query(SystemQuestionBank).filter(SystemQuestionBank.id == question_id).first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")

    q.is_active = not q.is_active
    db.commit()
    return {"id": q.id, "is_active": q.is_active, "message": "Question active status toggled."}


@router.get("/stats")
def get_system_stats(
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    total_users = db.query(User).count()
    total_resumes = db.query(Resume).count()
    total_interviews = db.query(InterviewSession).count()
    completed_interviews = db.query(InterviewSession).filter(InterviewSession.status == "completed").count()
    question_bank_size = db.query(SystemQuestionBank).count()

    # Aggregate performance score across system
    completed_sessions = db.query(InterviewSession).filter(InterviewSession.status == "completed").all()
    avg_score = 0.0
    if completed_sessions:
        avg_score = round(sum(s.overall_score or 0.0 for s in completed_sessions) / len(completed_sessions), 1)

    return {
        "total_registered_users": total_users,
        "total_resumes_analyzed": total_resumes,
        "total_interviews_initiated": total_interviews,
        "total_interviews_completed": completed_interviews,
        "curated_question_bank_count": question_bank_size,
        "system_average_score": avg_score,
        "note": "Per strict privacy architecture, individual user resumes and interview transcripts are isolated and not displayed.",
    }
