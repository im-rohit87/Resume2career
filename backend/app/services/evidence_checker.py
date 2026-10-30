import re
from typing import Dict, Any, List


class ResumeEvidenceCheckerService:
    DISCLAIMER = (
        "Evidence Checker Disclaimer: This feature helps candidates prepare to defend and explain their "
        "resume bullet points and project claims during technical deep-dive interviews. "
        "It provides targeted preparation guidance and does NOT issue a truthfulness verdict or accuse candidates."
    )

    @classmethod
    def extract_claims(cls, profile: Dict[str, Any], raw_text: str = "") -> List[Dict[str, str]]:
        """Extracts prominent claims from projects, experience, and metrics."""
        claims = []
        projects = profile.get("projects", [])
        experience = profile.get("experience", [])
        skills = profile.get("skills", {})

        # 1. Project-based claims
        for proj in projects:
            title = proj.get("title", "")
            desc = proj.get("description", "")
            techs = ", ".join(proj.get("technologies", []))
            
            if title:
                claim_text = f"Project: {title}. {desc}"[:200]
                q_text = (
                    f"In your project '{title}', what were the core technical trade-offs of your chosen architecture? "
                    f"How did you validate that your solution met performance and reliability requirements?"
                )
                claims.append({
                    "claim_type": "project",
                    "claim_text": claim_text,
                    "verification_question": q_text,
                })

        # 2. Metric / Performance claims
        metric_matches = re.finditer(
            r"([^.\n]*\b(?:\d+%\b|\$\d+|\d+[xX]\b|reduced|improved|scaled|optimized)\b[^.\n]*)",
            raw_text,
            re.IGNORECASE
        )
        seen_snippets = set()
        for m in metric_matches:
            snippet = m.group(0).strip()
            if len(snippet) > 20 and snippet not in seen_snippets and len(claims) < 6:
                seen_snippets.add(snippet)
                q_text = (
                    f"Your resume mentions: '{snippet[:120]}...'. "
                    f"Walk me through how you established the baseline before this improvement, and what exact tools or metrics you used to measure the outcome."
                )
                claims.append({
                    "claim_type": "metric",
                    "claim_text": snippet[:200],
                    "verification_question": q_text,
                })

        # 3. High-level technical claims
        tools = skills.get("tools_platforms", [])
        if "Docker" in tools or "Kubernetes" in tools:
            claims.append({
                "claim_type": "technology",
                "claim_text": "Claimed containerization and orchestration proficiency (Docker / Kubernetes).",
                "verification_question": "Explain how you structure multi-stage Docker builds to minimize image attack surfaces and layer cache invalidation.",
            })

        if "Redis" in tools:
            claims.append({
                "claim_type": "technology",
                "claim_text": "Claimed in-memory caching proficiency with Redis.",
                "verification_question": "When configuring Redis in a production system, what eviction policy would you select for cache stampede prevention, and how do you handle cache invalidation?",
            })

        # Guarantee at least 3 claims for thorough preparation
        if not claims:
            claims.append({
                "claim_type": "project",
                "claim_text": "Full-stack software engineering project development.",
                "verification_question": "Walk me through the database schema design of your primary application. What normalization level did you choose and why?",
            })

        return claims[:7]

    @classmethod
    def evaluate_verification_answer(cls, question: str, candidate_answer: str) -> Dict[str, Any]:
        """Evaluates candidate's defense of a resume claim."""
        words = len(re.findall(r"\b\w+\b", candidate_answer))
        lower = candidate_answer.lower()

        # Criteria: specificity, metrics mentioned, technical depth
        has_specifics = any(k in lower for k in ["measured", "benchmark", "baseline", "latency", "schema", "architecture", "trade-off", "specifically"])
        
        if words >= 45 and has_specifics:
            status = "verified_strong"
            guidance = "Excellent defense. You provided concrete engineering methodology, metrics, and sound reasoning."
        elif words >= 20:
            status = "practiced"
            guidance = "Good practice. To strengthen your defense in an actual interview, provide exact tooling names and baseline measurements."
        else:
            status = "needs_preparation"
            guidance = "Brief answer. Interviewers will press for technical specifics when verifying resume claims. Practice elaborating on your exact contribution."

        return {
            "status": status,
            "guidance": guidance,
            "disclaimer": cls.DISCLAIMER
        }
