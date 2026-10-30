import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
import app.models.models  # Ensures all models are registered on Base.metadata
from app.models.models import SystemQuestionBank
from app.services.fallback_bank import FALLBACK_QUESTIONS
from app.routers import (
    auth,
    resumes,
    matching,
    interviews,
    evidence,
    analytics,
    admin,
    reports,
)


# Initialize tables and initial seed data synchronously
Base.metadata.create_all(bind=engine)


def init_seed_data():
    db = SessionLocal()
    try:
        count = db.query(SystemQuestionBank).count()
        if count == 0:
            for q in FALLBACK_QUESTIONS:
                record = SystemQuestionBank(
                    role=q["role"],
                    category=q["category"],
                    difficulty=q["difficulty"],
                    skill_tag=q["skill_tag"],
                    question_text=q["question_text"],
                    expected_points_json=json.dumps(q.get("expected_points", [])),
                    sample_good_answer=q.get("sample_good_answer", ""),
                    is_active=True,
                )
                db.add(record)
            db.commit()
    except Exception as e:
        print(f"Notice during seed: {e}")
    finally:
        db.close()


init_seed_data()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(resumes.router, prefix=settings.API_PREFIX)
app.include_router(matching.router, prefix=settings.API_PREFIX)
app.include_router(interviews.router, prefix=settings.API_PREFIX)
app.include_router(evidence.router, prefix=settings.API_PREFIX)
app.include_router(analytics.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)
app.include_router(reports.router, prefix=settings.API_PREFIX)


# Root endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to Resume2Career API",
        "status": "running",
        "documentation": "/api/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": "development",
        "database": "sqlite_active",
        "llm_configured": bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
