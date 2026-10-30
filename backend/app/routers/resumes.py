import os
import json
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Resume
from app.schemas.schemas import ResumeResponse, ResumeProfile, ResumeUpdateProfileRequest
from app.services.resume_parser import ResumeParserService
from app.services.resume_analyzer import ResumeAnalyzerService

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Validate file extension
    original_name = file.filename or "resume"
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Only .pdf and .docx files are permitted."
        )

    # 2. Validate MIME type
    content_type = file.content_type or ""
    if content_type not in settings.ALLOWED_MIME_TYPES and not content_type.startswith("application/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid MIME type '{content_type}'. Please upload an authentic PDF or DOCX file."
        )

    # 3. Read content with size check
    content = await file.read()
    file_size = len(content)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    if file_size < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty or corrupted."
        )

    # 4. Safe save path to prevent path traversal
    safe_filename = f"{uuid.uuid4().hex}_{os.path.basename(original_name)}"
    save_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    with open(save_path, "wb") as f:
        f.write(content)

    # 5. Parse document
    try:
        raw_text, profile = ResumeParserService.parse_document(save_path, original_name)
    except HTTPException:
        # Clean up file on validation error
        if os.path.exists(save_path):
            os.remove(save_path)
        raise
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while parsing the resume: {str(e)}"
        )

    # 6. Run initial heuristic analysis
    analysis = ResumeAnalyzerService.analyze_profile(profile, raw_text)

    # 7. Persist to DB
    new_resume = Resume(
        user_id=current_user.id,
        filename=original_name,
        file_path=save_path,
        file_type="pdf" if ext == ".pdf" else "docx",
        file_size_bytes=file_size,
        extracted_text=raw_text,
        raw_profile_json=json.dumps(profile),
        edited_profile_json=json.dumps(profile),
        analysis_json=json.dumps(analysis),
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return {
        "id": new_resume.id,
        "filename": new_resume.filename,
        "file_type": new_resume.file_type,
        "file_size_bytes": new_resume.file_size_bytes,
        "profile": profile,
        "analysis": analysis,
        "created_at": new_resume.created_at,
        "updated_at": new_resume.updated_at,
    }


@router.get("")
def list_user_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()
    results = []
    for r in resumes:
        profile = json.loads(r.edited_profile_json or r.raw_profile_json)
        analysis = json.loads(r.analysis_json) if r.analysis_json else None
        results.append({
            "id": r.id,
            "filename": r.filename,
            "file_type": r.file_type,
            "file_size_bytes": r.file_size_bytes,
            "profile": profile,
            "analysis": analysis,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        })
    return results


@router.get("/{resume_id}")
def get_resume(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or you do not have permission to access it."
        )

    profile = json.loads(resume.edited_profile_json or resume.raw_profile_json)
    analysis = json.loads(resume.analysis_json) if resume.analysis_json else None

    return {
        "id": resume.id,
        "filename": resume.filename,
        "file_type": resume.file_type,
        "file_size_bytes": resume.file_size_bytes,
        "profile": profile,
        "analysis": analysis,
        "created_at": resume.created_at,
        "updated_at": resume.updated_at,
    }


@router.put("/{resume_id}/profile")
def update_resume_profile(
    resume_id: int,
    payload: ResumeUpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or you do not have permission to modify it."
        )

    updated_profile_dict = payload.profile.model_dump()
    new_analysis = ResumeAnalyzerService.analyze_profile(updated_profile_dict, resume.extracted_text)

    resume.edited_profile_json = json.dumps(updated_profile_dict)
    resume.analysis_json = json.dumps(new_analysis)
    db.commit()
    db.refresh(resume)

    return {
        "id": resume.id,
        "message": "Resume profile updated and re-analyzed successfully.",
        "profile": updated_profile_dict,
        "analysis": new_analysis,
    }


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found."
        )

    # Delete physical file if exists
    if os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception:
            pass

    db.delete(resume)
    db.commit()
    return None
