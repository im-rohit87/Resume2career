"""
Generate Synopsis.docx for Resume2Interview AI BTech Major Project
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "Synopsis_Resume2Interview_AI.docx")

def set_font(run, name="Times New Roman", size=12, bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)

def add_heading(doc, text, level=1, center=False, size=14, bold=True, color=None, space_before=12, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_font(run, size=size, bold=bold, color=color)
    return p

def add_para(doc, text, size=12, indent=False, justify=True, space_before=4, space_after=4, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent:
        p.paragraph_format.first_line_indent = Inches(0.4)
    run = p.add_run(text)
    set_font(run, size=size, italic=italic)
    return p

def add_bullet(doc, text, size=12):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    set_font(run, size=size)
    return p

def set_page_margins(doc, top=1, bottom=1, left=1.25, right=1):
    for section in doc.sections:
        section.top_margin    = Inches(top)
        section.bottom_margin = Inches(bottom)
        section.left_margin   = Inches(left)
        section.right_margin  = Inches(right)

def add_horizontal_rule(doc):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '4F46E5')
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p

# ─────────────────────────────────────────────
doc = Document()
set_page_margins(doc)

# ══════════════════ COVER PAGE ══════════════════
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(4)
r = p.add_run("PROJECT SYNOPSIS")
set_font(r, size=22, bold=True, color=(79, 70, 229))

add_horizontal_rule(doc)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(8)
r = p.add_run("Resume2Interview AI")
set_font(r, size=18, bold=True, color=(17, 24, 39))

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("An Intelligent Resume Analysis and Adaptive Mock Interview System")
set_font(r, size=13, italic=True, color=(107, 114, 128))

add_horizontal_rule(doc)
doc.add_paragraph()

# Info Table
table = doc.add_table(rows=7, cols=2)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.style = 'Table Grid'
rows_data = [
    ("Submitted By",       "Alex Chen / [Your Full Name]"),
    ("Roll Number",        "[Your Roll Number]"),
    ("Department",         "Computer Science and Engineering"),
    ("Institution",        "[Your College / University Name]"),
    ("Degree",             "Bachelor of Technology (B.Tech)"),
    ("Academic Year",      "2025 – 2026"),
    ("Guided By",          "Prof. [Supervisor Name]"),
]
for i, (label, value) in enumerate(rows_data):
    row = table.rows[i]
    c0, c1 = row.cells[0], row.cells[1]
    c0.width = Inches(2.0)
    c1.width = Inches(4.0)
    r0 = c0.paragraphs[0].add_run(label)
    set_font(r0, size=11, bold=True)
    r1 = c1.paragraphs[0].add_run(value)
    set_font(r1, size=11)

doc.add_paragraph()
add_horizontal_rule(doc)

# ══════════════════ SECTIONS ══════════════════

# 1. Abstract
add_heading(doc, "1.  ABSTRACT", size=13, color=(79, 70, 229))
add_para(doc,
    "The modern job market demands that candidates not only possess relevant technical skills but also "
    "demonstrate them effectively during interviews. However, most candidates lack structured, personalised "
    "preparation tools. Resume2Interview AI addresses this gap by providing an end-to-end, web-based platform "
    "that ingests a candidate's resume, analyses it against a target job description, and drives a fully adaptive "
    "mock interview — all without requiring human interviewers. The system leverages Natural Language Processing "
    "(TF-IDF cosine similarity), rule-based adaptive difficulty adjustment, and an optional Large Language Model "
    "(LLM) integration (Google Gemini / OpenAI GPT) to generate contextually grounded questions, evaluate "
    "answers across five rubric criteria, and produce comprehensive improvement plans. A unique Resume Evidence "
    "Checker module further verifies whether candidates can substantiate the skills and projects claimed on their "
    "resumes. The platform is built on a React + FastAPI stack with SQLite persistence, full JWT-based "
    "authentication, and a downloadable PDF report feature.",
    indent=True)

# 2. Problem Statement
add_heading(doc, "2.  PROBLEM STATEMENT", size=13, color=(79, 70, 229))
add_para(doc,
    "Interview preparation is largely generic. Candidates practise from static question banks that do not "
    "account for individual skills, project experience, or target job requirements. This leads to:",
    indent=True)
add_bullet(doc, "Wasted preparation time on irrelevant topics.")
add_bullet(doc, "Inability to identify personal skill gaps relative to a specific job description.")
add_bullet(doc, "Lack of objective, criterion-wise feedback on practice answers.")
add_bullet(doc, "No mechanism to verify whether resume claims are actually understood by the candidate.")
add_bullet(doc, "No adaptive system that increases or decreases question difficulty based on live performance.")

# 3. Objectives
add_heading(doc, "3.  OBJECTIVES", size=13, color=(79, 70, 229))
bullets = [
    "Parse PDF and DOCX resumes to extract structured information: skills, projects, experience, education, certifications.",
    "Compare extracted skills against a user-supplied job description using TF-IDF cosine similarity and skill-taxonomy matching.",
    "Identify skill gaps and generate a transparent, explainable matching score.",
    "Generate HR, technical, behavioural, and project-based interview questions grounded in the candidate's actual resume.",
    "Conduct adaptive mock interviews where question difficulty adjusts dynamically based on previous answer quality.",
    "Evaluate answers using a five-criterion rubric: Relevance, Correctness, Completeness, Clarity, and Reasoning.",
    "Implement a Resume Evidence Checker to verify candidate understanding of resume claims.",
    "Track interview history, criterion-wise performance trends, and generate 7/15/30-day learning plans.",
    "Generate downloadable PDF reports summarising questions, answers, scores, and improvement suggestions.",
    "Maintain a secure multi-user system with JWT authentication, role-based access, and full data isolation.",
]
for b in bullets:
    add_bullet(doc, b)

# 4. Scope
add_heading(doc, "4.  SCOPE OF THE PROJECT", size=13, color=(79, 70, 229))
add_para(doc,
    "The project covers the complete candidate-preparation lifecycle: upload → parse → analyse → match → "
    "interview → evaluate → report. It is scoped for English-language resumes and text-based interviews. "
    "Voice input is supported where the browser permits (Web Speech API). The system operates as a local "
    "web application suitable for a college/university lab environment. All AI features degrade gracefully "
    "to an offline curated question-bank when no LLM API key is configured.",
    indent=True)

# 5. Methodology
add_heading(doc, "5.  METHODOLOGY", size=13, color=(79, 70, 229))
add_para(doc, "The system follows an Agile development methodology with the following phases:", indent=True)
phases = [
    ("Phase 1 – Requirements Analysis:",
     "Identified functional requirements across 12 modules through iterative refinement."),
    ("Phase 2 – System Design:",
     "Designed the 11-table relational schema, REST API endpoints, and component hierarchy."),
    ("Phase 3 – Backend Development:",
     "Implemented FastAPI routers, SQLAlchemy models, Pydantic validation, and all service layers."),
    ("Phase 4 – Frontend Development:",
     "Built 11 React pages with TypeScript, Tailwind CSS, and custom SVG charts."),
    ("Phase 5 – Integration & Testing:",
     "Executed 10 automated pytest tests covering auth, isolation, upload, matching, interview flow, admin, evidence, and analytics."),
    ("Phase 6 – Documentation:",
     "Prepared synopsis, project report, and presentation slides."),
]
for title, desc in phases:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.4)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(2)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r1 = p.add_run(title + " ")
    set_font(r1, size=12, bold=True)
    r2 = p.add_run(desc)
    set_font(r2, size=12)

# 6. Technology Stack
add_heading(doc, "6.  TECHNOLOGY STACK", size=13, color=(79, 70, 229))
table2 = doc.add_table(rows=10, cols=3)
table2.style = 'Table Grid'
table2.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ["Layer", "Technology", "Purpose"]
for j, h in enumerate(headers):
    c = table2.rows[0].cells[j]
    r = c.paragraphs[0].add_run(h)
    set_font(r, size=11, bold=True)
    c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

stack = [
    ("Frontend",         "React 18 + Vite + TypeScript",       "SPA, state-based routing"),
    ("Styling",          "Tailwind CSS 3",                      "Utility-first responsive UI"),
    ("Backend",          "Python FastAPI 0.115",                "REST API framework"),
    ("ORM",              "SQLAlchemy 2.0 + Pydantic v2",        "Database abstraction & validation"),
    ("Database",         "SQLite (dev) / PostgreSQL-ready",     "Relational data persistence"),
    ("Auth",             "PyJWT + bcrypt",                      "JWT tokens + password hashing"),
    ("Resume Parsing",   "PyMuPDF + python-docx",               "PDF and DOCX extraction"),
    ("NLP Matching",     "Pure-Python TF-IDF cosine",           "Skill gap and JD matching"),
    ("PDF Reports",      "ReportLab",                           "Downloadable interview reports"),
]
for i, row_data in enumerate(stack):
    row = table2.rows[i + 1]
    for j, val in enumerate(row_data):
        r = row.cells[j].paragraphs[0].add_run(val)
        set_font(r, size=11)

doc.add_paragraph()

# 7. System Modules
add_heading(doc, "7.  KEY SYSTEM MODULES", size=13, color=(79, 70, 229))
modules = [
    ("M1 – Authentication & Profiles",   "Secure registration/login, JWT sessions, bcrypt hashing, role-based access."),
    ("M2 – Resume Upload & Parsing",      "PDF/DOCX ingestion, structured extraction, scanned-PDF detection, editable preview."),
    ("M3 – Resume Analysis Dashboard",    "5-criterion heuristic quality score, strengths & improvement suggestions."),
    ("M4 – Job Description Matching",     "TF-IDF + skill taxonomy; matched/missing/related skills with evidence snippets."),
    ("M5 – Question Generation",          "LLM-driven (Gemini/OpenAI) + offline fallback bank; HR/technical/behavioural/project."),
    ("M6 – Adaptive Mock Interview",      "One-question-at-a-time UI, voice input, dynamic difficulty adjustment."),
    ("M7 – Answer Evaluation",            "Rubric: Relevance / Correctness / Completeness / Clarity / Reasoning (0–100 each)."),
    ("M8 – Resume Evidence Checker",      "Extracts resume claims, generates verification Qs, tracks preparation coverage."),
    ("M9 – Analytics & Learning Plans",   "SVG trend + radar charts, 7/15/30-day day-by-day study plans."),
    ("M10 – Interview Reports",           "JSON + downloadable PDF report per session, owner-only access."),
    ("M11 – Admin Panel",                 "Question bank CRUD, system stats, role-enforced on backend."),
]
for mod, desc in modules:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.4)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r1 = p.add_run(mod + ": ")
    set_font(r1, size=12, bold=True)
    r2 = p.add_run(desc)
    set_font(r2, size=12)

# 8. Expected Outcomes
add_heading(doc, "8.  EXPECTED OUTCOMES", size=13, color=(79, 70, 229))
outcomes = [
    "A fully functional, deployable web application covering the complete interview-preparation lifecycle.",
    "Accurate resume skill extraction with graceful handling of unsupported formats.",
    "Transparent job-matching score with explainable formula and documented limitations.",
    "Adaptive interview sessions that respond to candidate performance in real time.",
    "Criterion-wise feedback with evidence, sample stronger answers, and next steps.",
    "Personalised 7/15/30-day learning plans derived from identified skill gaps.",
    "Downloadable PDF interview reports for portfolio and self-assessment use.",
    "10 automated backend tests passing with verified results.",
]
for o in outcomes:
    add_bullet(doc, o)

# 9. References
add_heading(doc, "9.  REFERENCES", size=13, color=(79, 70, 229))
refs = [
    "Mikolov, T. et al. (2013). Efficient Estimation of Word Representations in Vector Space. ICLR.",
    "Devlin, J. et al. (2018). BERT: Pre-training of Deep Bidirectional Transformers. NAACL.",
    "Salton, G. & Buckley, C. (1988). Term-Weighting Approaches in Automatic Text Retrieval. IPM.",
    "FastAPI Documentation. https://fastapi.tiangolo.com/",
    "SQLAlchemy 2.0 Documentation. https://docs.sqlalchemy.org/en/20/",
    "React Documentation. https://react.dev/",
    "Tailwind CSS Documentation. https://tailwindcss.com/",
    "PyMuPDF Documentation. https://pymupdf.readthedocs.io/",
    "OWASP Web Application Security Testing Guide v4.2.",
    "Google Gemini API Documentation. https://ai.google.dev/",
]
for i, ref in enumerate(refs):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.4)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(f"[{i+1}] {ref}")
    set_font(r, size=11)

add_horizontal_rule(doc)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("— End of Synopsis —")
set_font(r, size=11, italic=True, color=(107, 114, 128))

doc.save(OUTPUT)
print(f"Synopsis saved → {OUTPUT}")
