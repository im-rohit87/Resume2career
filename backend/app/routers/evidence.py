import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Resume, ResumeEvidenceClaim
from app.schemas.schemas import EvidenceClaimResponse, EvidenceAnswerRequest
from app.services.evidence_checker import ResumeEvidenceCheckerService

router = APIRouter(prefix="/evidence", tags=["Resume Evidence Checker"])


@router.post("/extract/{resume_id}")
def extract_evidence_claims(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found or access denied.")

    # Check if claims already exist for this resume
    existing_claims = db.query(ResumeEvidenceClaim).filter(ResumeEvidenceClaim.resume_id == resume.id).all()
    if existing_claims:
        return [
            {
                "id": c.id,
                "resume_id": c.resume_id,
                "claim_type": c.claim_type,
                "claim_text": c.claim_text,
                "verification_question": c.verification_question,
                "candidate_answer": c.candidate_answer,
                "status": c.status,
                "notes": c.notes,
                "created_at": c.created_at,
            }
            for c in existing_claims
        ]

    profile = json.loads(resume.edited_profile_json or resume.raw_profile_json)
    extracted = ResumeEvidenceCheckerService.extract_claims(profile, resume.extracted_text)

    records = []
    for item in extracted:
        claim_record = ResumeEvidenceClaim(
            user_id=current_user.id,
            resume_id=resume.id,
            claim_type=item["claim_type"],
            claim_text=item["claim_text"],
            verification_question=item["verification_question"],
            status="pending",
        )
        db.add(claim_record)
        records.append(claim_record)

    db.commit()

    return [
        {
            "id": c.id,
            "resume_id": c.resume_id,
            "claim_type": c.claim_type,
            "claim_text": c.claim_text,
            "verification_question": c.verification_question,
            "candidate_answer": c.candidate_answer,
            "status": c.status,
            "notes": c.notes,
            "created_at": c.created_at,
        }
        for c in records
    ]


@router.get("/claims/{resume_id}")
def list_claims(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    claims = db.query(ResumeEvidenceClaim).filter(ResumeEvidenceClaim.resume_id == resume.id).all()
    return [
        {
            "id": c.id,
            "resume_id": c.resume_id,
            "claim_type": c.claim_type,
            "claim_text": c.claim_text,
            "verification_question": c.verification_question,
            "candidate_answer": c.candidate_answer,
            "status": c.status,
            "notes": c.notes,
            "created_at": c.created_at,
        }
        for c in claims
    ]


@router.post("/answer")
def answer_claim_verification(
    payload: EvidenceAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    claim = (
        db.query(ResumeEvidenceClaim)
        .filter(ResumeEvidenceClaim.id == payload.claim_id, ResumeEvidenceClaim.user_id == current_user.id)
        .first()
    )
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence claim record not found.")

    eval_result = ResumeEvidenceCheckerService.evaluate_verification_answer(
        question=claim.verification_question,
        candidate_answer=payload.candidate_answer.strip()
    )

    claim.candidate_answer = payload.candidate_answer.strip()
    claim.status = eval_result["status"]
    claim.notes = eval_result["guidance"]
    db.commit()
    db.refresh(claim)

    return {
        "id": claim.id,
        "status": claim.status,
        "guidance": claim.notes,
        "disclaimer": eval_result["disclaimer"],
    }
