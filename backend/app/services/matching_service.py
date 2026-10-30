import re
import math
from typing import Dict, Any, List, Set, Tuple
from app.services.resume_parser import SKILL_TAXONOMY

# Skill taxonomy mappings for related skill discovery
RELATED_SKILL_GRAPH = {
    "react": ["vue", "angular", "next.js", "javascript", "typescript"],
    "vue": ["react", "angular", "javascript"],
    "angular": ["react", "typescript", "javascript"],
    "node.js": ["express", "fastapi", "django", "javascript", "backend"],
    "fastapi": ["flask", "django", "python", "rest", "api"],
    "django": ["fastapi", "flask", "python", "postgresql"],
    "flask": ["fastapi", "django", "python"],
    "postgresql": ["mysql", "sqlite", "sql", "mongodb"],
    "mysql": ["postgresql", "sqlite", "sql"],
    "mongodb": ["nosql", "redis", "postgresql"],
    "docker": ["kubernetes", "ci/cd", "linux", "aws"],
    "kubernetes": ["docker", "terraform", "aws", "gcp"],
    "aws": ["gcp", "azure", "docker", "cloud"],
    "gcp": ["aws", "azure", "docker", "cloud"],
    "azure": ["aws", "gcp", "cloud"],
    "c++": ["c", "c#", "java", "data structures"],
    "java": ["kotlin", "spring boot", "c#", "scala"],
    "python": ["golang", "fastapi", "django", "pandas"],
    "golang": ["python", "rust", "docker", "backend"],
}


class MatchingService:
    DISCLAIMER = (
        "Notice: A missing keyword does not prove that a candidate lacks capability; it solely indicates "
        "that the term or concept was not explicitly detected in the uploaded resume. This analysis is designed "
        "as an objective diagnostic tool for interview preparation and skill gap prioritization."
    )

    FORMULA_EXPLANATION = (
        "Match Score = (Required Skills Coverage * 60%) + (Preferred Skills Coverage * 25%) + "
        "(Text Corpus TF-IDF Cosine Similarity * 15%)."
    )

    @classmethod
    def match_resume_to_job(
        cls, resume_profile: Dict[str, Any], raw_resume_text: str, role_title: str, job_text: str
    ) -> Dict[str, Any]:
        """Compares resume with JD, extracts required/preferred skills, finds evidence, and calculates score."""
        required_skills, preferred_skills = cls.extract_skills_from_jd(job_text, role_title)
        
        # Aggregate all candidate skills from profile and text
        candidate_skills_set = cls._gather_candidate_skills(resume_profile, raw_resume_text)

        # Match required skills
        matched_required: List[Dict[str, Any]] = []
        missing_required: List[str] = []
        for req in required_skills:
            found, snippet = cls._find_skill_evidence(req, raw_resume_text, candidate_skills_set)
            if found:
                matched_required.append({
                    "skill": req,
                    "found_in_resume": True,
                    "evidence_snippet": snippet,
                    "category": "required"
                })
            else:
                missing_required.append(req)

        # Match preferred skills
        matched_preferred: List[Dict[str, Any]] = []
        missing_preferred: List[str] = []
        for pref in preferred_skills:
            found, snippet = cls._find_skill_evidence(pref, raw_resume_text, candidate_skills_set)
            if found:
                matched_preferred.append({
                    "skill": pref,
                    "found_in_resume": True,
                    "evidence_snippet": snippet,
                    "category": "preferred"
                })
            else:
                missing_preferred.append(pref)

        # Find related skills for missing ones
        related_skills_present: List[Dict[str, str]] = []
        for missing in (missing_required + missing_preferred):
            key = missing.lower()
            if key in RELATED_SKILL_GRAPH:
                for rel in RELATED_SKILL_GRAPH[key]:
                    if rel in candidate_skills_set:
                        related_skills_present.append({
                            "missing_target": missing,
                            "related_candidate_skill": rel.title(),
                            "bridge_rationale": f"Candidate has strong background in '{rel.title()}', which demonstrates transferable capability to learn '{missing}'."
                        })
                        break

        # Calculate Coverage
        req_ratio = len(matched_required) / max(len(required_skills), 1)
        pref_ratio = len(matched_preferred) / max(len(preferred_skills), 1)

        # Calculate TF-IDF Cosine Similarity
        cosine_sim = cls.compute_tfidf_similarity(raw_resume_text, job_text)

        # Weighted score (0 to 100)
        final_score = round((req_ratio * 60.0) + (pref_ratio * 25.0) + (cosine_sim * 15.0), 1)
        final_score = min(max(final_score, 0.0), 100.0)

        # Recommendations
        recommendations = []
        if missing_required:
            top_missing = ", ".join(missing_required[:3])
            recommendations.append(f"High Priority: Prepare talking points or quick project proof-of-concepts for required competencies: {top_missing}.")
        if related_skills_present:
            sample_rel = related_skills_present[0]
            recommendations.append(
                f"Transferable Advantage: When asked about {sample_rel['missing_target']}, highlight your proficiency in {sample_rel['related_candidate_skill']} to prove adaptability."
            )
        if final_score >= 80:
            recommendations.append("Strong candidate alignment. Focus mock interview practice on architectural trade-offs and behavioral depth.")
        elif final_score >= 50:
            recommendations.append("Moderate alignment. Dedicate mock interview rounds to bridging identified missing skill gaps.")
        else:
            recommendations.append("Consider reviewing project bullet points to ensure applicable tools used in coursework or side projects are explicitly named.")

        return {
            "match_score": final_score,
            "score_breakdown": {
                "required_skills_coverage": round(req_ratio * 60.0, 1),
                "preferred_skills_coverage": round(pref_ratio * 25.0, 1),
                "semantic_corpus_similarity": round(cosine_sim * 15.0, 1),
            },
            "role_title": role_title,
            "required_skills_matched": matched_required,
            "required_skills_missing": missing_required,
            "preferred_skills_matched": matched_preferred,
            "preferred_skills_missing": missing_preferred,
            "related_skills_present": related_skills_present,
            "recommendations": recommendations,
            "formula_explanation": cls.FORMULA_EXPLANATION,
            "disclaimer": cls.DISCLAIMER,
        }

    @classmethod
    def extract_skills_from_jd(cls, job_text: str, role_title: str) -> Tuple[List[str], List[str]]:
        """Extracts required vs preferred skills from job description text."""
        lower_jd = job_text.lower()
        all_skills_flat = []
        for cat in SKILL_TAXONOMY.values():
            all_skills_flat.extend(cat)

        found_skills = set()
        for skill in all_skills_flat:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, lower_jd):
                found_skills.add(skill.title() if len(skill) > 3 else skill.upper())

        # If job description mentions 'required', 'must have', 'qualifications' vs 'preferred', 'nice to have'
        required = []
        preferred = []

        # Split by sections if possible
        sections = re.split(r"\b(preferred|nice to have|bonus|good to have|plus)\b", lower_jd)
        if len(sections) > 1:
            req_part = sections[0]
            pref_part = " ".join(sections[1:])
            for skill in found_skills:
                sk_clean = skill.lower()
                if sk_clean in pref_part and sk_clean not in req_part:
                    preferred.append(skill)
                else:
                    required.append(skill)
        else:
            # Heuristic: split 70% required, 30% preferred
            skill_list = sorted(list(found_skills))
            split_idx = max(int(len(skill_list) * 0.7), 1)
            required = skill_list[:split_idx]
            preferred = skill_list[split_idx:]

        # Guarantee at least some required skills based on role title if none matched
        if not required:
            role_lower = role_title.lower()
            if "frontend" in role_lower or "web" in role_lower:
                required = ["React", "JavaScript", "HTML", "CSS"]
                preferred = ["TypeScript", "Tailwind"]
            elif "python" in role_lower or "backend" in role_lower:
                required = ["Python", "SQL", "FastAPI", "API"]
                preferred = ["Docker", "Redis"]
            elif "data" in role_lower or "ml" in role_lower:
                required = ["Python", "SQL", "Pandas", "Scikit-Learn"]
                preferred = ["Docker", "PyTorch"]
            else:
                required = ["Data Structures", "Algorithms", "Git", "Problem Solving"]
                preferred = ["Cloud", "CI/CD"]

        return sorted(required), sorted(preferred)

    @classmethod
    def _gather_candidate_skills(cls, profile: Dict[str, Any], raw_text: str) -> Set[str]:
        candidate_skills = set()
        skills_obj = profile.get("skills", {})
        for cat_list in skills_obj.values():
            for s in cat_list:
                candidate_skills.add(s.lower())

        # Also scan text for known skills
        for cat in SKILL_TAXONOMY.values():
            for s in cat:
                if re.search(r"\b" + re.escape(s) + r"\b", raw_text.lower()):
                    candidate_skills.add(s.lower())

        return candidate_skills

    @classmethod
    def _find_skill_evidence(cls, skill: str, raw_text: str, candidate_skills: Set[str]) -> Tuple[bool, str]:
        sk_lower = skill.lower()
        if sk_lower in candidate_skills:
            # Find evidence snippet around the word in resume text
            match = re.search(r"([^.\n]*\b" + re.escape(sk_lower) + r"\b[^.\n]*)", raw_text, re.IGNORECASE)
            snippet = match.group(0).strip() if match else f"Verified in parsed skills list ({skill})"
            return True, snippet[:140]

        # Check in raw text directly
        match = re.search(r"([^.\n]*\b" + re.escape(sk_lower) + r"\b[^.\n]*)", raw_text, re.IGNORECASE)
        if match:
            return True, match.group(0).strip()[:140]

        return False, ""

    @staticmethod
    def compute_tfidf_similarity(text1: str, text2: str) -> float:
        """Pure-Python transparent TF-IDF vectorization and cosine similarity."""
        def tokenize(text: str) -> List[str]:
            return [w for w in re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())]

        tokens1 = tokenize(text1)
        tokens2 = tokenize(text2)

        if not tokens1 or not tokens2:
            return 0.0

        vocab = sorted(list(set(tokens1 + tokens2)))
        n_docs = 2

        # Term counts
        tf1: Dict[str, int] = {}
        for t in tokens1:
            tf1[t] = tf1.get(t, 0) + 1

        tf2: Dict[str, int] = {}
        for t in tokens2:
            tf2[t] = tf2.get(t, 0) + 1

        # Document frequencies & TF-IDF vectors
        v1 = []
        v2 = []
        for w in vocab:
            df = (1 if w in tf1 else 0) + (1 if w in tf2 else 0)
            idf = math.log((1 + n_docs) / (1 + df)) + 1.0
            score1 = (tf1.get(w, 0) / len(tokens1)) * idf
            score2 = (tf2.get(w, 0) / len(tokens2)) * idf
            v1.append(score1)
            v2.append(score2)

        # Dot product & magnitudes
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return max(min(dot / (mag1 * mag2), 1.0), 0.0)
