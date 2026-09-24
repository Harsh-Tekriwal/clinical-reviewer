# AI/ML Design

## Model used

Google **Gemini** (`gemini-2.5-flash` by default — configurable via the
`GEMINI_MODEL` environment variable). Gemini was chosen because:

- it is natively **multimodal** — one API call accepts plain text, an
  image, or a PDF, and reads typed, scanned, and (to a good extent)
  handwritten content directly;
- it supports **schema-enforced structured output**, so the response can be
  constrained to match a Pydantic model rather than parsed out of free text;
- Google AI Studio offers a genuine **free tier** (no credit card required),
  which matters for a student project with no budget.

> Gemini model names change fairly often — new versions ship and older ones
> are retired on a published schedule. Check
> https://ai.google.dev/gemini-api/docs/models for the current recommended
> Flash model before deploying, and update `GEMINI_MODEL` if needed.

## How a submitted document is processed

1. **Text** input is sent to the model as-is, inside a prompt.
2. **Image** and **PDF** uploads are sent as raw bytes with their MIME type
   (`types.Part.from_bytes(...)`), so Gemini reads the actual file rather
   than working from text that was OCR'd separately in a prior step.
3. Before either of those happens, the document-processing layer confirms
   the file is a supported type, under the size limit, not corrupted, and
   (for PDFs) under a page-count cap — see `ARCHITECTURE.md`.

## How information is extracted and passed into the AI/ML pipeline

A single request combines:
- a **system instruction** describing the task and the rules the model must
  follow (below),
- the document itself (text or file bytes), and
- a **response schema** — the `ClinicalReport` Pydantic model — passed via
  Gemini's structured-output feature
  (`response_mime_type="application/json"`, `response_schema=ClinicalReport`).

## How the final report and structured output are produced

Gemini's structured-output mode constrains the model's output to match the
schema's fields and types, so the backend always gets back a **parseable**
object containing `report_summary` plus the detailed fields (patient
information, symptoms, diagnoses, medications, vitals, allergies,
observations, concerns, missing information, inconsistencies, items needing
review). The backend re-validates the result through the same Pydantic
model before storing it, so a malformed response can't silently reach the
database or the frontend.

The summary and the detailed structured output are produced in a **single
model call**, rather than two separate calls, to keep latency and cost down
for this assignment's scope. See `TECHNICAL_DECISIONS.md` for the trade-off
this involves.

## How missing or uncertain information is handled

The system instruction explicitly tells the model to:
- leave a field empty and list it under `missing_information` rather than
  guess, when information isn't present or isn't legible;
- put ambiguous or hard-to-read content (e.g. unclear handwriting) into
  `potential_inconsistencies` or `requires_review` instead of silently
  picking one interpretation;
- ignore information that's clearly irrelevant to a clinical review.

## How incorrect or unsupported generated information is reduced

- The prompt explicitly instructs the model to extract only what's actually
  present in the document and never invent or assume facts.
- Schema-enforced structured output means the model can't substitute
  free-form prose where a specific field is expected.
- `temperature` is set low (`0.2`) to favor consistent, literal extraction
  over creative variation.
- None of this eliminates misreadings entirely, which is exactly why the
  review-flagging fields above exist — as a safety net for a human
  reviewer, not a guarantee of correctness.

## How failures or malformed model responses are handled

- If the Gemini call itself raises an error (network issue, API error,
  etc.), the backend retries **once** before giving up.
- The SDK's own parsed object is used when available; if that's missing,
  the backend manually parses and re-validates the JSON against
  `ClinicalReport`.
- If the response still can't be turned into a valid `ClinicalReport`, it's
  treated as a failure rather than saving partial or malformed data.
- On failure, the report row is saved with `status = "failed"` and a
  human-readable `error_message`, and the frontend shows this clearly
  instead of a blank or broken report.
