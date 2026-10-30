import re
from typing import Dict, Any, List


class ResumeAnalyzerService:
    DISCLAIMER = (
        "This is an objective heuristic resume-quality score calculated from industry-standard technical "
        "recruiting criteria (completeness, technical depth, quantifiable impact, and structural clarity). "
        "It is not an official proprietary ATS score and does not guarantee employer shortlisting or hiring decisions."
    )

    FORMULA_EXPLANATION = (
        "Overall Heuristic Score = Contact Completeness (15%) + Skills Breadth & Depth (25%) + "
        "Experience & Projects Detail (30%) + Section Structure (20%) + Quantified Impact & Metrics (10%)."
    )

    @classmethod
    def analyze_profile(cls, profile: Dict[str, Any], raw_text: str = "") -> Dict[str, Any]:
        """Calculates transparent heuristic score, strengths, missing sections, and actionable advice."""
        contact = profile.get("contact", {})
        skills = profile.get("skills", {})
        experience = profile.get("experience", [])
        projects = profile.get("projects", [])
        education = profile.get("education", [])
        certifications = profile.get("certifications", [])
        summary = profile.get("summary", "")

        strengths: List[str] = []
        missing_sections: List[str] = []
        suggestions: List[str] = []
        quantified_metrics: List[str] = []

        # 1. Contact Score (max 15)
        contact_score = 0.0
        if contact.get("email"):
            contact_score += 5.0
        else:
            suggestions.append("Add a professional email address for recruiter contact.")

        if contact.get("phone"):
            contact_score += 4.0
        else:
            suggestions.append("Include a reachable phone number with country code.")

        if contact.get("linkedin") or contact.get("github"):
            contact_score += 6.0
            strengths.append("Contains professional online profiles (LinkedIn / GitHub).")
        else:
            suggestions.append("Add links to your LinkedIn profile and GitHub portfolio.")

        # 2. Skills Score (max 25)
        tech_skills = skills.get("technical_skills", [])
        frameworks = skills.get("frameworks_libraries", [])
        tools = skills.get("tools_platforms", [])
        soft = skills.get("soft_skills", [])

        total_skills_count = len(tech_skills) + len(frameworks) + len(tools)
        if total_skills_count >= 12:
            skills_score = 25.0
            strengths.append(f"Strong, diverse technical vocabulary ({total_skills_count} verified technical skills detected).")
        elif total_skills_count >= 6:
            skills_score = 18.0
            strengths.append("Good foundational skill set, consider adding cloud or database tooling.")
        elif total_skills_count >= 2:
            skills_score = 10.0
            suggestions.append("Expand your skills section with specific databases, cloud tools, and frameworks.")
        else:
            skills_score = 4.0
            missing_sections.append("Dedicated Technical Skills Section")
            suggestions.append("Explicitly list programming languages, frameworks, and developer tools.")

        # 3. Experience & Projects Score (max 30)
        exp_score = 0.0
        if len(projects) >= 2:
            exp_score += 15.0
            strengths.append(f"Includes {len(projects)} distinct technical projects demonstrating practical implementation.")
        elif len(projects) == 1:
            exp_score += 9.0
            suggestions.append("Add at least 2 to 3 detailed technical projects showing end-to-end development.")
        else:
            missing_sections.append("Projects Section")
            suggestions.append("Include substantive technical projects with links, architecture details, and results.")

        if len(experience) >= 1:
            exp_score += 15.0
            strengths.append(f"Demonstrates practical professional or internship experience ({len(experience)} role(s)).")
        else:
            # If no corporate experience, award partial credit if projects are strong
            if len(projects) >= 2:
                exp_score += 10.0
            else:
                suggestions.append("If you have completed internships, freelance work, or open-source contributions, add an Experience section.")

        # 4. Section Structure Score (max 20)
        structure_score = 0.0
        if summary and len(summary) > 40:
            structure_score += 5.0
            strengths.append("Clear professional summary providing role identity.")
        else:
            suggestions.append("Add a 2-3 sentence executive summary highlighting your core expertise and target role.")

        if education and len(education) >= 1:
            structure_score += 8.0
        else:
            missing_sections.append("Formal Education Section")
            suggestions.append("Include your degree, university or institute name, and graduation year.")

        if certifications and len(certifications) >= 1:
            structure_score += 4.0
            strengths.append(f"Features recognized professional certifications ({len(certifications)} found).")
        else:
            suggestions.append("Consider earning industry-standard certifications (e.g. AWS, GCP, or specialized developer certificates).")

        if len(soft) >= 2:
            structure_score += 3.0

        # 5. Quantified Metrics & Action Verbs (max 10)
        # Scan raw text or descriptions for numbers, percentages, scales
        search_corpus = raw_text if raw_text else str(profile)
        metric_patterns = [
            r"\b\d+%\b",  # e.g. 40%, 15%
            r"\$\d+[kKmMbB]?",  # e.g. $10k, $500
            r"\b\d+[xX]\b",  # e.g. 2x, 10x
            r"\b(?:reduced|improved|increased|boosted|optimized|scaled)\s+(?:by\s+)?\d+",
            r"\b\d+[\+]?\s+(?:users|requests|rps|qps|stars|downloads|clients)\b"
        ]

        for pat in metric_patterns:
            matches = re.findall(pat, search_corpus, re.IGNORECASE)
            for m in matches:
                clean_m = str(m).strip()
                if clean_m not in quantified_metrics:
                    quantified_metrics.append(clean_m)

        metrics_count = len(quantified_metrics)
        if metrics_count >= 3:
            metrics_score = 10.0
            strengths.append(f"High-impact bullet points with quantified results ({metrics_count} performance metrics identified).")
        elif metrics_count >= 1:
            metrics_score = 6.0
            suggestions.append("Increase quantifiable outcomes: mention percentage performance gains, latency drops, or user counts.")
        else:
            metrics_score = 2.0
            suggestions.append("Transform descriptive task statements into measurable outcomes using the 'Action Verb + Context + Quantified Metric' pattern.")

        total_score = round(contact_score + skills_score + exp_score + structure_score + metrics_score, 1)
        total_score = min(max(total_score, 0.0), 100.0)

        score_breakdown = {
            "contact_completeness": round(contact_score, 1),
            "skills_breadth": round(skills_score, 1),
            "experience_and_projects": round(exp_score, 1),
            "structure_and_formatting": round(structure_score, 1),
            "quantified_metrics": round(metrics_score, 1),
        }

        return {
            "heuristic_score": total_score,
            "score_breakdown": score_breakdown,
            "strengths": strengths,
            "missing_sections": missing_sections,
            "actionable_suggestions": suggestions,
            "quantified_metrics_found": quantified_metrics[:8],
            "formula_explanation": cls.FORMULA_EXPLANATION,
            "disclaimer": cls.DISCLAIMER,
        }
