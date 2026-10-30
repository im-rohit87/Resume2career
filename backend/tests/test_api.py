import os
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.config import settings
import app.models.models  # Register all models on Base.metadata
from app.models.models import SystemQuestionBank
from app.services.fallback_bank import FALLBACK_QUESTIONS
from app.main import app as fastapi_app

# Test in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_temp.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
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
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_temp.db"):
        try:
            os.remove("./test_temp.db")
        except Exception:
            pass


@pytest.fixture(scope="module")
def client():
    with TestClient(fastapi_app) as client:
        yield client


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "sqlite_active"


def test_auth_registration_and_login(client):
    # 1. Register User A
    reg_payload = {
        "email": "candidate.a@example.com",
        "username": "candidateA",
        "password": "Password123!",
        "full_name": "Candidate Alpha",
    }
    r = client.post("/api/auth/register", json=reg_payload)
    assert r.status_code == 201
    data = r.json()
    assert "access_token" in data
    assert data["user"]["username"] == "candidatea"

    # 2. Duplicate registration should fail
    r_dup = client.post("/api/auth/register", json=reg_payload)
    assert r_dup.status_code == 400
    assert "already exists" in r_dup.json()["detail"].lower()

    # 3. Login with correct credentials
    login_payload = {
        "username_or_email": "candidateA",
        "password": "Password123!",
    }
    r_login = client.post("/api/auth/login", json=login_payload)
    assert r_login.status_code == 200
    assert "access_token" in r_login.json()

    # 4. Login with incorrect password
    bad_login = {
        "username_or_email": "candidateA",
        "password": "WrongPassword",
    }
    r_bad = client.post("/api/auth/login", json=bad_login)
    assert r_bad.status_code == 401


def test_unauthorized_endpoints(client):
    # Endpoints requiring auth must reject unauthenticated requests
    r1 = client.get("/api/resumes")
    assert r1.status_code == 401

    r2 = client.get("/api/interviews/history")
    assert r2.status_code == 401

    r3 = client.get("/api/analytics/dashboard")
    assert r3.status_code == 401


def test_cross_user_isolation(client):
    # Register User A
    u1 = client.post("/api/auth/register", json={
        "email": "user1@example.com",
        "username": "userone",
        "password": "Password123!",
        "full_name": "User One",
    }).json()
    t1 = u1["access_token"]

    # Register User B
    u2 = client.post("/api/auth/register", json={
        "email": "user2@example.com",
        "username": "usertwo",
        "password": "Password123!",
        "full_name": "User Two",
    }).json()
    t2 = u2["access_token"]

    # User A creates interview
    r_create = client.post(
        "/api/interviews/create",
        headers={"Authorization": f"Bearer {t1}"},
        json={"target_role": "Backend Engineer", "difficulty_level": "intermediate", "total_questions": 3}
    )
    assert r_create.status_code == 200
    session_id = r_create.json()["session_id"]

    # User B attempts to access User A's session -> must be 404 or 403
    r_cross = client.get(
        f"/api/interviews/session/{session_id}",
        headers={"Authorization": f"Bearer {t2}"}
    )
    assert r_cross.status_code == 404


def test_resume_upload_and_scanned_error(client):
    # Register user
    user = client.post("/api/auth/register", json={
        "email": "uploader@example.com",
        "username": "uploader",
        "password": "Password123!",
        "full_name": "Resume Uploader",
    }).json()
    token = user["access_token"]

    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_data"))
    pdf_file = os.path.join(sample_dir, "alex_chen_resume.pdf")
    blank_file = os.path.join(sample_dir, "blank_scanned_sample.pdf")

    # 1. Upload valid PDF
    with open(pdf_file, "rb") as f:
        r = client.post(
            "/api/resumes/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("alex_chen_resume.pdf", f, "application/pdf")},
        )
    assert r.status_code == 200
    res_data = r.json()
    assert res_data["profile"]["contact"]["email"] == "alex.chen.engineer@example.com"
    assert "fastapi" in str(res_data["profile"]["skills"]).lower()
    assert res_data["analysis"]["heuristic_score"] > 60

    # 2. Upload blank/scanned PDF -> must return 422 with OCR notice
    with open(blank_file, "rb") as f:
        r_blank = client.post(
            "/api/resumes/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("blank_scanned_sample.pdf", f, "application/pdf")},
        )
    assert r_blank.status_code == 422
    assert "ocr" in r_blank.json()["detail"].lower()


def test_job_matching_and_scoring(client):
    user = client.post("/api/auth/register", json={
        "email": "matcher@example.com",
        "username": "matcher",
        "password": "Password123!",
        "full_name": "Job Matcher",
    }).json()
    token = user["access_token"]

    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_data"))
    pdf_file = os.path.join(sample_dir, "alex_chen_resume.pdf")
    jd_file = os.path.join(sample_dir, "sample_fullstack_job_description.txt")

    with open(pdf_file, "rb") as f:
        r_up = client.post(
            "/api/resumes/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("alex_chen_resume.pdf", f, "application/pdf")},
        )
    resume_id = r_up.json()["id"]

    with open(jd_file, "r", encoding="utf-8") as f:
        jd_text = f.read()

    r_match = client.post(
        "/api/matching/match",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "resume_id": resume_id,
            "role_title": "Senior Full Stack Engineer",
            "company_name": "CloudScale Innovations",
            "job_description_text": jd_text,
        }
    )
    assert r_match.status_code == 200
    m_data = r_match.json()
    assert m_data["match_score"] >= 50.0
    assert "formula_explanation" in m_data
    assert "disclaimer" in m_data


def test_mock_interview_flow_and_duplicate_prevention(client):
    user = client.post("/api/auth/register", json={
        "email": "interviewee@example.com",
        "username": "interviewee",
        "password": "Password123!",
        "full_name": "Mock Interviewee",
    }).json()
    token = user["access_token"]

    # 1. Create Interview Session
    r_create = client.post(
        "/api/interviews/create",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "target_role": "Full Stack Developer",
            "difficulty_level": "adaptive",
            "total_questions": 3,
        }
    )
    assert r_create.status_code == 200
    sess = r_create.json()
    session_id = sess["session_id"]

    # 2. Get Session detail & Question 1
    r_detail = client.get(f"/api/interviews/session/{session_id}", headers={"Authorization": f"Bearer {token}"})
    assert r_detail.status_code == 200
    questions = r_detail.json()["questions"]
    assert len(questions) == 3
    q1 = questions[0]

    # 3. Submit Answer for Question 1
    ans_payload = {
        "question_id": q1["id"],
        "answer_text": "In JavaScript, strict equality === checks both value and type without type coercion, preventing unexpected bugs, whereas == coerces types before checking equality.",
        "speech_used": False,
        "time_taken_seconds": 35,
    }
    r_ans = client.post("/api/interviews/submit-answer", headers={"Authorization": f"Bearer {token}"}, json=ans_payload)
    assert r_ans.status_code == 200
    eval_data = r_ans.json()
    assert eval_data["overall_score"] > 50.0
    assert "relevance_score" in eval_data
    assert "disclaimer" in eval_data

    # 4. Attempt Duplicate Submission on same question -> handled gracefully
    r_dup = client.post("/api/interviews/submit-answer", headers={"Authorization": f"Bearer {token}"}, json=ans_payload)
    assert r_dup.status_code == 200
    assert "already submitted" in r_dup.json()["message"].lower()

    # 5. Answer remaining questions to complete session
    for q in questions[1:]:
        client.post(
            "/api/interviews/submit-answer",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "question_id": q["id"],
                "answer_text": "I utilized Docker containerization and Redis caching to optimize throughput and isolate microservice environments.",
                "speech_used": False,
                "time_taken_seconds": 40,
            }
        )

    # 6. Verify Session is completed
    r_done = client.get(f"/api/interviews/session/{session_id}", headers={"Authorization": f"Bearer {token}"})
    assert r_done.json()["status"] == "completed"
    assert r_done.json()["overall_score"] is not None

    # 7. Check PDF report generation endpoint
    r_pdf = client.get(f"/api/reports/session/{session_id}/pdf", headers={"Authorization": f"Bearer {token}"})
    assert r_pdf.status_code == 200
    assert r_pdf.headers["content-type"] == "application/pdf"
    assert len(r_pdf.content) > 500


def test_admin_authorization(client):
    # Regular user attempting admin endpoint -> 403 Forbidden
    reg_user = client.post("/api/auth/register", json={
        "email": "normal@example.com",
        "username": "normaluser",
        "password": "Password123!",
        "full_name": "Normal User",
    }).json()
    token_normal = reg_user["access_token"]

    r_forbidden = client.get("/api/admin/questions", headers={"Authorization": f"Bearer {token_normal}"})
    assert r_forbidden.status_code == 403

    # Admin user
    admin_user = client.post("/api/auth/register", json={
        "email": "admin@example.com",
        "username": "admin",
        "password": "AdminPassword123!",
        "full_name": "System Administrator",
    }).json()
    token_admin = admin_user["access_token"]

    r_admin = client.get("/api/admin/questions", headers={"Authorization": f"Bearer {token_admin}"})
    assert r_admin.status_code == 200
    assert isinstance(r_admin.json(), list)


def test_evidence_claims_and_defense(client):
    user = client.post("/api/auth/register", json={
        "email": "defender@example.com",
        "username": "defender",
        "password": "Password123!",
        "full_name": "Defense Candidate",
    }).json()
    token = user["access_token"]

    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_data"))
    pdf_file = os.path.join(sample_dir, "alex_chen_resume.pdf")

    with open(pdf_file, "rb") as f:
        r_up = client.post(
            "/api/resumes/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("alex_chen_resume.pdf", f, "application/pdf")},
        )
    resume_id = r_up.json()["id"]

    # 1. Extract Claims
    r_extract = client.post(f"/api/evidence/extract/{resume_id}", headers={"Authorization": f"Bearer {token}"})
    assert r_extract.status_code == 200
    claims = r_extract.json()
    assert len(claims) >= 2
    claim_id = claims[0]["id"]

    # 2. Defend a claim
    r_ans = client.post(
        "/api/evidence/answer",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "claim_id": claim_id,
            "candidate_answer": "In our architecture, we established baseline benchmarks of 240ms latency. We integrated Redis LRU caching for product catalog endpoints which reduced query latency to 85ms measured using Datadog APM.",
        }
    )
    assert r_ans.status_code == 200
    res = r_ans.json()
    assert res["status"] in ["verified_strong", "practiced"]
    assert "guidance" in res


def test_analytics_and_learning_plan(client):
    user = client.post("/api/auth/register", json={
        "email": "planner@example.com",
        "username": "planner",
        "password": "Password123!",
        "full_name": "Plan Candidate",
    }).json()
    token = user["access_token"]

    # 1. Generate 15-day learning plan
    r_plan = client.post(
        "/api/analytics/learning-plan",
        headers={"Authorization": f"Bearer {token}"},
        json={"duration_days": 15, "target_role": "Full Stack Developer", "focus_skills": ["Redis", "Docker"]}
    )
    assert r_plan.status_code == 200
    plan = r_plan.json()
    assert len(plan["daily_schedule"]) == 15
    assert plan["daily_schedule"][0]["day"] == 1

    # 2. Check dashboard metrics
    r_dash = client.get("/api/analytics/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r_dash.status_code == 200
    dash = r_dash.json()
    assert "criterion_averages" in dash
    assert "disclaimer" in dash
