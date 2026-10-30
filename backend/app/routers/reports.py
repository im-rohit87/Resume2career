import json
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import (
    User,
    InterviewSession,
    InterviewQuestion,
    InterviewAnswer,
    AnswerEvaluation,
)
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Interview Reports"])


@router.get("/session/{session_id}")
def get_session_report(
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found or access denied.")

    questions = (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.session_id == session.id)
        .order_by(InterviewQuestion.question_order.asc())
        .all()
    )

    q_data = []
    for q in questions:
        ans = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == q.id).first()
        ans_dict = None
        eval_dict = None
        if ans:
            eval_record = db.query(AnswerEvaluation).filter(AnswerEvaluation.answer_id == ans.id).first()
            if eval_record:
                eval_dict = {
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
            ans_dict = {
                "answer_text": ans.answer_text,
                "speech_used": ans.speech_used,
                "time_taken_seconds": ans.time_taken_seconds,
                "submitted_at": ans.submitted_at.isoformat(),
                "evaluation": eval_dict,
            }

        q_data.append({
            "id": q.id,
            "order": q.question_order,
            "category": q.category,
            "difficulty": q.difficulty,
            "question_text": q.question_text,
            "context_grounding": q.context_grounding,
            "answer": ans_dict,
        })

    report_payload = {
        "id": session.id,
        "title": session.title,
        "target_role": session.target_role,
        "difficulty_level": session.difficulty_level,
        "status": session.status,
        "overall_score": session.overall_score or 0.0,
        "readiness_score": session.readiness_score or 0.0,
        "summary_feedback": session.summary_feedback or "Interview session evaluation completed.",
        "created_at": session.created_at.isoformat(),
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
        "questions": q_data,
        "disclaimer": (
            "Diagnostic Report Disclaimer: This evaluation report is generated for interview practice "
            "and skill benchmarking. Scores reflect adherence to defined technical criteria and structure, "
            "and do not constitute an official employment guarantee."
        ),
    }

    return report_payload


@router.get("/session/{session_id}/pdf")
def download_session_report_pdf(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session_report = get_session_report(session_id, current_user, db)
    pdf_bytes = ReportService.generate_pdf_report(session_report)

    filename = f"Resume2Interview_Report_{session_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
