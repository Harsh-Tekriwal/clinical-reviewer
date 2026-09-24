# Load .env before any local module reads os.environ at import time.
from dotenv import load_dotenv

load_dotenv()

import logging
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from ai_service import AIProcessingError, analyze_document
from database import Base, engine, get_db
from document_service import (
    ALLOWED_IMAGE_TYPES,
    ALLOWED_PDF_TYPE,
    DocumentValidationError,
    validate_and_read,
)
from models import Report
from schemas import ReportDetail, ReportListItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Clinical Document Reviewer")

# Tighten allow_origins to your deployed frontend URL before/at submission.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze", response_model=ReportDetail)
async def analyze(
    db: Session = Depends(get_db),
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    if not text and not file:
        raise HTTPException(status_code=400, detail="Provide either text or a file.")
    MAX_TEXT_LENGTH = 250       # characters
    MAX_FILE_SIZE = 10 * 1024   # 50 KB

    if text and len(text) > MAX_TEXT_LENGTH:
        raise HTTPException(status_code=413, detail="Document too large to process")

    if file is not None and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Document too large to process")
    raw_bytes = None
    mime_type = None

    if file is not None:
        raw_bytes = await file.read()
        try:
            validate_and_read(file, raw_bytes)
        except DocumentValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        input_type = "pdf" if file.content_type == ALLOWED_PDF_TYPE else "image"
        mime_type = file.content_type
    else:
        input_type = "text"

    # Create the row up front so a failed analysis still shows up in history
    # with a clear "failed" status, instead of silently disappearing.
    report_row = Report(input_type=input_type, status="pending")
    db.add(report_row)
    db.commit()
    db.refresh(report_row)

    try:
        try:
            result = analyze_document(
                text=text if input_type == "text" else None,
                file_bytes=raw_bytes,
                mime_type=mime_type,
            )
        except AIProcessingError:
            # Transient API hiccups are common enough to justify one retry
            # before giving up.
            result = analyze_document(
                text=text if input_type == "text" else None,
                file_bytes=raw_bytes,
                mime_type=mime_type,
            )
    except AIProcessingError as exc:
        report_row.status = "failed"
        report_row.error_message = str(exc)
        db.commit()
        raise HTTPException(
            status_code=502,
            detail="We couldn't generate a report for this document. Please try again.",
        )

    report_row.status = "completed"
    report_row.report_summary = result.report_summary
    report_row.full_report = result.model_dump()
    db.commit()
    db.refresh(report_row)
    return report_row


@app.get("/api/reports", response_model=list[ReportListItem])
def list_reports(db: Session = Depends(get_db)):
    return db.query(Report).order_by(Report.created_at.desc()).all()


@app.get("/api/reports/{report_id}", response_model=ReportDetail)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report_row = db.query(Report).filter(Report.id == report_id).first()
    if not report_row:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report_row
