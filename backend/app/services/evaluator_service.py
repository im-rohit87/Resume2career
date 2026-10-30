import re
import json
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings
from app.services.llm_service import LLMService


class EvaluatorService:
    DISCLAIMER = (
        "Evaluation Disclaimer: All scores and critiques represent automated estimations based on "
        "defined technical rubrics and response structure. They are diagnostic preparation tools, not objective "
        "hiring facts or employment guarantees. This system does not evaluate or make claims based on "
        "accent, appearance, gender, emotion, or any protected personal characteristics."
    )

    RUBRIC_WEIGHTS = {
        "relevance": 0.20,
        "technical": 0.25,
        "completeness": 0.20,
        "clarity": 0.15,
        "reasoning": 0.20,
    }

    @classmethod
    def evaluate_answer(
        cls,
        question_text: str,
        category: str,
        difficulty: str,
        expected_points: List[str],
        sample_good_answer: str,
        candidate_answer: str,
    ) -> Dict[str, Any]:
        """Evaluates candidate answer using LLM or structured rubric heuristics."""
        clean_answer = candidate_answer.strip()

        # Check if LLM is configured
        if LLMService.is_llm_configured():
            try:
                result = cls._evaluate_with_llm(
                    question_text, category, difficulty, expected_points, sample_good_answer, clean_answer
                )
                if result:
                    result["evaluated_by"] = "ai_llm"
                    result["disclaimer"] = cls.DISCLAIMER
                    result["adaptive_next_difficulty"] = cls._determine_adaptive_difficulty(result["overall_score"])
                    return result
            except Exception:
                pass  # Fallback to deterministic heuristic engine

        # Fallback heuristic engine
        result = cls._evaluate_heuristic(
            question_text, category, difficulty, expected_points, sample_good_answer, clean_answer
        )
        result["evaluated_by"] = "heuristic_engine"
        result["disclaimer"] = cls.DISCLAIMER
        result["adaptive_next_difficulty"] = cls._determine_adaptive_difficulty(result["overall_score"])
        return result

    @classmethod
    def _determine_adaptive_difficulty(cls, score: float) -> str:
        """Adaptive rules: dynamically calibrate next question difficulty."""
        if score >= 75.0:
            return "advanced"
        elif score >= 50.0:
            return "intermediate"
        else:
            return "beginner"

    @classmethod
    def _evaluate_heuristic(
        cls,
        question: str,
        category: str,
        difficulty: str,
        expected_points: List[str],
        sample_answer: str,
        answer: str,
    ) -> Dict[str, Any]:
        """
        Comprehensive rule-based scoring engine evaluating answer length,
        key phrase coverage, structural markers (STAR method), and clarity.
        """
        words = re.findall(r"\b\w+\b", answer.lower())
        word_count = len(words)
        lower_ans = answer.lower()

        # 1. Relevance Score (max 100)
        # Check overlap of significant words from question and expected points
        q_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", question.lower()))
        matched_q = [w for w in q_words if w in lower_ans]
        relevance_score = min(max(len(matched_q) / max(len(q_words), 1) * 110.0, 35.0), 95.0)
        if word_count < 15:
            relevance_score = min(relevance_score, 40.0)

        # 2. Technical Score (max 100)
        # Check coverage of expected points and technical terms
        pts_matched = 0
        for pt in expected_points:
            pt_keywords = re.findall(r"\b[a-zA-Z]{4,}\b", pt.lower())
            if any(kw in lower_ans for kw in pt_keywords):
                pts_matched += 1

        if expected_points:
            tech_ratio = pts_matched / len(expected_points)
            tech_score = round(30.0 + (tech_ratio * 65.0), 1)
        else:
            tech_score = 75.0 if word_count >= 50 else 55.0

        if word_count < 20:
            tech_score = min(tech_score, 35.0)

        # 3. Completeness Score (max 100)
        # Evaluates word count and comprehensive explanation
        if word_count >= 90:
            comp_score = 90.0
        elif word_count >= 50:
            comp_score = 75.0
        elif word_count >= 25:
            comp_score = 60.0
        else:
            comp_score = 35.0

        # 4. Clarity & Communication (max 100)
        # Evaluates sentence structure, transitions, absence of gibberish
        sentences = [s for s in re.split(r"[.!?]", answer) if len(s.strip()) > 3]
        clarity_score = 70.0
        if len(sentences) >= 3:
            clarity_score += 15.0
        if any(tr in lower_ans for tr in ["for example", "because", "specifically", "in order to", "however", "therefore"]):
            clarity_score += 10.0
        clarity_score = min(clarity_score, 95.0)

        # 5. Reasoning & Problem Solving (max 100)
        # Looks for STAR patterns (situation, action, outcome) or trade-offs (pros/cons)
        reasoning_score = 60.0
        if any(term in lower_ans for term in ["trade-off", "latency", "bottleneck", "optimized", "decided to", "resulted in", "measure"]):
            reasoning_score += 25.0
        if category == "behavioral" and any(st in lower_ans for st in ["situation", "task", "action", "result", "outcome", "learned"]):
            reasoning_score += 15.0
        reasoning_score = min(reasoning_score, 95.0)

        # Overall weighted score
        overall = round(
            (relevance_score * cls.RUBRIC_WEIGHTS["relevance"]) +
            (tech_score * cls.RUBRIC_WEIGHTS["technical"]) +
            (comp_score * cls.RUBRIC_WEIGHTS["completeness"]) +
            (clarity_score * cls.RUBRIC_WEIGHTS["clarity"]) +
            (reasoning_score * cls.RUBRIC_WEIGHTS["reasoning"]),
            1
        )
        overall = min(max(overall, 15.0), 100.0)

        # Dynamic feedback & actionable recommendations
        strengths = []
        improvements = []

        if relevance_score >= 70:
            strengths.append("Directly addressed the core intent of the interview question.")
        else:
            improvements.append("Ensure your answer directly tackles the primary prompt before introducing tangential details.")

        if tech_score >= 70:
            strengths.append(f"Demonstrated good command of key technical concepts ({pts_matched}/{len(expected_points)} target points evidenced).")
        else:
            improvements.append("Incorporate deeper architectural specifics or underlying mechanics rather than high-level statements.")

        if word_count < 40:
            improvements.append("Expand on your response with concrete examples from your past projects or coursework.")
        else:
            strengths.append("Provided a well-elaborated explanation with sufficient contextual depth.")

        feedback_critique = (
            f"Your response shows solid familiarity with the topic. "
            f"You effectively touched upon {len(strengths)} key positive aspects. "
            f"To achieve an exceptional score, focus on: {improvements[0] if improvements else 'quantifying your project impact'}."
        )

        return {
            "relevance_score": round(relevance_score, 1),
            "technical_score": round(tech_score, 1),
            "completeness_score": round(comp_score, 1),
            "clarity_score": round(clarity_score, 1),
            "reasoning_score": round(reasoning_score, 1),
            "overall_score": overall,
            "feedback_critique": feedback_critique,
            "strengths": strengths,
            "improvements": improvements,
            "model_answer": sample_answer if sample_answer else "Model answer unavailable for this custom question.",
        }

    @classmethod
    def _evaluate_with_llm(
        cls, question: str, category: str, difficulty: str, expected_points: List[str], sample_answer: str, answer: str
    ) -> Optional[Dict[str, Any]]:
        prompt = f"""You are a fair, objective technical interview evaluator.
Evaluate this candidate's interview answer based strictly on merit and technical correctness.
Do NOT evaluate or penalize for gender, accent, background, or style. Distinguish factual technical correctness from communication structure.

Question: {question}
Category: {category}
Difficulty: {difficulty}
Expected Key Points: {json.dumps(expected_points)}
Candidate Answer: {answer}

Provide a JSON object adhering exactly to this structure:
{{
  "relevance_score": float 0-100,
  "technical_score": float 0-100,
  "completeness_score": float 0-100,
  "clarity_score": float 0-100,
  "reasoning_score": float 0-100,
  "overall_score": float 0-100,
  "feedback_critique": "2-3 constructive sentences explaining the score",
  "strengths": ["Strength 1", "Strength 2"],
  "improvements": ["Actionable improvement 1", "Actionable improvement 2"],
  "model_answer": "{sample_answer or 'Model answer demonstrating best practices.'}"
}}
Output pure JSON only."""

        raw_resp = LLMService._call_provider(prompt)
        clean = re.sub(r"^```json\s*", "", raw_resp.strip(), flags=re.MULTILINE)
        clean = re.sub(r"```$", "", clean.strip(), flags=re.MULTILINE)
        data = json.loads(clean)
        if "overall_score" in data and "feedback_critique" in data:
            return data
        return None
