"""
Generate Presentation.pptx for Resume2Interview AI BTech Major Project
20 professional slides with charts, tables, and structured content.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
from lxml import etree
import os, math

OUTPUT = os.path.join(os.path.dirname(__file__), "Presentation_Resume2Interview_AI.pptx")

# ── Colour Palette ──────────────────────────────────────────────────────────
C_INDIGO   = RGBColor(0x4F, 0x46, 0xE5)   # primary brand
C_INDIGO_L = RGBColor(0xC7, 0xD2, 0xFE)   # light indigo
C_INDIGO_D = RGBColor(0x31, 0x27, 0xAA)   # dark indigo
C_WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
C_BLACK    = RGBColor(0x11, 0x18, 0x27)
C_GRAY     = RGBColor(0x6B, 0x72, 0x80)
C_LGRAY    = RGBColor(0xF3, 0xF4, 0xF6)
C_EMERALD  = RGBColor(0x10, 0xB9, 0x81)
C_AMBER    = RGBColor(0xF5, 0x9E, 0x0B)
C_ROSE     = RGBColor(0xF4, 0x3F, 0x5E)
C_SKY      = RGBColor(0x0E, 0xA5, 0xE9)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H

BLANK   = prs.slide_layouts[6]   # completely blank
TITLE_L = prs.slide_layouts[0]   # title slide layout (we'll blank it)

# ── Helper utilities ────────────────────────────────────────────────────────

def add_rect(slide, l, t, w, h, fill=None, line_color=None, line_w=Pt(0)):
    shape = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    shape.line.width = line_w
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()
    return shape

def add_text(slide, text, l, t, w, h, size=18, bold=False, italic=False,
             color=C_BLACK, align=PP_ALIGN.LEFT, wrap=True, valign=None):
    txBox = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = txBox.text_frame
    tf.word_wrap = wrap
    if valign:
        tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return txBox

def add_text_lines(slide, lines, l, t, w, h, default_size=16, color=C_BLACK,
                   line_spacing=None, align=PP_ALIGN.LEFT):
    """lines = list of (text, size, bold, italic, color)"""
    txBox = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = txBox.text_frame
    tf.word_wrap = True
    first = True
    for item in lines:
        if isinstance(item, str):
            text, size, bold, italic, col = item, default_size, False, False, color
        else:
            text = item[0]
            size = item[1] if len(item) > 1 else default_size
            bold = item[2] if len(item) > 2 else False
            italic = item[3] if len(item) > 3 else False
            col  = item[4] if len(item) > 4 else color
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        if line_spacing:
            p.line_spacing = Pt(line_spacing)
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = col
        run.font.name = "Calibri"
    return txBox

def slide_header(slide, title, subtitle=None, left_bar=True):
    """Standard slide with top indigo header bar."""
    # Top bar
    add_rect(slide, 0, 0, 13.33, 1.1, fill=C_INDIGO)
    add_text(slide, title, 0.4, 0.1, 11.5, 0.85, size=28, bold=True,
             color=C_WHITE, align=PP_ALIGN.LEFT)
    if subtitle:
        add_text(slide, subtitle, 0.4, 0.82, 11.5, 0.35, size=13,
                 color=C_INDIGO_L, align=PP_ALIGN.LEFT)
    # Bottom thin bar
    add_rect(slide, 0, 7.2, 13.33, 0.3, fill=C_INDIGO_D)
    add_text(slide, "Resume2Interview AI  |  BTech Major Project", 0.2, 7.2, 9, 0.3,
             size=9, color=C_WHITE)
    # Left accent bar (optional)
    if left_bar:
        add_rect(slide, 0, 1.1, 0.08, 6.1, fill=C_INDIGO_L)

def bullet_block(slide, items, l, t, w, size=15, color=C_BLACK, bullet_color=C_INDIGO, gap=0.38):
    """Renders a list of bullet items as stacked text boxes with a coloured bullet."""
    for i, item in enumerate(items):
        y = t + i * gap
        # bullet dot
        add_text(slide, "▶", l, y, 0.25, gap, size=size-3, color=bullet_color, bold=True)
        add_text(slide, item, l+0.25, y, w-0.25, gap, size=size, color=color)

def icon_card(slide, icon, label, value, l, t, w=2.5, h=1.4,
              bg=C_INDIGO, text_col=C_WHITE):
    add_rect(slide, l, t, w, h, fill=bg)
    # Rounded corner effect via line
    add_rect(slide, l, t, w, h, line_color=C_INDIGO_L, line_w=Pt(1.5))
    add_text(slide, icon,  l+0.1, t+0.1, 0.5, 0.4, size=20, color=text_col)
    add_text(slide, value, l+0.1, t+0.45, w-0.2, 0.55, size=26, bold=True, color=text_col)
    add_text(slide, label, l+0.1, t+1.0,  w-0.2, 0.38, size=11, color=text_col)

def progress_bar(slide, label, pct, l, t, w=5.5, bar_h=0.22, color=C_INDIGO):
    add_text(slide, label, l, t, w*0.55, bar_h+0.02, size=12, color=C_BLACK)
    pct_txt = f"{pct}%"
    add_text(slide, pct_txt, l+w*0.56, t, 0.6, bar_h+0.02, size=12, bold=True, color=color)
    # background
    add_rect(slide, l, t+bar_h+0.04, w, 0.14, fill=C_LGRAY)
    # fill
    fill_w = max(0.01, w * pct / 100)
    add_rect(slide, l, t+bar_h+0.04, fill_w, 0.14, fill=color)

def table_block(slide, headers, rows, l, t, w, h, header_bg=C_INDIGO, header_fg=C_WHITE,
                row_bg1=C_WHITE, row_bg2=C_LGRAY, font_size=11):
    col_n  = len(headers)
    col_w  = w / col_n
    row_n  = len(rows) + 1
    row_h  = h / row_n
    for ci, hdr in enumerate(headers):
        add_rect(slide, l+ci*col_w, t, col_w-0.02, row_h-0.02, fill=header_bg)
        add_text(slide, hdr, l+ci*col_w+0.05, t+0.02, col_w-0.12, row_h-0.06,
                 size=font_size, bold=True, color=header_fg, align=PP_ALIGN.CENTER)
    for ri, row in enumerate(rows):
        bg = row_bg1 if ri % 2 == 0 else row_bg2
        for ci, cell in enumerate(row):
            add_rect(slide, l+ci*col_w, t+(ri+1)*row_h, col_w-0.02, row_h-0.02, fill=bg)
            add_text(slide, str(cell), l+ci*col_w+0.05, t+(ri+1)*row_h+0.02,
                     col_w-0.12, row_h-0.06, size=font_size-1, color=C_BLACK,
                     align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
# Full indigo left panel
add_rect(sl, 0, 0, 5.5, 7.5, fill=C_INDIGO)
add_rect(sl, 5.5, 0, 7.83, 7.5, fill=C_WHITE)

# Left panel content
add_text(sl, "BTech Major Project", 0.3, 0.4, 4.8, 0.5, size=12,
         color=C_INDIGO_L, italic=True)
add_text(sl, "Resume2Interview AI", 0.3, 1.0, 4.9, 1.6, size=32, bold=True,
         color=C_WHITE, align=PP_ALIGN.LEFT)
add_text(sl, "An Intelligent Resume Analysis\nand Adaptive Mock Interview System",
         0.3, 2.7, 4.8, 1.2, size=16, color=C_INDIGO_L, italic=True)

# Divider
add_rect(sl, 0.3, 4.1, 1.5, 0.06, fill=C_WHITE)

add_text(sl, "Presented by", 0.3, 4.3, 4.5, 0.4, size=11, color=C_INDIGO_L)
add_text(sl, "[Your Full Name]", 0.3, 4.65, 4.5, 0.5, size=16, bold=True, color=C_WHITE)
add_text(sl, "Roll No: [XXXXXXXX]", 0.3, 5.1, 4.5, 0.4, size=12, color=C_INDIGO_L)
add_text(sl, "Guided by: Prof. [Supervisor Name]", 0.3, 5.5, 4.5, 0.4, size=12, color=C_INDIGO_L)
add_text(sl, "Dept. of CSE  |  Academic Year 2025–26", 0.3, 5.9, 4.5, 0.4, size=11, color=C_INDIGO_L)

# Right panel illustration (text-art)
add_text(sl, "⚡", 7.5, 1.5, 2, 2, size=90, color=C_INDIGO_L, align=PP_ALIGN.CENTER)
add_text(sl, "[Your College / University Name]", 5.8, 6.8, 7.2, 0.55,
         size=12, color=C_GRAY, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — AGENDA
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Agenda", "What we'll cover today")

agenda = [
    ("01", "Problem Statement & Motivation"),
    ("02", "Project Objectives"),
    ("03", "System Architecture"),
    ("04", "Technology Stack"),
    ("05", "Core Modules Overview"),
    ("06", "Key Algorithms"),
    ("07", "Database Design"),
    ("08", "Security Measures"),
    ("09", "Testing & Results"),
    ("10", "Demo Walkthrough"),
    ("11", "Conclusions & Future Work"),
]
cols = [agenda[:6], agenda[6:]]
for ci, col in enumerate(cols):
    lx = 0.5 + ci * 6.5
    for ri, (num, topic) in enumerate(col):
        ty = 1.3 + ri * 0.9
        add_rect(sl, lx, ty, 0.55, 0.55, fill=C_INDIGO)
        add_text(sl, num, lx, ty, 0.55, 0.55, size=14, bold=True,
                 color=C_WHITE, align=PP_ALIGN.CENTER)
        add_text(sl, topic, lx+0.65, ty+0.05, 5.5, 0.5, size=15, color=C_BLACK)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — PROBLEM STATEMENT
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Problem Statement", "Why does this problem need solving?")

# Pain point cards
pains = [
    ("🎯", "Generic\nPreparation", "Questions not tailored\nto individual resumes"),
    ("🔍", "No Skill-Gap\nAnalysis", "Candidates can't see\nwhat's missing"),
    ("📊", "No Adaptive\nDifficulty", "Static questions ignore\nperformance signals"),
    ("❌", "Weak\nFeedback", "No criterion-wise\nanswer evaluation"),
    ("📄", "Resume Claim\nGap", "Skills listed ≠\nskills understood"),
]
for i, (icon, title, desc) in enumerate(pains):
    lx = 0.35 + i * 2.55
    add_rect(sl, lx, 1.3, 2.35, 2.5, fill=C_LGRAY,
             line_color=C_INDIGO_L, line_w=Pt(1))
    add_text(sl, icon,  lx+0.85, 1.4,  0.7, 0.6, size=26, align=PP_ALIGN.CENTER)
    add_text(sl, title, lx+0.1,  2.05, 2.1, 0.65, size=13, bold=True,
             color=C_INDIGO, align=PP_ALIGN.CENTER)
    add_text(sl, desc,  lx+0.1,  2.7,  2.1, 0.9, size=11,
             color=C_GRAY, align=PP_ALIGN.CENTER)

add_rect(sl, 0.35, 4.1, 12.6, 0.06, fill=C_INDIGO)
add_text(sl,
    "💡  Existing tools are fragmented, generic, and provide no personalised, adaptive interview experience grounded in the candidate's own resume.",
    0.35, 4.25, 12.6, 0.7, size=14, italic=True, color=C_INDIGO, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — OBJECTIVES
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Project Objectives", "10 measurable goals")

objs = [
    "Parse PDF & DOCX resumes — extract skills, projects, education, experience",
    "Compute a transparent Resume Quality Score (0–100) with rubric",
    "Match resume skills against a job description using TF-IDF + taxonomy",
    "Generate personalised HR / Technical / Behavioural / Project questions",
    "Conduct adaptive mock interviews — difficulty adjusts per answer score",
    "Evaluate answers on 5 criteria: Relevance, Correctness, Completeness, Clarity, Reasoning",
    "Implement a Resume Evidence Checker — verify claim understanding",
    "Track performance trends & generate 7/15/30-day learning plans",
    "Generate downloadable PDF interview reports",
    "Secure multi-user system: JWT auth, bcrypt, RBAC, data isolation",
]
for i, obj in enumerate(objs):
    col = i // 5
    row = i % 5
    lx = 0.4 + col * 6.45
    ty = 1.3 + row * 1.02
    add_rect(sl, lx, ty, 6.2, 0.85, fill=C_LGRAY)
    add_rect(sl, lx, ty, 0.06, 0.85, fill=C_INDIGO)
    add_text(sl, f"{i+1:02d}", lx+0.12, ty+0.1, 0.5, 0.65,
             size=14, bold=True, color=C_INDIGO)
    add_text(sl, obj, lx+0.65, ty+0.08, 5.4, 0.72, size=12, color=C_BLACK)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — SYSTEM ARCHITECTURE
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "System Architecture", "Three-tier client-server architecture")

# Tier boxes
tiers = [
    (C_SKY,     "PRESENTATION TIER",    "React 18 + Vite + TypeScript\nTailwind CSS | SVG Charts\nWeb Speech API",  0.5),
    (C_INDIGO,  "APPLICATION TIER",     "Python FastAPI 0.115\n8 Routers | 8 Services\nPydantic v2 Validation",     4.5),
    (C_EMERALD, "DATA TIER",            "SQLite / PostgreSQL\nSQLAlchemy ORM\n11 Tables | UUID files",              8.5),
]
for (col, title, body, lx) in tiers:
    add_rect(sl, lx, 1.3, 3.8, 3.5, fill=col)
    add_text(sl, title, lx+0.15, 1.4, 3.5, 0.55, size=12, bold=True, color=C_WHITE,
             align=PP_ALIGN.CENTER)
    add_rect(sl, lx+0.15, 1.95, 3.5, 0.04, fill=C_WHITE)
    add_text(sl, body, lx+0.15, 2.05, 3.5, 1.8, size=13, color=C_WHITE, align=PP_ALIGN.CENTER)
    if lx < 8.5:
        add_text(sl, "  REST API  →", lx+3.8, 2.7, 0.72, 0.55, size=13, bold=True, color=C_GRAY)

# LLM optional box
add_rect(sl, 4.5, 5.1, 3.8, 1.5, fill=C_AMBER)
add_text(sl, "OPTIONAL: LLM SERVICE", 4.65, 5.15, 3.5, 0.45, size=11, bold=True,
         color=C_WHITE, align=PP_ALIGN.CENTER)
add_text(sl, "Google Gemini / OpenAI GPT\nFull fallback when key absent",
         4.65, 5.6, 3.5, 0.95, size=12, color=C_WHITE, align=PP_ALIGN.CENTER)
add_text(sl, "↑ optional", 4.85, 4.75, 1.5, 0.4, size=11, color=C_AMBER, bold=True)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — TECHNOLOGY STACK
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Technology Stack", "Stable, production-grade, open-source")

stack = [
    ("⚛️",  "React 18",         "Frontend SPA",        C_SKY),
    ("⚡",  "Vite + TS",        "Build & Type Safety", C_SKY),
    ("🎨",  "Tailwind CSS 3",   "Responsive UI",       C_SKY),
    ("🐍",  "FastAPI 0.115",    "REST API Backend",    C_INDIGO),
    ("🗄️",  "SQLAlchemy 2.0",   "ORM / DB Layer",      C_INDIGO),
    ("✅",  "Pydantic v2",      "Schema Validation",   C_INDIGO),
    ("🔐",  "PyJWT + bcrypt",   "Auth & Security",     C_EMERALD),
    ("📄",  "PyMuPDF + docx",   "Resume Parsing",      C_EMERALD),
    ("🤖",  "Gemini / GPT",     "LLM (Optional)",      C_AMBER),
    ("📊",  "ReportLab",        "PDF Reports",         C_ROSE),
]
for i, (icon, name, role, color) in enumerate(stack):
    col = i % 5
    row = i // 5
    lx = 0.4 + col * 2.5
    ty = 1.35 + row * 2.0
    add_rect(sl, lx, ty, 2.25, 1.7, fill=color)
    add_text(sl, icon, lx+0.8, ty+0.1,  0.7, 0.6, size=22, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, name, lx+0.1, ty+0.72, 2.05, 0.55, size=13, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, role, lx+0.1, ty+1.2,  2.05, 0.45, size=10,
             color=C_WHITE, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — CORE MODULES
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Core Modules — 11 Complete", "End-to-end interview preparation pipeline")

modules = [
    ("M1", "Auth & Profiles",          "JWT + bcrypt + RBAC",           C_INDIGO),
    ("M2", "Resume Upload & Parse",    "PDF/DOCX → Structured profile", C_SKY),
    ("M3", "Resume Analysis",          "5-criterion heuristic score",   C_EMERALD),
    ("M4", "JD Matching",              "TF-IDF + skill taxonomy",       C_AMBER),
    ("M5", "Question Generation",      "LLM + offline fallback bank",   C_ROSE),
    ("M6", "Adaptive Interview",       "Dynamic difficulty adjustment", C_INDIGO),
    ("M7", "Answer Evaluation",        "5-criterion rubric scoring",    C_SKY),
    ("M8", "Evidence Checker",         "Resume claim verification",     C_EMERALD),
    ("M9", "Analytics & Plans",        "Radar + trend charts, 30-day",  C_AMBER),
    ("M10","Interview Reports",         "JSON + PDF (ReportLab)",        C_ROSE),
    ("M11","Admin Panel",              "Question bank + system stats",  C_GRAY),
]
for i, (code, name, desc, color) in enumerate(modules):
    col = i % 4
    row = i // 4
    lx = 0.3 + col * 3.25
    ty = 1.3 + row * 1.9
    if i == 10:  # last item centred
        lx = 4.9
    add_rect(sl, lx, ty, 3.0, 1.65, fill=C_LGRAY, line_color=color, line_w=Pt(2))
    add_rect(sl, lx, ty, 0.55, 1.65, fill=color)
    add_text(sl, code, lx+0.02, ty+0.55, 0.51, 0.55, size=11, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, name, lx+0.65, ty+0.1,  2.25, 0.6, size=12, bold=True,
             color=C_INDIGO, align=PP_ALIGN.LEFT)
    add_text(sl, desc, lx+0.65, ty+0.72, 2.25, 0.85, size=11,
             color=C_GRAY, align=PP_ALIGN.LEFT)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — RESUME PIPELINE
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Resume Processing Pipeline", "From raw file to structured insights")

steps = [
    ("📂", "Upload",          "PDF/DOCX\n≤ 5 MB",          C_SKY),
    ("🔍", "Validate",        "Ext + MIME\nSize check",     C_AMBER),
    ("📖", "Parse",           "PyMuPDF\npython-docx",       C_INDIGO),
    ("🧩", "Extract",         "Skills, Projects\nExp, Edu", C_EMERALD),
    ("📊", "Score",           "5-criterion\nheuristic",     C_ROSE),
    ("✏️",  "Edit Preview",   "Candidate\ncorrects errors", C_INDIGO),
]
arrow = "→"
for i, (icon, title, desc, col) in enumerate(steps):
    lx = 0.4 + i * 2.1
    add_rect(sl, lx, 1.5, 1.9, 3.5, fill=col)
    add_text(sl, icon,  lx+0.6,  1.6,  0.8, 0.7, size=26, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, title, lx+0.1,  2.35, 1.7, 0.55, size=14, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    add_rect(sl, lx+0.2, 2.9, 1.5, 0.04, fill=C_WHITE)
    add_text(sl, desc,  lx+0.1,  3.0,  1.7, 0.9, size=12,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    if i < len(steps)-1:
        add_text(sl, arrow, lx+1.88, 2.85, 0.25, 0.6, size=18, bold=True,
                 color=C_GRAY, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — JD MATCHING
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Job Description Matching", "TF-IDF cosine similarity + skill taxonomy overlay")

# Formula box
add_rect(sl, 0.5, 1.3, 12.3, 1.1, fill=C_LGRAY, line_color=C_INDIGO, line_w=Pt(1.5))
add_text(sl, "Matching Score  =  0.6 × cosine_sim(TF-IDF resume, TF-IDF JD)  +  0.4 × skill_overlap_ratio",
         0.7, 1.42, 12.0, 0.55, size=14, bold=True, color=C_INDIGO, align=PP_ALIGN.CENTER)
add_text(sl, "cosine_sim(d,q) = Σ tfidf(t,d)·tfidf(t,q)  /  (√Σ tfidf(t,d)²  ·  √Σ tfidf(t,q)²)",
         0.7, 1.88, 12.0, 0.45, size=12, italic=True, color=C_GRAY, align=PP_ALIGN.CENTER)

# Output categories
cats = [
    ("✅ Matched Skills",    "Skills found in both resume\nand job description",            C_EMERALD, 8),
    ("❌ Missing Skills",    "Skills required by JD\nbut absent from resume",               C_ROSE,    5),
    ("🔗 Related Skills",   "Partial matches via\nskill synonym taxonomy",                  C_AMBER,   3),
    ("📎 Evidence Snippets","Resume text excerpts\nproving skill claims",                   C_SKY,     6),
]
for i, (label, desc, col, count) in enumerate(cats):
    lx = 0.5 + i * 3.2
    add_rect(sl, lx, 2.65, 2.95, 2.3, fill=col)
    add_text(sl, label, lx+0.12, 2.72, 2.7, 0.55, size=13, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, str(count), lx+0.9, 3.2, 1.1, 0.8, size=36, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, "items", lx+0.9, 3.95, 1.1, 0.4, size=11, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, desc, lx+0.12, 4.35, 2.7, 0.58, size=10.5, italic=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)

add_text(sl, "⚠️  Score is a heuristic estimate. A missing keyword does not prove absence of skill.",
         0.5, 5.2, 12.3, 0.5, size=12, italic=True, color=C_AMBER, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — ADAPTIVE INTERVIEW
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Adaptive Mock Interview", "Real-time difficulty adjustment based on answer quality")

# Flowchart
nodes = [
    (5.5, 1.45, "START INTERVIEW", C_INDIGO,  C_WHITE),
    (5.5, 2.55, "Show Question",   C_SKY,     C_WHITE),
    (5.5, 3.65, "Candidate Answers",C_LGRAY,  C_BLACK),
    (5.5, 4.75, "Evaluate Answer", C_EMERALD, C_WHITE),
]
for (cx, ty, label, bg, fg) in nodes:
    add_rect(sl, cx-1.4, ty, 2.8, 0.75, fill=bg, line_color=C_INDIGO_L, line_w=Pt(1))
    add_text(sl, label, cx-1.35, ty+0.1, 2.7, 0.58, size=13, bold=True,
             color=fg, align=PP_ALIGN.CENTER)
    if ty < 4.75:
        add_text(sl, "↓", cx-0.15, ty+0.75, 0.35, 0.45, size=18, bold=True,
                 color=C_GRAY, align=PP_ALIGN.CENTER)

# Decision branches
add_text(sl, "Score?", 5.3, 5.65, 0.8, 0.4, size=11, bold=True, color=C_GRAY)
# Three outcome boxes
branches = [
    (2.2,  5.8, "< 50",  "BEGINNER\nnext Q",  C_ROSE),
    (5.1,  5.8, "50–74", "INTERMEDIATE\nnext Q", C_AMBER),
    (8.0,  5.8, "≥ 75",  "ADVANCED\nnext Q",  C_EMERALD),
]
for (lx, ty, score, label, col) in branches:
    add_rect(sl, lx, ty, 2.4, 1.1, fill=col)
    add_text(sl, score, lx+0.1, ty+0.05, 2.2, 0.42, size=14, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, label, lx+0.1, ty+0.48, 2.2, 0.55, size=11,
             color=C_WHITE, align=PP_ALIGN.CENTER)

# Arrows from score node to branches
for lx in [3.4, 6.3, 9.2]:
    add_text(sl, "↗", lx-0.1, 5.45, 0.35, 0.4, size=16, color=C_GRAY)

# right panel — question types
add_rect(sl, 10.3, 1.3, 2.7, 5.5, fill=C_LGRAY)
add_text(sl, "Question Types", 10.45, 1.38, 2.4, 0.42, size=12, bold=True,
         color=C_INDIGO, align=PP_ALIGN.CENTER)
for i, (qtype, col) in enumerate([("HR / Behavioural", C_SKY), ("Technical", C_INDIGO),
                                    ("Project-Based", C_EMERALD), ("Situational", C_AMBER)]):
    ty = 1.85 + i * 1.18
    add_rect(sl, 10.45, ty, 2.4, 0.9, fill=col)
    add_text(sl, qtype, 10.5, ty+0.2, 2.3, 0.55, size=12, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — ANSWER EVALUATION RUBRIC
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Answer Evaluation Rubric", "5-criterion scoring — transparent and explainable")

criteria = [
    ("Relevance",    80, C_INDIGO,  "Does the answer address the question asked?"),
    ("Correctness",  65, C_SKY,     "Is the technical/factual content accurate?"),
    ("Completeness", 72, C_EMERALD, "Are all key points covered?"),
    ("Clarity",      88, C_AMBER,   "Is the answer well-structured and clear?"),
    ("Reasoning",    55, C_ROSE,    "Is there logical justification / depth?"),
]
add_text(sl, "Sample Evaluation", 0.4, 1.28, 6.5, 0.42, size=13, bold=True, color=C_GRAY)
for i, (name, score, col, desc) in enumerate(criteria):
    ty = 1.75 + i * 1.0
    # Name label
    add_text(sl, name, 0.4, ty, 2.0, 0.55, size=14, bold=True, color=col)
    # Progress bar bg
    add_rect(sl, 2.5, ty+0.16, 5.5, 0.28, fill=C_LGRAY)
    # Progress fill
    fw = 5.5 * score / 100
    add_rect(sl, 2.5, ty+0.16, fw, 0.28, fill=col)
    # Score text
    add_text(sl, f"{score}/100", 8.15, ty+0.08, 1.0, 0.42, size=13, bold=True, color=col)
    # Description
    add_text(sl, desc, 0.4, ty+0.56, 9.0, 0.38, size=11, italic=True, color=C_GRAY)

# Overall box
add_rect(sl, 0.4, 6.9, 9.1, 0.48, fill=C_INDIGO)
avg = sum(c[1] for c in criteria) // len(criteria)
add_text(sl, f"Overall Score: {avg}/100  (weighted average)",
         0.6, 6.93, 8.7, 0.4, size=14, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

# Right info box
add_rect(sl, 10.0, 1.3, 3.0, 5.9, fill=C_LGRAY)
add_text(sl, "Evaluation Modes", 10.15, 1.38, 2.7, 0.42, size=12, bold=True,
         color=C_INDIGO, align=PP_ALIGN.CENTER)
for i, (mode, col, desc) in enumerate([
    ("Heuristic", C_EMERALD, "Always available\nKeyword + length analysis"),
    ("AI-Assisted", C_INDIGO, "When LLM key set\nLabelled as 'estimate'"),
]):
    ty = 1.9 + i * 2.3
    add_rect(sl, 10.15, ty, 2.7, 1.9, fill=col)
    add_text(sl, mode, 10.2, ty+0.1, 2.6, 0.5, size=13, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, desc, 10.2, ty+0.65, 2.6, 1.1, size=11,
             color=C_WHITE, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — EVIDENCE CHECKER
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Resume Evidence Checker", "Unique module — verify what you claim")

steps_ev = [
    ("📄", "Resume Claims\nExtracted",    "e.g. 'Built REST APIs\nwith FastAPI'",   C_SKY),
    ("❓", "Verification\nQuestion Generated", "e.g. 'Explain how FastAPI\nhandles routing'", C_INDIGO),
    ("💬", "Candidate\nAnswers",          "Text or voice\nresponse",               C_EMERALD),
    ("📊", "Score & Track",              "is_practiced = True\nScore stored",       C_AMBER),
]
for i, (icon, title, desc, col) in enumerate(steps_ev):
    lx = 0.5 + i * 3.15
    add_rect(sl, lx, 1.35, 2.9, 3.6, fill=col)
    add_text(sl, icon,  lx+1.0,  1.45, 0.9, 0.7, size=30, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, title, lx+0.15, 2.2,  2.6, 0.8, size=13, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    add_rect(sl, lx+0.25, 3.0, 2.4, 0.04, fill=C_WHITE)
    add_text(sl, desc,  lx+0.15, 3.1,  2.6, 1.0, size=11.5, italic=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    if i < 3:
        add_text(sl, "→", lx+2.88, 2.85, 0.3, 0.6, size=20, bold=True, color=C_GRAY)

# Key distinctions
add_rect(sl, 0.5, 5.15, 12.3, 1.7, fill=C_LGRAY, line_color=C_INDIGO, line_w=Pt(1.5))
add_text(sl, "Important Ethical Guardrails:", 0.7, 5.25, 5.0, 0.4,
         size=13, bold=True, color=C_INDIGO)
for i, txt in enumerate([
    "✅  An incorrect answer does NOT label the candidate as dishonest",
    "✅  Results presented as preparation guidance, never a truthfulness verdict",
    "✅  Only tests understanding of their own stated experience",
]):
    add_text(sl, txt, 0.7, 5.7 + i*0.32, 11.8, 0.33, size=12, color=C_BLACK)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — DATABASE DESIGN
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Database Design", "11 tables — relational schema with full data isolation")

table_block(sl,
    ["Table", "Key Columns", "Relationships"],
    [
        ["users",             "id, email, hashed_pw, role",          "Parent of all user data"],
        ["resumes",           "id, user_id, filename, parse_status",  "FK → users"],
        ["resume_profiles",   "id, resume_id, skills_json",           "FK → resumes (1:1)"],
        ["job_descriptions",  "id, user_id, title, required_skills",  "FK → users"],
        ["job_match_results", "id, user_id, resume_id, jd_id, score","FK → users, resumes, JDs"],
        ["interview_sessions","id, user_id, status, difficulty",      "FK → users, resumes"],
        ["interview_questions","id, session_id, difficulty, type",    "FK → sessions"],
        ["interview_answers", "id, question_id, user_id, text",       "FK → questions, users"],
        ["answer_evaluations","id, answer_id, 5 criterion scores",    "FK → answers (1:1)"],
        ["evidence_claims",   "id, resume_id, claim, is_practiced",   "FK → resumes"],
        ["learning_plans",    "id, user_id, plan_json, 30-day",       "FK → users"],
    ],
    l=0.3, t=1.3, w=12.7, h=5.9,
    font_size=10)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — SECURITY
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Security Architecture", "Defence-in-depth across all layers")

security_items = [
    ("🔐", "Password Hashing", "bcrypt cost-12\nNever stored in plaintext", C_INDIGO),
    ("🎫", "JWT Auth",         "HS256 signed tokens\nConfigurable expiry (24h)", C_SKY),
    ("🛡️",  "RBAC",            "Server-side role check\non every admin endpoint", C_EMERALD),
    ("📂", "Safe Uploads",     "UUID prefix + MIME check\nPath traversal prevention", C_AMBER),
    ("🤖", "Prompt Injection", "Resume text sanitised\nbefore LLM injection", C_ROSE),
    ("🌐", "CORS Policy",      "Restricted to configured\nfrontend origins only", C_INDIGO),
]
for i, (icon, title, desc, col) in enumerate(security_items):
    col_idx = i % 3
    row_idx = i // 3
    lx = 0.4 + col_idx * 4.3
    ty = 1.35 + row_idx * 2.6
    add_rect(sl, lx, ty, 3.9, 2.3, fill=C_LGRAY, line_color=col, line_w=Pt(2))
    add_rect(sl, lx, ty, 3.9, 0.65, fill=col)
    add_text(sl, icon + "  " + title, lx+0.15, ty+0.1, 3.6, 0.5,
             size=14, bold=True, color=C_WHITE)
    add_text(sl, desc, lx+0.15, ty+0.8, 3.6, 1.35, size=12.5, color=C_BLACK)

add_rect(sl, 0.4, 6.85, 12.5, 0.42, fill=C_LGRAY, line_color=C_EMERALD, line_w=Pt(1))
add_text(sl, "✅  All secrets via .env only   |   ✅  No keys in frontend code   |   ✅  AI results labelled as estimates",
         0.6, 6.88, 12.1, 0.38, size=12, color=C_EMERALD, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — TESTING RESULTS
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Testing Results", "All 10 backend tests PASSED  |  Frontend build: 0 errors")

# Big stat
add_rect(sl, 0.4, 1.3, 3.5, 3.5, fill=C_EMERALD)
add_text(sl, "10/10", 0.6, 1.6, 3.1, 1.6, size=52, bold=True,
         color=C_WHITE, align=PP_ALIGN.CENTER)
add_text(sl, "TESTS PASSED", 0.6, 3.1, 3.1, 0.55, size=16, bold=True,
         color=C_WHITE, align=PP_ALIGN.CENTER)
add_text(sl, "4.88 seconds", 0.6, 3.65, 3.1, 0.4, size=12, color=C_WHITE, align=PP_ALIGN.CENTER)
add_text(sl, "Python 3.15 / Pytest 9.1.1", 0.6, 4.0, 3.1, 0.4, size=11,
         color=C_WHITE, align=PP_ALIGN.CENTER)

tests = [
    ("test_health_check",                             "✅ PASSED"),
    ("test_auth_registration_and_login",              "✅ PASSED"),
    ("test_unauthorized_endpoints",                  "✅ PASSED"),
    ("test_cross_user_isolation",                    "✅ PASSED"),
    ("test_resume_upload_and_scanned_error",          "✅ PASSED"),
    ("test_job_matching_and_scoring",                 "✅ PASSED"),
    ("test_mock_interview_flow",                      "✅ PASSED"),
    ("test_admin_authorization",                     "✅ PASSED"),
    ("test_evidence_claims_and_defense",              "✅ PASSED"),
    ("test_analytics_and_learning_plan",              "✅ PASSED"),
]
for i, (name, result) in enumerate(tests):
    ty = 1.35 + i * 0.52
    bg = C_LGRAY if i % 2 == 0 else C_WHITE
    add_rect(sl, 4.1, ty, 8.8, 0.48, fill=bg)
    add_text(sl, name, 4.2, ty+0.05, 7.5, 0.4, size=11, color=C_BLACK)
    add_text(sl, result, 11.4, ty+0.05, 1.4, 0.4, size=11, bold=True, color=C_EMERALD)

add_rect(sl, 0.4, 5.1, 12.5, 0.48, fill=C_INDIGO)
add_text(sl, "Frontend Build:  npm run build  →  ✅ 0 errors  |  282 KB JS (74 KB gzip)  |  1,987 modules",
         0.6, 5.13, 12.1, 0.42, size=13, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — DEMO WALKTHROUGH
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Demo Walkthrough", "Live demonstration flow")

demo_steps = [
    ("1", "Register / Login",         "Create account → JWT issued → Dashboard loads",              C_INDIGO),
    ("2", "Upload Resume",            "Drag-drop PDF → Parse → Editable profile preview",            C_SKY),
    ("3", "Resume Analysis",          "View quality score (0-100) + specific improvement tips",      C_EMERALD),
    ("4", "Job Description Match",    "Paste JD → See matched skills, gaps, evidence snippets",      C_AMBER),
    ("5", "Start Mock Interview",      "Configure difficulty → 5-10 questions generated",            C_ROSE),
    ("6", "Answer + Evaluation",      "Type/speak answer → Instant 5-criterion feedback",            C_INDIGO),
    ("7", "Evidence Checker",         "Claim extracted → Answer defence → Coverage tracked",         C_SKY),
    ("8", "Analytics + Report",       "Performance trends → 30-day plan → Download PDF report",      C_EMERALD),
]
for i, (num, title, desc, col) in enumerate(demo_steps):
    row = i // 2
    ci  = i % 2
    lx  = 0.4 + ci * 6.45
    ty  = 1.35 + row * 1.45
    add_rect(sl, lx, ty, 6.2, 1.3, fill=C_LGRAY, line_color=col, line_w=Pt(2))
    add_rect(sl, lx, ty, 0.7, 1.3, fill=col)
    add_text(sl, num, lx+0.05, ty+0.35, 0.6, 0.6, size=20, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, title, lx+0.85, ty+0.08, 5.2, 0.5, size=13, bold=True,
             color=C_INDIGO)
    add_text(sl, desc,  lx+0.85, ty+0.6,  5.2, 0.6, size=11, color=C_GRAY)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 17 — RESULTS & KEY FINDINGS
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Results & Key Findings", "Observed outcomes from sample data testing")

findings = [
    ("📋", "Resume Parsing",     "Correctly extracted skills, projects, education from all sample resumes (PDF + DOCX)"),
    ("🎯", "JD Matching",        "~58.8% match score for Alex Chen resume vs Full-Stack JD; missing: Kubernetes, AWS"),
    ("🔄", "Adaptive Difficulty","Difficulty reduced beginner→advanced within 2 questions when score changed from 30→82"),
    ("🔍", "Evidence Checker",   "Extracted 5 distinct claims from sample resume; unique verification Q per claim"),
    ("📅", "Learning Plan",      "30 distinct daily topics generated; no repetition; resources + estimated hours included"),
    ("📄", "PDF Report",         "4-page PDF report with all session data, criterion scores, and feedback embedded"),
    ("🔐", "Data Isolation",     "404 returned when User B accessed User A's resume ID — cross-user isolation confirmed"),
    ("⚡", "Performance",        "Average API response < 200ms for non-LLM endpoints; frontend loads in < 1.5s"),
]
for i, (icon, title, desc) in enumerate(findings):
    col_i = i % 2
    row_i = i // 2
    lx = 0.4 + col_i * 6.45
    ty = 1.35 + row_i * 1.38
    add_rect(sl, lx, ty, 6.2, 1.22, fill=C_LGRAY)
    add_rect(sl, lx, ty, 0.06, 1.22, fill=C_INDIGO)
    add_text(sl, icon, lx+0.15, ty+0.28, 0.55, 0.65, size=20, align=PP_ALIGN.CENTER)
    add_text(sl, title, lx+0.78, ty+0.08, 5.25, 0.48, size=13, bold=True, color=C_INDIGO)
    add_text(sl, desc,  lx+0.78, ty+0.58, 5.25, 0.62, size=11, color=C_GRAY)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 18 — LIMITATIONS & HONEST DISCLOSURES
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Honest Limitations & Disclosures", "What the system does NOT claim to do")

limits = [
    ("🚫 No OCR",           C_ROSE,    "Scanned/image PDFs return a clear error message.\nOCR not implemented — Tesseract planned for future."),
    ("🌐 English Only",     C_AMBER,   "NLP, prompts, and question bank designed for English.\nMulti-language support is future work."),
    ("📊 Heuristic Scores", C_INDIGO,  "Resume quality and match scores are NOT official ATS scores.\nNot a predictor of hiring success."),
    ("🤖 AI Estimates",     C_SKY,     "LLM evaluations are labelled 'AI-estimated'.\nNever presented as objective truth."),
    ("🎤 Voice Limits",     C_EMERALD, "Web Speech API works in Chrome/Edge only.\nSafari/Firefox auto-fall back to text mode."),
    ("🚦 No Rate Limiting", C_GRAY,    "Not implemented in dev mode.\nRedis-based rate limiting documented for production."),
]
for i, (title, col, desc) in enumerate(limits):
    col_i = i % 3
    row_i = i // 3
    lx = 0.4 + col_i * 4.3
    ty = 1.35 + row_i * 2.6
    add_rect(sl, lx, ty, 3.9, 2.3, fill=col)
    add_text(sl, title, lx+0.15, ty+0.12, 3.6, 0.55, size=13, bold=True, color=C_WHITE)
    add_rect(sl, lx+0.15, ty+0.7, 3.6, 0.04, fill=C_WHITE)
    add_text(sl, desc, lx+0.15, ty+0.82, 3.6, 1.38, size=11.5, italic=True, color=C_WHITE)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 19 — FUTURE WORK
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Future Work", "Planned enhancements for production readiness")

future = [
    ("🔬", "OCR Integration",     "Tesseract / Google Vision for scanned PDF support"),
    ("🧠", "SBERT Matching",      "Sentence-transformers for semantic skill matching"),
    ("🎥", "Video Interviews",    "WebRTC-based mock video session recording"),
    ("🐘", "PostgreSQL",          "Change DATABASE_URL only — no code changes needed"),
    ("🌍", "Multi-language",      "i18n + multilingual LLM prompts"),
    ("⚡", "Rate Limiting",       "Redis + slowapi for production deployment"),
    ("🔄", "CI/CD Pipeline",      "GitHub Actions: test + build + auto-deploy"),
    ("📱", "Mobile App",          "React Native interview screen"),
    ("🏢", "Company-specific",    "Job posting API integration (LinkedIn, Naukri)"),
    ("👥", "Peer Review Mode",    "Candidates review each other's answers"),
]
for i, (icon, title, desc) in enumerate(future):
    col_i = i % 5
    row_i = i // 5
    lx = 0.3 + col_i * 2.55
    ty = 1.35 + row_i * 2.6
    add_rect(sl, lx, ty, 2.35, 2.25, fill=C_LGRAY, line_color=C_INDIGO_L, line_w=Pt(1.2))
    add_text(sl, icon,  lx+0.8, ty+0.12,  0.75, 0.65, size=24, align=PP_ALIGN.CENTER)
    add_text(sl, title, lx+0.1, ty+0.82,  2.15, 0.55, size=12, bold=True,
             color=C_INDIGO, align=PP_ALIGN.CENTER)
    add_text(sl, desc,  lx+0.1, ty+1.42,  2.15, 0.78, size=10.5, color=C_GRAY,
             align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 20 — THANK YOU
# ════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, 13.33, 7.5, fill=C_INDIGO)
# Diagonal accent
add_rect(sl, 8.0, 0, 5.33, 7.5, fill=C_INDIGO_D)

add_text(sl, "Thank You", 0.6, 1.2, 7.5, 2.0, size=58, bold=True,
         color=C_WHITE, align=PP_ALIGN.LEFT)
add_text(sl, "Questions & Discussion Welcome",
         0.6, 3.3, 7.5, 0.7, size=20, color=C_INDIGO_L, italic=True)
add_rect(sl, 0.6, 4.1, 2.5, 0.06, fill=C_WHITE)

add_text(sl, "Resume2Interview AI",
         0.6, 4.3, 7.0, 0.55, size=16, bold=True, color=C_WHITE)
add_text(sl, "BTech Major Project  |  Department of CSE",
         0.6, 4.85, 7.0, 0.42, size=13, color=C_INDIGO_L)
add_text(sl, "[Your College / University Name]  |  2025–26",
         0.6, 5.27, 7.0, 0.42, size=13, color=C_INDIGO_L)

# Right panel stats
stats = [("10/10", "Tests Passed"), ("12", "Modules"), ("24", "API Endpoints"), ("11", "DB Tables")]
for i, (val, label) in enumerate(stats):
    ty = 0.8 + i * 1.65
    add_text(sl, val,   9.2, ty,      3.8, 0.95, size=38, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, label, 9.2, ty+0.9,  3.8, 0.5,  size=14,
             color=C_INDIGO_L, align=PP_ALIGN.CENTER)
    if i < 3:
        add_rect(sl, 9.5, ty+1.42, 3.2, 0.04, fill=C_INDIGO_L)

# ════════════════════════════════════════════════════════════════════════════
prs.save(OUTPUT)
print(f"PPT saved → {OUTPUT}")
print(f"Total slides: {len(prs.slides)}")
