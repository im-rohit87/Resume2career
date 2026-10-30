# Resume2Interview AI

> **An Intelligent Resume Analysis and Adaptive Mock Interview System**  
> A complete, functional BTech Major Project — Python FastAPI backend + React TypeScript frontend

---

## 🎯 Project Overview

Resume2Interview AI is a full-stack web application that:
1. **Parses resumes** (PDF/DOCX) and extracts structured profile data
2. **Analyzes resumes** with a transparent heuristic scoring system
3. **Matches resumes** against job descriptions using TF-IDF cosine similarity + skill taxonomy
4. **Generates adaptive mock interviews** with AI or curated fallback questions
5. **Evaluates answers** using a multi-criterion rubric engine
6. **Checks resume evidence** — verifies candidates can explain their own claims
7. **Tracks performance** with trend analytics and criterion-wise radar charts
8. **Generates learning plans** (7/15/30-day roadmaps) based on skill gaps
9. **Produces downloadable PDF reports** for each completed interview session

---

## 🏗️ Architecture

```
resume2interview-ai/
├── backend/                     # Python 3.15 + FastAPI
│   ├── app/
│   │   ├── core/               # Config, DB session, JWT security
│   │   │   ├── config.py       # Environment-based Settings class
│   │   │   ├── database.py     # SQLAlchemy engine + session factory
│   │   │   └── security.py     # bcrypt hashing, JWT encode/decode
│   │   ├── models/
│   │   │   └── models.py       # 9 SQLAlchemy ORM models
│   │   ├── routers/
│   │   │   ├── auth.py         # Register, Login, Me
│   │   │   ├── resumes.py      # Upload, parse, analyze, edit, delete
│   │   │   ├── matching.py     # Job description matching
│   │   │   ├── interviews.py   # Create, submit answers, adaptive flow
│   │   │   ├── evidence.py     # Resume claim extraction & defense
│   │   │   ├── analytics.py    # Dashboard, learning plans
│   │   │   ├── reports.py      # JSON + PDF report endpoints
│   │   │   └── admin.py        # Question bank, system stats
│   │   ├── schemas/
│   │   │   └── schemas.py      # 30+ Pydantic v2 schemas
│   │   ├── services/
│   │   │   ├── resume_parser.py      # PyMuPDF + python-docx
│   │   │   ├── resume_analyzer.py    # Heuristic scoring engine
│   │   │   ├── matching_service.py   # Pure-Python TF-IDF cosine sim
│   │   │   ├── llm_service.py        # Gemini/OpenAI with fallback
│   │   │   ├── fallback_bank.py      # 10 curated interview questions
│   │   │   ├── evaluator_service.py  # Multi-criterion rubric engine
│   │   │   ├── evidence_checker.py   # Resume claim extractor
│   │   │   ├── learning_plan_service.py  # Day-by-day plan generator
│   │   │   └── report_service.py     # ReportLab PDF generation
│   │   └── main.py             # FastAPI app, CORS, routing, lifespan
│   ├── tests/
│   │   └── test_api.py         # 10 pytest integration tests (all passing)
│   ├── uploads/                # Uploaded resume files (gitignored)
│   └── requirements.txt
├── frontend/                    # React 18 + TypeScript + Vite
│   ├── src/
│   │   ├── components/         # Navbar, ScoreGauge, RadarChart, TrendChart,
│   │   │                       # AudioRecorder (Web Speech API), VoiceSpeaker
│   │   ├── pages/              # 11 full-featured pages
│   │   │   ├── AuthPage.tsx    # Login + Registration
│   │   │   ├── ResumesPage.tsx # Upload, parse, edit, analyze
│   │   │   ├── MatchingPage.tsx# JD matching with evidence snippets
│   │   │   ├── InterviewSetupPage.tsx
│   │   │   ├── InterviewPage.tsx     # Live adaptive interview
│   │   │   ├── EvidenceCheckerPage.tsx
│   │   │   ├── HistoryPage.tsx
│   │   │   ├── ReportPage.tsx        # Full report + PDF download
│   │   │   ├── AnalyticsDashboard.tsx
│   │   │   ├── LearningPlanPage.tsx
│   │   │   └── AdminPage.tsx
│   │   ├── services/api.ts     # Type-safe API client
│   │   ├── types.ts            # All TypeScript interfaces
│   │   ├── App.tsx             # State-based routing
│   │   └── main.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts          # Proxy /api → localhost:8000
├── sample_data/
│   ├── alex_chen_resume.pdf    # Fictional candidate resume (PDF)
│   ├── alex_chen_resume.docx   # Same resume (DOCX)
│   └── sample_fullstack_job_description.txt
├── .env.example                # Placeholder env vars (no secrets)
├── .gitignore
└── README.md
```

---

## ⚙️ Database Schema

9 SQLAlchemy models with relationships, cascades and foreign-key integrity:

| Table | Purpose |
|-------|---------|
| `users` | Accounts with bcrypt-hashed passwords, role-based access |
| `resumes` | Uploaded files + extracted text + parsed/edited profile JSON |
| `job_descriptions` | Pasted JD text + extracted required/preferred skills |
| `job_match_results` | Per-match scores, evidence, recommendations |
| `interview_sessions` | Session state, adaptive difficulty, completion status |
| `interview_questions` | Per-question text, category, expected points |
| `interview_answers` | Candidate answers with timing |
| `answer_evaluations` | 5-criterion rubric scores + feedback |
| `resume_evidence_claims` | Resume claims + verification questions + defense status |
| `learning_plans` | Generated day-by-day study plans |
| `system_question_bank` | Admin-managed curated questions (seeded on startup) |

---

## 🚀 Setup & Installation

### Prerequisites
- **Python 3.10+** (tested on 3.15)
- **Node.js 18+** (tested on 22.23)
- **npm** (no pnpm needed)

### Step 1 — Clone / Enter the Project

```bash
cd C:\Users\YourName\path\to\resume2interview-ai
```

### Step 2 — Backend Setup

```bash
cd backend

# Install Python dependencies (all already available if using the provided environment)
pip install -r requirements.txt

# Copy environment config (already done — .env exists)
# Edit .env if you want to add an AI API key for live LLM features
# The system works fully without an API key using the curated fallback question bank
```

### Step 3 — Frontend Setup

```bash
cd frontend

# If node_modules is missing (fresh clone):
npm install

# node_modules is pre-installed in this workspace
```

### Step 4 — Run Both Services

Open **two terminals**:

**Terminal 1 — Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

### Step 5 — Access the Application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **API Docs (Swagger)** | http://localhost:8000/api/docs |
| **API Redoc** | http://localhost:8000/api/redoc |
| **Health Check** | http://localhost:8000/api/health |

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Required for full AI features (optional — system runs with fallbacks)
GEMINI_API_KEY=your_gemini_api_key_here
# OR
OPENAI_API_KEY=your_openai_key_here

# Security (must change for production)
SECRET_KEY=your_64_character_random_hex_string

# Database (default: SQLite local file)
DATABASE_URL=sqlite:///./resume2interview.db

# File upload constraints
MAX_UPLOAD_SIZE_MB=5
```

> **Note:** The system runs fully without any AI key. All interview questions come from the curated `fallback_bank.py` and all evaluations use the deterministic rubric engine. Only `evaluated_by` will show `"heuristic_engine"` instead of `"ai_llm"`.

---

## 🧪 Test Results

All 10 backend integration tests pass (executed 2026-10-30):

```
tests/test_api.py::test_health_check                              PASSED
tests/test_api.py::test_auth_registration_and_login               PASSED
tests/test_api.py::test_unauthorized_endpoints                    PASSED
tests/test_api.py::test_cross_user_isolation                      PASSED
tests/test_api.py::test_resume_upload_and_scanned_error           PASSED
tests/test_api.py::test_job_matching_and_scoring                  PASSED
tests/test_api.py::test_mock_interview_flow_and_duplicate_prevention PASSED
tests/test_api.py::test_admin_authorization                       PASSED
tests/test_api.py::test_evidence_claims_and_defense               PASSED
tests/test_api.py::test_analytics_and_learning_plan               PASSED

10 passed in 5.17s
```

**Run tests yourself:**
```bash
cd backend
python -m pytest -v tests/test_api.py
```

> ⚠️ Tests require `BypassSandbox=true` (network socket binding) when running inside the Antigravity sandbox environment. Outside sandbox, run normally.

---

## 📖 API Documentation

All endpoints are documented via FastAPI's auto-generated OpenAPI spec.

**Interactive:** http://localhost:8000/api/docs

### Endpoint Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/login` | Sign in, get JWT token |
| GET | `/api/auth/me` | Get current user profile |
| POST | `/api/resumes/upload` | Upload PDF/DOCX resume |
| GET | `/api/resumes` | List my resumes |
| PUT | `/api/resumes/{id}/profile` | Edit parsed profile + re-analyze |
| POST | `/api/matching/match` | Match resume against JD |
| GET | `/api/matching/history` | Past match results |
| POST | `/api/interviews/create` | Start new interview session |
| GET | `/api/interviews/session/{id}` | Get session + questions + answers |
| POST | `/api/interviews/submit-answer` | Submit answer (evaluates immediately) |
| POST | `/api/interviews/session/{id}/finish` | Mark session complete |
| GET | `/api/interviews/history` | All past sessions |
| POST | `/api/evidence/extract/{resume_id}` | Extract resume claims |
| POST | `/api/evidence/answer` | Submit claim defense |
| GET | `/api/analytics/dashboard` | Performance metrics |
| POST | `/api/analytics/learning-plan` | Generate learning roadmap |
| GET | `/api/reports/session/{id}` | Full JSON interview report |
| GET | `/api/reports/session/{id}/pdf` | Download PDF report |
| GET | `/api/admin/questions` | List question bank (admin only) |
| GET | `/api/admin/stats` | System statistics (admin only) |
| GET | `/api/health` | Health check |

---

## 📁 Sample Data

Located in `sample_data/` — all fictional test data:

- **`alex_chen_resume.pdf`** — Full-stack engineer resume with Python, React, FastAPI, Docker, PostgreSQL, Redis
- **`alex_chen_resume.docx`** — Same resume in DOCX format
- **`sample_fullstack_job_description.txt`** — "Senior Full Stack Engineer" JD at fictional CloudScale Innovations
- **`blank_scanned_sample.pdf`** — A blank PDF to test scanned-document detection

---

## 🏫 BTech Project Documentation Outline

### Abstract
Resume2Interview AI addresses the gap between academic preparation and job-readiness for software engineering candidates. It provides an end-to-end pipeline from resume analysis → job description matching → adaptive mock interviews → evidence-based preparation tracking.

### Problem Statement
Most candidates prepare for interviews without objective feedback on their resume quality, skill gaps vs. target roles, or answer quality in mock interviews. Existing tools either provide ATS scores without transparency, or generic interview questions unrelated to the candidate's specific background.

### Objectives
1. Parse and analyze any PDF/DOCX resume with zero fabricated data
2. Match a candidate's profile against any job description with explained scoring
3. Generate personalized, resume-grounded interview questions
4. Adapt difficulty based on answer quality in real-time
5. Provide criterion-level feedback with model answers and improvement guidance
6. Help candidates practice defending their resume claims under questioning
7. Track performance trends and generate targeted learning plans

### Technology Stack
- **Frontend:** React 18 + TypeScript + Tailwind CSS + Vite (port 3000)
- **Backend:** Python 3.15 + FastAPI + Uvicorn (port 8000)
- **Database:** SQLite with SQLAlchemy ORM (PostgreSQL-compatible via DATABASE_URL)
- **Resume Parsing:** PyMuPDF (PDF) + python-docx (DOCX)
- **Skill Matching:** Pure-Python TF-IDF cosine similarity + curated taxonomy
- **Authentication:** bcrypt password hashing + PyJWT RS256 tokens
- **PDF Reports:** ReportLab
- **AI (Optional):** Gemini 1.5 Flash or OpenAI GPT-3.5 (via GEMINI_API_KEY / OPENAI_API_KEY)

### Key Algorithms
1. **Resume Parsing:** Section-header detection + regex-based field extraction (email, phone, LinkedIn, GitHub, skills taxonomy matching)
2. **Heuristic Resume Score:** Weighted rubric across 5 dimensions (contact 15%, skills 25%, experience+projects 30%, structure 20%, metrics 10%)
3. **Job Match Score:** `(Required Skills Coverage × 60%) + (Preferred Skills Coverage × 25%) + (TF-IDF Cosine Similarity × 15%)`
4. **Adaptive Difficulty:** Score ≥75 → next question "advanced"; 50–74 → "intermediate"; <50 → "beginner"
5. **Answer Evaluation:** 5-criterion weighted rubric (relevance 20%, technical 25%, completeness 20%, clarity 15%, reasoning 20%)

### Known Limitations
- **OCR not implemented:** Scanned/image-only PDFs return a clear error asking the user to provide text-based PDFs; no fabricated data is returned
- **Skill extraction heuristic:** Based on a curated taxonomy (~80 skills); uncommon or highly specialized skills may be missed
- **AI features optional:** Without an API key, all questions come from the curated fallback bank (10 high-quality questions covering Full Stack, Backend, Behavioral, HR categories)
- **Rate limiting not implemented:** Development build; add middleware (e.g., slowapi) for production
- **No email verification:** Accounts are created immediately without email confirmation
- **SQLite in development:** Switch to PostgreSQL for production by changing DATABASE_URL

### Future Scope
- Integrate OCR (Tesseract) for scanned PDF support
- Add sentence-transformers for semantic skill similarity
- Implement video interview mode with facial landmark detection (with explicit consent and bias disclaimer)
- Add OAuth2 (Google/GitHub) login
- Build a company-side portal for bulk candidate assessment
- Add multilingual support for non-English resumes

---

## ⚠️ Security Notes

- All passwords are hashed with bcrypt (cost factor 12) — never stored in plaintext
- JWT tokens expire after 24 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Every user-data endpoint verifies the authenticated user's ID server-side
- File uploads validate extension, MIME type, size limit, and use UUIDs to prevent path traversal
- CORS is restricted to configured origins (localhost:3000 and localhost:5173 by default)
- API keys are read from environment variables only — never exposed to the frontend
- Scanned PDFs return a clear error rather than fabricated data
- All AI evaluations are labeled as estimates — never presented as objective facts

---

## 🙏 Acknowledgements

Built as a BTech Major Project demonstrating:
- Full-stack web development (FastAPI + React + TypeScript)
- Natural Language Processing (resume parsing, TF-IDF similarity)
- Database architecture (SQLAlchemy ORM with relational schema)
- Secure authentication (JWT + bcrypt)
- Adaptive algorithmic systems (difficulty calibration)
- Responsible AI disclosure (disclaimers, fallbacks, no fabrication)
