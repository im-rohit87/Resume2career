# Resume2Interview AI — BTech Major Project Report Outline

**Project Title:** Resume2Interview AI — An Intelligent Resume Analysis and Adaptive Mock Interview System  
**Degree:** Bachelor of Technology (B.Tech)  
**Branch:** Computer Science and Engineering  
**Academic Year:** 2025–2026

---

## Chapter 1: Introduction

### 1.1 Background and Motivation
The gap between candidate preparation and actual interview readiness is a persistent challenge in the job market. Traditional interview preparation methods—textbooks, coaching classes, and generic online resources—lack personalization. Candidates often study topics irrelevant to their specific resume and target role.

### 1.2 Problem Statement
Develop a web-based AI system that:
- Automatically analyzes a candidate's resume
- Identifies skill gaps relative to a target job description
- Conducts a personalized, adaptive mock interview
- Evaluates answers using defined rubrics
- Generates actionable improvement plans

### 1.3 Project Objectives
1. Parse resumes (PDF/DOCX) and extract structured information automatically
2. Compare resume skills against job description requirements using TF-IDF cosine similarity
3. Generate contextually relevant interview questions using LLM integration with offline fallback
4. Conduct adaptive mock interviews where difficulty adjusts based on answer quality
5. Evaluate answers across five criteria: relevance, correctness, completeness, clarity, reasoning
6. Verify resume claims through targeted evidence-checking questions
7. Track performance over time with analytics dashboards and learning plans
8. Generate downloadable PDF interview reports

### 1.4 Scope and Limitations
**In Scope:**
- Text-based resume parsing (PDF and DOCX)
- Single-user interview sessions
- English-language interviews
- Local development deployment

**Out of Scope:**
- OCR for scanned/image-based PDFs (system detects and informs user)
- Real-time video interviews
- Multi-language support
- Production cloud deployment (documented for future scope)

---

## Chapter 2: Literature Review

### 2.1 Natural Language Processing in Resume Analysis
- TF-IDF (Term Frequency–Inverse Document Frequency) as a baseline text similarity method
- Cosine similarity for skill matching
- Named Entity Recognition for structured extraction

### 2.2 Adaptive Testing Systems
- Item Response Theory (IRT) as foundation for adaptive assessments
- Simplified rule-based difficulty adjustment (Score ≥75 → advanced; 50–74 → intermediate; <50 → beginner)
- Computer-Adaptive Testing (CAT) research

### 2.3 LLM-Based Question Generation
- Prompt engineering for structured output generation
- Schema validation of LLM responses
- Fallback strategies when LLM is unavailable

### 2.4 Existing Systems
| System | Features | Limitations |
|--------|----------|-------------|
| LinkedIn Resume Analysis | Basic keyword matching | No interview simulation |
| HackerRank Interviews | Technical coding focus | No resume integration |
| Pramp | Peer-to-peer | No AI feedback |
| InterviewBit | Practice questions | No personalization |
| **Resume2Interview AI** | End-to-end pipeline | English only, local deployment |

---

## Chapter 3: System Design

### 3.1 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENT (Browser)                      │
│  React 18 + Vite + TypeScript + Tailwind CSS             │
│  State-based routing | SVG charts | Web Speech API        │
└──────────────────────────┬───────────────────────────────┘
                           │ HTTPS / REST API (JSON)
                           │ Vite dev proxy → :8000
┌──────────────────────────▼───────────────────────────────┐
│               BACKEND (FastAPI / Python 3.15)             │
│                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  Auth Router│  │Resume Router │  │Matching Router  │  │
│  │  JWT/bcrypt │  │PyMuPDF/docx  │  │TF-IDF cosine    │  │
│  └─────────────┘  └──────────────┘  └─────────────────┘  │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Interviews  │  │  Evidence    │  │  Analytics &    │  │
│  │ Adaptive Q  │  │  Checker     │  │  Learning Plans │  │
│  └─────────────┘  └──────────────┘  └─────────────────┘  │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Reports   │  │  Admin Panel │  │  LLM Service    │  │
│  │  ReportLab  │  │  RBAC        │  │  Gemini/OpenAI  │  │
│  └─────────────┘  └──────────────┘  │  + Fallback     │  │
│                                     └─────────────────┘  │
│                                                           │
│  SQLAlchemy ORM + Pydantic v2 validation                  │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│              DATABASE (SQLite / PostgreSQL)                │
│  11 tables: users, resumes, resume_profiles, job_descs,   │
│  job_match_results, interview_sessions, interview_qs,     │
│  interview_answers, answer_evaluations, evidence_claims,  │
│  learning_plans, system_question_bank                     │
└──────────────────────────────────────────────────────────┘
```

### 3.2 Database Schema

#### Core Tables
| Table | Key Columns | Purpose |
|-------|-------------|---------|
| `users` | id, username, email, hashed_password, role | Authentication & authorization |
| `resumes` | id, user_id, filename, file_path, parsed_at | File tracking |
| `resume_profiles` | id, resume_id, name, skills_json, projects_json | Extracted structured data |
| `job_descriptions` | id, user_id, title, content, required_skills_json | JD storage |
| `job_match_results` | id, user_id, resume_id, jd_id, overall_score | Match outcomes |
| `interview_sessions` | id, user_id, resume_id, status, difficulty | Interview state |
| `interview_questions` | id, session_id, question_text, category, order_index | Per-session questions |
| `interview_answers` | id, question_id, user_id, answer_text, submitted_at | Candidate answers |
| `answer_evaluations` | id, answer_id, overall_score, criterion_scores_json | Rubric scores |
| `resume_evidence_claims` | id, resume_id, claim_text, verification_question | Claim tracking |
| `learning_plans` | id, user_id, plan_json, duration_days | Study plans |

### 3.3 API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | None | Create account |
| POST | `/api/auth/login` | None | Get JWT token |
| GET | `/api/auth/me` | User | Get current user |
| POST | `/api/resumes/upload` | User | Upload PDF/DOCX |
| GET | `/api/resumes/` | User | List user resumes |
| GET | `/api/resumes/{id}` | Owner | Get resume details |
| PUT | `/api/resumes/{id}/profile` | Owner | Edit parsed profile |
| DELETE | `/api/resumes/{id}` | Owner | Delete resume |
| POST | `/api/matching/match` | User | Match resume to JD |
| GET | `/api/matching/history` | User | Match history |
| POST | `/api/interviews/create` | User | Create interview session |
| GET | `/api/interviews/{id}` | Owner | Get session + questions |
| POST | `/api/interviews/{id}/submit-answer` | Owner | Submit answer |
| POST | `/api/interviews/{id}/finish` | Owner | Complete interview |
| GET | `/api/interviews/history` | User | All sessions |
| POST | `/api/evidence/{resume_id}/extract` | Owner | Extract claims |
| POST | `/api/evidence/claim/{id}/answer` | Owner | Answer a claim |
| GET | `/api/analytics/dashboard` | User | Stats + trends |
| POST | `/api/analytics/learning-plan` | User | Generate plan |
| GET | `/api/reports/{session_id}` | Owner | JSON report |
| GET | `/api/reports/{session_id}/pdf` | Owner | PDF download |
| GET | `/api/admin/questions` | Admin | List question bank |
| POST | `/api/admin/questions` | Admin | Add question |
| GET | `/api/admin/stats` | Admin | System stats |

### 3.4 Adaptive Difficulty Algorithm

```python
def next_difficulty(prev_score: float) -> str:
    """
    Rule-based adaptive difficulty selection.
    Score range: 0–100
    """
    if prev_score >= 75:
        return "advanced"      # Strong answer → harder challenge
    elif prev_score >= 50:
        return "intermediate"  # Adequate answer → maintain level
    else:
        return "beginner"      # Weak answer → consolidate basics
```

### 3.5 TF-IDF Skill Matching Formula

For a resume document **d** and JD query **q**, the cosine similarity score is:

$$\text{sim}(d, q) = \frac{\vec{d} \cdot \vec{q}}{|\vec{d}||\vec{q}|} = \frac{\sum_{t} tf\text{-}idf(t,d) \cdot tf\text{-}idf(t,q)}{\sqrt{\sum_t tf\text{-}idf(t,d)^2} \cdot \sqrt{\sum_t tf\text{-}idf(t,q)^2}}$$

Where:
- `tf(t, d)` = frequency of term `t` in document `d`
- `idf(t)` = log(N / df(t)) — N=total docs, df=docs containing term
- The implementation uses a custom pure-Python corpus built from both documents

**Matching score composition:**
- 60% TF-IDF cosine similarity (text-level)
- 40% Explicit skill set overlap (keyword taxonomy matching)

### 3.6 Resume Quality Scoring Rubric

| Criterion | Weight | How Measured |
|-----------|--------|--------------|
| Completeness | 25% | Presence of name, email, phone, education, skills, experience, projects |
| Skills Depth | 25% | Count of identifiable technical and soft skills |
| Experience Breadth | 20% | Count and quality of work experience entries |
| Project Evidence | 20% | Number of projects with descriptions |
| Certifications | 10% | Presence of certifications or achievements |

**Score interpretation:** 80–100 = Excellent, 60–79 = Good, 40–59 = Fair, 0–39 = Needs Improvement

---

## Chapter 4: Implementation

### 4.1 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | React | 18.3.x | UI component framework |
| Build | Vite | 5.4.x | Dev server + bundler |
| Language | TypeScript | 5.x | Type safety |
| Styling | Tailwind CSS | 3.x | Utility-first CSS |
| Icons | lucide-react | Latest | Icon library |
| Backend | FastAPI | 0.115.14 | REST API framework |
| Language | Python | 3.15.1 | Backend runtime |
| ORM | SQLAlchemy | 2.0.55 | Database abstraction |
| Validation | Pydantic | 2.14.1 | Schema validation |
| Auth | PyJWT + bcrypt | 2.15.1 + 4.3.0 | Token auth + hashing |
| PDF Parsing | PyMuPDF | 1.28.2 | PDF text extraction |
| DOCX Parsing | python-docx | Latest | Word file extraction |
| PDF Reports | ReportLab | 5.1.0 | PDF generation |
| Database | SQLite | Built-in | Local storage |
| Testing | Pytest | 9.1.1 | Backend test suite |

### 4.2 Key Implementation Details

#### Resume Parser (resume_parser.py)
- Uses PyMuPDF for PDF text extraction per-page
- Detects scanned PDFs by checking if text byte count < 100 per page
- Uses python-docx for DOCX paragraph iteration
- Regex patterns for email, phone, LinkedIn, GitHub
- Section detection via heading keywords (EXPERIENCE, EDUCATION, SKILLS, etc.)
- Returns `ParsedResume` dataclass with all structured fields
- Never invents data; returns empty lists/strings for missing sections

#### LLM Service (llm_service.py)
- Supports Gemini (`gemini-1.5-flash`) and OpenAI (`gpt-4o-mini`)
- Sanitizes resume/JD content before injection into prompts (removes prompt injection markers)
- Validates LLM response against JSON schema before use
- Falls back to `FallbackQuestionBank` on timeout, API error, or missing key
- Labels all AI evaluations as "AI-estimated" not "objective"
- Configurable via environment variables only — no API keys in frontend

#### Evaluator Service (evaluator_service.py)
Five-criterion rubric:
1. **Relevance** (0–100): Does the answer address the question?
2. **Correctness** (0–100): Is the content factually accurate?
3. **Completeness** (0–100): Are key points covered?
4. **Clarity** (0–100): Is the answer well-structured?
5. **Reasoning** (0–100): Is there logical justification?

Overall score = weighted average (equal weights in heuristic mode)

### 4.3 Security Measures
- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens with configurable expiry (default 24h)
- All user-specific endpoints verify `current_user.id == resource.user_id`
- File uploads: extension + MIME validation, size limit (5MB), safe UUID-prefixed filenames
- Path traversal prevention via secure filename handling
- CORS configured to specific frontend origins only
- No secrets in code; all from environment variables
- Admin role enforced server-side (not trusted from client)

---

## Chapter 5: Testing and Results

### 5.1 Test Coverage

| Test | Scenario Covered | Result |
|------|-----------------|--------|
| `test_health_check` | Server up, DB initialized | ✅ PASSED |
| `test_auth_registration_and_login` | Register, login, token, duplicate prevention | ✅ PASSED |
| `test_unauthorized_endpoints` | 401 on protected routes without token | ✅ PASSED |
| `test_cross_user_isolation` | User A cannot read User B's data | ✅ PASSED |
| `test_resume_upload_and_scanned_error` | Valid DOCX parsed; empty PDF rejected | ✅ PASSED |
| `test_job_matching_and_scoring` | Match score ≥ 50, skills identified | ✅ PASSED |
| `test_mock_interview_flow_and_duplicate_prevention` | Full interview; duplicate blocked | ✅ PASSED |
| `test_admin_authorization` | Non-admin blocked from admin endpoints | ✅ PASSED |
| `test_evidence_claims_and_defense` | Claims extracted, answers evaluated | ✅ PASSED |
| `test_analytics_and_learning_plan` | Dashboard stats; 7/15/30-day plans | ✅ PASSED |

**All 10 tests passed. Execution time: 4.88 seconds.**  
Run: `cd backend && python -m pytest -v tests/test_api.py`

### 5.2 Frontend Build Verification
- `npm run build` → ✅ Success
- Bundle: 283KB JS (74KB gzip), 28KB CSS
- Zero TypeScript errors, zero Vite warnings

---

## Chapter 6: Results and Discussion

### 6.1 Feature Completeness

| Module | Status | Notes |
|--------|--------|-------|
| Auth & User Profiles | ✅ Complete | JWT + bcrypt, role-based |
| Resume Upload & Parsing | ✅ Complete | PDF + DOCX; scanned detection |
| Resume Analysis Dashboard | ✅ Complete | 5-criterion heuristic score |
| Job Description Matching | ✅ Complete | TF-IDF + skill taxonomy |
| Question Generation | ✅ Complete | LLM + fallback bank |
| Adaptive Mock Interview | ✅ Complete | Text + voice (browser permitting) |
| Answer Evaluation | ✅ Complete | 5-criterion rubric, LLM-optional |
| Resume Evidence Checker | ✅ Complete | Claim extraction + defense |
| Performance Dashboard | ✅ Complete | SVG trend + radar charts |
| Interview Reports | ✅ Complete | JSON + PDF (ReportLab) |
| Admin Panel | ✅ Complete | Question bank management |
| Learning Plans | ✅ Complete | 7/15/30-day plans |

### 6.2 Known Limitations
1. **No OCR**: Scanned/image PDFs return a clear error message; OCR not implemented
2. **English only**: NLP and question generation designed for English
3. **Local deployment**: Not production-hardened (no rate limiting in dev mode)
4. **LLM dependency**: AI features need a valid API key; heuristic fallback always available
5. **Voice input**: Web Speech API available in Chrome/Edge; Safari/Firefox use text-only fallback

---

## Chapter 7: Conclusion and Future Work

### 7.1 Conclusion
Resume2Interview AI successfully implements an end-to-end pipeline for personalized interview preparation. The system demonstrates:
- Practical NLP application (TF-IDF matching, regex-based extraction)
- Adaptive assessment design (rule-based difficulty adjustment)
- Secure full-stack architecture (JWT auth, RBAC, input validation)
- Responsible AI usage (labeled estimates, offline fallback, prompt injection prevention)

### 7.2 Future Enhancements
1. **OCR Integration**: Tesseract/Google Vision for scanned resume support
2. **Video Interviews**: WebRTC-based mock video sessions
3. **Sentence Transformers**: Upgrade from TF-IDF to semantic embeddings (SBERT)
4. **PostgreSQL Migration**: Switch DATABASE_URL; no code changes required
5. **Multi-language Support**: i18n for regional language candidates
6. **Company-specific Prep**: Integration with job posting APIs
7. **Peer Review Mode**: Candidates review each other's answers
8. **Mobile App**: React Native version of the interview interface
9. **Rate Limiting**: Redis-based rate limiting for production
10. **CI/CD Pipeline**: GitHub Actions for automated test + deploy

---

## References

1. Mikolov, T. et al. (2013). *Efficient Estimation of Word Representations in Vector Space*. ICLR.
2. Devlin, J. et al. (2018). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*. NAACL.
3. Salton, G. & Buckley, C. (1988). *Term-Weighting Approaches in Automatic Text Retrieval*. Information Processing & Management.
4. Lord, F.M. (1980). *Applications of Item Response Theory to Practical Testing Problems*. Lawrence Erlbaum.
5. FastAPI Documentation. https://fastapi.tiangolo.com/
6. SQLAlchemy 2.0 Documentation. https://docs.sqlalchemy.org/en/20/
7. PyMuPDF Documentation. https://pymupdf.readthedocs.io/
8. React Documentation. https://react.dev/
9. Tailwind CSS Documentation. https://tailwindcss.com/docs/
10. OWASP Web Security Testing Guide. https://owasp.org/www-project-web-security-testing-guide/
