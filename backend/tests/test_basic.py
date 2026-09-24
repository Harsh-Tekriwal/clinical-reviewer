"""
Basic validation tests. These deliberately avoid calling the real Gemini API
(no network, no API key needed) — they check the parts that don't depend on
a live model: schema shape, the health endpoint, and the document-validation
layer's failure cases.

Run with: pytest
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("GEMINI_API_KEY", "test-key-not-used")  # app just needs it to be set

from fastapi.testclient import TestClient

from document_service import DocumentValidationError, validate_and_read
from main import app
from schemas import ClinicalReport, PatientInformation, VitalSigns

client = TestClient(app)


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_analyze_rejects_empty_request():
    res = client.post("/api/analyze")
    assert res.status_code == 400


def test_clinical_report_schema_accepts_minimal_valid_data():
    report = ClinicalReport(
        report_summary="No significant findings noted.",
        patient_information=PatientInformation(),
        vitals=VitalSigns(),
    )
    assert report.symptoms == []
    assert report.missing_information == []


class _FakeUploadFile:
    def __init__(self, content_type):
        self.content_type = content_type


def test_validate_and_read_rejects_unsupported_file_type():
    fake_file = _FakeUploadFile(content_type="application/zip")
    try:
        validate_and_read(fake_file, b"some bytes")
        assert False, "expected DocumentValidationError"
    except DocumentValidationError:
        pass


def test_validate_and_read_rejects_empty_file():
    fake_file = _FakeUploadFile(content_type="image/png")
    try:
        validate_and_read(fake_file, b"")
        assert False, "expected DocumentValidationError"
    except DocumentValidationError:
        pass
