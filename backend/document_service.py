"""
Document processing layer.

Responsible for validating an uploaded file BEFORE it's sent to the AI/ML
layer: type, size, and (for PDFs) that it actually opens and isn't absurdly
long. This is deliberately kept separate from ai_service.py so the AI logic
never has to deal with "is this even a real file" concerns, and so a bad
upload gets rejected quickly and cheaply instead of burning an AI call.
"""

import pymupdf  # PyMuPDF — "import fitz" is the old, now-deprecated spelling

MAX_FILE_SIZE_MB = 10
MAX_PDF_PAGES = 15

ALLOWED_PDF_TYPE = "application/pdf"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


class DocumentValidationError(Exception):
    """Raised with a message that is safe to show directly to the user."""


def validate_and_read(file, raw_bytes: bytes) -> None:
    """
    Validate an uploaded file. Raises DocumentValidationError with a
    user-facing message if the file can't be processed. Returns None
    (nothing to transform — Gemini reads the original bytes directly) if
    the file is OK to send to the AI layer.
    """
    if len(raw_bytes) == 0:
        raise DocumentValidationError("The uploaded file is empty.")

    size_mb = len(raw_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise DocumentValidationError(
            f"File is too large ({size_mb:.1f} MB). Max allowed is {MAX_FILE_SIZE_MB} MB."
        )

    content_type = file.content_type

    if content_type == ALLOWED_PDF_TYPE:
        try:
            doc = pymupdf.open(stream=raw_bytes, filetype="pdf")
        except Exception:
            raise DocumentValidationError(
                "This PDF could not be opened — it may be corrupted."
            )
        try:
            if doc.page_count == 0:
                raise DocumentValidationError("This PDF has no pages.")
            if doc.page_count > MAX_PDF_PAGES:
                raise DocumentValidationError(
                    f"This PDF has {doc.page_count} pages; the max supported is "
                    f"{MAX_PDF_PAGES}."
                )
        finally:
            doc.close()

    elif content_type in ALLOWED_IMAGE_TYPES:
        pass  # Gemini validates image bytes itself; nothing extra needed here

    else:
        raise DocumentValidationError(
            f"Unsupported file type: {content_type or 'unknown'}. "
            "Please upload a PDF or an image (JPEG, PNG, or WebP)."
        )
