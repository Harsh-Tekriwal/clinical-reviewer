from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text

from database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    input_type = Column(String, nullable=False)  # "text" | "image" | "pdf"
    status = Column(String, nullable=False, default="pending")  # pending | completed | failed

    report_summary = Column(Text, nullable=True)
    full_report = Column(JSON, nullable=True)  # the full ClinicalReport, as JSON
    error_message = Column(Text, nullable=True)
