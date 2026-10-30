import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Resume, JobDescription, JobMatchResult
from app.schemas.schemas import JobMatchRequest, JobMatchResponse
from app.services.matching_service import MatchingService

router = APIRouter(prefix="/matching", tags=["Job Matching"])


@router.post("/match")
def match_job(payload: JobMatchRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Verify resume ownership
    resume = db.query(Resume).filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified resume not found or access denied."
        )

    profile = json.loads(resume.edited_profile_json or resume.raw_profile_json)

    # 2. Run matching analysis
    match_data = MatchingService.match_resume_to_job(
        resume_profile=profile,
        raw_resume_text=resume.extracted_text,
        role_title=payload.role_title,
        job_text=payload.job_description_text,
    )

    # 3. Save JobDescription entity
    extracted_skills = {
        "required": [s["skill"] for s in match_data["required_skills_matched"]] + match_data["required_skills_missing"],
        "preferred": [s["skill"] for s in match_data["preferred_skills_matched"]] + match_data["preferred_skills_missing"],
    }
    job_record = JobDescription(
        user_id=current_user.id,
        role_title=payload.role_title,
        company_name=payload.company_name or "",
        raw_text=payload.job_description_text,
        extracted_skills_json=json.dumps(extracted_skills),
    )
    db.add(job_record)
    db.commit()
    db.refresh(job_record)

    # 4. Save JobMatchResult
    match_record = JobMatchResult(
        user_id=current_user.id,
        resume_id=resume.id,
        job_id=job_record.id,
        match_score=match_data["match_score"],
        score_breakdown_json=json.dumps(match_data["score_breakdown"]),
        matched_skills_json=json.dumps({
            "required": match_data["required_skills_matched"],
            "preferred": match_data["preferred_skills_matched"],
        }),
        missing_skills_json=json.dumps({
            "required": match_data["required_skills_missing"],
            "preferred": match_data["preferred_skills_missing"],
        }),
        related_skills_json=json.dumps(match_data["related_skills_present"]),
        recommendations_json=json.dumps(match_data["recommendations"]),
    )
    db.add(match_record)
    db.commit()
    db.refresh(match_record)

    return {
        "id": match_record.id,
        "job_id": job_record.id,
        "resume_id": resume.id,
        "role_title": payload.role_title,
        "company_name": payload.company_name,
        "match_score": match_data["match_score"],
        "score_breakdown": match_data["score_breakdown"],
        "required_skills_matched": match_data["required_skills_matched"],
        "required_skills_missing": match_data["required_skills_missing"],
        "preferred_skills_matched": match_data["preferred_skills_matched"],
        "preferred_skills_missing": match_data["preferred_skills_missing"],
        "related_skills_present": match_data["related_skills_present"],
        "recommendations": match_data["recommendations"],
        "formula_explanation": match_data["formula_explanation"],
        "disclaimer": match_data["disclaimer"],
        "created_at": match_record.created_at,
    }


@router.get("/history")
def list_match_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = db.query(JobMatchResult).filter(JobMatchResult.user_id == current_user.id).order_by(JobMatchResult.created_at.desc()).all()
    out = []
    for r in results:
        job = db.query(JobDescription).filter(JobDescription.id == r.job_id).first()
        resume = db.query(Resume).filter(Resume.id == r.resume_id).first()
        breakdown = json.loads(r.score_breakdown_json) if r.score_breakdown_json else {}
        matched = json.loads(r.matched_skills_json) if r.matched_skills_json else {}
        missing = json.loads(r.missing_skills_json) if r.missing_skills_json else {}
        related = json.loads(r.related_skills_json) if r.related_skills_json else []
        recs = json.loads(r.recommendations_json) if r.recommendations_json else []

        out.append({
            "id": r.id,
            "resume_id": r.resume_id,
            "resume_filename": resume.filename if resume else "Unknown",
            "job_id": r.job_id,
            "role_title": job.role_title if job else "Software Engineer",
            "company_name": job.company_name if job else "",
            "match_score": r.match_score,
            "score_breakdown": breakdown,
            "required_skills_matched": matched.get("required", []),
            "required_skills_missing": missing.get("required", []),
            "preferred_skills_matched": matched.get("preferred", []),
            "preferred_skills_missing": missing.get("preferred", []),
            "related_skills_present": related,
            "recommendations": recs,
            "created_at": r.created_at,
        })
    return out


@router.get("/{match_id}")
def get_match_detail(match_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = db.query(JobMatchResult).filter(JobMatchResult.id == match_id, JobMatchResult.user_id == current_user.id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match record not found.")

    job = db.query(JobDescription).filter(JobDescription.id == r.job_id).first()
    resume = db.query(Resume).filter(Resume.id == r.resume_id).first()

    return {
        "id": r.id,
        "resume_id": r.resume_id,
        "resume_filename": resume.filename if resume else "Unknown",
        "job_id": r.job_id,
        "role_title": job.role_title if job else "Software Engineer",
        "company_name": job.company_name if job else "",
        "job_text": job.raw_text if job else "",
        "match_score": r.match_score,
        "score_breakdown": json.loads(r.score_breakdown_json),
        "required_skills_matched": json.loads(r.matched_skills_json).get("required", []),
        "required_skills_missing": json.loads(r.missing_skills_json).get("required", []),
        "preferred_skills_matched": json.loads(r.matched_skills_json).get("preferred", []),
        "preferred_skills_missing": json.loads(r.missing_skills_json).get("preferred", []),
        "related_skills_present": json.loads(r.related_skills_json),
        "recommendations": json.loads(r.recommendations_json),
        "created_at": r.created_at,
    }
