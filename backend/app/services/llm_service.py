import os
import json
import re
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings
from app.services.fallback_bank import get_fallback_questions


class LLMService:
    """
    Unified LLM service interfacing with Gemini or OpenAI compatible endpoints.
    Provides strict input sanitization, JSON schema enforcement, and zero-crash fallbacks.
    """

    @classmethod
    def sanitize_untrusted_input(cls, text: str, max_chars: int = 4000) -> str:
        """Strip prompt injection attempts and enforce string length limits."""
        if not text:
            return ""
        # Remove markdown instructions or potential system overrides
        cleaned = re.sub(r"(ignore\s+all\s+previous\s+instructions|system\s+prompt|role:\s*system)", "[filtered]", text, flags=re.IGNORECASE)
        return cleaned[:max_chars].strip()

    @classmethod
    def is_llm_configured(cls) -> bool:
        """Check if any LLM API key is present."""
        return bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY)

    @classmethod
    def generate_interview_questions(
        cls,
        resume_profile: Dict[str, Any],
        job_description: str,
        role: str,
        difficulty: str,
        count: int = 5
    ) -> Tuple_Result:
        """
        Generates grounded interview questions using LLM if configured;
        otherwise safely returns genuine curated questions from FallbackBank.
        """
        # If no key configured, immediately return curated fallback
        if not cls.is_llm_configured():
            target_skills = []
            for s_list in resume_profile.get("skills", {}).values():
                target_skills.extend(s_list)
            return get_fallback_questions(role, target_skills, difficulty, count), "fallback_bank"

        # Attempt LLM call
        try:
            prompt = cls._build_question_generation_prompt(resume_profile, job_description, role, difficulty, count)
            response_json_str = cls._call_provider(prompt)
            parsed_data = cls._parse_and_validate_questions_json(response_json_str)
            if parsed_data and len(parsed_data) >= count:
                return parsed_data[:count], "ai_llm"
        except Exception as e:
            # Fallback on any network/format error
            pass

        # Return fallback with indicator
        target_skills = []
        for s_list in resume_profile.get("skills", {}).values():
            target_skills.extend(s_list)
        return get_fallback_questions(role, target_skills, difficulty, count), "fallback_bank"

    @classmethod
    def _build_question_generation_prompt(
        cls, resume_profile: Dict[str, Any], job_description: str, role: str, difficulty: str, count: int
    ) -> str:
        sanitized_resume = cls.sanitize_untrusted_input(str(resume_profile), 2000)
        sanitized_jd = cls.sanitize_untrusted_input(job_description, 2000)

        return f"""You are a professional technical interviewer hiring for the role of '{role}'.
Target Difficulty: {difficulty}
Number of Questions: {count}

Candidate Resume Summary:
{sanitized_resume}

Target Job Description:
{sanitized_jd}

INSTRUCTIONS:
1. Generate exactly {count} distinct interview questions:
   - Mix: Technical, Project-grounded (referencing real projects from resume), Behavioral, and HR.
   - Ground project questions in actual candidate resume items. Do not invent unlisted companies or projects.
2. Return ONLY a valid JSON array of objects with the following schema:
[
  {{
    "role": "{role}",
    "category": "technical|project|behavioral|hr",
    "difficulty": "beginner|intermediate|advanced",
    "skill_tag": "Skill or Concept Name",
    "question_text": "The exact interview question",
    "expected_points": ["Key concept 1", "Key concept 2"],
    "sample_good_answer": "Model exemplary answer"
  }}
]
DO NOT include markdown code fences or conversational text. Output pure JSON only."""

    @classmethod
    def _call_provider(cls, prompt: str) -> str:
        """Executes API call to Gemini or OpenAI with timeout."""
        if settings.GEMINI_API_KEY:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
            }
            with httpx.Client(timeout=12.0) as client:
                res = client.post(url, json=payload)
                res.raise_for_status()
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
        elif settings.OPENAI_API_KEY:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            with httpx.Client(timeout=12.0) as client:
                res = client.post(url, headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                return data["choices"][0]["message"]["content"]
        raise ValueError("No LLM key configured.")

    @classmethod
    def _parse_and_validate_questions_json(cls, raw: str) -> Optional[List[Dict[str, Any]]]:
        try:
            # Strip markdown fences if present
            clean = re.sub(r"^```json\s*", "", raw.strip(), flags=re.MULTILINE)
            clean = re.sub(r"```$", "", clean.strip(), flags=re.MULTILINE)
            items = json.loads(clean)
            if isinstance(items, list) and len(items) > 0:
                validated = []
                for item in items:
                    if "question_text" in item and "category" in item:
                        validated.append({
                            "role": item.get("role", "General"),
                            "category": item.get("category", "technical"),
                            "difficulty": item.get("difficulty", "intermediate"),
                            "skill_tag": item.get("skill_tag", "General"),
                            "question_text": item["question_text"],
                            "expected_points": item.get("expected_points", []),
                            "sample_good_answer": item.get("sample_good_answer", "")
                        })
                return validated
        except Exception:
            return None
        return None


# Helper type annotation
Tuple_Result = tuple[List[Dict[str, Any]], str]
