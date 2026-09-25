"""AI-powered field mapping using Gemini API with intelligent fallback."""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx

from models.schemas import FormQuestion, MatchedField, StudentProfile

logger = logging.getLogger("gemini_mapper")


class GeminiFormMapper:
    """
    Maps Google Form questions/entry_ids to student profile values using
    Gemini API (when GEMINI_API_KEY is available) with automatic fallback
    to semantic heuristic keyword matching.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model

    async def map_fields(
        self,
        questions: List[FormQuestion],
        student: StudentProfile,
        custom_mapping: Optional[Dict[str, str]] = None,
    ) -> Tuple[List[MatchedField], List[str]]:
        """
        Map extracted FormQuestions to StudentProfile values.
        Tries Gemini LLM mapping first if API key is present; falls back to heuristic matching.
        """
        flattened_student = student.to_flattened_dict()

        if self.api_key and questions:
            try:
                matched, unmatched = await self._map_with_gemini_api(questions, flattened_student, custom_mapping)
                if matched:
                    logger.info(f"Successfully mapped {len(matched)} fields using Gemini API.")
                    return matched, unmatched
            except Exception as e:
                logger.warning(f"Gemini API mapping failed, falling back to heuristic mapper: {e}")

        # Fallback to local heuristic matching
        from services.google_form_service import GoogleFormService
        fallback_service = GoogleFormService()
        return fallback_service.match_fields(
            questions=questions,
            student=student,
            custom_mapping=custom_mapping,
            auto_match=True,
        )

    async def _map_with_gemini_api(
        self,
        questions: List[FormQuestion],
        student_data: Dict[str, str],
        custom_mapping: Optional[Dict[str, str]] = None,
    ) -> Tuple[List[MatchedField], List[str]]:
        """Call Gemini API via httpx to determine optimal field matches."""
        questions_payload = [
            {
                "entry_id": q.entry_id,
                "title": q.title,
                "description": q.description,
                "options": q.options,
                "required": q.required,
            }
            for q in questions
        ]

        prompt = f"""
You are an expert data-matching engine for automated form filling.
Map the provided Google Form questions to the candidate's profile data.

### CANDIDATE PROFILE:
{json.dumps(student_data, indent=2)}

### FORM QUESTIONS:
{json.dumps(questions_payload, indent=2)}

### OPTIONAL CUSTOM MAPPINGS:
{json.dumps(custom_mapping or {}, indent=2)}

### INSTRUCTIONS:
1. For each question, decide if there is a matching value in the candidate's profile.
2. If the question has multiple choice options, select the exact option string that best fits.
3. Return a valid JSON array of objects with the exact schema:
[
  {{
    "entry_id": "<string>",
    "question_title": "<string>",
    "profile_field": "<matched field key or 'custom'>",
    "value": "<value string to fill into the form>"
  }}
]
Only include questions that have a confident match. Return ONLY the JSON array, no extra commentary or markdown.
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json"
            }
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            res_data = response.json()

            raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            # Clean markdown if present
            cleaned_text = re.sub(r"^```json\s*", "", raw_text.strip())
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text)

            matches_json = json.loads(cleaned_text)

            matched_fields: List[MatchedField] = []
            matched_entry_ids = set()

            for item in matches_json:
                entry_id = str(item.get("entry_id", ""))
                val = str(item.get("value", ""))
                if entry_id and val:
                    matched_fields.append(
                        MatchedField(
                            entry_id=entry_id,
                            question_title=item.get("question_title", ""),
                            profile_field=item.get("profile_field", "gemini_matched"),
                            value=val,
                        )
                    )
                    matched_entry_ids.add(entry_id)

            unmatched_questions = [
                q.title for q in questions if q.entry_id not in matched_entry_ids
            ]

            return matched_fields, unmatched_questions
