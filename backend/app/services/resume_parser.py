import re
import os
from typing import Dict, Any, Tuple
import pymupdf  # Modern PyMuPDF import
import docx
from fastapi import HTTPException, status

# Technical & professional taxonomy for accurate categorization
SKILL_TAXONOMY = {
    "technical_skills": {
        "python", "javascript", "typescript", "java", "c++", "c#", "golang", "go",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "html", "css",
        "nosql", "graphql", "rest", "api", "data structures", "algorithms"
    },
    "frameworks_libraries": {
        "react", "react.js", "next.js", "vue", "angular", "node.js", "express", "fastapi",
        "django", "flask", "spring boot", "asp.net", "laravel", "rails", "tensorflow",
        "pytorch", "scikit-learn", "pandas", "numpy", "tailwind", "bootstrap", "redux"
    },
    "tools_platforms": {
        "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "gitlab",
        "ci/cd", "jenkins", "linux", "postgresql", "mysql", "mongodb", "redis",
        "sqlite", "nginx", "kafka", "rabbitmq", "terraform", "jira", "vite"
    },
    "soft_skills": {
        "leadership", "teamwork", "communication", "problem solving", "critical thinking",
        "agile", "scrum", "mentorship", "collaboration", "time management", "adaptability"
    }
}


class ResumeParserService:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from a PDF file using PyMuPDF."""
        try:
            doc = pymupdf.open(file_path)
            extracted_pages = []
            for page in doc:
                text = page.get_text()
                if text:
                    extracted_pages.append(text)
            doc.close()
            return "\n".join(extracted_pages).strip()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read PDF document: {str(e)}. The file may be corrupt or encrypted."
            )

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from a DOCX file using python-docx."""
        try:
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        paragraphs.append(row_text)
            return "\n".join(paragraphs).strip()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read DOCX document: {str(e)}. Please verify the file integrity."
            )

    @classmethod
    def parse_document(cls, file_path: str, filename: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parses PDF or DOCX, handles scanned document detection,
        and extracts structured resume profile.
        """
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            raw_text = cls.extract_text_from_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            raw_text = cls.extract_text_from_docx(file_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format '{ext}'. Only .pdf and .docx documents are supported."
            )

        # Check for empty text or scanned PDF
        if not raw_text or len(raw_text.strip()) < 35:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "This document contains little or no selectable digital text. "
                    "If this is a scanned or image-only PDF, optical character recognition (OCR) is required. "
                    "Please upload a text-based PDF or DOCX file to proceed without fabricated data."
                )
            )

        profile = cls.extract_structured_profile(raw_text)
        return raw_text, profile

    @classmethod
    def extract_structured_profile(cls, text: str) -> Dict[str, Any]:
        """Extracts candidate profile with zero fabricated data."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        contact = cls._extract_contact(lines, text)
        skills = cls._extract_skills(text)
        education = cls._extract_education(lines, text)
        experience = cls._extract_experience(lines, text)
        projects = cls._extract_projects(lines, text)
        certifications = cls._extract_certifications(lines, text)
        summary = cls._extract_summary(lines)

        return {
            "contact": contact,
            "summary": summary,
            "skills": skills,
            "education": education,
            "experience": experience,
            "projects": projects,
            "certifications": certifications,
        }

    @staticmethod
    def _extract_contact(lines: list[str], full_text: str) -> Dict[str, str]:
        # Extract email
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", full_text)
        email = email_match.group(0) if email_match else ""

        # Extract phone
        phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{2,5}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{4,5}", full_text)
        phone = phone_match.group(0).strip() if phone_match else ""

        # Extract LinkedIn & GitHub
        linkedin_match = re.search(r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+", full_text, re.IGNORECASE)
        linkedin = linkedin_match.group(0) if linkedin_match else ""

        github_match = re.search(r"(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+", full_text, re.IGNORECASE)
        github = github_match.group(0) if github_match else ""

        # Name heuristic: look at top 5 non-empty lines, exclude words like 'resume', 'curriculum', 'page'
        candidate_name = ""
        for line in lines[:6]:
            clean = re.sub(r"[^a-zA-Z\s]", "", line).strip()
            lower = clean.lower()
            if lower in ["resume", "curriculum vitae", "cv", "portfolio", "contact"]:
                continue
            if len(clean.split()) in [2, 3, 4] and not any(char.isdigit() for char in line) and "@" not in line:
                candidate_name = clean
                break

        if not candidate_name and lines:
            candidate_name = lines[0][:40]

        return {
            "name": candidate_name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "location": ""
        }

    @staticmethod
    def _extract_summary(lines: list[str]) -> str:
        summary_lines = []
        in_summary = False
        for line in lines[:15]:
            lower = line.lower().strip()
            if any(h in lower for h in ["summary", "profile", "about me", "professional summary"]):
                in_summary = True
                continue
            if in_summary:
                if any(h in lower for h in ["education", "experience", "skills", "projects", "certifications"]):
                    break
                summary_lines.append(line)
        return " ".join(summary_lines).strip()

    @classmethod
    def _extract_skills(cls, full_text: str) -> Dict[str, list]:
        lower_text = full_text.lower()
        extracted = {
            "technical_skills": [],
            "frameworks_libraries": [],
            "tools_platforms": [],
            "soft_skills": []
        }

        # Tokenize and match against taxonomy
        for category, skills in SKILL_TAXONOMY.items():
            for skill in skills:
                # Word boundary match to avoid false positives (e.g. 'go' in 'good')
                pattern = r"\b" + re.escape(skill) + r"\b"
                if re.search(pattern, lower_text):
                    extracted[category].append(skill.title() if len(skill) > 3 else skill.upper())

        # Deduplicate and sort
        for cat in extracted:
            extracted[cat] = sorted(list(set(extracted[cat])))

        return extracted

    @staticmethod
    def _extract_education(lines: list[str], full_text: str) -> list[Dict[str, str]]:
        education = []
        degree_keywords = ["bachelor", "b.tech", "b.e", "btech", "master", "m.tech", "mtech", "b.sc", "m.sc", "bca", "mca", "ph.d", "diploma", "high school"]
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(deg in line_lower for deg in degree_keywords):
                degree = line
                institution = ""
                year = ""
                # Check next 2 lines for university or year
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", next_line)
                    if year_match:
                        year = year_match.group(0)
                    if any(w in next_line.lower() for w in ["university", "college", "institute", "school"]):
                        institution = next_line
                
                education.append({
                    "degree": degree,
                    "institution": institution,
                    "year": year,
                    "gpa_or_percentage": ""
                })
        return education

    @staticmethod
    def _extract_experience(lines: list[str], full_text: str) -> list[Dict[str, Any]]:
        experience = []
        job_titles = ["engineer", "developer", "intern", "consultant", "analyst", "lead", "architect", "manager", "designer", "researcher"]
        
        in_exp_section = False
        current_exp = None

        for line in lines:
            line_lower = line.lower()
            if any(h in line_lower for h in ["experience", "employment", "work history"]):
                in_exp_section = True
                continue
            if in_exp_section and any(h in line_lower for h in ["education", "projects", "certifications", "skills", "publications"]):
                if current_exp:
                    experience.append(current_exp)
                    current_exp = None
                in_exp_section = False
                continue

            if in_exp_section:
                # Check if this line looks like a job title
                if any(t in line_lower for t in job_titles):
                    if current_exp:
                        experience.append(current_exp)
                    current_exp = {
                        "title": line,
                        "company": "",
                        "duration": "",
                        "responsibilities": []
                    }
                elif current_exp:
                    if line.startswith(("-", "•", "*", "–")):
                        current_exp["responsibilities"].append(line.lstrip("-•*– ").strip())
                    elif not current_exp["company"] and len(line.split()) < 6:
                        current_exp["company"] = line

        if current_exp:
            experience.append(current_exp)
        return experience

    @staticmethod
    def _extract_projects(lines: list[str], full_text: str) -> list[Dict[str, Any]]:
        projects = []
        in_proj_section = False
        current_proj = None

        for line in lines:
            line_lower = line.lower()
            if any(h in line_lower for h in ["projects", "personal projects", "academic projects", "key projects"]):
                in_proj_section = True
                continue
            if in_proj_section and any(h in line_lower for h in ["education", "experience", "certifications", "skills", "achievements"]):
                if current_proj:
                    projects.append(current_proj)
                    current_proj = None
                in_proj_section = False
                continue

            if in_proj_section:
                # If bullet point, attach to current project
                if line.startswith(("-", "•", "*", "–")):
                    if current_proj:
                        current_proj["description"] += " " + line.lstrip("-•*– ").strip()
                elif len(line.split()) <= 8 and not line.endswith("."):
                    # Potential project title
                    if current_proj:
                        projects.append(current_proj)
                    current_proj = {
                        "title": line,
                        "technologies": [],
                        "description": "",
                        "metrics_or_outcomes": ""
                    }
                elif current_proj and not current_proj["description"]:
                    current_proj["description"] = line

        if current_proj:
            projects.append(current_proj)
        return projects

    @staticmethod
    def _extract_certifications(lines: list[str], full_text: str) -> list[str]:
        certs = []
        in_cert = False
        for line in lines:
            line_lower = line.lower()
            if "certification" in line_lower or "licenses" in line_lower:
                in_cert = True
                continue
            if in_cert and any(h in line_lower for h in ["education", "experience", "skills", "projects"]):
                in_cert = False
                continue
            if in_cert:
                clean = line.lstrip("-•*– ").strip()
                if clean and len(clean) > 4:
                    certs.append(clean)
        return certs[:6]
