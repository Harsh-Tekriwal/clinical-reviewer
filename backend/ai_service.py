"""
AI/ML layer.

One Gemini call per document. The document (raw text, or the original
image/PDF bytes) is sent together with a system instruction and a response
schema, so Gemini returns JSON that matches ClinicalReport exactly, in one
step — no separate OCR pass, no second "now summarize this" call.

Why no separate OCR step: Gemini reads images and PDFs natively (typed,
scanned, and handwritten), so feeding it the raw file directly tends to be
more robust than OCR-then-LLM, which compounds OCR mistakes into extraction
mistakes. See docs/AI_ML_DESIGN.md and docs/TECHNICAL_DECISIONS.md.
"""

import json
import logging
import os
from typing import Optional

from google import genai
from google.genai import types

from schemas import ClinicalReport

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_INSTRUCTION = """You are a clinical documentation reviewer assistant.

You will be given a piece of clinical documentation, either as plain text or
as an image/PDF of a document. The document may be typed, scanned, or
handwritten; complete or incomplete; and may contain information unrelated
to a clinical review.

Follow these rules strictly:
1. Extract only information that is actually present in the document. Never
   invent, assume, or infer facts that are not stated or clearly implied.
2. If a field is not present or not legible, leave it empty and list it in
   "missing_information" instead of guessing.
3. If something is ambiguous, contradictory, or you are not confident about
   a reading (e.g. hard-to-read handwriting, an unclear abbreviation), note
   it in "potential_inconsistencies" or "requires_review" instead of
   silently picking one interpretation.
4. Ignore information that is clearly irrelevant to a clinical review.
5. All documents you will see are SYNTHETIC test data created for a software
   engineering assignment. Analyze them exactly as you would real clinical
   documentation, for demonstration purposes only. This is not medical
   advice and is not used for real patient care.
6. Respond using only the provided JSON schema — no extra commentary
   outside those fields.
"""


class AIProcessingError(Exception):
    """Raised with a message that is safe to show directly to the user."""


_client: Optional["genai.Client"] = None


def _get_client() -> "genai.Client":
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file — "
                "see .env.example."
            )
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def analyze_document(
    *,
    text: Optional[str] = None,
    file_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None,
) -> ClinicalReport:
    """
    Send a document to Gemini and return a validated ClinicalReport.
    Pass either `text`, or `file_bytes` + `mime_type` (not both).
    Raises AIProcessingError on any failure — network, API, or a response
    that doesn't match the schema.
    """
    client = _get_client()

    contents: list = []
    if file_bytes is not None:
        contents.append(types.Part.from_bytes(data=file_bytes, mime_type=mime_type))
        contents.append("Review the attached clinical document and produce the structured report.")
    elif text is not None and text.strip():
        contents.append(
            "Review the following clinical documentation and produce the "
            f"structured report:\n\n{text}"
        )
    else:
        raise AIProcessingError("No input was provided to analyze.")

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=ClinicalReport,
                temperature=0.2,
            ),
        )
    except Exception as exc:  # network issues, API errors, rate limits, etc.
        logger.exception("Gemini API call failed")
        raise AIProcessingError(f"The AI service call failed: {exc}") from exc

    # Prefer the SDK's own parsed object. Fall back to manual JSON parsing +
    # Pydantic validation in case `parsed` isn't populated for some reason —
    # either way, a bad/malformed response is caught here, not downstream.
    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, ClinicalReport):
        return parsed

    try:
        data = json.loads(response.text)
        return ClinicalReport(**data)
    except Exception as exc:
        logger.exception("Model response did not match the expected schema")
        raise AIProcessingError(
            "The AI model did not return a valid structured report."
        ) from exc
